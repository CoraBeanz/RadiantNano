import requests
import json

def test_screening():
    url = "http://localhost:8000/screen"
    payload = {
        "max_strain": 5.0,
        "min_perovskite_bandgap": 1.5,
        "max_perovskite_bandgap": 3.0,
        "min_qd_bandgap": 0.0,
        "max_qd_bandgap": 1.5
    }
    
    print("Sending screening request...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            results = response.json()
            print(f"Success! Found {len(results)} compatible pairs.")
            if results:
                print("Top 3 matches:")
                for r in results[:3]:
                    print(f"  {r['perovskite']} + {r['qd']} (Strain: {r['strain']}%)")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_screening()
