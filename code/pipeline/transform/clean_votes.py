


def correct_senate_bioguide_id():
    # Builds a map: "LastName (P-ST)" -> bioguide_id
    def build_member_lookup(members_path):
        with open(members_path, "r", encoding="utf-8") as f:
            members = json.load(f)

        lookup = {}

        for m in members:
            last_name = m["last_name"].strip()
            party = m["party"].strip()
            state = m["state_name"].strip()
            bioguide_id = m["member_id"].strip()

            key = f"{last_name} ({party}-{state})"
            lookup[key] = bioguide_id

        return lookup

    # Adds bioguide_id field to each vote entry.
    def attach_bioguide_ids(votes_path, member_lookup):


        with open(votes_path, "r", encoding="utf-8") as f:
            vote_data = json.load(f)

        for vote in vote_data.get("votes", []):
            member_key = vote.get("member")

            if member_key in member_lookup:
                vote["member_id"] = member_lookup[member_key]
            else:
                vote["member_id"] = None  # unmatched case

        with open(votes_path, "w", encoding="utf-8") as f:
            json.dump(vote_data, f, indent=2)


    members_file = "../data/gold/members_119.json"
    votes_file_1 = "../data/silver/senate_votes_119_1.json"
    votes_file_2 = "../data/silver/senate_votes_119_2.json"

    member_lookup = build_member_lookup(members_file)

    attach_bioguide_ids(votes_file_1, member_lookup)
    attach_bioguide_ids(votes_file_2, member_lookup)

