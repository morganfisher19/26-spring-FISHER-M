'''
clean_laws.py cleans law data
from silver/
    laws_119.csv

'''

from utils.helpers import import_silver, export_gold, cast_record

def clean_laws():
    data = import_silver("laws_119.json")


# Fix this to fit data:
    cleaned_laws = []

    # Flatten pages -> bills
    for bill in data.get("pages", {}).get("bills", []):
        congress = bill.get("congress")
        bill_type = bill.get("type")
        number = bill.get("number")
        chamber = bill.get("originChamberCode")
        date = bill.get("latestAction", {}).get("actionDate")

        # Extract law number and type (bills can technically have multiple laws, but take first)
        laws = bill.get("laws", [])
        law_number = laws[0].get("number") if laws else None
        law_type = laws[0].get("type") if laws else None

        # Construct bill_id
        bill_id = f"{bill_type}{number}_{congress}"


        cleaned_laws.append({
            "law_num": law_number,
            "law_type": law_type,
            "bill_id": bill_id,
            "law_date": date,
            "congress": congress,
            "chamber": chamber,
        })

    # Make sure data type is correct
    TYPE_MAP_LAWS = {
        "law_num": str,
        "law_type": str,
        "bill_id": str,
        "law_date": str,
        "congress": int,
        "chamber": str,
    }

    cleaned_laws = [cast_record(r, TYPE_MAP_LAWS) for r in cleaned_laws]

    # Check data:
    print("Total records:", len(cleaned_laws))
    print("Unique IDs:", len(set(r["law_num"] for r in cleaned_laws)))

    # Save cleaned data
    export_gold("laws_119.json", cleaned_laws, 4)