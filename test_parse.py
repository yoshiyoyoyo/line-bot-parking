import sys
sys.path.insert(0, '.venv/lib/python3.9/site-packages')
from linebot.v3.webhook import WebhookParser
parser = WebhookParser("2b6d9dd0486d5eecd4767d2c79c200ba")
print("WebhookParser built successfully")
