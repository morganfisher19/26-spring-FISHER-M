'''
update_db.py takes clean gold data
and updates the database

'''

import psycopg2
from psycopg2.extras import execute_values
import json
import os
from dotenv import load_dotenv

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
    rows = [(
        v.get("vote_id"),
        v.get("bill_id"),
        v.get("question"),
        v.get("chamber"),
        v.get("congress"),
        v.get("session_num"),
        v.get("vote_date"),
        v.get("result")
    ) for v in votes]

    execute_values(cur, """
        INSERT INTO votes (vote_id, bill_id, question, chamber, congress, session_num, vote_date, result)
        VALUES %s
        ON CONFLICT (vote_id) DO NOTHING
    """, rows)
    print(f"  Votes: {len(rows)} rows processed")

def upsert_vote_records(cur):
    vote_records = load_gold("vote_records_119.json")
    votes = load_gold("votes_119.json")
    members = load_gold("members_119.json")

    valid_vote_ids = {v.get("vote_id") for v in votes if v.get("vote_id")}
    valid_member_ids = {m.get("member_id") for m in members if m.get("member_id")}

    rows = [(
        vr.get("vote_id"),
        vr.get("member_id"),
        vr.get("position")
    ) for vr in vote_records
        if vr.get("vote_id") in valid_vote_ids and vr.get("member_id") in valid_member_ids]

    execute_values(cur, """
        INSERT INTO vote_records (vote_id, member_id, position)
        VALUES %s
        ON CONFLICT (vote_id, member_id) DO NOTHING
    """, rows)
    print(f"  Vote records: {len(rows)} rows processed")

def upsert_vote_party_totals(cur):
    vote_party_totals = load_gold("vote_party_totals_119.json")
    votes = load_gold("votes_119.json")

    valid_vote_ids = {v.get("vote_id") for v in votes if v.get("vote_id")}

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
