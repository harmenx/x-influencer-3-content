# generate_posts.py
import os
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

def generate_post():
    """Generates a single post using the Poe API."""
    print("Generating post...")
    response = client.chat.completions.create(
        # gpt-4 is powerful but expensive. 
        # Consider "gpt-3.5-turbo" for a cheaper alternative.
        model="gpt-4", 
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=500
    )
    post_text = response.choices[0].message.content.strip()
    return post_text

def save_post(text):
    """Saves the post to a markdown file with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{POSTS_DIR}/post_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved post: {filename}")
    
    # Output the filename for the GitHub Action
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(f"filename={filename}\n")

if __name__ == "__main__":
    post = generate_post()
    save_post(post)
