import asyncio
import os
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration, PushMessageRequest, TextMessage

async def main():
    token = "3+582YNFK/+a+4MJqb+Ep+HYdSEYaCNKo0ew6qPikBlw7LS2DlaOoIwD1+EHPNk9HG7snU8vizmrclM7OiWWpt2rLo2O3Gd3Bl33g82k3Rl3Br5C00CKJv1qdFREpjT2IuiKC6IfyvFKV/lqpIeFUAdB04t89/1O/w1cDnyilFU="
    config = Configuration(access_token=token)
    async with AsyncApiClient(config) as client:
        api = AsyncMessagingApi(client)
        req = PushMessageRequest(
            to="Ue01bc54d825cd5bf090b0164aeb0905e",
            messages=[TextMessage(text="Test reply from developer tools!")]
        )
        try:
            res = await api.push_message(req)
            print("Successfully sent:", res)
        except Exception as e:
            print("Exception:", e)

asyncio.run(main())
