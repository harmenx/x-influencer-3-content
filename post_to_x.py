import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

# Get tweet text from environment variable
tweet_text = os.getenv("TWEET_TEXT")

if not tweet_text:
    print("Error: TWEET_TEXT environment variable is not set.")
    exit(1)

# Authenticate with Tweepy
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Post the tweet
try:
    response = client.create_tweet(text=tweet_text)
    print(f"Tweet posted successfully! ID: {response.data['id']}")
except Exception as e:
    print(f"Error posting tweet: {e}")
