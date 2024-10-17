import json
import os
import time
import requests

# API key
api_key = "M3rnj5aYmoFbXpt7tTtSp3rgwXIrwZ4lhEHBeGlV"

# Base URL for the API endpoint
base_url = "https://api.sportradar.com/handball/trial/v2/en/seasons/{}/info.json"


def make_request(url, api_key):
    """
    Makes a GET request to the specified URL with the given API key.

    Args:
        url (str): The URL to send the request to.
        api_key (str): The API key for authentication.

    Returns:
        dict: The JSON response from the API.
    """
    headers = {
        'accept': 'application/json'
    }
    response = requests.get(f"{url}?api_key={api_key}", headers=headers)
    response.raise_for_status()
    return response.json()


# Path to the input file containing season information (adjusted for macOS)
input_path = os.path.join('/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw', 'seasons.json')

with open(input_path, 'r') as f:
    seasons_data = json.load(f)

# Extract season IDs and names from the loaded season data
season_ids = [(season['id'], season['year']) for season in seasons_data['seasons']]

try:
    # Iterate through each season and fetch detailed information
    for season_id, season_year in season_ids:
        print(f"Starting season {season_id} ({season_year})...")
        url = base_url.format(season_id)
        season_info = make_request(url, api_key)

        # Pause between requests to avoid hitting rate limits
        time.sleep(1)

        print(f"Season {season_id} ({season_year}) completed.")

        # Save each season's data in a separate file
        output_file = f"season_{season_year.replace('/', '_')}_info.json"
        output_path = os.path.join('/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw', output_file)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the data to a JSON file
        with open(output_path, 'w') as f:
            json.dump(season_info, f, indent=2)

        print(f"Data for season {season_year} saved to {output_path}")
except Exception as e:
    # Print any error that occurs during the request or file operation
    print(f"Error: {e}")