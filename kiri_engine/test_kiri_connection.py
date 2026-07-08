import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.kiriengine.app/api"
API_KEY = os.environ.get("KIRI_API_KEY")

if not API_KEY:
    raise RuntimeError("KIRI_API_KEY not found. Check your .env file.")

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

url = f"{BASE_URL}/v1/open/balance"

response = requests.get(url, headers=headers, timeout=30)

print("HTTP status:", response.status_code)
print("Response:")
print(response.text)