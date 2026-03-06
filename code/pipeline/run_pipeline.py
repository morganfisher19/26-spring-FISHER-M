'''
run_pipeline.py callls functions from other scirpts in the specified order:

1. calls extract steps (hits APIs/scrapes XML, saves to silver/)
2. calls transform steps (reads silver/, cleans, saves to gold/)
3. calls load steps (reads gold/, inserts into DB)

'''

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- Extract ---
from pipeline.extract.congress_api import (
    fetch_house_rollcall,
    fetch_house_party_totals,
    fetch_members,
    fetch_bills,
    fetch_bill_policy_area_and_sponsorship
)
from pipeline.extract.house_votes import fetch_house_votes
from pipeline.extract.senate_votes import fetch_senate_votes

'''
Working calls:
fetch_house_rollcall()
fetch_house_party_totals()
fetch_members()
fetch_bills()

'''
fetch_bill_policy_area_and_sponsorship()
# fetch_house_votes()
# fetch_senate_votes()

# --- Transform ---
# from pipeline.transform.clean_members import clean_members
# from pipeline.transform.clean_bills import clean_bills
# from pipeline.transform.clean_votes import clean_votes
# from pipeline.transform.clean_vote_records import clean_vote_records
# from pipeline.transform.clean_vote_party_totals import clean_vote_party_totals
# from pipeline.transform.clean_bill_sponsorships import clean_bill_sponsorships


'''
# --- Load ---
(To be included later)
'''