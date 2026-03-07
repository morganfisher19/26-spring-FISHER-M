'''
congress_api.py gathers data from the congress.gov API

data extracted:
- members
- bills
- house rollcall
- house vote party totals
- bill policy area
- bill sponsorship

'''

import requests
import random
import json
import time
from requests.exceptions import HTTPError
from pathlib import Path
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import API_KEY, SILVER_DIR, CACHE_DIR, CONGRESS as congress
from utils.helpers import save_to_file

base_url = "https://api.congress.gov/v3"

session = requests.Session()

output_path = SILVER_DIR
retrieved_at = datetime.now(timezone.utc).isoformat()

# Function for extracting API data
def get_api_info(search_string, max_retries=5):
    url = f"{base_url}/{search_string}&api_key={API_KEY}"
    # print(url) #DEBUGGING: DELETE LATER
    for i in range(max_retries):
        response = session.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            wait = (2 ** i) + random.uniform(0, 0.5)  # exponential backoff + jitter
            print(f"429 Rate limited. Waiting {wait:.1f}s...")
            time.sleep(wait)
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()
    raise Exception(f"Failed after {max_retries} retries: {url}")

def fetch_members():
    print("Fetching members!")

    pages = []

    for offset in range(0, 541, 250):
        search_string = f"member?format=json&offset={offset}&limit=250&currentMember=true"
        page_data = get_api_info(search_string)
        pages.append(page_data)

    final_payload = {
        "source": "https://api.congress.gov/",
        "retrieved_at": retrieved_at,
        "congress" : 119,
        "pages": pages
    }

    save_to_file(final_payload, f"{output_path}/members_119.json")
    print("Fetch complete!")

def fetch_bills():
    print("Fetching bills!")
    output_file = f"{output_path}/bills_119.json"
    limit = 250

    # Load existing data if available
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_data = json.load(f)
        pages = existing_data.get("pages", [])

        # Count total bills already stored
        total_bills_saved = sum(len(page.get("bills", [])) for page in pages)
        offset = total_bills_saved
        print(f"Resuming from offset {offset} (already have {total_bills_saved} bills)")
    else:
        pages = []
        offset = 0
    

    while True:
        search_string = f"bill/119?format=json&offset={offset}&limit={limit}"
        page_data = get_api_info(search_string)

        # Stop if no bills returned
        bills = page_data.get("bills")
        if bills is None or len(bills) == 0:
            print("No more bills returned from API. Stopping.")
            break

        pages.append(page_data)
        offset += len(bills)  # move to next batch

    final_payload = {
        "source": "https://api.congress.gov/",
        "retrieved_at": retrieved_at,
        "congress": 119,
        "pages": pages
    }

    save_to_file(final_payload, f"{output_path}/bills_119.json")
    print("Fetch complete!")

def fetch_house_rollcall():
    print("Fetching house rollcall!")

    pages = []
    offset = 0
    limit = 250  # API max per request

    while True:
        search_string = f"house-vote/119?format=json&offset={offset}&limit={limit}"
        page_data = get_api_info(search_string)

        # Stop the loop if no data returned
        if not page_data.get("houseRollCallVotes"):
            break

        pages.append(page_data)
        offset += limit  # move to next page

    final_payload = {
        "source": "https://api.congress.gov/",
        "retrieved_at": retrieved_at,
        "congress": 119,
        "pages": pages
    }

    save_to_file(final_payload, f"{output_path}/house_rollcall_119.json")
    print("Fetch complete!")

def fetch_house_party_totals():
    print("Fetching House vote party totals!")

    # Only extracting for session 2 (since first session past)
    session = 2
    output_file = f"{output_path}/house_vote_party_totals_119_2.json"

    # Load existing data if available
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_data = json.load(f)
        pages = existing_data.get("pages", [])

        # Extract rollCallNumber from the nested "houseRollCallVote" dict
        rollcall_numbers = [
            page["houseRollCallVote"]["rollCallNumber"]
            for page in pages
            if page.get("houseRollCallVote") and "rollCallNumber" in page["houseRollCallVote"]
        ]

        last_rollcall = max(rollcall_numbers, default=0)
        rollcall = last_rollcall + 1
        print(f"Resuming from roll call {rollcall}")
    else:
        pages = []
        rollcall = 1
    
    while True:
        search_string = f"house-vote/119/2/{rollcall}?format=json"
        page_data = get_api_info(search_string)

        if page_data is None:
            print(f"No votes found at roll call {rollcall}. Stopping.")
            break

        pages.append(page_data)
        rollcall += 1

    final_payload = {
        "source": "https://api.congress.gov/",
        "retrieved_at": retrieved_at,
        "congress" : 119,
        "pages": pages
    }

    save_to_file(final_payload, output_file)
    print("Fetch complete!")

def fetch_bill_policy_area_and_sponsorship():
    print("Fetching bill policy area and sponsorship!")
    CACHE_PATH = CACHE_DIR / "bill_cache_119.json"
    print(CACHE_PATH)

    # 1. Load cache data
    if Path(CACHE_PATH).exists():
        with open(CACHE_PATH, "r") as f:
            bill_cache = json.load(f)
    else:
        bill_cache = {}


    # 2. Load bills data
    with open(f"{output_path}/bills_119.json", "r", encoding="utf-8") as f:
        bills_data = json.load(f)
    unique_bills = set()
    for page in bills_data.get("pages", []):
        for bill in page.get("bills", []):
            bill_type = bill.get("type", "").lower()  # e.g., "hr"
            bill_number = str(bill.get("number", ""))  # e.g., "144"
            if bill_type and bill_number:
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

    except RuntimeError as e:
        if str(e) == "RATE_LIMIT_REACHED":
            print("Rate limit reached. Cache saved. Re-run script to continue.")
        else:
            raise

    # 4. Build output files from cache
    sponsorships_bills = []
    policy_area_bills = []

    for bill in bill_cache.values():

        sponsorships_bills.append({
            "bill_id": bill["bill_id"],
            "sponsor_ids": bill["sponsor_ids"],
            "cosponsor_ids": bill["cosponsor_ids"]
        })

        policy_area_bills.append({
            "bill_id": bill["bill_id"],
            "policy_area": bill["policy_area"]
        })

    sponsorships_output = {
        "source": "https://api.congress.gov/",
        "retrieved_at": retrieved_at,
        "congress": congress,
        "bills": sponsorships_bills
    }

    policy_area_output = {
        "source": "https://api.congress.gov/",
        "retrieved_at": retrieved_at,
        "congress": congress,
        "bills": policy_area_bills
    }

    save_to_file(sponsorships_output, f"{output_path}/bills_sponsorships_119.json")
    save_to_file(policy_area_output, f"{output_path}/bills_policy_area_119.json")

    print("Fetch complete!")
