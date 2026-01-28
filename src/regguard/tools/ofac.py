"""OFAC SDN compliance checking tool with fuzzy matching."""

from langchain_core.tools import tool
import httpx
import xmltodict
from datetime import datetime
from typing import Dict, Optional, List
from rapidfuzz import fuzz

# Official OFAC SDN list URL
OFAC_SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"

# In-Memory cache
_ofac_data: Optional[Dict] = None
_cache_time: Optional[datetime] = None


async def download_ofac_sdn_data() -> Dict:
    """
    Download and cache OFAC SDN data.
    
    Returns:
        OFAC SDN data dictionary
        
    Raises:
        Exception: If download fails and no valid cache exists
    """
    global _ofac_data, _cache_time

    # Check cache (24 hrs)
    if _ofac_data and _cache_time:
        span = datetime.now() - _cache_time
        if span.total_seconds() < 86400:
            print("📦 Using cached OFAC SDN data")
            return _ofac_data
    
    print("⬇️ Downloading OFAC data...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OFAC_SDN_URL, 
                timeout=180.0, 
                follow_redirects=True
            )
        
        # Check status
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'xml' not in content_type.lower() and 'text' not in content_type.lower():
            raise Exception(f"Unexpected content type: {content_type}")
        
        # Check size
        if not response.content or len(response.content) < 1000:
            raise Exception(f"Response too small ({len(response.content)} bytes)")
        
        print(f"✅ Downloaded {len(response.content):,} bytes")
        print("📄 Parsing XML...")
        
        # Parse XML
        try:
            data = xmltodict.parse(response.content)
        except Exception as parse_error:
            raise Exception(f"XML parsing failed: {parse_error}")
        
        # Cache it
        _ofac_data = data
        _cache_time = datetime.now()
        
        # Show stats
        entries = data.get('sdnList', {}).get('sdnEntry', [])
        count = len(entries) if isinstance(entries, list) else 1
        print(f"✅ Loaded {count:,} entries")
        
        return data
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        
        # Fallback to stale cache
        if _ofac_data:
            print("⚠️ Using stale cache")
            return _ofac_data
        
        raise Exception(f"Failed to get OFAC data: {e}")


def extract_addresses(entry: Dict) -> List[str]:
    """
    Extract addresses from an OFAC entry.
    
    Args:
        entry: OFAC SDN entry dictionary
        
    Returns:
        List of formatted address strings
    """
    addresses = []
    
    addr_list = entry.get('addressList', {}).get('address', [])
    if isinstance(addr_list, dict):
        addr_list = [addr_list]
    
    for addr in addr_list:
        # Build address from available fields
        parts = []
        
        for field in ['address1', 'address2', 'address3', 'city', 'stateOrProvince', 'postalCode', 'country']:
            value = addr.get(field, '')
            if value:
                parts.append(value)
        
        if parts:
            addresses.append(', '.join(parts))
    
    return addresses


@tool
async def check_ofac(name: str, fuzzy: bool = True, threshold: int = 85) -> str:
    """
    Check if a name is on the OFAC SDN list with fuzzy matching support.

    Args:
        name: Name of company or person to check
        fuzzy: Use fuzzy matching to handle typos (default: True)
        threshold: Fuzzy match threshold 0-100 (default: 85, higher = stricter)
    
    Returns:
        Match details including aliases, addresses, and remarks, or "No match found"
    """
    # Input validation
    if not name or not name.strip():
        return "❌ Error: Please provide a name to search"
    
    name = name.strip()

    try:
        # Get OFAC data
        data = await download_ofac_sdn_data()

        # Navigate to entries
        sdn_list = data.get('sdnList', {})
        entries = sdn_list.get('sdnEntry', [])
        pub_date = sdn_list.get('publshInformation', {}).get('Publish_Date', 'Unknown')
        
        # Ensure entries is a list
        if not isinstance(entries, list):
            entries = [entries]
        
        # Search
        search_lower = name.lower()
        matches = []
        
        for entry in entries:
            # Get primary name
            last_name = entry.get('lastName', '')
            first_name = entry.get('firstName', '')
            full_name = f"{first_name} {last_name}".strip()
            
            # Collect all names (primary + aliases)
            all_names = [full_name]
            
            # Get aliases
            akas = entry.get('akaList', {}).get('aka', [])
            if isinstance(akas, dict):
                akas = [akas]
            
            for aka in akas:
                aka_name = f"{aka.get('firstName', '')} {aka.get('lastName', '')}".strip()
                if aka_name:
                    all_names.append(aka_name)
            
            # Check for match (exact or fuzzy)
            is_match = False
            match_score = 0
            matched_name = full_name
            
            # Check for match (exact or fuzzy)
            is_match = False
            match_score = 0
            matched_name = full_name
            
            if fuzzy:
                # Fuzzy matching - check full name and individual words
                for check_name in all_names:
                    # Score for full name match
                    full_score = fuzz.token_sort_ratio(search_lower, check_name.lower())
                    
                    # Score for individual word matches
                    name_words = check_name.lower().split()
                    word_scores = [fuzz.ratio(search_lower, word) for word in name_words if word]
                    best_word_score = max(word_scores) if word_scores else 0
                    
                    # Use the better score
                    score = max(full_score, best_word_score)
                    
                    if score >= threshold and score > match_score:
                        is_match = True
                        match_score = score
                        matched_name = check_name
            else:
                # Exact substring matching
                for check_name in all_names:
                    if search_lower in check_name.lower():
                        is_match = True
                        match_score = 100
                        matched_name = check_name
                        break
            
            if is_match:
                # Extract program
                program_data = entry.get('programList', {})
                program = program_data.get('program', 'Unknown') if isinstance(program_data, dict) else 'Unknown'
                
                # Extract addresses
                addresses = extract_addresses(entry)
                
                # Extract remarks
                remarks = entry.get('remarks', '')
                
                matches.append({
                    'name': full_name,
                    'matched_name': matched_name if matched_name != full_name else None,
                    'match_score': match_score,
                    'aliases': [n for n in all_names[1:] if n][:3],  # First 3 aliases
                    'type': entry.get('sdnType', 'Unknown'),
                    'program': program,
                    'addresses': addresses[:2],  # First 2 addresses
                    'remarks': remarks,
                    'uid': entry.get('uid', 'Unknown')
                })
        
        # Sort by match score (best matches first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Format results
        if matches:
            results = []
            for i, match in enumerate(matches[:5], 1):  # Top 5 matches
                result = f"MATCH #{i}: {match['name']}"
                
                # Show match score if fuzzy matching
                if fuzzy and match['match_score'] < 100:
                    result += f" ({match['match_score']}% match)"
                
                result += f"\n  Type: {match['type']}"
                result += f"\n  Program: {match['program']}"
                
                # Show which name matched if it was an alias
                if match['matched_name']:
                    result += f"\n  Matched: {match['matched_name']}"
                
                # Show aliases
                if match.get('aliases'):
                    result += f"\n  AKAs: {', '.join(match['aliases'])}"
                
                # Show addresses
                if match.get('addresses'):
                    result += f"\n  Addresses:"
                    for addr in match['addresses']:
                        result += f"\n    • {addr}"
                
                # Show remarks (truncated)
                if match.get('remarks'):
                    remarks_text = match['remarks']
                    if len(remarks_text) > 200:
                        remarks_text = remarks_text[:200] + "..."
                    result += f"\n  Remarks: {remarks_text}"
                
                result += f"\n  UID: {match['uid']}"
                results.append(result)
            
            match_type = "Fuzzy" if fuzzy else "Exact"
            header = f"⚠️ OFAC SANCTIONS MATCH - {len(matches)} result(s) ({match_type} search)\n"
            header += f"📅 List Published: {pub_date}\n"
            header += f"🔍 Search: '{name}'\n"
            header += "="*60 + "\n\n"
            
            return header + "\n\n".join(results)
        
        match_type = "fuzzy" if fuzzy else "exact"
        return (
            f"✅ NO SANCTIONS MATCH\n"
            f"📅 List Published: {pub_date}\n"
            f"🔍 Search: '{name}' ({match_type} search)\n"
            f"No matches found on OFAC SDN list."
        )
    
    except Exception as e:
        return (
            f"❌ OFAC CHECK FAILED\n"
            f"Unable to check sanctions list: {str(e)}\n\n"
            f"This could be due to:\n"
            f"  • Network connectivity issues\n"
            f"  • OFAC server temporarily unavailable\n"
            f"  • Data format changes\n\n"
            f"Please try again later."
        )


# if __name__ == "__main__":
#     import asyncio
    
#     async def test():
#         print("="*60)
#         print("TEST 1: Download and validate")
#         print("="*60)
        
#         try:
#             data = await download_ofac_sdn_data()
#             print("\n✅ Download test passed")
#         except Exception as e:
#             print(f"\n❌ Download test failed: {e}")
#             return
        
#         print("\n" + "="*60)
#         print("TEST 2: Exact search for PUTIN")
#         print("="*60)
        
#         result = await check_ofac("PUTIN")
#         print(result)
        
#         print("\n" + "="*60)
#         print("TEST 3: Fuzzy search with typo (Puttin)")
#         print("="*60)
        
#         result = await check_ofac("Puttin", fuzzy=True, threshold=80)
#         print(result)
        
#         print("\n" + "="*60)
#         print("TEST 4: Search with typo (Kim Jong Un → Kim Jon Un)")
#         print("="*60)
        
#         result = await check_ofac("Kim Jon Un", fuzzy=True)
#         print(result)
        
#         print("\n" + "="*60)
#         print("TEST 5: Non-existent entity")
#         print("="*60)
        
#         result = await check_ofac("Apple Inc")
#         print(result)
        
#         print("\n" + "="*60)
#         print("TEST 6: Exact matching only (disable fuzzy)")
#         print("="*60)
        
#         result = await check_ofac("PUTIN", fuzzy=False)
#         print(result)
    
#     asyncio.run(test())