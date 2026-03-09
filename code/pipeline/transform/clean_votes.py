'''
clean_votes.py cleans voting rollcall data
from silver/
    house_rollcall_119.csv
    senate_rollcall_119.csv

'''

from datetime import datetime
import pytz
import re

from config import SILVER_DIR
from utils.helpers import import_silver, export_gold, cast_record


def adding_question_field(house_rollcall_data):
    party_totals_files = [
        "house_vote_party_totals_119_1.json",
        "house_vote_party_totals_119_2.json"
    ]

    rollcall_file = SILVER_DIR / "house_rollcall_119.json"

    # 1) Build identifier -> voteQuestion mapping
    identifier_to_question = {}

    for fpath in party_totals_files:
        data = import_silver(fpath)

        for page in data.get("pages", []):
            vote = page.get("houseRollCallVote")
            if (
                vote
                and vote.get("identifier")
                and vote.get("voteQuestion")
            ):
                identifier_to_question[vote["identifier"]] = vote["voteQuestion"]

    # 2) Load rollcall data
    rollcall_data =  house_rollcall_data


    updates = 0
    skipped_existing = 0

    # 3) Add 'voteQuestion' only if missing or empty
    for page in rollcall_data.get("pages", []):
        for vote in page.get("houseRollCallVotes", []):
            ident = vote.get("identifier")

            if not ident:
                continue

            # Skip if voteQuestion already exists and is non-empty
            existing_value = vote.get("voteQuestion")
            if existing_value and str(existing_value).strip():
                skipped_existing += 1
                continue

            if ident in identifier_to_question:
                vote["voteQuestion"] = identifier_to_question[ident]
                updates += 1

    return rollcall_data

def clean_votes():

    def clean_house_votes():
        # Getting data & adding question field
        data = adding_question_field(import_silver("house_rollcall_119.json"))

        cleaned_votes = []
        seen_ids = set()

        for page in data.get("pages", []):
            for vote in page.get("houseRollCallVotes", []):

                congress = vote.get("congress")
                session = vote.get("sessionNumber")
                roll_number = vote.get("rollCallNumber")
                leg_type = vote.get("legislationType")
                leg_num = vote.get("legislationNumber")
                question = vote.get("voteQuestion")

                vote_id = f"roll_H{str(roll_number).zfill(5)}_{congress}_{session}"

                bill_id = f"{leg_type}{leg_num}_{congress}"

                # EXCLUDING AMENDMENTS (fix later if you want amendments)
                if leg_type == None:
                    continue

                if vote_id in seen_ids:
                    continue
                seen_ids.add(vote_id)


                cleaned_votes.append({
                    "vote_id": vote_id,
                    "bill_id": bill_id,
                    "question": question,
                    "chamber": "H",
                    "congress": congress,
                    "session_num": session,
                    "vote_date": vote.get("startDate"),
                    "result": vote.get("result")
                })

        # Make sure data type is correct
        TYPE_MAP_VOTES = {
            "vote_id": str,
            "bill_id": str,
            "question": str,
            "chamber": str,
            "congress": int,
            "session_num": int,
            "vote_date": str,
            "result": str
        }

        cleaned_votes = [cast_record(r, TYPE_MAP_VOTES) for r in cleaned_votes]

        # Check data:    
        print("House votes")
        print("Total records:", len(cleaned_votes))
        print("Unique IDs:", len(set(r["vote_id"] for r in cleaned_votes)))

        return cleaned_votes

    def clean_senate_votes():
        data = import_silver("senate_rollcall_119.json")

        cleaned_votes = []

        for session_key, session_data in data.get("votes", {}).items():
            vote_summary = session_data["vote_summary"]

            congress = int(vote_summary.get("congress"))
            session = int(vote_summary.get("session"))

            for vote in vote_summary.get("votes", {}).get("vote", []):

                vote_number = vote.get("vote_number")
                vote_id = f"roll_S{vote_number}_{congress}_{session}"

                leg_type, leg_num = normalize_senate_issue(vote.get("issue"))

                if leg_type == None:
                        continue
                
                # Extract question
                q = vote.get("question")
                if isinstance(q, dict):
                    question = q.get("#text", "")
                elif isinstance(q, str):
                    question = q
                else:
                    question = ""

                # Construct bill_id
                bill_id = f"{leg_type}{leg_num}_{congress}"

                vote_date = normalize_senate_date(
                    vote.get("vote_date"),
                    congress,
                    session
                )


                cleaned_votes.append({
                    "vote_id": vote_id,
                    "bill_id": bill_id,
                    "question": question,
                    "chamber": "S",
                    "congress": congress,
                    "session_num": session,
                    "vote_date": vote_date,
                    "result": vote.get("result")
                })
            
        # Make sure data type is correct
        TYPE_MAP_VOTES = {
            "vote_id": str,
            "bill_id": str,
            "question": str,
            "chamber": str,
            "congress": int,
            "session_num": int,
            "vote_date": str,
            "result": str
        }

        cleaned_votes = [cast_record(r, TYPE_MAP_VOTES) for r in cleaned_votes]

        # Check data:    
        print("Senate votes")
        print("Total records:", len(cleaned_votes))
        print("Unique IDs:", len(set(r["vote_id"] for r in cleaned_votes)))

        return cleaned_votes

    # Dealing with nomination vote data
    def normalize_senate_issue(issue):
        if not issue:
            return None, None

        # Remove periods and extra whitespace
        cleaned = issue.replace(".", "").strip()

        # PN case (nominations)
        if cleaned.startswith("PN"):
            number = cleaned[2:].strip()
            # return "PN", number

            # REMOVING NOMINATIONS (fix later if wanting nominations)
            return None, None

        # Handle SRes / SJRes + number, remove space
        match_special = re.match(r"(S(?:J)?RES)\s*(\d+[-\d]*)", cleaned, re.IGNORECASE)
        if match_special:
            leg_type = match_special.group(1).upper()  # Ensure uppercase
            leg_number = match_special.group(2)
            return leg_type, leg_number

        # General legislation pattern (letters + number)
        match = re.match(r"([A-Z]+)\s*(\d+[-\d]*)", cleaned, re.IGNORECASE)
        if match:
            leg_type = match.group(1).upper()
            leg_number = match.group(2)
            return leg_type, leg_number

        # Fallback (procedural / unknown)
        return cleaned, None

    # Converting senate date to timestamp format
    def normalize_senate_date(raw_date, congress, session):
        if not raw_date:
            return None

        # Map congress/session to calendar year
        base_year = 1789 + (congress - 1) * 2
        year = base_year if session == 1 else base_year + 1

        dt = datetime.strptime(f"{raw_date}-{year}", "%d-%b-%Y")

        eastern = pytz.timezone("US/Eastern")
        dt = eastern.localize(dt.replace(hour=12))

        return dt.isoformat()

    # Call functions
    house_votes = clean_house_votes()
    senate_votes = clean_senate_votes()

    all_votes = house_votes + senate_votes

    export_gold("votes_119.json", all_votes, 2)
