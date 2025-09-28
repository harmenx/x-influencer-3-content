import os
import tweepy
import logging
import json
import time
import random
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

logging.info("Starting post_to_x.py script.")

# Add a random delay up to an hour (3600 seconds)
random_delay_seconds = random.randint(0, 3600)
logging.info(f"Delaying post for {random_delay_seconds} seconds...")
time.sleep(random_delay_seconds)
logging.info("Delay complete. Proceeding with post.")

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

# --- Image Handling ---
media_id = None
try:
    image_dir = "post_images"
    if os.path.exists(image_dir) and os.path.isdir(image_dir):
        image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
        if image_files:
            image_to_post = os.path.join(image_dir, random.choice(image_files))
            logging.info(f"Selected image to post: {image_to_post}")

            # Authenticate with v1.1 API for media upload
            auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
            api = tweepy.API(auth)
            media = api.media_upload(filename=image_to_post)
            media_id = media.media_id_string
            logging.info(f"Image uploaded successfully. Media ID: {media_id}")
except Exception as e:
    logging.error(f"Error handling image: {e}")
# --- End of Image Handling ---


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

# Post the tweets with retry logic
last_tweet_id = None
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30

for i, tweet_part in enumerate(tweets_to_post):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            logging.info(f"Attempting to post tweet part {i+1}/{len(tweets_to_post)}: {tweet_part[:100]}...") # Log first 100 chars
            if i == 0:
                if media_id:
                    response = client.create_tweet(text=tweet_part, media_ids=[media_id])
                else:
                    response = client.create_tweet(text=tweet_part)
            else:
                # Wait for 30 seconds before posting subsequent tweets in a thread
                logging.info("Waiting 30 seconds before posting next tweet part...")
                time.sleep(30)
                response = client.create_tweet(text=tweet_part, in_reply_to_tweet_id=last_tweet_id)
            
            last_tweet_id = response.data['id']
            logging.info(f"Tweet part {i+1}/{len(tweets_to_post)} posted successfully! ID: {last_tweet_id}")
            logging.info(f"Response data: {response.data}")
            print(f"Tweet part {i+1}/{len(tweets_to_post)} posted successfully! ID: {last_tweet_id}")
            break  # Break out of retry loop if successful
        except tweepy.errors.TweepyException as e:
            retry_count += 1
            logging.error(f"Tweepy error posting tweet part {i+1}/{len(tweets_to_post)} (Attempt {retry_count}/{MAX_RETRIES}): {e}")
            logging.error(f"Tweepy error details: {e.response.text if e.response else 'No response text'}")
            print(f"Tweepy error posting tweet part {i+1}/{len(tweets_to_post)} (Attempt {retry_count}/{MAX_RETRIES}): {e}")
        except Exception as e:
            retry_count += 1
            logging.error(f"General error posting tweet part {i+1}/{len(tweets_to_post)} (Attempt {retry_count}/{MAX_RETRIES}): {e}")
            print(f"General error posting tweet part {i+1}/{len(tweets_to_post)} (Attempt {retry_count}/{MAX_RETRIES}): {e}")
            if retry_count < MAX_RETRIES:
                logging.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logging.error(f"Failed to post tweet part {i+1}/{len(tweets_to_post)} after {MAX_RETRIES} attempts.")
                exit(1)

logging.info("Script finished.")
