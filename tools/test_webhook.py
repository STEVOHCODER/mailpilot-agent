import json, os, sys, requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "")
CF_NS = os.environ.get("CF_KV_NAMESPACE", "")

print(f"CF_TOKEN: {bool(CF_TOKEN)} CF_ACC: {bool(CF_ACC)} CF_NS: {bool(CF_NS)}")

base = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACC}/storage/kv/namespaces/{CF_NS}"
h = {"Authorization": f"Bearer {CF_TOKEN}"}

# Store a command
cmd = [{"from": "250786508880", "text": "/plus stevohsunb@gmail.com:kv debug test", "ts": 1234567890}]
r = requests.put(f"{base}/values/pending", headers={**h, "Content-Type": "application/json"}, 
                   data=json.dumps(cmd), timeout=15)
print(f"PUT: {r.status_code} {r.text[:100]}")

# Read it back  
r2 = requests.get(f"{base}/values/pending", headers=h, timeout=15)
print(f"GET: {r2.status_code} type={type(r2.json()).__name__} data={r2.text[:200]}")

# Now test what CommandProcessor would do
from agent.reply import parse_plus_command
data = r2.json()
print(f"isinstance list: {isinstance(data, list)}")
print(f"isinstance dict: {isinstance(data, dict)}")

if isinstance(data, list):
    commands = data
elif isinstance(data, dict):
    commands = [data]
else:
    commands = []

print(f"Commands to process: {len(commands)}")
for cmd in commands:
    parsed = parse_plus_command(cmd.get("text", ""))
    print(f"  text={cmd.get('text','')[:50]} -> parsed={parsed}")

# Delete
requests.delete(f"{base}/values/pending", headers=h, timeout=10)
print("Cleaned up")
