import asyncio
import httpx
from parking_tdx import get_tdx_token

async def main():
    client_id = "lin0504000-4197e491-5bbc-41a8"
    client_secret = "a0deb9a3-2538-437f-a14b-7cbb322a2a3f"
    token = await get_tdx_token(client_id, client_secret)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/City/Taipei?$top=1&$format=JSON"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                print("Dict keys:", data.keys())
                for k in data.keys():
                    if isinstance(data[k], list):
                        print(f"{k} is a list of len {len(data[k])}")
                        if len(data[k]) > 0:
                            print(data[k][0].keys())
            else:
                print("List of len:", len(data))
                if len(data) > 0:
                    print(data[0].keys())

if __name__ == '__main__':
    asyncio.run(main())
