import json
import psycopg2
from psycopg2.extras import execute_batch

# conn = psycopg2.connect(
#     dbname="data4001",
#     user="postgres",
#     password="data4001",
#     host="localhost",
#     port=5432
# )
# cur = conn.cursor()

with open("members.json", "r", encoding="utf-8") as f:
    data = json.load(f)["members"]

# member_rows = []
# term_rows = []

# for m in data:
#     member_rows.append((
#         m["bioguideId"],
#         m["name"],
#         m.get("partyName"),
#         m.get("state"),
#         m.get("district"),
#         m.get("depiction", {}).get("imageUrl"),
#         m.get("depiction", {}).get("attribution"),
#         m.get("updateDate"),
#         m.get("url")
#     ))

#     for term in m.get("terms", {}).get("item", []):
#         term_rows.append((
#             m["bioguideId"],
#             term["chamber"],
#             term["startYear"]
#         ))

# execute_batch("""
#     INSERT INTO members (
#         bioguide_id, name, party, state, district,
#         image_url, image_attribution, update_date, api_url
#     )
#     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
#     ON CONFLICT (bioguide_id) DO NOTHING;
# """, member_rows)

# execute_batch("""
#     INSERT INTO terms (bioguide_id, chamber, start_year)
#     VALUES (%s,%s,%s);
# """, term_rows)

# conn.commit()
# cur.close()
# conn.close()
