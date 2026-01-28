"""Debug OFAC download."""

import asyncio
import httpx

async def debug_download():
    print("⬇️ Attempting download...")
    
    url = "https://www.treasury.gov/ofac/downloads/sdn.xml"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=120.0, follow_redirects=True)
    
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📦 Content Length: {len(response.content)} bytes")
    print(f"📝 Content Type: {response.headers.get('content-type', 'unknown')}")
    
    # Show first 500 characters
    print("\n" + "="*60)
    print("FIRST 500 CHARACTERS OF RESPONSE")
    print("="*60)
    print(response.text[:500])
    
    # Check if it's actually XML
    if response.text.strip().startswith('<?xml'):
        print("\n✅ Looks like XML!")
    elif response.text.strip().startswith('<'):
        print("\n⚠️ Looks like HTML (probably error page)")
    else:
        print("\n❌ Not XML or HTML - unknown format")

asyncio.run(debug_download())