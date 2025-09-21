import os
import tweepy
import logging
import json
import time # Import the time module
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

logging.info("Starting post_to_x.py script.")

# Get environment variables
consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    logging.error("Missing one or more X API credentials in environment variables.")
    exit(1)

logging.info("X API credentials loaded.")

# Get tweet text from environment variable
tweet_json_string = os.getenv("TWEET_TEXT")

if not tweet_json_string:
    logging.error("Error: TWEET_TEXT environment variable is not set or is empty.")
    exit(1)

try:
    tweets_to_post = json.loads(tweet_json_string)
    if not isinstance(tweets_to_post, list) or not all(isinstance(t, str) for t in tweets_to_post):
        logging.error("Error: TWEET_TEXT is not a valid JSON list of strings.")
        exit(1)
except json.JSONDecodeError as e:
    logging.error(f"Error decoding TWEET_TEXT JSON: {e}")
    exit(1)

logging.info(f"Loaded {len(tweets_to_post)} tweets from TWEET_TEXT.")

# Authenticate with Tweepy
try:
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    logging.info("Tweepy client authenticated.")
except Exception as e:
    logging.error(f"Error authenticating with Tweepy: {e}")
    exit(1)

# Post the tweets
last_tweet_id = None
for i, tweet_part in enumerate(tweets_to_post):
    try:
        if i == 0:
            response = client.create_tweet(text=tweet_part)
        else:
            # Wait for 30 seconds before posting subsequent tweets in a thread
            logging.info("Waiting 30 seconds before posting next tweet part...")
            time.sleep(30)
            response = client.create_tweet(text=tweet_part, in_reply_to_tweet_id=last_tweet_id)
        
        last_tweet_id = response.data['id']
        logging.info(f"Tweet part {i+1}/{len(tweets_to_post)} posted successfully! ID: {last_tweet_id}")
        print(f"Tweet part {i+1}/{len(tweets_to_post)} posted successfully! ID: {last_tweet_id}")
    except Exception as e:
        logging.error(f"Error posting tweet part {i+1}/{len(tweets_to_post)}: {e}")
        print(f"Error posting tweet part {i+1}/{len(tweets_to_post)}: {e}")
        exit(1)

logging.info("Script finished.")
