import asyncio
import httpx
from parking_tdx import get_tdx_token

async def main():
    client_id = "lin0504000-4197e491-5bbc-41a8"
    client_secret = "a0deb9a3-2538-437f-a14b-7cbb322a2a3f"
    token = await get_tdx_token(client_id, client_secret)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    bases = [
        "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/City/Taipei?$top=1&$format=JSON",
        "https://tdx.transportdata.tw/api/advanced/v3/Parking/OffStreet/CarPark?$top=1&$format=JSON",
        "https://tdx.transportdata.tw/api/advanced/v2/Parking/OffStreet/CarPark?$top=1&$format=JSON",
        "https://tdx.transportdata.tw/api/advanced/v1/Parking/OffStreet/CarPark?$top=1&$format=JSON",
        "https://tdx.transportdata.tw/api/advanced/V3/Parking/OffStreet/CarPark?$top=1&$format=JSON"
    ]
    
    async with httpx.AsyncClient() as client:
        for u in bases:
            try:
                r = await client.get(u, headers=headers)
                print(f"{r.status_code} - {u.split('?')[0]}")
                if r.status_code == 200:
                    data = r.json()
                    print(f"Type: {type(data)}")
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, list) and len(v) > 0:
                                print(f"  List key '{k}' item keys:", v[0].keys())
                                break
                    elif isinstance(data, list) and len(data) > 0:
                        print("  List item keys:", data[0].keys())
            except Exception as e:
                print(e)

if __name__ == '__main__':
    asyncio.run(main())
