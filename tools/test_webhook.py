import requests

WORKER = "https://mailpilot-bridge.growths.workers.dev"
VERIFY = "28ada79281805079cda4f9b9d3ae5877"

# Test 1: Basic
r = requests.get(f"{WORKER}/", timeout=10)
print("Test 1 - Root:", r.status_code, r.text[:100])

# Test 2: Verification challenge at /webhook (what Meta actually sends)
r = requests.get(f"{WORKER}/webhook", params={
    "hub.mode": "subscribe",
    "hub.verify_token": VERIFY,
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 2 - Verify /webhook:", r.status_code, r.text[:100])
assert r.status_code == 200 and r.text == "CHALLENGE_ACCEPTED", "VERIFICATION FAILED at /webhook"
print("VERIFY OK at /webhook - challenge returned correctly")

# Test 3: Wrong token
r = requests.get(f"{WORKER}/", params={
    "hub.mode": "subscribe",
    "hub.verify_token": "wrong",
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 3 - Wrong token:", r.status_code, r.text[:100])
