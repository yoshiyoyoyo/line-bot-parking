import asyncio
import httpx
from parking_tdx import get_tdx_token

async def main():
    client_id = "lin0504000-4197e491-5bbc-41a8"
    client_secret = "a0deb9a3-2538-437f-a14b-7cbb322a2a3f"
    token = await get_tdx_token(client_id, client_secret)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    urls = [
        "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark?$top=1&$format=JSON",
        "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability?$top=1&$format=JSON",
    ]
    
    async with httpx.AsyncClient() as client:
        for u in urls:
            r = await client.get(u, headers=headers)
            print("URL:", u)
            print("Status:", r.status_code)
            if r.status_code == 200:
                print("Keys:", r.json()[0].keys() if len(r.json()) > 0 else "Empty")

if __name__ == '__main__':
    asyncio.run(main())
