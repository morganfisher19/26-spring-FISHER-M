'''
clean_vote_records.py cleans voting data by member
from silver/
    house_votes_119_1.csv
    house_votes_119_2.csv
    senate_votes_119_1.csv
    senate_votes_119_2.csv

'''
import json

from config import SILVER_DIR, GOLD_DIR, CONGRESS as congress
from utils.helpers import import_silver, export_gold, cast_record


def correct_senate_bioguide_id():

    # Gets cleaned member data
    with open(GOLD_DIR / "members_119.json", "r", encoding="utf-8") as f:
        members = json.load(f)

    # Builds a map: "LastName (P-ST)" -> bioguide_id
    member_lookup = {}

    for m in members:
        last_name = m["last_name"].strip()
        party = m["party"].strip()
        state = m["state_name"].strip()
        bioguide_id = m["member_id"].strip()

        key = f"{last_name} ({party}-{state})"
        member_lookup[key] = bioguide_id

    # Adds bioguide_id field to each vote entry.
    def attach_bioguide_ids(votes_path, member_lookup):
        
        vote_data = import_silver(votes_path)

        for vote in vote_data.get("votes", []):
            member_key = vote.get("member")

            if member_key in member_lookup:
                vote["member_id"] = member_lookup[member_key]
            else:
                vote["member_id"] = None  # unmatched case

        with open(SILVER_DIR / votes_path, "w", encoding="utf-8") as f:
            json.dump(vote_data, f, indent=2)

    attach_bioguide_ids("senate_votes_119_1.json", member_lookup)
    attach_bioguide_ids("senate_votes_119_2.json", member_lookup)


def clean_vote_records():

    correct_senate_bioguide_id()

    files = [
        "house_votes_119_1.json",
        "house_votes_119_2.json",
        "senate_votes_119_1.json",
        "senate_votes_119_2.json"
    ]

    cleaned_records = []

    for file_path in files:
        data = import_silver(file_path)
            
        # Determine chamber & session
        if file_path.startswith("senate"):
            chamber = "S"  # Senate
        else:
            chamber = "H"  # House
        session = int(file_path.split("_")[-1].replace(".json", ""))

        for vote in data.get("votes", []):
            roll_number = str(vote.get("roll_number"))
            vote_id = f"roll_{chamber}{roll_number.zfill(5)}_{congress}_{session}"

            cleaned_records.append({
                "vote_id": vote_id,
                "member_id": vote.get("member_id"),
                "position": vote.get("vote")
            })

    # Deduplication
    unique_records = { (r["vote_id"], r["member_id"]) : r for r in cleaned_records }
    cleaned_records = list(unique_records.values())

    # Make sure data type is correct
    TYPE_MAP_VOTE_RECORDS = {
        "vote_id": str,
        "member_id": str,
        "position": str
    }

    cleaned_records = [cast_record(r, TYPE_MAP_VOTE_RECORDS) for r in cleaned_records]

    # Check data:    
    print("Total records:", len(cleaned_records))
    unique_combinations = set((r["vote_id"], r["member_id"]) for r in cleaned_records)
    print("Unique IDs:", len(unique_combinations))


    # Save to gold JSON
    export_gold("vote_records_119.json", cleaned_records, 2)


