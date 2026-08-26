import requests

WORKER = "https://mailpilot-bridge.growths.workers.dev"
VERIFY = "28ada79281805079cda4f9b9d3ae5877"

print(f"Testing {WORKER}")

r = requests.get(f"{WORKER}/", timeout=10)
print(f"Root: {r.status_code} {r.text[:80]}")

r = requests.get(f"{WORKER}/webhook", params={
    "hub.mode": "subscribe",
    "hub.verify_token": VERIFY,
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print(f"Verify: {r.status_code} {r.text[:80]}")

if r.status_code == 200 and r.text == "CHALLENGE_ACCEPTED":
    print("WEBHOOK VERIFICATION WORKS!")
else:
    print("STILL BROKEN")

# Test 3: Wrong token
r = requests.get(f"{WORKER}/", params={
    "hub.mode": "subscribe",
    "hub.verify_token": "wrong",
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 3 - Wrong token:", r.status_code, r.text[:100])
