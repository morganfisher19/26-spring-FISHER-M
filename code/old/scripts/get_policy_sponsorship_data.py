# Sponsors, cosponsors, & policy area data (JSON via API)

import requests
import json
import time
from pathlib import Path
import os
from dotenv import load_dotenv

# Setup
base_url = "https://api.congress.gov/v3"
load_dotenv()  # loads variables from .env
API_KEY = os.getenv("API_KEY")
session = requests.Session()
congress = 119
CACHE_PATH = "./code/data/cache/bill_cache_119.json"

# Function to save data as json file
def save_to_file(data, file_path):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Function to call API
def get_api_info(search_string):
    url = f"{base_url}/{search_string}&api_key={API_KEY}"
    response = session.get(url)
    if response.status_code == 200:
        return response.json()
    if response.status_code == 429:
        raise RuntimeError("RATE_LIMIT_REACHED")
    response.raise_for_status()


# 1. Load cache data
if Path(CACHE_PATH).exists():
    with open(CACHE_PATH, "r") as f:
        bill_cache = json.load(f)
else:
    bill_cache = {}


# 2. Load bills data
with open("./code/data/gold/bills_119.json", "r", encoding="utf-8") as f:
    bills_data = json.load(f)
unique_bills = set()
for bill in bills_data:
    bill_id = bill.get("bill_id")  # e.g., HR3424_119
    if bill_id:
        bill_part, congress_part = bill_id.split("_")
        bill_type = ''.join(filter(str.isalpha, bill_part)).lower()
        bill_number = ''.join(filter(str.isdigit, bill_part))
        unique_bills.add((bill_type, bill_number))
print(f"Unique bills collected: {len(unique_bills)}")


# 3. Loop through bills and call APIs
try:
    for bill_type, bill_number in sorted(unique_bills):

        bill_id = f"{bill_type.upper()}{bill_number}_{congress}"

        # Skip already completed bills
        if bill_id in bill_cache:
            continue

        print(f"Fetching {bill_id}")

        # First API Call - sponsors & policy area
        bill_endpoint = f"bill/{congress}/{bill_type}/{bill_number}?format=json"
        bill_data = get_api_info(bill_endpoint)
        bill_obj = bill_data.get("bill", {})

        policy_area = bill_obj.get("policyArea", {}).get("name")

        sponsor_ids = [
            s.get("bioguideId")
            for s in bill_obj.get("sponsors", [])
            if isinstance(s, dict) and s.get("bioguideId")
        ]

        # time.sleep(0.15)

        # Second API Call - cosponsors
        cosponsor_endpoint = f"bill/{congress}/{bill_type}/{bill_number}/cosponsors?format=json"
        cosponsor_data = get_api_info(cosponsor_endpoint)

        cosponsor_ids = [
            c.get("bioguideId")
            for c in cosponsor_data.get("cosponsors", [])
            if isinstance(c, dict) and c.get("bioguideId")
        ]

        # Store Structured Result
        bill_cache[bill_id] = {
            "bill_id": bill_id,
            "bill_type": bill_type.upper(),
            "bill_number": bill_number,
            "policy_area": policy_area,
            "sponsor_ids": sponsor_ids,
            "cosponsor_ids": cosponsor_ids
        }

        # Persist immediately (safe resume after 429)
        save_to_file(bill_cache, CACHE_PATH)

        # time.sleep(0.15)

except RuntimeError as e:
    if str(e) == "RATE_LIMIT_REACHED":
        print("Rate limit reached. Cache saved. Re-run script to continue.")
    else:
        raise



# 4. Build output files from cache
sponsorships_output = {"congress": congress, "bills": []}
policy_area_output = {"congress": congress, "bills": []}

for bill in bill_cache.values():

    sponsorships_output["bills"].append({
        "bill_id": bill["bill_id"],
        "sponsor_ids": bill["sponsor_ids"],
        "cosponsor_ids": bill["cosponsor_ids"]
    })

    policy_area_output["bills"].append({
        "bill_id": bill["bill_id"],
        "policy_area": bill["policy_area"]
    })

save_to_file(sponsorships_output, "./code/data/silver/bills_sponsorships_119.json")
save_to_file(policy_area_output, "./code/data/silver/bills_policy_area_119.json")

print("Finished successfully.")