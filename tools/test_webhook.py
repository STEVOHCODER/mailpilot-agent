import requests

WORKER = "https://mailpilot-bridge.growths.workers.dev"
VERIFY = "28ada79281805079cda4f9b9d3ae5877"

# Test 1: Basic connectivity
r = requests.get(f"{WORKER}/test", timeout=10)
print("Test 1 - Basic:", r.status_code, r.text[:100])

# Test 2: Verification challenge (what Meta sends)
r = requests.get(f"{WORKER}/webhook", params={
    "hub.mode": "subscribe",
    "hub.verify_token": VERIFY,
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 2 - Verify:", r.status_code, r.text[:100])

# Test 3: Wrong token
r = requests.get(f"{WORKER}/webhook", params={
    "hub.mode": "subscribe",
    "hub.verify_token": "wrong_token",
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 3 - Wrong token:", r.status_code, r.text[:100])
