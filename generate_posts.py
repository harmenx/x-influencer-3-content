# generate_posts.py
import os
import json
import sys # Import sys
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

import argparse

# Setup argument parser
parser = argparse.ArgumentParser(description="Generate tweets from a prompt file.")
parser.add_argument("--prompt", type=str, default="prompts/original_prompt.txt",
                    help="Path to the prompt file.")
args = parser.parse_args()

# Read prompt from the specified file
with open(args.prompt, "r", encoding="utf-8") as f:
    PROMPT = f.read()

def generate_tweets():
    """Generates a list of tweets using the Poe API, expecting a JSON array response."""
    print("Generating tweets...", file=sys.stderr) # Redirect to stderr
    # Modify the prompt to instruct Poe to return a JSON array of strings
    json_prompt = PROMPT + "\n\nPlease return the response as a JSON array of strings, where each string is a tweet."
    
    response = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": json_prompt}],
        max_tokens=500
    )
    json_response = response.choices[0].message.content.strip()
    
    # Clean the response: remove markdown code block delimiters if present
    if json_response.startswith("```json"):
        json_response = json_response[len("```json"):].strip()
    if json_response.endswith("```"):
        json_response = json_response[:-len("```")].strip()
    
    try:
        tweets = json.loads(json_response)
        if not isinstance(tweets, list) or not all(isinstance(t, str) for t in tweets):
            raise ValueError("Poe response is not a JSON list of strings.")
        return tweets
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Poe: {e}", file=sys.stderr) # Redirect to stderr
        print(f"Poe's raw response: {json_response}", file=sys.stderr) # Redirect to stderr
        exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr) # Redirect to stderr
        print(f"Poe's raw response: {json_response}", file=sys.stderr) # Redirect to stderr
        exit(1)

def save_raw_response(json_string):
    """Saves the raw JSON response to a markdown file with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{POSTS_DIR}/raw_tweets_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_string)
    print(f"Saved raw JSON response: {filename}", file=sys.stderr) # Redirect to stderr

if __name__ == "__main__":
    tweets_list = generate_tweets()
    json_output = json.dumps(tweets_list)
    save_raw_response(json_output)
    
    # Output the JSON string for the GitHub Action
    print(json_output) # This should be the only thing printed to stdout

    # The GitHub Action expects an output named 'filename' for the next step.
    # Since we are now outputting the JSON directly, we can output a dummy filename
    # or remove the 'Read Post Content' step from the workflow if it's no longer needed.
    # For now, let's output a dummy filename to avoid breaking the workflow.
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(f"filename=dummy_filename.md\n")
