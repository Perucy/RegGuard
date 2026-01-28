"""Explore OFAC XML structure."""

import asyncio
import httpx
import xmltodict
import json

async def explore():
    print("⬇️ Downloading XML...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.treasury.gov/ofac/downloads/sdn.xml",
            timeout=120.0,
            follow_redirects=True 
        )
    
    print("📄 Parsing XML...")
    print(response.status_code)
    print(response.text[:1000] + "\n...")
    data = xmltodict.parse(response.text)
    
    print("\n" + "="*60)
    print("ROOT STRUCTURE")
    print("="*60)
    
    # Show top-level keys
    print("\nTop-level keys:")
    for key in data.keys():
        print(f"  • {key}")
    
    # Navigate into the data
    root = data.get('sanctionsData') or data.get('sdnList')
    
    print("\nSecond-level keys:")
    for key in root.keys():
        print(f"  • {key}")
    
    # Find where entries are
    print("\n" + "="*60)
    print("LOOKING FOR SDN ENTRIES...")
    print("="*60)
    
    # Try common names
    possible_entry_keys = ['sdnEntries', 'sdnEntry', 'entries', 'entry', 'records']
    
    for key in possible_entry_keys:
        if key in root:
            entries = root[key]
            count = len(entries) if isinstance(entries, list) else 1
            print(f"\n✅ Found entries at: '{key}'")
            print(f"   Count: {count}")
            
            # Show first entry structure
            first = entries[0] if isinstance(entries, list) else entries
            print(f"\n   First entry keys:")
            for field in first.keys():
                print(f"     • {field}")
            
            # Show sample entry
            print(f"\n   Sample entry:")
            print(json.dumps(first, indent=2)[:1000])
            break
    
    # Also check publication date
    pub_info = root.get('publicationInfo') or root.get('publshInformation')
    if pub_info:
        print("\n" + "="*60)
        print("PUBLICATION INFO")
        print("="*60)
        print(json.dumps(pub_info, indent=2))

asyncio.run(explore())