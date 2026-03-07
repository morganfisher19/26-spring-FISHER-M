'''
congress_xml.py gathers data by combining xml files from senate.gov & clerk.house.gov

data extracted:
- senate rollcall
- house member votes
- senate votes

'''

import requests
import xml.etree.ElementTree as ET
import xmltodict
from io import BytesIO
import os
import time
import json
from datetime import datetime, timezone
from pathlib import Path


from config import SILVER_DIR, CONGRESS as congress
from utils.helpers import save_to_file

output_path = SILVER_DIR
retrieved_at = datetime.now(timezone.utc).isoformat()

def fetch_senate_rollcall():
    print("Fetching senate rollcall data!")

    # URLs
    urls = []
    for i in range(1,3):
        url = f"https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_119_{i}.xml"
        urls.append(url)

    # print(urls)

    combined_data = {}

    for i, url in enumerate(urls, start=1):
        response = requests.get(url)
        response.raise_for_status()  # stop on HTTP errors

        # Parse XML to dict
        xml_dict = xmltodict.parse(response.text)

        # Store under a convenient key
        combined_data[f"vote_menu_119_{i}"] = xml_dict
    
    final_payload = {
        "source": "https://www.senate.gov/legislative/LIS/roll_call_lists/",
        "retrieved_at": retrieved_at,
        "congress": congress,
        "votes": combined_data
    }

    # Write combined JSON
    save_to_file(final_payload, f"{output_path}/senate_rollcall_119.json")

    print("Fetching complete!")


def fetch_all_member_votes():
    print("Fetching all voting data!")

    session = requests.Session()

    def getting_voting_data_xml_to_json(xml_base_url, json_output_name, chamber, congress, congress_session):
        session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0 Safari/537.36")
        })

        file_path = Path(f"{output_path}/{json_output_name}")

        # Load existing data if file exists
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            rows = existing_data.get("votes", [])
            start_roll = max(int(r["roll_number"]) for r in rows) + 1 if rows else 1
            print(f"Resuming {json_output_name} from roll {start_roll} ({len(rows)} existing records)")
        else:
            rows = []
            start_roll = 1

        delay_between_requests = 0.1
        if chamber == "Senate":
            delay_between_requests = 0.8
        max_backoff = 60

        # Loop to gather all valid URLs
        for i in range(start_roll, 1000):  # safety upper bound
            url = xml_base_url.format(i)

            backoff = 2
            while True:
                r = session.get(url)
                if r.status_code == 403:
                    print(f"403 received, backing off {backoff}s: {url}")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
                    continue
                break

            if r.status_code == 404:
                print("404 received at: ", url)
                break

            r.raise_for_status()

            # Parse XML from memory
            try:
                tree = ET.parse(BytesIO(r.content))
            except ET.ParseError:
                break

            root = tree.getroot()

            # Construct data from XML
            if chamber == "House":
                roll_number = root.findtext(".//rollcall-num")
                bill = root.findtext(".//legis-num")
                date = root.findtext(".//action-date")

                for vote in root.findall(".//recorded-vote"):
                    legislator = vote.find("legislator")
                    rows.append({
                        "roll_number": roll_number,
                        "bill": bill,
                        "date": date,
                        "member": legislator.text,
                        "member_id": legislator.attrib.get("name-id"),
                        "vote": vote.findtext("vote")
                    })

            elif chamber == "Senate":
                roll_number = root.findtext(".//vote_number")
                bill = root.findtext(".//document/document_name")
                date = root.findtext(".//vote_date")

                for vote in root.findall(".//members/member"):
                    rows.append({
                        "roll_number": roll_number,
                        "bill": bill,
                        "date": date,
                        "member": vote.findtext('member_full'),
                        "vote": vote.findtext("vote_cast")
                    })

            time.sleep(delay_between_requests)

        # Establish source & timestamp
        if chamber == "House":
                source = "https://clerk.house.gov/Votes"
        elif chamber == "Senate":
                source = "https://www.senate.gov/legislative/votes_new.htm"
        retrieved_at = datetime.now(timezone.utc).isoformat()


        # Build final payload
        final_payload = {
            "source": source,
            "retrieved_at": retrieved_at,
            "congress" : congress,
            "session" : congress_session,
            "votes": rows   # your scraped records
        }

        # Save collected data as JSON
        save_to_file(final_payload, f"{output_path}/{json_output_name}")

        print(f"Saved {len(rows)} records to silver/{json_output_name}")

    for i in range(1,3):
        congress_session = i
        year = 1786+congress*2 + congress_session

        senate_base_url = f"https://www.senate.gov/legislative/LIS/roll_call_votes/vote{congress}{congress_session}/vote_{congress}_{congress_session}_00{{:03d}}.xml"
        senate_output_json = f"senate_votes_{congress}_{congress_session}.json"

        getting_voting_data_xml_to_json(senate_base_url, senate_output_json, "Senate", congress, congress_session)

        house_base_url = f"https://clerk.house.gov/evs/{year}/roll{{:03d}}.xml"
        house_output_json = f"house_votes_{congress}_{congress_session}.json"

        getting_voting_data_xml_to_json(house_base_url, house_output_json, "House", congress, congress_session)
    
    print("Fetch complete!")