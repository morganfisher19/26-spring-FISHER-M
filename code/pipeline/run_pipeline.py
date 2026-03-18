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
    fetch_bill_policy_area_and_sponsorship,
    fetch_laws
)
from pipeline.extract.congress_xml import (
    fetch_senate_rollcall,
    fetch_all_member_votes
)
from pipeline.extract.congress_build import (
    fetch_senate_party_totals
)

# fetch_house_rollcall()
# fetch_house_party_totals()
# fetch_members()
# fetch_bills()
# fetch_bill_policy_area_and_sponsorship()
# fetch_senate_rollcall()
# fetch_all_member_votes()
# fetch_senate_party_totals()
# fetch_laws()

# --- Transform ---
from pipeline.transform.clean_members import clean_members
from pipeline.transform.clean_bills import clean_bills
from pipeline.transform.clean_votes import clean_votes
from pipeline.transform.clean_vote_records import clean_vote_records
from pipeline.transform.clean_vote_party_totals import clean_vote_party_totals
from pipeline.transform.clean_bill_sponsorships import clean_bill_sponsorships
from pipeline.transform.clean_laws import clean_laws


clean_members()
clean_bills()
clean_votes()
clean_vote_records()
clean_vote_party_totals()
clean_bill_sponsorships()
clean_laws()


# # --- Load ---
# from pipeline.load.update_db import update_db

# update_db()
