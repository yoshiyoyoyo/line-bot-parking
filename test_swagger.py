import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get('https://tdx.transportdata.tw/api-docs/swagger/basic/v1/Parking')
        if r.status_code == 200:
            paths = r.json().get('paths', {})
            for p in paths:
                print("BASIC PATH:", p)
        
        r2 = await client.get('https://tdx.transportdata.tw/api-docs/swagger/advanced/v3/Parking')
        if r2.status_code == 200:
            for p in r2.json().get('paths', {}):
                print("ADVANCED PATH:", p)

if __name__ == '__main__':
    asyncio.run(main())
