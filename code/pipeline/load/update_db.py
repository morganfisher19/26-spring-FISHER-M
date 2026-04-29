'''
update_db.py takes clean gold data
and updates the database

'''

import psycopg2
from psycopg2.extras import execute_values
import json
import os
from dotenv import load_dotenv

from datetime import datetime
import pytz

from config import GOLD_DIR, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

load_dotenv()


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def load_gold(file_name):
    with open( GOLD_DIR / file_name, "r", encoding="utf-8") as f:
        return json.load(f)
    
def parse_law_date(date_str):
    if not date_str:
        return None
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    eastern = pytz.timezone("US/Eastern")
    return eastern.localize(dt.replace(hour=12))

def upsert_members(cur):
    members = load_gold("members_119.json")
    rows = [(
        m.get("member_id"),
        m.get("full_name"),
        m.get("first_name"),
        m.get("last_name"),
        m.get("party"),
        m.get("chamber"),
        m.get("state_name"),
        m.get("district"),
        m.get("years_in_congress"),
        m.get("age")
    ) for m in members]

    execute_values(cur, """
        INSERT INTO members (member_id, full_name, first_name, last_name, party, chamber, state_name, district, years_in_congress, age)
        VALUES %s
        ON CONFLICT (member_id) DO UPDATE SET
            years_in_congress = EXCLUDED.years_in_congress,
            age = EXCLUDED.age,
            district = EXCLUDED.district
    """, rows)
    print(f"  Members: {len(rows)} rows processed")

def upsert_bills(cur):
    bills = load_gold("bills_119.json")
    rows = [(
        b.get("bill_id"),
        b.get("bill_type"),
        b.get("bill_number"),
        b.get("congress"),
        b.get("chamber"),
        b.get("title"),
        b.get("policy_area")
    ) for b in bills]

    execute_values(cur, """
        INSERT INTO bills (bill_id, bill_type, bill_num, congress, chamber, title, policy_area)
        VALUES %s
        ON CONFLICT (bill_id) DO NOTHING
    """, rows)
    print(f"  Bills: {len(rows)} rows processed")

def upsert_votes(cur):
    votes = load_gold("votes_119.json")
    bills = load_gold("bills_119.json")

    valid_bill_ids = {b.get("bill_id") for b in bills if b.get("bill_id")}

    rows = [(
        v.get("vote_id"),
        v.get("bill_id"),
        v.get("question"),
        v.get("chamber"),
        v.get("congress"),
        v.get("session_num"),
        v.get("vote_date"),
        v.get("result")
    ) for v in votes
        if v.get("bill_id") in valid_bill_ids]
    
    execute_values(cur, """
        INSERT INTO votes (vote_id, bill_id, question, chamber, congress, session_num, vote_date, result)
        VALUES %s
        ON CONFLICT (vote_id) DO NOTHING
    """, rows)
    print(f"  Votes: {len(rows)} rows processed")

def upsert_vote_records(cur):
    vote_records = load_gold("vote_records_119.json")
    members = load_gold("members_119.json")

    cur.execute("SELECT vote_id FROM votes")
    valid_vote_ids = {row[0] for row in cur.fetchall()}
    valid_member_ids = {m.get("member_id") for m in members if m.get("member_id")}

    rows = [(
        vr.get("vote_id"),
        vr.get("member_id"),
        vr.get("position")
    ) for vr in vote_records
        if vr.get("vote_id") in valid_vote_ids and vr.get("member_id") in valid_member_ids]
    
    # Remove any rows with NULL member_id left over from before the fix
    cur.execute("DELETE FROM vote_records WHERE member_id IS NULL")

    execute_values(cur, """
        INSERT INTO vote_records (vote_id, member_id, position)
        VALUES %s
        ON CONFLICT (vote_id, member_id) DO UPDATE
        SET position = EXCLUDED.position
    """, rows)
    print(f"  Vote records: {len(rows)} rows processed")

def upsert_vote_party_totals(cur):
    vote_party_totals = load_gold("vote_party_totals_119.json")

    cur.execute("SELECT vote_id FROM votes")
    valid_vote_ids = {row[0] for row in cur.fetchall()}

    rows = [(
        vt.get("vote_id"),
        vt.get("party"),
        vt.get("yes_count"),
        vt.get("no_count"),
        vt.get("present_count"),
        vt.get("not_voting_count")
    ) for vt in vote_party_totals
        if vt.get("vote_id") in valid_vote_ids]

    execute_values(cur, """
        INSERT INTO vote_party_totals (vote_id, party, yes_count, no_count, present_count, not_voting_count)
        VALUES %s
        ON CONFLICT (vote_id, party) DO NOTHING
    """, rows)
    print(f"  Vote party totals: {len(rows)} rows processed")

def upsert_bill_sponsorships(cur):
    sponsorships = load_gold("bill_sponsorships_119.json")
    members = load_gold("members_119.json")

    valid_member_ids = {m.get("member_id") for m in members if m.get("member_id")}

    rows = [(
        s.get("bill_id"),
        s.get("member_id"),
        s.get("sponsor_type")
    ) for s in sponsorships
        if s.get("member_id") in valid_member_ids]

    execute_values(cur, """
        INSERT INTO bill_sponsorships (bill_id, member_id, sponsor_type)
        VALUES %s
        ON CONFLICT (bill_id, member_id, sponsor_type) DO NOTHING
    """, rows)
    print(f"  Bill sponsorships: {len(rows)} rows processed")

def upsert_laws(cur):


    laws = load_gold("laws_119.json")
    bills = load_gold("bills_119.json")

    valid_bill_ids = {b.get("bill_id") for b in bills if b.get("bill_id")}

    # Deduplicate by law_num, keeping last occurrence
    seen = {}
    for law in laws:
        if law.get("bill_id") in valid_bill_ids and law.get("law_num"):
            seen[law["law_num"]] = law

    rows = [(
        law.get("law_num"),
        law.get("law_type"),
        law.get("bill_id"),
        parse_law_date(law.get("law_date")),
        law.get("congress"),
        law.get("chamber")
    ) for law in seen.values()]

    execute_values(cur, """
        INSERT INTO laws (law_num, law_type, bill_id, law_date, congress, chamber)
        VALUES %s
        ON CONFLICT (law_num) DO UPDATE SET
            law_type = EXCLUDED.law_type,
            bill_id  = EXCLUDED.bill_id,
            law_date = EXCLUDED.law_date,
            congress = EXCLUDED.congress,
            chamber  = EXCLUDED.chamber
    """, rows)
    print(f"  Laws: {len(rows)} rows processed")

def update_db():
    conn = get_connection()
    cur = conn.cursor()

    steps = [
        ("Members",             upsert_members),
        ("Bills",               upsert_bills),
        ("Votes",               upsert_votes),
        ("Vote Records",        upsert_vote_records),
        ("Vote Party Totals",   upsert_vote_party_totals),
        ("Bill Sponsorships",   upsert_bill_sponsorships),
        ("Laws",                upsert_laws)
    ]

    for name, fn in steps:
        try:
            print(f"Upserting {name}...")
            fn(cur)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"  ERROR on {name}: {e}")
            raise

    cur.close()
    conn.close()
    print("Database updated.")
