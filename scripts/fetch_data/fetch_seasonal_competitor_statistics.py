import json
import os
import requests
import time

# API key
api_key = "M3rnj5aYmoFbXpt7tTtSp3rgwXIrwZ4lhEHBeGlV"

# Base URL for the API endpoint
base_url = "https://api.sportradar.com/handball/trial/v2/en/seasons/{}/competitors/{}/statistics.json"


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


def fetch_competitor_statistics(season_id, competitor_id):
    """
    Fetches the seasonal statistics for a given competitor in a specific season.

    Args:
        season_id (str): The ID of the season.
        competitor_id (str): The ID of the competitor.

    Returns:
        dict: The JSON response containing the competitor's statistics.
    """
    url = base_url.format(season_id, competitor_id)
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


# Paths to the season info files
season_info = {
    "22_23": {
        "season_id": "sr:season:95685",
        "file_path": "/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw/season_22_23_info.json"
    },
    "23_24": {
        "season_id": "sr:season:107903",
        "file_path": "/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw/season_23_24_info.json"
    }
}

try:
    # Iterate through each season info file
    for season_key, details in season_info.items():
        season_id = details["season_id"]
        info_path = details["file_path"]

        # Load the season-specific info file
        with open(info_path, 'r') as season_file:
            season_data = json.load(season_file)

        # Extract competitor IDs from the season information
        competitor_ids = set()
        for stage in season_data.get('stages', []):
            for group in stage.get('groups', []):
                for team in group.get('competitors', []):
                    competitor_ids.add(team['id'])

        # Fetch statistics for all competitors in this season
        all_competitor_stats = []
        for competitor_id in competitor_ids:
            print(f"Fetching statistics for competitor {competitor_id} in season {season_key}...")
            stats = fetch_competitor_statistics(season_id, competitor_id)
            if stats:
                all_competitor_stats.append({
                    'competitor_id': competitor_id,
                    'statistics': stats
                })
            
            # Pause between requests to avoid hitting rate limits
            time.sleep(1)

        # Save all competitor statistics for the season in one file
        output_file = f"season_{season_key}_competitor_statistics.json"
        output_path = os.path.join('/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw', output_file)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the statistics data to a JSON file
        save_progress(all_competitor_stats, output_path)

        print(f"All competitor statistics for season {season_key} saved to {output_path}")

except Exception as e:
    # Print any error that occurs during the request or file operation
    print(f"Error: {e}")
