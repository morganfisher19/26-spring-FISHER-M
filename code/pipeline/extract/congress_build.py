'''
congress_build.py gathers data based on previous data from api & xml extractions

data extracted:
- senate vote party totals

'''
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
import requests
from pathlib import Path
from time import sleep

from config import REFERENCE_DIR, SILVER_DIR, MEMBER_IMAGE_DIR, CONGRESS as congress
from utils.helpers import save_to_file



output_path = SILVER_DIR
retrieved_at = datetime.now(timezone.utc).isoformat()


def fetch_senate_party_totals():
    print("Fetching senate party totals!")

    # Extracts party letter from member string
    def extract_party(member_string):
        match = re.search(r"\(([A-Z])-", member_string)
        if match:
            return match.group(1)
        return None


    def clean_and_tally_votes(input_file, output_file):
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        congress = str(data.get("congress"))
        session = str(data.get("session"))
        chamber = "S"  # Senate

        # Nested dictionary:
        # { (vote_id, party): {yes_count, no_count, present_count, not_voting_count} }
        tally = defaultdict(lambda: {
            "yes_count": 0,
            "no_count": 0,
            "present_count": 0,
            "not_voting_count": 0
        })

        valid_votes = {"Yea", "Nay", "Present", "Not Voting"}

        for record in data.get("votes", []):
            vote_type = record.get("vote")

            # Skip invalid vote types
            if vote_type not in valid_votes:
                continue

            roll_number = str(record.get("roll_number")).zfill(5)
            vote_id = f"roll_{chamber}{roll_number}_{congress}_{session}"

            party = extract_party(record.get("member", ""))

            # Skip if party cannot be extracted
            if party is None:
                continue

            key = (vote_id, party)

            if vote_type == "Yea":
                tally[key]["yes_count"] += 1
            elif vote_type == "Nay":
                tally[key]["no_count"] += 1
            elif vote_type == "Present":
                tally[key]["present_count"] += 1
            elif vote_type == "Not Voting":
                tally[key]["not_voting_count"] += 1

        # Convert aggregated results to list
        cleaned_records = []
        for (vote_id, party), counts in tally.items():
            cleaned_records.append({
                "vote_id": vote_id,
                "party": party,
                "yes_count": counts["yes_count"],
                "no_count": counts["no_count"],
                "present_count": counts["present_count"],
                "not_voting_count": counts["not_voting_count"]
            })
        final_payload = {
            "source": "Already extracted senate voting data",
            "retrieved_at": retrieved_at,
            "congress" : congress,
            "session": session,
            "votes": cleaned_records
        }

        save_to_file(final_payload, output_file)


    clean_and_tally_votes(
        f"{output_path}/senate_votes_119_1.json",
        f"{output_path}/senate_vote_party_totals_119_1.json"
    )

    clean_and_tally_votes(
        f"{output_path}/senate_votes_119_2.json",
        f"{output_path}/senate_vote_party_totals_119_2.json"
    )

    print("Fetch complete!")


def fetch_member_bios():
    print("Transforming member bios!")

    # Load raw JSON member bios data
    with open(REFERENCE_DIR / "raw_member_bios_119.json", "r") as f:
        data = json.load(f)

    with open(SILVER_DIR / "member_bios_119.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Complete!")

def fetch_member_images():
    INPUT_FILE = SILVER_DIR / "members_119.json"
    OUTPUT_DIR = MEMBER_IMAGE_DIR
    

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    success, skipped, failed = 0, 0, 0

    for page in data.get("pages", []):
        for member in page.get("members", []):
            bioguide_id = member.get("bioguideId")
            image_url = member.get("depiction", {}).get("imageUrl")

            # Fix malformed URLs with duplicate https://
            if image_url:
                second = image_url.find("https://", 1)
                if second != -1:
                    image_url = image_url[second:]

            if not bioguide_id or not image_url:
                print(f"Skipping {bioguide_id or 'unknown'}: missing data")
                skipped += 1
                continue

            # Preserve original file extension (.jpg, .png, etc.)
            ext = Path(image_url.split("?")[0]).suffix or ".jpg"
            out_path = OUTPUT_DIR / f"{bioguide_id}{ext}"

            if out_path.exists():
                # print(f"Skipping {bioguide_id}: already downloaded")
                skipped += 1
                continue

            try:
                r = session.get(image_url, timeout=10)
                r.raise_for_status()
                out_path.write_bytes(r.content)
                print(f"Saved {bioguide_id}{ext}")
                success += 1
                sleep(0.1)  # be polite
            except requests.RequestException as e:
                print(f"Failed {bioguide_id}: {e}")
                failed += 1

    print(f"\nDone — {success} saved, {skipped} skipped, {failed} failed")