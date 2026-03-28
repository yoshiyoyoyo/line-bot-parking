import asyncio
from parking_tdx import get_tdx_token, get_nearby_parking
import httpx

async def main():
    client_id = "lin0504000-4197e491-5bbc-41a8"
    client_secret = "a0deb9a3-2538-437f-a14b-7cbb322a2a3f"
    
    print("Testing token...")
    token = await get_tdx_token(client_id, client_secret)
    print("Token fetched:", "SUCCESS" if token else "FAILED")
    
    if token:
        print("Testing nearby parking near Taipei 101 (25.033964, 121.564472)...")
        results = await get_nearby_parking(25.033964, 121.564472, client_id, client_secret)
        print(f"Found {len(results)} parking spots.")
        for r in results[:2]:
            print(" -", r)

if __name__ == "__main__":
    asyncio.run(main())
