import json
import os
import time
import requests

# API key
api_key = "M3rnj5aYmoFbXpt7tTtSp3rgwXIrwZ4lhEHBeGlV"

# Base URL for the API endpoint
base_url = "https://api.sportradar.com/handball/trial/v2/en/seasons/{}/summaries.json"


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


def fetch_all_summaries(season_id):
    """
    Fetches all summaries for a given season ID, handling pagination and avoiding duplicates.

    Args:
        season_id (str): The ID of the season to fetch summaries for.

    Returns:
        list: A list of summaries for the season.
    """
    start = 0
    limit = 100
    all_summaries = []
    unique_event_ids = set()
    request_count = 0

    while True:
        url = f"{base_url.format(season_id)}?start={start}&limit={limit}"
        print(f"Requesting data from {url}")
        try:
            response = make_request(url, api_key)
            if 'summaries' not in response:
                print(f"Unexpected response format: {response}")
                break
            summaries = response['summaries']
            if not summaries:
                print(f"No more summaries found for season {season_id}.")
                break

            new_summaries = []
            for summary in summaries:
                event_id = summary.get('sport_event', {}).get('id')
                if event_id and event_id not in unique_event_ids:
                    unique_event_ids.add(event_id)
                    new_summaries.append(summary)
                else:
                    print(f"Duplicate or missing event ID: {summary}")

            if not new_summaries:
                print(f"No new summaries found for season {season_id}.")
                break

            all_summaries.extend(new_summaries)
            start += limit
            request_count += 1

            # Pause between requests to avoid hitting rate limits
            time.sleep(1)

            # Print progress
            print(f"Request {request_count}: {len(new_summaries)} summaries")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limit reached. Please wait and try again later.")
                break
            else:
                print(f"HTTP error: {e}")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    return all_summaries


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
    # Iterate through each season and fetch summaries
    for season in all_season_info['seasons']:
        season_id = season['id']
        season_year = season['year'].replace("/", "_")
        print(f"Starting season {season_id}...")

        # Fetch summaries for the season
        season_summaries = fetch_all_summaries(season_id)

        # Save the summaries in a separate file for each season
        output_path = f"/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw/season_{season_year}_summaries.json"
        save_progress(season_summaries, output_path)

        print(f"Summaries for season {season_year} saved to {output_path}")

except Exception as e:
    print(f"Error: {e}")