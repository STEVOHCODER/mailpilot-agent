"""Deploy the MailPilot Cloudflare Worker.
Usage: CF_ACCOUNT_ID=... CF_API_TOKEN=... CF_KV_NAMESPACE=... python deploy.py
"""
import requests, os, json

CF_ACC = os.environ["CF_ACCOUNT_ID"]
CF_TOK = os.environ["CF_API_TOKEN"]
CF_NS = os.environ["CF_KV_NAMESPACE"]

with open(os.path.join(os.path.dirname(__file__), "worker.js"), "rb") as f:
    script = f.read()

metadata = {
    "main_module": "index.js",
    "compatibility_date": "2026-01-01",
    "bindings": [
        {"name": "MAILPLOT_KV", "namespace_id": CF_NS, "type": "kv_namespace"}
    ]
}

url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACC}/workers/scripts/mailpilot-bridge"
files = {
    "metadata": (None, json.dumps(metadata), "application/json"),
    "index.js": ("index.js", script, "application/javascript+module"),
}

r = requests.put(url, headers={"Authorization": f"Bearer {CF_TOK}"}, files=files, timeout=30)
data = r.json()
print(f"Success: {data.get('success')}")
if data.get("errors"):
    for e in data["errors"]:
        print(f"Error: {e}")
