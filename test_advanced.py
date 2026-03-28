import asyncio
import httpx
from parking_tdx import get_tdx_token

async def main():
    client_id = "lin0504000-4197e491-5bbc-41a8"
    client_secret = "a0deb9a3-2538-437f-a14b-7cbb322a2a3f"
    token = await get_tdx_token(client_id, client_secret)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    url = "https://tdx.transportdata.tw/api/advanced/v1/Parking/OffStreet/CarPark?$spatialFilter=nearby(25.033964,121.564472,500)&$format=JSON"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        print("Status:", r.status_code)
        if r.status_code == 200:
            print("Items:", len(r.json()))
            if len(r.json()) > 0:
                print("First:", r.json()[0]['CarParkName'])

if __name__ == '__main__':
    asyncio.run(main())
