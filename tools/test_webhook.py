import requests

VERIFY = "28ada79281805079cda4f9b9d3ae5877"
URLS = [
    "https://mailpilot.growths.dev",
    "https://mailpilot-bridge.growths.workers.dev",
]

for WORKER in URLS:
    print(f"\n--- Testing {WORKER} ---")
    try:
        r = requests.get(f"{WORKER}/", timeout=8)
        print(f"  Root: {r.status_code} {r.text[:80]}")
    except Exception as e:
        print(f"  Root: ERROR {e}")

    try:
        r = requests.get(f"{WORKER}/webhook", params={
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY,
            "hub.challenge": "CHALLENGE_ACCEPTED"
        }, timeout=8)
        print(f"  Verify: {r.status_code} {r.text[:80]}")
        if r.status_code == 200 and r.text == "CHALLENGE_ACCEPTED":
            print(f"  *** VERIFICATION WORKS at {WORKER} ***")
    except Exception as e:
        print(f"  Verify: ERROR {e}")

# Test 3: Wrong token
r = requests.get(f"{WORKER}/", params={
    "hub.mode": "subscribe",
    "hub.verify_token": "wrong",
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 3 - Wrong token:", r.status_code, r.text[:100])
