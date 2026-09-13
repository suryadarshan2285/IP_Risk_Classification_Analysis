import json

def verify():
    rows = []
    with open("final_dataset.jsonl", "r") as f:
        for line in f:
            rows.append(json.loads(line))
    
    print(f"Total rows: {len(rows)}")
    
    # Count by label
    malicious = [r for r in rows if r["label"] == 1]
    benign = [r for r in rows if r["label"] == 0]
    print(f"Malicious (label=1): {len(malicious)}")
    print(f"Benign (label=0): {len(benign)}")
    
    # Count by source_dataset (finer breakdown)
    from collections import Counter
    source_counts = Counter(r["source_dataset"] for r in rows)
    print(f"\nBreakdown by source:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    
    # Check for failed lookups
    failed = [r for r in rows if r["status"] != "success"]
    print(f"\nFailed ip-api lookups: {len(failed)}")
    if failed:
        print("Failed IPs:")
        for r in failed:
            print(f"  {r['ip']} ({r['source_dataset']}) — status: {r['status']}")
    
    # Check for duplicate IPs (shouldn't happen, but worth confirming)
    ip_list = [r["ip"] for r in rows]
    duplicates = [ip for ip in set(ip_list) if ip_list.count(ip) > 1]
    print(f"\nDuplicate IPs: {len(duplicates)}")
    if duplicates:
        print(duplicates)

if __name__ == "__main__":
    verify()