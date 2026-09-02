import requests
import json
from pathlib import Path

# Base url for extraction
base_url = "https://api.congress.gov/v3"

# API call
def get_api_info(search_string):
    API_key = 'Y1rHJZnyeQR8VTyevR7cFJt0bjjzZn5nCDcvhj8f'
    url = f"{base_url}/{search_string}api_key={API_key}"
    response = requests.get(url)

    # Checking for status error
    if response.status_code == 200:
        # Storing response as json
        api_data = response.json()
        return api_data
    else:
        print(f"Failed to retrieve data {response.status_code}")

# Save data as json file
def save_to_file(data, file_path):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

output_path = "./code/data/bronze/json_files"

# Search strings:

# List of bills & summaries for 119th Congress
bill_summaries_search_string = "summaries/119?format=json&"
save_to_file(get_api_info(bill_summaries_search_string), f"{output_path}/bill_summaries.json")

# List of members, bioguide, and basic info for 119th Congress
members_search_string = "member/congress/119?format=json&currentMember=true&"
save_to_file(get_api_info(members_search_string), f"{output_path}/members.json")

# List of laws passed by 119th congress
laws_search_string = "law/119?format=json&"
save_to_file(get_api_info(laws_search_string), f"{output_path}/laws.json")

# House voting data for 119th congress, second session
# house_2_search_string = "house-vote/119/2?format=json&"
# save_to_file(get_api_info(house_2_search_string), f"{output_path}/house_votes_session_2.json")

# House voting data for 119th congress, first session
# house_1_search_string = "house-vote/119/1?format=json&"
# save_to_file(get_api_info(house_1_search_string), f"{output_path}/house_votes_session_1.json")

