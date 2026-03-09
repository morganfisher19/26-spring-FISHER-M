'''
clean_bills.py cleans bills data
from silver/
    bills_119.csv
    bills_policy_area_119.csv

'''

# from config import SILVER_DIR, GOLD_DIR
from utils.helpers import import_silver, export_gold, cast_record


def clean_bills():
    data = import_silver("bills_119.json")
    data_policy_area = import_silver("bills_policy_area_119.json")

    cleaned_bills = []

    # Lookup policy area
    policy_lookup = {}

    for bill in data_policy_area.get("bills", []):
        bill_id = bill.get("bill_id")
        policy_area = bill.get("policy_area")

        policy_lookup[bill_id] = policy_area

    # Flatten pages -> bills
    for page in data.get("pages", []):
        for bill in page.get("bills", []):

            congress = bill.get("congress")
            chamber = bill.get("originChamber")[0]
            bill_type = bill.get("type")
            number = bill.get("number")
            title = bill.get("title")
            
            # Construct bill_id
            bill_id = f"{bill_type}{number}_{congress}"

            # Lookup policy area
            policy_area = policy_lookup.get(bill_id)


            cleaned_bills.append({
                "bill_id": bill_id,
                "bill_type": bill_type,
                "bill_number": number,
                "congress": congress,
                "chamber": chamber,
                "title": title,
                "policy_area": policy_area
            })

    # Make sure data type is correct
    TYPE_MAP_BILLS = {
        "bill_id": str,
        "bill_type": str,
        "bill_number": int,
        "congress": int,
        "chamber": str,
        "title": str,
        "policy_area": str,
    }

    cleaned_bills = [cast_record(r, TYPE_MAP_BILLS) for r in cleaned_bills]

    # Check data:
    print("Total records:", len(cleaned_bills))
    print("Unique IDs:", len(set(r["bill_id"] for r in cleaned_bills)))

    # Save cleaned data
    export_gold("bills_119.json", cleaned_bills, 4)