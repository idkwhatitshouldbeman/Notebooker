"""
Test Supabase connection with direct database URL
"""

import os
import psycopg2

# Set environment variables
os.environ['SUPABASE_URL'] = 'https://kqwwwmhuczwksraysvpp.supabase.co'
os.environ['SUPABASE_KEY'] = 'snJrAKpW4jqAuzUa'

# Try different database URL formats
project_ref = 'kqwwwmhuczwksraysvpp'
password = 'snJrAKpW4jqAuzUa'

# Format 1: Direct database URL
db_url_1 = f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres"

# Format 2: Alternative format
db_url_2 = f"postgresql://postgres:{password}@{project_ref}.supabase.co:5432/postgres"

# Format 3: With different port
db_url_3 = f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:6543/postgres"

print("Testing Supabase connection formats...")
print(f"Project ref: {project_ref}")
print(f"Password: {password[:10]}...")

# Test each format
formats = [
    ("Format 1 (db.project.supabase.co:5432)", db_url_1),
    ("Format 2 (project.supabase.co:5432)", db_url_2),
    ("Format 3 (db.project.supabase.co:6543)", db_url_3)
]

for name, db_url in formats:
    try:
        print(f"\nTesting {name}...")
        print(f"URL: {db_url[:50]}...")
        
        conn = psycopg2.connect(db_url, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Success! PostgreSQL version: {version[0][:50]}...")
        conn.close()
        break
        
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}...")

print("\nIf all formats failed, the database might not be accessible or the credentials might be incorrect.")
