import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# --- CONFIG ---
URL = os.getenv("PUBLIC_SUPABASE_URL")
KEY = os.getenv("PUBLIC_SUPABASE_ANON_KEY")


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

# --- CLEANING (The Pandas Magic) ---
print("🧹 2. Cleaning data...")

# A. Fix Dates: "August 29th, 1914" -> 1914-08-29 (Real Date Object)
# Remove st, nd, rd, th suffixes
df['clean_date'] = df['date_of_death'].astype(str).str.replace(r'(\d+)(st|nd|rd|th)', r'\1', regex=True)
# Convert to datetime (coerce errors turns garbage into NaT)
df['iso_date'] = pd.to_datetime(df['clean_date'], errors='coerce')

# B. Fix Regiments: Standardize "North Staffs" vs "N. Staffs"
def clean_regiment(reg):
    if not isinstance(reg, str): return "Other"
    reg_lower = reg.lower()
    
    if 'north' in reg_lower and 'staff' in reg_lower:
        return "North Staffordshire Regiment"
    if 'south' in reg_lower and 'staff' in reg_lower:
        return "South Staffordshire Regiment"
    if 'artillery' in reg_lower:
        return "Royal Artillery"
    return reg # Return original if no match

df['regiment_clean'] = df['regiment'].apply(clean_regiment)

# C. Prepare for Upload
# We only want specific columns for the new clean table
clean_df = df[[
    'forename', 'surname', 'regiment_clean', 'cemetery', 
    'iso_date', 'Latitude', 'Longitude'
]].copy()

# Rename columns to match the new SQL schema we will create
clean_df.columns = ['forename', 'surname', 'regiment', 'cemetery', 'date_of_death', 'lat', 'lng']

# Replace NaNs with None (JSON standard) because Supabase hates NaN
clean_df = clean_df.where(pd.notnull(clean_df), None)

#%%
# --- UPLOAD ---
print("🚀 3. Uploading to 'wardead_clean'...")

records = clean_df.to_dict(orient='records')

# Upload in chunks (Supabase limits write size)
for i in range(0, len(records), batch_size):
    batch = records[i : i + batch_size]
    try:
        supabase.table("wardead_clean").insert(batch).execute()
        print(f"   Uploaded batch {i}...")
    except Exception as e:
        print(f"   Error on batch {i}: {e}")

print("🎉 Done! Data is clean and uploaded.")