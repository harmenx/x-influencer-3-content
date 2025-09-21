import os
import tweepy
import logging
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

print("XKEYS",consumer_key, consumer_secret, access_token, access_token_secret)  # Debug print to verify env vars are loaded

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    logging.error("Missing one or more X API credentials in environment variables.")
    exit(1)

logging.info("X API credentials loaded.")

# Get tweet text from environment variable
tweet_text = os.getenv("TWEET_TEXT")

if not tweet_text:
    logging.error("Error: TWEET_TEXT environment variable is not set.")
    exit(1)

logging.info(f"Tweet text loaded: {tweet_text[:50]}...") # Log first 50 chars of tweet

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

# Post the tweet
try:
    response = client.create_tweet(text=tweet_text)
    logging.info(f"Tweet posted successfully! ID: {response.data['id']}")
    print(f"Tweet posted successfully! ID: {response.data['id']}") # Keep print for GitHub Actions output
except Exception as e:
    logging.error(f"Error posting tweet: {e}")
    print(f"Error posting tweet: {e}") # Keep print for GitHub Actions output
    exit(1)

logging.info("Script finished.")
