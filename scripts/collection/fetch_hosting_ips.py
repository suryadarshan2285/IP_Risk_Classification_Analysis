import requests
import random
import json
import ipaddress
import time

def random_ip_from_prefix(prefix):
    """
    Same helper as before — picks one usable random IP from a CIDR range.
    """
    try:
        network = ipaddress.ip_network(prefix, strict=False)
        if network.version != 4 or network.num_addresses < 4:
            return None
        random_offset = random.randint(1, network.num_addresses - 2)
        return str(network[random_offset])
    except ValueError:
        return None

def get_aws_prefixes():
    url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    response = requests.get(url, timeout=15)
    data = response.json()
    # AWS format: list of dicts, each with 'ip_prefix'
    prefixes = [entry["ip_prefix"] for entry in data["prefixes"]]
    return prefixes

def get_google_prefixes():
    url = "https://www.gstatic.com/ipranges/cloud.json"
    response = requests.get(url, timeout=15)
    data = response.json()
    # Google format: list of dicts, each with 'ipv4Prefix' (some entries are ipv6 only)
    prefixes = [entry["ipv4Prefix"] for entry in data["prefixes"] if "ipv4Prefix" in entry]
    return prefixes

def get_cloudflare_prefixes():
    url = "https://api.cloudflare.com/client/v4/ips"
    response = requests.get(url, timeout=15)
    data = response.json()
    # Cloudflare format: nested under result -> ipv4_cidrs
    prefixes = data["result"]["ipv4_cidrs"]
    return prefixes

def collect_hosting_ips(target_count=170):
    sources = {
        "AWS": get_aws_prefixes,
        "Google Cloud": get_google_prefixes,
        "Cloudflare": get_cloudflare_prefixes
    }
    
    per_source_target = target_count // len(sources)
    final_ips = []
    
    for name, fetch_func in sources.items():
        print(f"Fetching prefixes for {name}...")
        try:
            prefixes = fetch_func()
            print(f"   Found {len(prefixes)} IPv4 prefixes")
        except Exception as e:
            print(f"   ⚠️ Failed to fetch {name}: {e}")
            continue
        
        picked = 0
        attempts = 0
        while picked < per_source_target and attempts < per_source_target * 5:
            prefix = random.choice(prefixes)
            ip = random_ip_from_prefix(prefix)
            attempts += 1
            if ip:
                final_ips.append({"ip": ip, "source": name})
                picked += 1
        
        print(f"✅ {name}: picked {picked} IPs")
        time.sleep(1)
    
    return final_ips

if __name__ == "__main__":
    hosting_ips = collect_hosting_ips(target_count=170)
    print(f"\nTotal hosting candidate IPs: {len(hosting_ips)}")
    
    with open("hosting_benign_ips.json", "w") as f:
        json.dump(hosting_ips, f, indent=2)
    print("💾 Saved to hosting_benign_ips.json")