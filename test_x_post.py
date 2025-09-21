import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

# Authenticate with Tweepy
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Post "Hello world"
try:
    response = client.create_tweet(text="Hello world from Gemini CLI!")
    print(f"Tweet posted successfully! ID: {response.data['id']}")
except Exception as e:
    print(f"Error posting tweet: {e}")
