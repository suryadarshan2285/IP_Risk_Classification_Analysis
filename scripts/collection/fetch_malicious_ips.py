import os
import requests
from dotenv import load_dotenv

# Load the API key from .env
load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")

def fetch_malicious_ips(confidence_minimum=75, limit=300):
    """
    Calls AbuseIPDB's blacklist endpoint to get IPs 
    that meet our malicious threshold.
    """
    url = "https://api.abuseipdb.com/api/v2/blacklist"
    
    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }
    
    params = {
        "confidenceMinimum": confidence_minimum,
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✅ Fetched {len(data)} malicious IPs")
        return data
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return []

# Test it
if __name__ == "__main__":
    malicious_ips = fetch_malicious_ips()
    print(malicious_ips[:3])  # print first 3 to check

import json

if __name__ == "__main__":
    malicious_ips = fetch_malicious_ips()
    print(malicious_ips[:3])
    
    # Save to a file so we don't need to re-fetch every time
    with open("malicious_ips_raw.json", "w") as f:
        json.dump(malicious_ips, f, indent=2)
    print("💾 Saved to malicious_ips_raw.json")