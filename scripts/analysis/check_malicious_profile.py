import json
import requests
import time

def get_ip_features(ip):
    url = f"http://ip-api.com/json/{ip}"
    params = {
        "fields": "status,country,countryCode,isp,org,as,mobile,proxy,hosting,query"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ Request failed for {ip}: {e}")
        return {"status": "fail"}

def check_profile(sample_size=50):
    with open("malicious_ips_raw.json", "r") as f:
        malicious_ips = json.load(f)
    
    sample = malicious_ips[:sample_size]
    
    hosting_count = 0
    proxy_count = 0
    mobile_count = 0
    failed = 0
    
    for i, entry in enumerate(sample, start=1):
        ip = entry["ipAddress"]
        print(f"[{i}/{sample_size}] Checking {ip}...")  # progress tracker
        
        result = get_ip_features(ip)
        
        if result.get("status") == "success":
            if result.get("hosting"):
                hosting_count += 1
            if result.get("proxy"):
                proxy_count += 1
            if result.get("mobile"):
                mobile_count += 1
        else:
            failed += 1
        
        time.sleep(2)  # increased delay, being more cautious
    
    checked = sample_size - failed
    print(f"\n--- Malicious IP Profile (sample of {checked}) ---")
    if checked > 0:
        print(f"Hosting: {hosting_count}/{checked} ({hosting_count/checked*100:.1f}%)")
        print(f"Proxy:   {proxy_count}/{checked} ({proxy_count/checked*100:.1f}%)")
        print(f"Mobile:  {mobile_count}/{checked} ({mobile_count/checked*100:.1f}%)")
    print(f"Failed lookups: {failed}")

if __name__ == "__main__":
    check_profile(sample_size=50)