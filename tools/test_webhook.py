import json, os, requests

WORKER = "https://mailpilot-bridge.growths.workers.dev"
VERIFY = "28ada79281805079cda4f9b9d3ae5877"
CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "")
CF_NS = os.environ.get("CF_KV_NAMESPACE", "")

print(f"CF_TOKEN set: {bool(CF_TOKEN)}")
print(f"CF_ACC: {CF_ACC}")
print(f"CF_NS: {CF_NS}")

if CF_TOKEN and CF_ACC and CF_NS:
    base = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACC}/storage/kv/namespaces/{CF_NS}"
    h = {"Authorization": f"Bearer {CF_TOKEN}"}
    
    r = requests.get(f"{base}/values/pending", headers=h, timeout=15)
    print(f"KV GET pending: {r.status_code} {r.text[:300]}")
    
    r2 = requests.get(f"{base}/keys", headers=h, timeout=15)
    print(f"KV keys: {r2.text[:300]}")
    
    cmd = [{"from": "250786508880", "text": "/plus stevohsunb@gmail.com:kv api test", "ts": 1234567890}]
    r3 = requests.put(f"{base}/values/pending", headers={**h, "Content-Type": "application/json"}, 
                       data=json.dumps(cmd), timeout=15)
    print(f"KV PUT: {r3.status_code} {r3.text[:200]}")
    
    r4 = requests.get(f"{base}/values/pending", headers=h, timeout=15)
    print(f"KV READ back: {r4.status_code} {r4.text[:300]}")
else:
    print("CF env vars not set!")
