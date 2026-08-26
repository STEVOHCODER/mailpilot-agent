import json, requests

WORKER = "https://mailpilot-bridge.growths.workers.dev"
VERIFY = "28ada79281805079cda4f9b9d3ae5877"

# Test 1: Verification
r = requests.get(f"{WORKER}/webhook", params={
    "hub.mode": "subscribe",
    "hub.verify_token": VERIFY,
    "hub.challenge": "TEST123"
}, timeout=10)
print(f"Verify: {r.status_code} {r.text}")
assert r.status_code == 200 and r.text == "TEST123", "VERIFY FAILED"

# Test 2: Simulate incoming WhatsApp message
payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {"display_phone_number": "15551999734", "phone_number_id": "1287317304459774"},
                "contacts": [{"profile": {"name": "Steven"}, "wa_id": "250786508880"}],
                "messages": [{
                    "from": "250786508880",
                    "id": "wamid.TEST123",
                    "timestamp": "1234567890",
                    "type": "text",
                    "text": {"body": "/plus test@acme.com:Hello from WhatsApp test"}
                }]
            },
            "field": "messages"
        }]
    }]
}
r = requests.post(f"{WORKER}/webhook", json=payload, timeout=10)
print(f"POST: {r.status_code} {r.json()}")

# Test 3: Simulate non-command message
payload2 = dict(payload)
payload2["entry"][0]["changes"][0]["value"]["messages"] = [{
    "from": "250786508880", "id": "wamid.TEST456", "timestamp": "1234567890",
    "type": "text", "text": {"body": "Just a regular message"}
}]
r2 = requests.post(f"{WORKER}/webhook", json=payload2, timeout=10)
print(f"POST non-cmd: {r2.status_code} {r2.json()}")

print("\nAll tests passed!")

# Test 3: Wrong token
r = requests.get(f"{WORKER}/", params={
    "hub.mode": "subscribe",
    "hub.verify_token": "wrong",
    "hub.challenge": "CHALLENGE_ACCEPTED"
}, timeout=10)
print("Test 3 - Wrong token:", r.status_code, r.text[:100])
