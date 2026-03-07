'''
congress_build.py gathers data based on previous data from api & xml extractions

data extracted:
- senate vote party totals

'''
import json
import re
from collections import defaultdict
from datetime import datetime, timezone

from config import SILVER_DIR, CONGRESS as congress
from utils.helpers import save_to_file

output_path = SILVER_DIR
retrieved_at = datetime.now(timezone.utc).isoformat()

# TODO: FIX & TEST
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

