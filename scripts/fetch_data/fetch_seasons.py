import json
import os
import requests
from datetime import datetime

# API key
api_key = "M3rnj5aYmoFbXpt7tTtSp3rgwXIrwZ4lhEHBeGlV"

# Base URL for the API endpoint
base_url = "https://api.sportradar.com/handball/trial/v2/en/competitions/sr%3Acompetition%3A149/seasons.json"


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


def filter_completed_seasons(seasons):
    """
    Filters out seasons that have not ended yet.

    Args:
        seasons (list): List of season dictionaries.

    Returns:
        list: Filtered list of completed seasons.
    """
    today = datetime.now().date()
    completed_seasons = [season for season in seasons if datetime.strptime(season['end_date'], "%Y-%m-%d").date() < today]
    return completed_seasons


try:
    # Fetch data from the API
    data = make_request(base_url, api_key)
    all_seasons = data['seasons']

    # Filter out current season
    completed_seasons = filter_completed_seasons(all_seasons)

    # Define the path to save the filtered data
    output_path = os.path.join('/Users/oleksiishcherbak/Projects/handball-bundesliga-analysis/data/raw', 'seasons.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the filtered data to a JSON file
    with open(output_path, 'w') as f:
        json.dump({"seasons": completed_seasons}, f, indent=2)

    print(f"Data saved to {output_path}")
except Exception as e:
    # Print any error that occurs during the request or file operation
    print(f"Error: {e}")
