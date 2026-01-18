import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# --- CONFIG ---
URL = os.getenv("PUBLIC_SUPABASE_URL")
KEY = "sb_secret_GaNRnx1sxkEzRbfQzYh6Bg_zwOZNtC-"


supabase = create_client(URL, KEY)

print("⏳ 1. Downloading raw data...")

# Fetch all rows. Supabase limits fetch size, so we might need to paginate.
# For 14k, this simple loop works best:
all_rows = []
start = 0
batch_size = 1000

while True:
    print(f"   Fetching rows {start} to {start + batch_size}...")
    response = supabase.table("staffordshire_wardead").select("*").range(start, start + batch_size - 1).execute()
    rows = response.data
    if not rows:
        break
    all_rows.extend(rows)
    start += batch_size

df = pd.DataFrame(all_rows)
print(f"✅ Downloaded {len(df)} rows.")

## --- CLEANING (The Pandas Magic) ---
print("🧹 2. Cleaning data...")

# A. Fix Dates: "August 29th, 1914" -> 1914-08-29
# Remove st, nd, rd, th suffixes
df['clean_date'] = df['date_of_death'].astype(str).str.replace(r'(\d+)(st|nd|rd|th)', r'\1', regex=True)

# Convert to datetime objects
df['iso_date'] = pd.to_datetime(df['clean_date'], errors='coerce')

# CRITICAL STEP: Convert valid dates back to Strings (YYYY-MM-DD) for JSON upload
df['iso_date'] = df['iso_date'].dt.strftime('%Y-%m-%d')
df = df.drop(columns=['clean_date'], errors='ignore')

# 2. SELECT COLUMNS FOR UPLOAD
# Only keep columns that actually exist in your database.

print(f"🚀 Updating 'iso_date' for {len(df)} rows in staffordshire_wardead...")

# 1. Select ONLY the columns we need to update
# We don't need to drop 'clean_date' explicitly if we just don't select it here.
data_to_upload = df[['id', 'iso_date']].copy()

# 2. Handle NaNs (Supabase needs None for nulls)
data_to_upload = data_to_upload.where(pd.notnull(data_to_upload), None)

# 3. Batch Upsert
records = data_to_upload.to_dict(orient='records')

for i in range(0, len(records), batch_size):
    batch = records[i : i + batch_size]
    try:
        # UPSERT on 'id'. This updates the date for existing soldiers.
        supabase.table("staffordshire_wardead").upsert(batch).execute()
        print(f"   Batch {i} updated.")
    except Exception as e:
        print(f"   ❌ Error on batch {i}: {e}")
        break

print("🎉 Done. No trash columns sent.")