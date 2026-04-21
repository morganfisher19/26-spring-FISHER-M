'''
clean_bill_sponsorships.py cleans sponsor & cosponsor data
from silver/
    bills_sponsorships_119.csv

'''

from utils.helpers import import_silver, export_gold, cast_record

def clean_bill_sponsorships():
    data = import_silver("bills_sponsorships_119.json")

    cleaned_sponsorships = []

    for bill in data.get("bills", []):
        bill_id = bill.get("bill_id")

        for member_id in bill.get("sponsor_ids", []):
            cleaned_sponsorships.append({
                "bill_id": bill_id,
                "member_id": member_id,
                "sponsor_type": "S"
            })

        for member_id in bill.get("cosponsor_ids", []):
            cleaned_sponsorships.append({
                "bill_id": bill_id,
                "member_id": member_id,
                "sponsor_type": "C"
            })

    TYPE_MAP_SPONSORSHIPS = {
        "bill_id": str,
        "member_id": str,
        "sponsor_type": str
    }

    cleaned_sponsorships = [cast_record(r, TYPE_MAP_SPONSORSHIPS) for r in cleaned_sponsorships]

    # Deduplicate on (bill_id, member_id, sponsor_type)
    unique = {(r["bill_id"], r["member_id"], r["sponsor_type"]): r for r in cleaned_sponsorships}
    cleaned_sponsorships = list(unique.values())

    print("Total records:", len(cleaned_sponsorships))
    print("Unique IDs:", len(set((r["bill_id"], r["member_id"], r["sponsor_type"]) for r in cleaned_sponsorships)))

    if len(cleaned_sponsorships) != len(set((r["bill_id"], r["member_id"], r["sponsor_type"]) for r in cleaned_sponsorships)):
        raise ValueError(
            f"Repeated IDs in bill_sponsorships_119.json"
        )


    export_gold("bill_sponsorships_119.json", cleaned_sponsorships, 2)