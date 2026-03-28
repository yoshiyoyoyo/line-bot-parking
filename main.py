import os
from fastapi import FastAPI, Request, HTTPException
from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    LocationMessageContent
)
from dotenv import load_dotenv

from parking_tdx import get_nearby_parking
from flex_builder import build_parking_carousel

load_dotenv()

app = FastAPI()

channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN')

configuration = Configuration(access_token=channel_access_token)
parser = WebhookParser(channel_secret)

# Mock DB mapping User ID to TDX credentials
MOCK_DB: dict = {
    # "U1234567890abcdef...": {"client_id": "YOUR_TDX_CLEINT_ID", "client_secret": "YOUR_TDX_CLIENT_SECRET"}
}

DEFAULT_CLIENT_ID = os.getenv("TDX_CLIENT_ID") or "YOUR_TDX_CLIENT_ID"
DEFAULT_CLIENT_SECRET = os.getenv("TDX_CLIENT_SECRET") or "YOUR_TDX_CLIENT_SECRET"

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    body_str = body.decode('utf-8')

    try:
        events = parser.parse(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, LocationMessageContent):
            await handle_location_message(event)

    return 'OK'

async def handle_location_message(event):
    user_id = event.source.user_id
    lat = event.message.latitude
    lon = event.message.longitude

    # Get credentials
    creds = MOCK_DB.get(user_id)
    if not creds:
        client_id = DEFAULT_CLIENT_ID
        client_secret = DEFAULT_CLIENT_SECRET
    else:
        client_id = creds['client_id']
        client_secret = creds['client_secret']
        
    async with AsyncApiClient(configuration) as api_client:
        line_bot_api = AsyncMessagingApi(api_client)
        
        if client_id == "YOUR_TDX_CLIENT_ID":
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="系統尚未設定 TDX 憑證，請聯絡管理員以更新 MOCK_DB。")]
                )
            )
            return

        parkings = await get_nearby_parking(lat, lon, client_id, client_secret)
        
        if not parkings:
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="附近 1 公里內找不到停車場。")]
                )
            )
            return
            
        flex_dict = build_parking_carousel(parkings)
        flex_container = FlexContainer.from_dict(flex_dict)
        
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[FlexMessage(alt_text="附近停車場資訊", contents=flex_container)]
            )
        )
