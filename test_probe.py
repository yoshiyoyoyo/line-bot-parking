import asyncio
import httpx
from parking_tdx import get_tdx_token

async def main():
    client_id = "lin0504000-4197e491-5bbc-41a8"
    client_secret = "a0deb9a3-2538-437f-a14b-7cbb322a2a3f"
    token = await get_tdx_token(client_id, client_secret)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    bases = [
        "https://tdx.transportdata.tw/api/advanced/v1/Parking/OffStreet/CarPark",
        "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/City/Taipei",
        "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/Taipei",
        "https://tdx.transportdata.tw/api/advanced/V3/Parking/OffStreet/CarPark",
        "https://tdx.transportdata.tw/api/basic/v3/Parking/OffStreet/CarPark/City/Taipei",
        "https://tdx.transportdata.tw/api/basic/v1/Parking/CarPark/City/Taipei",
        "https://tdx.transportdata.tw/api/advanced/v1/Parking/CarPark",
        "https://tdx.transportdata.tw/api/advanced/v2/Parking/OffStreet/CarPark"
    ]
    
    async with httpx.AsyncClient() as client:
        for b in bases:
            url = b + "?$top=1&$format=JSON"
            r = await client.get(url, headers=headers)
            print(f"{r.status_code} - {b}")
            if r.status_code == 200:
                print("Works!", r.json()[:1])

if __name__ == '__main__':
    asyncio.run(main())
