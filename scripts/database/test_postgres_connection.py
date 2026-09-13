import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        print("✅ Connected successfully!")
        
        # Run a trivial query just to confirm the connection actually works,
        # not just that it opened
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Postgres version: {db_version[0]}")
        
        cursor.close()
        conn.close()
        print("✅ Connection closed cleanly.")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()