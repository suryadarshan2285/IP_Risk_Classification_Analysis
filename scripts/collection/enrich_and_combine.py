import requests
import json
import time
import os

OUTPUT_FILE = "final_dataset.jsonl"

SOURCE_FILES = [
    {"filename": "malicious_ips_raw.json", "ip_key": "ipAddress", "label": 1, "source_name": "abuseipdb_malicious"},
    {"filename": "residential_benign_ips.json", "ip_key": "ip", "label": 0, "source_name": "residential_isp"},
    {"filename": "hosting_benign_ips.json", "ip_key": "ip", "label": 0, "source_name": "hosting_provider"},
]

def load_all_ips():
    all_ips = []
    for source in SOURCE_FILES:
        with open(source["filename"], "r") as f:
            entries = json.load(f)
        for entry in entries:
            ip = entry[source["ip_key"]]
            all_ips.append({
                "ip": ip,
                "label": source["label"],
                "source_dataset": source["source_name"]
            })
    return all_ips

def deduplicate_output_file():
    """
    NEW: Cleans up the output file by keeping only ONE row per IP —
    preferring a successful row over a failed one if both exist.
    Run this at the start of every enrich_all() call.
    """
    if not os.path.exists(OUTPUT_FILE):
        return
    
    best_row_per_ip = {}
    with open(OUTPUT_FILE, "r") as f:
        for line in f:
            row = json.loads(line)
            ip = row["ip"]
            
            # If we haven't seen this IP yet, keep it
            if ip not in best_row_per_ip:
                best_row_per_ip[ip] = row
            else:
                # If we have seen it, only replace if the new one is a success 
                # and the old one wasn't
                if row.get("status") == "success" and best_row_per_ip[ip].get("status") != "success":
                    best_row_per_ip[ip] = row
    
    # Rewrite the file with just the deduplicated rows
    with open(OUTPUT_FILE, "w") as f:  # 'w' = overwrite, not append, this time
        for row in best_row_per_ip.values():
            f.write(json.dumps(row) + "\n")
    
    print(f"🧹 Deduplicated: {len(best_row_per_ip)} unique IPs kept")

def load_already_done():
    done_ips = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            for line in f:
                row = json.loads(line)
                if row.get("status") == "success":
                    done_ips.add(row["ip"])
    return done_ips

def get_ip_features(ip, max_retries=3):
    """
    UPDATED: Now retries on a 'fail' status (not just connection errors),
    with increasing wait time between attempts (backoff).
    """
    url = f"http://ip-api.com/json/{ip}"
    params = {
        "fields": "status,country,countryCode,isp,org,as,mobile,proxy,hosting,query,message"
    }
    
    wait_times = [5, 10, 20]  # backoff schedule
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("status") == "success":
                return result
            else:
                # Got a real response, but it says fail — likely rate limited
                print(f"      ⚠️ Attempt {attempt + 1}: status=fail, message: {result.get('message')}")
                if attempt < max_retries - 1:
                    print(f"      Waiting {wait_times[attempt]}s before retry...")
                    time.sleep(wait_times[attempt])
        
        except requests.exceptions.RequestException as e:
            print(f"      ⚠️ Attempt {attempt + 1}: connection error: {e}")
            if attempt < max_retries - 1:
                time.sleep(wait_times[attempt])
    
    # All retries exhausted — genuinely give up on this IP
    return {"status": "fail", "message": "exhausted retries"}

def enrich_all():
    deduplicate_output_file()  # clean up old duplicate rows first
    
    all_ips = load_all_ips()
    done_ips = load_already_done()
    
    remaining = [entry for entry in all_ips if entry["ip"] not in done_ips]
    
    print(f"Total IPs: {len(all_ips)}")
    print(f"Already done: {len(done_ips)}")
    print(f"Remaining to process: {len(remaining)}")
    
    with open(OUTPUT_FILE, "a") as f:
        for i, entry in enumerate(remaining, start=1):
            ip = entry["ip"]
            print(f"[{i}/{len(remaining)}] {ip} ({entry['source_dataset']})")
            
            features = get_ip_features(ip)
            
            row = {
                "ip": ip,
                "label": entry["label"],
                "source_dataset": entry["source_dataset"],
                "status": features.get("status"),
                "country": features.get("country"),
                "countryCode": features.get("countryCode"),
                "isp": features.get("isp"),
                "org": features.get("org"),
                "as": features.get("as"),
                "mobile": features.get("mobile"),
                "proxy": features.get("proxy"),
                "hosting": features.get("hosting"),
            }
            
            f.write(json.dumps(row) + "\n")
            f.flush()
            
            time.sleep(3)
    
    print("\n✅ Done — all IPs processed.")

if __name__ == "__main__":
    enrich_all()