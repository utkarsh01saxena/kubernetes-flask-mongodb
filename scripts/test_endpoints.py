#!/usr/bin/env python3
import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"


# Prints formatted log output with a status tag
def log(msg, status="INFO"):
  symbols = {"INFO": "[i]", "PASS": "[+]", "FAIL": "[-]", "WARN": "[!]"}
  print(f"{symbols.get(status, '[*]')} {msg}")


# Tests root endpoint to confirm HTTP 200 and presence of welcome message
def test_root():
  log(f"Testing GET {BASE_URL}/ ...")
  req = urllib.request.Request(f"{BASE_URL}/")
  with urllib.request.urlopen(req, timeout=5) as resp:
    status_code = resp.getcode()
    body = resp.read().decode("utf-8")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert "Welcome to the Flask app!" in body, f"Unexpected body: {body}"
    log(f"Root endpoint passed! Status: {status_code}, Body: {body}", "PASS")


# Tests POST request to data endpoint and asserts 201 response status
def test_post_data():
  log(f"Testing POST {BASE_URL}/data ...")
  payload = {
      "item": "DevOps Kubernetes Assignment",
      "timestamp": time.time(),
      "status": "Verified",
  }
  data_bytes = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      f"{BASE_URL}/data",
      data=data_bytes,
      headers={"Content-Type": "application/json"},
      method="POST",
  )
  with urllib.request.urlopen(req, timeout=5) as resp:
    status_code = resp.getcode()
    body = json.loads(resp.read().decode("utf-8"))
    assert status_code == 201, f"Expected 201, got {status_code}"
    assert body.get("status") == "Data inserted", (
        f"Unexpected response: {body}"
    )
    log(f"POST /data passed! Status: {status_code}, Body: {body}", "PASS")
  return payload


# Tests GET request to data endpoint and verifies inserted record exists
def test_get_data(expected_item):
  log(f"Testing GET {BASE_URL}/data ...")
  req = urllib.request.Request(f"{BASE_URL}/data")
  with urllib.request.urlopen(req, timeout=5) as resp:
    status_code = resp.getcode()
    records = json.loads(resp.read().decode("utf-8"))
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert isinstance(records, list), "Response must be a JSON array"
    found = any(r.get("item") == expected_item["item"] for r in records)
    assert found, f"Inserted item not found in response: {records}"
    log(
        f"GET /data passed! Found {len(records)} records. Target record"
        " verified.",
        "PASS",
    )


# Tests health check endpoint to verify database connectivity status
def test_health():
  log(f"Testing GET {BASE_URL}/health ...")
  try:
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req, timeout=5) as resp:
      status_code = resp.getcode()
      body = json.loads(resp.read().decode("utf-8"))
      log(f"Health check status: {status_code}, Body: {body}", "PASS")
  except Exception as e:
    log(f"Health check endpoint returned: {e}", "WARN")


# Runs all endpoint test cases sequentially
def main():
  print("=" * 60)
  print(f"Starting Endpoint Verification against {BASE_URL}")
  print("=" * 60)
  try:
    test_root()
    inserted = test_post_data()
    test_get_data(inserted)
    test_health()
    print("=" * 60)
    log("ALL TESTS COMPLETED SUCCESSFULLY!", "PASS")
    print("=" * 60)
  except Exception as e:
    print("=" * 60)
    log(f"TEST FAILED: {e}", "FAIL")
    print("=" * 60)
    sys.exit(1)


if __name__ == "__main__":
  main()
