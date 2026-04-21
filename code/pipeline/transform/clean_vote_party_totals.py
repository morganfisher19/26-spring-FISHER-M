'''
clean_vote_party_totals.py cleans sponsor & cosponsor data
from silver/
    house_vote_party_totals_119_1.csv
    house_vote_party_totals_119_2.csv
    senate_vote_party_totals_119_1.csv
    senate_vote_party_totals_119_2.csv

'''

from utils.helpers import import_silver, export_gold, cast_record

def clean_vote_party_totals():
    files = [
        "house_vote_party_totals_119_1.json",
        "house_vote_party_totals_119_2.json",
        "senate_vote_party_totals_119_1.json",
        "senate_vote_party_totals_119_2.json"
    ]
    cleaned_records = []

    for file_path in files:
        data = import_silver(file_path)
        if file_path.startswith("house"):
            # Iterate through each page
            for page in data.get("pages", []):
                vote_data = page.get("houseRollCallVote", {})

                congress = str(vote_data.get("congress"))
                session = int(file_path.split("_")[-1].replace(".json", ""))
                roll_number = str(vote_data.get("rollCallNumber")).zfill(5)
                chamber = "H"                
                vote_id = f"roll_{chamber}{roll_number.zfill(5)}_{congress}_{session}"

                for party_total in vote_data.get("votePartyTotal", []):
                    party = party_total.get("voteParty")
                    # Skip records where party is null
                    if party is None:
                        continue

                    record = {
                        "vote_id": vote_id,
                        "party": party,
                        "yes_count": party_total.get("yeaTotal", 0),
                        "no_count": party_total.get("nayTotal", 0),
                        "present_count": party_total.get("presentTotal", 0),
                        "not_voting_count": party_total.get("notVotingTotal", 0)
                    }
                    cleaned_records.append(record)
        if file_path.startswith("senate"):
            for record in data.get("votes", []):
                cleaned_records.append({
                    "vote_id": record.get("vote_id"),
                    "party": record.get("party"),
                    "yes_count": record.get("yes_count", 0),
                    "no_count": record.get("no_count", 0),
                    "present_count": record.get("present_count", 0),
                    "not_voting_count": record.get("not_voting_count", 0)
                })

    TYPE_MAP_PARTY_TOTALS = {
        "vote_id": str,
        "party": str,
        "yes_count": int,
        "no_count": int,
        "present_count": int,
        "not_voting_count": int
    }

    cleaned_sponsorships = [cast_record(r, TYPE_MAP_PARTY_TOTALS) for r in cleaned_records]

    # Check data:
    # Deduplicate exact duplicates first
    seen_records = set()
    deduped_records = []
    for r in cleaned_records:
        record_tuple = tuple(r[k] for k in sorted(r.keys()))
        if record_tuple not in seen_records:
            seen_records.add(record_tuple)
            deduped_records.append(r)

    print(f"Removed {len(cleaned_records) - len(deduped_records)} exact duplicate(s)")

    # Now check for (vote_id, party) conflicts with differing data
    unique_combinations = set((r["vote_id"], r["party"]) for r in deduped_records)
    if len(deduped_records) != len(unique_combinations):
        from collections import Counter
        counts = Counter((r["vote_id"], r["party"]) for r in deduped_records)
        for key, n in sorted(counts.items()):
            if n > 1:
                matches = [r for r in deduped_records if (r["vote_id"], r["party"]) == key]
                print(f"CONFLICT {key} x{n}:")
                for m in matches:
                    print(f"  {m}")
        raise ValueError("Conflicting records with same (vote_id, party) but different data")

    cleaned_records = deduped_records

    # Save to gold JSON
    export_gold("vote_party_totals_119.json", cleaned_records, 4)

