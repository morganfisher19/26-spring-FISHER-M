'''
clean_members.py cleans members data
from silver/
    members_119.csv
    member_bios_119.csv

'''

import csv
import json

from config import REFERENCE_DIR, SILVER_DIR, GOLD_DIR, CURRENT_YEAR
from utils.helpers import export_gold, cast_record

input_path = SILVER_DIR / "members_119.json"
output_path = GOLD_DIR / "members_119.json"

def abbreviate_states(input_file):
    state_reference_file = REFERENCE_DIR / "states.csv"

    state_mapping = {}

    with open(state_reference_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            full_name = row["State"].strip()
            abbr = row["Abbreviation"].strip()
            state_mapping[full_name] = abbr

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Traverse structure: pages -> members -> state
    for page in data.get("pages", []):
        for member in page.get("members", []):
            full_state = member.get("state")
            if full_state in state_mapping:
                member["state"] = state_mapping[full_state]
    
    return data

def clean_members():

    # Upload file & abbreviate states
    raw_members = abbreviate_states(input_path)

    clean_members = []

    # Loop through pages
    for page in raw_members.get("pages", []):
        for member in page.get("members", []):
            
            bioguide_id = member.get("bioguideId")
            party = member.get("partyName")[0]
            state_name = member.get("state")
            district = member.get("district")

            # Get full name (first middle last)
            full_name = member.get("name")        
            last, first = full_name.split(",", 1)
            first = first.strip()
            last = last.strip()
            name = f"{first} {last}"

            # Determine terms spent in Congress
            terms = member.get("terms", {}).get("item", [])
            total_years = 0
            for term in terms:
                start_year = term.get("startYear")
                end_year = term.get("endYear")
                if start_year:
                    if end_year:
                        total_years += int(end_year) - int(start_year)
                    else:
                        total_years += CURRENT_YEAR - int(start_year)
            years_in_congress = total_years

            # Extract chamber
            chamber = None
            if terms:
                latest_term = terms[-1]
                chamber_raw = latest_term.get("chamber")
                if chamber_raw == "House of Representatives":
                    chamber = "H"
                elif chamber_raw == "Senate":
                    chamber = "S"
                else:
                    chamber = chamber_raw

            # Account for at-large districts
            if chamber == "H":
                if district in (None, "", "At-Large"):
                    district = 0

            clean_member = {
                "member_id": bioguide_id,
                "full_name": full_name,
                "party": party,
                "state_name": state_name,
                "district": district,
                "chamber": chamber,
                "years_in_congress": years_in_congress
            }

            clean_members.append(clean_member)

    # Load raw JSON member bios data
    with open(SILVER_DIR / "member_bios_119.json", "r") as f:
        raw_bio_data = json.load(f)

    clean_bios = []

    for member_bio in raw_bio_data:
        member_id = member_bio.get("id")
        first_name = member_bio.get("unaccentedGivenName")
        last_name = member_bio.get("unaccentedFamilyName")
        birth_year = member_bio.get("birthYear")

        # Calculate age safely
        if birth_year:
            age = CURRENT_YEAR - int(birth_year)
        else:
            age = None

        clean_member_bio = {
            "member_id": member_id,
            "first_name": first_name,
            "last_name": last_name,
            "age": age
        }

        clean_bios.append(clean_member_bio)


    # Convert bios list into dictionary for fast lookup
    bios_lookup = {bio["member_id"]: bio for bio in clean_bios}

    BIO_DOWNLOAD_URL = (
        "https://bioguide.congress.gov/search?index=%22bioguideprofiles%22&size=96&matches=[]"
        "&filters=%7B%22jobPositions.congressAffiliation.congress.name%22:[%22The%20119th%20United%20States%20Congress%22]%7D"
        "&sort=[%7B%22_score%22:true%7D,%7B%22field%22:%22unaccentedFamilyName%22,%22order%22:%22asc%22%7D,"
        "%7B%22field%22:%22unaccentedGivenName%22,%22order%22:%22asc%22%7D,"
        "%7B%22field%22:%22unaccentedMiddleName%22,%22order%22:%22asc%22%7D]&view=%22Table%22"
    )

    merged_members = []
    missing_bios = []

    for member in clean_members:
        member_id = member["member_id"]

        bio = bios_lookup.get(member_id)

        if bio is None:
            missing_bios.append(member_id)
            continue

        merged_member = {
            "member_id": member_id,
            "full_name": member.get("full_name"),
            "first_name": bio.get("first_name"),
            "last_name": bio.get("last_name"),
            "party": member.get("party"),
            "chamber": member.get("chamber"),
            "state_name": member.get("state_name"),
            "district": member.get("district"),
            "years_in_congress": member.get("years_in_congress"),
            "age": bio.get("age")
        }

        merged_members.append(merged_member)

    if missing_bios:
        raise ValueError(
            f"Member bio data out of date. Missing bio(s) for member ID(s): {', '.join(missing_bios)}\n"
            f"Download new json file here:\n{BIO_DOWNLOAD_URL}"
        )
    
    # Make sure data type is correct
    TYPE_MAP_MEMBERS = {
        "member_id": str,
        "full_name": str,
        "first_name": str,
        "last_name": str,
        "party": str,
        "state_name": str,
        "chamber": str,
        "district": int,
        "years_in_congress": int,
        "age": int,
    }

    merged_members = [cast_record(r, TYPE_MAP_MEMBERS) for r in merged_members]

    # Check data:
    print("Total records:", len(merged_members))
    print("Unique IDs:", len(set(r["member_id"] for r in merged_members)))


    # Write merged gold JSON
    export_gold("members_119.json", merged_members, 4)

