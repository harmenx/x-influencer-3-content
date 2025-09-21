# generate_posts.py
import os
import json
from openai import OpenAI
from datetime import datetime

# Initialize Poe client
# Your Poe API key is read from the POE_API_KEY environment variable
client = OpenAI(
    api_key=os.getenv("POE_API_KEY"),
    base_url="https://api.poe.com/v1"
)

# Folder to save posts
POSTS_DIR = "generated_posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# Read prompt from prompt.txt
with open("prompt.txt", "r", encoding="utf-8") as f:
    PROMPT = f.read()

def generate_tweets():
    """Generates a list of tweets using the Poe API, expecting a JSON array response."""
    print("Generating tweets...")
    # Modify the prompt to instruct Poe to return a JSON array of strings
    json_prompt = PROMPT + "\n\nPlease return the response as a JSON array of strings, where each string is a tweet. Each tweet should be a maximum of 140 characters."
    
    response = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": json_prompt}],
        max_tokens=500
    )
    json_response = response.choices[0].message.content.strip()
    
    try:
        tweets = json.loads(json_response)
        if not isinstance(tweets, list) or not all(isinstance(t, str) for t in tweets):
            raise ValueError("Poe response is not a JSON list of strings.")
        return tweets
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Poe: {e}")
        print(f"Poe's raw response: {json_response}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Poe's raw response: {json_response}")
        exit(1)

def save_raw_response(json_string):
    """Saves the raw JSON response to a markdown file with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{POSTS_DIR}/raw_tweets_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_string)
    print(f"Saved raw JSON response: {filename}")

if __name__ == "__main__":
    tweets_list = generate_tweets()
    json_output = json.dumps(tweets_list)
    save_raw_response(json_output)
    
    # Output the JSON string for the GitHub Action
    print(json_output)

    # The GitHub Action expects an output named 'filename' for the next step.
    # Since we are now outputting the JSON directly, we can output a dummy filename
    # or remove the 'Read Post Content' step from the workflow if it's no longer needed.
    # For now, let's output a dummy filename to avoid breaking the workflow.
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(f"filename=dummy_filename.md\n")
