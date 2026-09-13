import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "final_dataset.jsonl"

def load_data():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO ip_data (ip, label, source_dataset, country, country_code, isp, org, asn, mobile, proxy, hosting)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    inserted = 0
    skipped = 0
    
    with open(INPUT_FILE, "r") as f:
        for line in f:
            row = json.loads(line)
            
            values = (
                row.get("ip"),
                row.get("label"),
                row.get("source_dataset"),
                row.get("country"),
                row.get("countryCode"),
                row.get("isp"),
                row.get("org"),
                row.get("as"),
                row.get("mobile"),
                row.get("proxy"),
                row.get("hosting")
            )
            
            try:
                cursor.execute(insert_query, values)
                inserted += 1
            except psycopg2.errors.UniqueViolation:
                # This IP already exists in the table (primary key conflict)
                conn.rollback()  # undo just this failed insert, keep going
                skipped += 1
    
    conn.commit()  # actually save everything now
    
    print(f"✅ Inserted: {inserted}")
    print(f"⚠️ Skipped (already existed): {skipped}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_data()