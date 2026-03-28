import asyncio
from linebot.v3.webhooks import WebhookParser, LocationMessageContent, MessageEvent, UserSource
from linebot.v3.messaging import AsyncMessagingApi, AsyncApiClient, Configuration, ReplyMessageRequest, TextMessage
import os

async def dummy_reply(*args, **kwargs):
    print("Mock reply_message called with:", args, kwargs)

async def test_main():
    try:
        from main import handle_location_message
        
        # Mocking event
        msg = LocationMessageContent(
            id="123456",
            title="My Location",
            address="Taiwan",
            latitude=25.0478,
            longitude=121.5318
        )
        src = UserSource(user_id="U1234567890abcdef")
        event = MessageEvent(
            type="message",
            message=msg,
            timestamp=123456789,
            source=src,
            reply_token="dummy_token"
        )
        
        # Monkey patch AsyncMessagingApi inside main
        import main
        orig_AsyncMessagingApi = main.AsyncMessagingApi
        class MockApi:
            def __init__(self, client): pass
            async def reply_message(self, request):
                print("Mock api reply called:", request)

        main.AsyncMessagingApi = MockApi
        
        print("Calling handle_location_message...")
        await handle_location_message(event)
        print("Success without exceptions!")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_main())
