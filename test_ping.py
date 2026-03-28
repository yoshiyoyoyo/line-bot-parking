import urllib.request
import hmac
import hashlib
import base64

channel_secret = "2b6d9dd0486d5eecd4767d2c79c200ba"
body = b'{"events":[]}'
hash = hmac.new(channel_secret.encode('utf-8'), body, hashlib.sha256).digest()
signature = base64.b64encode(hash).decode('utf-8')

req = urllib.request.Request("http://127.0.0.1:8000/callback", data=body)
req.add_header('X-Line-Signature', signature)
req.add_header('Content-Type', 'application/json')

try:
    response = urllib.request.urlopen(req)
    print("Success:", response.read().decode('utf-8'))
except Exception as e:
    print("Failed:", e)
