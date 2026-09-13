import requests
import time
import random
import json
import ipaddress

# ASN -> friendly name mapping
ISP_ASNS = {
    "AS7922": "Comcast (US)",
    "AS7018": "AT&T (US)",
    "AS24560": "Airtel Telemedia (India)",
    "AS55836": "Reliance Jio (India)"
}

def get_prefixes(asn):
    """
    Calls RIPEstat to get all announced IP ranges (prefixes) for a given ASN.
    """
    # RIPEstat wants just the number, not "AS" prefix
    asn_number = asn.replace("AS", "")
    url = "https://stat.ripe.net/data/announced-prefixes/data.json"
    params = {"resource": asn_number}
    
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    
    prefixes = [p["prefix"] for p in data["data"]["prefixes"]]
    return prefixes

def random_ip_from_prefix(prefix):
    """
    Given a CIDR range like '73.0.0.0/16', picks one random usable IP inside it.
    """
    network = ipaddress.ip_network(prefix, strict=False)
    
    # Skip tiny or IPv6 ranges for now — keep this simple, IPv4 only
    if network.version != 4 or network.num_addresses < 4:
        return None
    
    # Pick a random address, avoiding network/broadcast addresses at the edges
    random_offset = random.randint(1, network.num_addresses - 2)
    return str(network[random_offset])

def collect_residential_ips(target_count=130):
    all_candidate_ips = []
    
    for asn, name in ISP_ASNS.items():
        print(f"Fetching prefixes for {name} ({asn})...")
        try:
            prefixes = get_prefixes(asn)
            print(f"   Found {len(prefixes)} prefixes")
            
            # Filter to only reasonably-sized IPv4 ranges (skip tiny /30s etc.)
            ipv4_prefixes = [p for p in prefixes if ":" not in p]
            all_candidate_ips.append((asn, name, ipv4_prefixes))
        except Exception as e:
            print(f"   ⚠️ Failed to fetch {name}: {e}")
        
        time.sleep(1)  # be polite to RIPEstat
    
    # Now pick random IPs, roughly evenly split across the 4 ISPs
    per_isp_target = target_count // len(ISP_ASNS)
    final_ips = []
    
    for asn, name, prefixes in all_candidate_ips:
        picked_for_this_isp = 0
        attempts = 0
        
        while picked_for_this_isp < per_isp_target and attempts < per_isp_target * 5:
            prefix = random.choice(prefixes)
            ip = random_ip_from_prefix(prefix)
            attempts += 1
            
            if ip:
                final_ips.append({"ip": ip, "source": name, "asn": asn})
                picked_for_this_isp += 1
        
        print(f"✅ {name}: picked {picked_for_this_isp} IPs")
    
    return final_ips

if __name__ == "__main__":
    residential_ips = collect_residential_ips(target_count=130)
    print(f"\nTotal residential candidate IPs: {len(residential_ips)}")
    
    with open("residential_benign_ips.json", "w") as f:
        json.dump(residential_ips, f, indent=2)
    print("💾 Saved to residential_benign_ips.json")