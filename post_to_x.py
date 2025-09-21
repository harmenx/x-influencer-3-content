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

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    logging.error("Missing one or more X API credentials in environment variables.")
    exit(1)

logging.info("X API credentials loaded.")

# Get tweet text from environment variable
tweet_text = os.getenv("TWEET_TEXT")

print("XKEYS",consumer_key, consumer_secret, access_token, access_token_secret, tweet_text)

if not tweet_text:
    logging.error("Error: TWEET_TEXT environment variable is not set.")
    exit(1)

logging.info(f"Original tweet text loaded (first 50 chars): {tweet_text[:50]}...")

def split_tweet(text, max_length=140):
    """Splits a long text into multiple tweets, respecting max_length and adding pagination."""
    tweets = []
    words = text.split(' ')
    current_tweet = []
    current_length = 0
    
    # Calculate max length for content, reserving space for " (X/N)"
    # Max suffix length for 99 parts: " (99/99)" is 8 characters.
    # For simplicity, let's reserve 10 characters for suffix to be safe.
    suffix_reserve = 10 
    content_max_length = max_length - suffix_reserve

    for word in words:
        # Check if adding the next word exceeds the content_max_length
        # +1 for the space before the word
        if current_length + len(word) + (1 if current_tweet else 0) > content_max_length:
            if not current_tweet: # Handle case where a single word is too long
                # If a single word is too long, it will be truncated by Twitter anyway,
                # but we'll try to split it if possible, though Twitter's own splitting
                # might be more sophisticated. For now, we'll just add it as is.
                tweets.append(word)
                current_tweet = []
                current_length = 0
                continue
            tweets.append(" ".join(current_tweet))
            current_tweet = [word]
            current_length = len(word)
        else:
            current_tweet.append(word)
            current_length += len(word) + (1 if len(current_tweet) > 1 else 0) # Add 1 for space

    if current_tweet:
        tweets.append(" ".join(current_tweet))

    # Add pagination
    total_tweets = len(tweets)
    paginated_tweets = []
    for i, tweet in enumerate(tweets):
        suffix = f" ({i+1}/{total_tweets})"
        # Ensure suffix fits. If not, truncate tweet content.
        if len(tweet) + len(suffix) > max_length:
            tweet = tweet[:max_length - len(suffix) - 1] + "…" # Truncate and add ellipsis
        paginated_tweets.append(tweet + suffix)
    
    return paginated_tweets

# Split the tweet text
split_tweets = split_tweet(tweet_text)
logging.info(f"Tweet split into {len(split_tweets)} parts.")

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
for i, tweet_part in enumerate(split_tweets):
    try:
        if i == 0:
            response = client.create_tweet(text=tweet_part)
        else:
            response = client.create_tweet(text=tweet_part, in_reply_to_tweet_id=last_tweet_id)
        
        last_tweet_id = response.data['id']
        logging.info(f"Tweet part {i+1}/{len(split_tweets)} posted successfully! ID: {last_tweet_id}")
        print(f"Tweet part {i+1}/{len(split_tweets)} posted successfully! ID: {last_tweet_id}")
    except Exception as e:
        logging.error(f"Error posting tweet part {i+1}/{len(split_tweets)}: {e}")
        print(f"Error posting tweet part {i+1}/{len(split_tweets)}: {e}")
        exit(1)

logging.info("Script finished.")
