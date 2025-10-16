import asyncio
import sys

import aiohttp
from dynaconf import Dynaconf

# --- Configuration and Setup ---

# Initialize Dynaconf to load settings
settings = Dynaconf(
    settings_files=["config/settings.toml", "config/.secrets.toml"],
    environments=True,
    envvar_prefix="PAKSENTIMENT"
)

# API Constants
TWITTER_API_URL = "https://api.twitter.com/2/tweets/search/recent"

# Headers for Authorization
HEADERS = {
    "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"
}

# --- Core Asynchronous Functions ---

async def fetch_twitter_data(session, tag):
    """
    Fetches recent tweets for a given tag from the Twitter API.
    """
    params = {
        "query": tag,
        "max_results": 10,
        # Request essential fields
        "tweet.fields": "created_at,author_id,text"
    }

    print(f"INFO: Attempting to fetch tweets for tag: '{tag}'")

    try:
        # Use the passed session for the GET request
        async with session.get(TWITTER_API_URL, params=params) as response:
            
            # 1. Handle HTTP Errors
            if response.status == 429:
                print("WARNING: Rate limit exceeded. Try again after the reset period.")
                return None
            
            if response.status != 200:
                error_text = await response.text()
                print(f"ERROR: Twitter API Error {response.status}: {error_text}")
                return None

            # 2. Handle successful JSON response
            data = await response.json()
            
            tweets = data.get("data", [])
            if not tweets:
                print(f"INFO: No tweets found for tag: '{tag}'")
                return None

            print(f"INFO: Successfully fetched {len(tweets)} tweets.")
            return tweets

    # 3. Handle Network and other Client-side Errors
    except aiohttp.ClientError as e:
        print(f"ERROR: Network or aiohttp Client Error: {e}")
        return None
    except Exception as e:
        print(f"CRITICAL: An unexpected critical error occurred: {e}")
        return None

def process_and_print_tweets(tweets, tag):
    """
    Processes and prints the fetched tweet data.
    """
    if not tweets:
        return

    print(f"\n--- Displaying Tweets for #{tag} ---")
    for tweet in tweets:
        print("--------------------------------------------------")
        print(f"Tweet ID: {tweet.get('id', 'N/A')}")
        print(f"Text: {tweet.get('text', '[No Text]')}")
        print(f"Author ID: {tweet.get('author_id', 'N/A')}")
        print(f"Created At: {tweet.get('created_at', 'N/A')}")
    print("--------------------------------------------------\n")


# --- Main Execution Function ---

async def main(tag):
    """
    The main asynchronous entry point of the script.
    """
    # Create the ClientSession here to manage its lifecycle efficiently
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # 1. Fetch the data
        tweet_data = await fetch_twitter_data(session, tag)
        
        # 2. Process and print the data
        if tweet_data:
            process_and_print_tweets(tweet_data, tag)

# --- Script Entry Point ---

if __name__ == "__main__":
    # Define the default search tag
    search_tag = "pakistan"

    # Start the asyncio event loop
    print("INFO: Starting Twitter Fetch Script...")
    try:
        asyncio.run(main(search_tag))
    except KeyboardInterrupt:
        print("INFO: Script interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"CRITICAL: A fatal error occurred in the main execution: {e}")
