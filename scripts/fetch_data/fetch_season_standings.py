import json
import os
import requests
import time

# API key
api_key = "M3rnj5aYmoFbXpt7tTtSp3rgwXIrwZ4lhEHBeGlV"

# Base URL for the API endpoint
base_url = "https://api.sportradar.com/handball/trial/v2/en/seasons/{}/standings.json?round={}"


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
    response = requests.get(f"{url}&api_key={api_key}", headers=headers)
    response.raise_for_status()
    return response.json()


def fetch_standings(season_id, round_number):
    """
    Fetches the standings for a given season and round number.

    Args:
        season_id (str): The ID of the season to fetch standings for.
        round_number (int): The round number to fetch standings for.

    Returns:
        dict: The JSON response containing the standings.
    """
    url = base_url.format(season_id, round_number)
    print(f"Requesting data from {url}")
    try:
        response = make_request(url, api_key)
        return response
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        if e.response.status_code == 429:
            print(f"Rate limit reached. Please wait and try again later.")
        else:
            print(f"HTTP error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None


def save_progress(data, filepath):
    """
    Saves the provided data to the specified filepath as a JSON file.

    Args:
        data (dict or list): The data to be saved.
        filepath (str): The path to the file where data should be saved.
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


# Load the season IDs from the input file
input_path = '/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw/seasons.json'

with open(input_path, 'r') as f:
    all_season_info = json.load(f)

try:
    # Iterate through each season
    for season in all_season_info['seasons']:
        season_id = season['id']
        season_year = season['year'].replace("/", "_")
        print(f"Fetching standings for season {season_id}...")

        # Structure to hold standings for each season
        season_standings = {'season_id': season_id, 'rounds': []}

        # Assuming there are up to 34 rounds
        for round_number in range(1, 35):
            print(f"Fetching standings for season {season_id}, round {round_number}...")
            standings = fetch_standings(season_id, round_number)
            if standings:
                season_standings['rounds'].append({
                    'round_number': round_number,
                    'standings': standings
                })
            
            # Pause between requests to avoid hitting rate limits
            time.sleep(1)

        # Save the standings for this season in a separate file
        output_file = f"season_{season_year}_standings.json"
        output_path = os.path.join('/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw', output_file)

        # Save to JSON file
        save_progress(season_standings, output_path)

        print(f"Standings for season {season_year} saved to {output_path}")

except Exception as e:
    print(f"Error: {e}")