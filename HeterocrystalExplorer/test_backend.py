import requests
import time
import sys

def test_backend():
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    for _ in range(10):
        try:
            requests.get(base_url)
            break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        print("Server failed to start.")
        sys.exit(1)

    print("Server is running.")

    # Test Search
    print("\nTesting Search Endpoint...")
    response = requests.get(f"{base_url}/search", params={"formula": "CsPbBr3"})
    if response.status_code == 200:
        data = response.json()
        print(f"Search successful. Found {len(data)} results.")
        print(f"First result ID: {data[0]['material_id']}")
    else:
        print(f"Search failed: {response.text}")

    # Test Analysis
    print("\nTesting Analysis Endpoint...")
    payload = {
        "perovskite_formula": "CsPbBr3",
        "qd_formula": "PbS"
    }
    response = requests.post(f"{base_url}/analyze", json=payload)
    if response.status_code == 200:
        data = response.json()
        print("Analysis successful.")
        print(f"Lattice Mismatch: {data['lattice_mismatch_percent']}%")
        print(f"Band Alignment: {data['band_alignment_note']}")
    else:
        print(f"Analysis failed: {response.text}")

if __name__ == "__main__":
    test_backend()
