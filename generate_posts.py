# generate_posts.py
import os
import json
import sys
from openai import OpenAI
from datetime import datetime
from googlesearch import search
import argparse

# Initialize Poe client
client = OpenAI(
    api_key=os.getenv("POE_API_KEY"),
    base_url="https://api.poe.com/v1"
)

# Folder to save posts
POSTS_DIR = "generated_posts"
os.makedirs(POSTS_DIR, exist_ok=True)

def get_recent_news():
    """Fetches recent news using a web search and returns a formatted string."""
    print("Fetching recent news...", file=sys.stderr)
    try:
        search_results = search("latest tech news", num_results=5)
        news_string = "Here is the latest news for context:\n"
        for result in search_results:
            news_string += f"- {result}\n"
        return news_string
    except Exception as e:
        print(f"Error fetching news: {e}", file=sys.stderr)
        return ""

def generate_tweets(prompt):
    """Generates a list of tweets using the Poe API, expecting a JSON array response."""
    print("Generating tweets...", file=sys.stderr)
    json_prompt = prompt + "\n\nPlease return the response as a JSON array of strings, where each string is a tweet."
    
    response = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": json_prompt}],
        max_tokens=1024, # Increased max_tokens for potentially longer prompts with news
    )
    json_response = response.choices[0].message.content.strip()
    
    if json_response.startswith("```json"):
        json_response = json_response[len("```json"):
].strip()
    if json_response.endswith("```"):
        json_response = json_response[:-len("```")].strip()
    
    try:
        tweets = json.loads(json_response)
        if not isinstance(tweets, list) or not all(isinstance(t, str) for t in tweets):
            raise ValueError("API response is not a JSON list of strings.")
        return tweets
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        print(f"Raw response: {json_response}", file=sys.stderr)
        exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"Raw response: {json_response}", file=sys.stderr)
        exit(1)

def save_raw_response(json_string):
    """Saves the raw JSON response to a markdown file with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{POSTS_DIR}/raw_tweets_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_string)
    print(f"Saved raw JSON response: {filename}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tweets from a prompt file.")
    parser.add_argument("--prompt", type=str, default="prompts/original_prompt.txt",
                        help="Path to the prompt file.")
    args = parser.parse_args()

    with open(args.prompt, "r", encoding="utf-8") as f:
        prompt_content = f.read()

    if "recent_news.txt" in args.prompt:
        news = get_recent_news()
        prompt_content = news + "\n" + prompt_content

    tweets_list = generate_tweets(prompt_content)
    json_output = json.dumps(tweets_list)
    save_raw_response(json_output)
    
    print(json_output)

    if os.getenv("GITHUB_OUTPUT"):
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(f"filename=dummy_filename.md\n")