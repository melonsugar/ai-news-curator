import os
notion_token = "os.environ.get('NOTION_TOKEN')"
database_id = "os.environ.get('DATABASE_ID')"

import requests
def save_to_notion(title, summary, link):
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
def save_to_notion(title, summary, link):
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]},
            "summary": {"rich_text": [{"text": {"content": summary}}]},
            "link": {"url": link}
        },
        "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": summary}}]}}]
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    print(response.text)
# Inside your loop, just add:
# save_to_notion(title, summary, link)
from types import new_class
# ============================================================
# AI News RSS Feed Fetcher — with AI-generated summaries
# Paste this into a Google Colab cell and run it.
# ============================================================

# --- 1. Install dependencies ---
# !pip install feedparser anthropic

import feedparser
import anthropic
from datetime import datetime
from IPython.display import HTML, display

# --- 2. Your Anthropic API key ---
# Get yours at https://console.anthropic.com/
ANTHROPIC_API_KEY = "os.environ.get('ANTHROPIC_API_KEY')"

# --- 3. Define your RSS feeds ---
FEEDS = {
    "MIT Technology Review – AI": "https://www.technologyreview.com/feed/",
    "The Verge – AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "VentureBeat – AI": "https://feeds.feedburner.com/venturebeat/SZYF",
    "Wired – AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "Ars Technica – AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "TechCrunch – AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "Marketing AI Institute": "https://www.marketingaiinstitute.com/blog/rss.xml",
    # NOTE: The Batch (DeepLearning.AI) is a newsletter with no official RSS feed.
    # The URL below may return limited results. Subscribe at deeplearning.ai/the-batch/
    "The Batch – DeepLearning.AI": "https://www.deeplearning.ai/blog/feed/",
}

# How many headlines per feed
MAX_ITEMS = 5


# --- 4. Fetch RSS feed entries ---
def fetch_feed(url, max_items=MAX_ITEMS):
    """Return a list of dicts with title, link, date, and snippet from an RSS feed."""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "No title").strip()
            link = entry.get("link", "#")
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            date_str = datetime(*published[:6]).strftime("%b %d, %Y") if published else "Date unknown"
            # Grab description/summary text to feed to Claude
            snippet = (
                entry.get("summary", "")
                or entry.get("description", "")
                or entry.get("content", [{}])[0].get("value", "")
            )
            items.append({"title": title, "link": link, "date": date_str, "snippet": snippet})
        return items
    except Exception as e:
        return [{"title": f"Error: {e}", "link": "#", "date": "", "snippet": ""}]


# --- 5. Generate a one-sentence summary via Claude ---
def summarize(client, title, snippet):
    """Ask Claude for a one-sentence plain-English summary of an article."""
    if not snippet and not title:
        return "No description available."
    prompt = (
        f"Article title: {title}\n\n"
        f"Article excerpt: {snippet[:1500]}\n\n"
        "Write exactly one clear, plain-English sentence summarizing what this article is about. "
        "No filler phrases like 'This article discusses' — just the substance. "
        "Keep it under 30 words."
    )
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"(Summary unavailable: {e})"


# --- 6. Build styled HTML output ---
def build_html(feeds_dict, client):
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html_parts = [f"""
<style>
  .ai-digest {{
    font-family: 'Georgia', serif;
    font-size: 17px;
    line-height: 1.7;
    max-width: 860px;
    color: #1a1a1a;
  }}
  .ai-digest h1 {{
    font-size: 2em;
    margin-bottom: 0.2em;
    letter-spacing: -0.5px;
  }}
  .ai-digest .timestamp {{
    font-size: 0.85em;
    color: #888;
    margin-bottom: 1.5em;
  }}
  .ai-digest h2 {{
    font-size: 1.15em;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #555;
    border-bottom: 1px solid #ddd;
    padding-bottom: 4px;
    margin-top: 2em;
  }}
  .ai-digest .item {{
    margin: 1em 0 1.4em 0;
  }}
  .ai-digest .headline {{
    font-size: 1.05em;
    font-weight: bold;
    display: block;
    margin-bottom: 3px;
  }}
  .ai-digest .headline a {{
    color: #1a1a1a;
    text-decoration: none;
  }}
  .ai-digest .headline a:hover {{
    text-decoration: underline;
  }}
  .ai-digest .meta {{
    font-size: 0.78em;
    color: #999;
    margin-bottom: 4px;
  }}
  .ai-digest .summary {{
    font-size: 0.95em;
    color: #444;
  }}
</style>
<div class="ai-digest">
  <h1>🤖 AI News Digest</h1>
  <div class="timestamp">Fetched on {now}</div>
  <hr>
"""]

    for source_name, url in feeds_dict.items():
        print(f"  Fetching: {source_name}...")
        items = fetch_feed(url)
        html_parts.append(f'<h2>{source_name}</h2>')

        if not items or items[0]["title"].startswith("Error"):
            html_parts.append('<p><em>No items found.</em></p>')
            continue
        for item in items:
            summary = summarize(client, item["title"], item["snippet"])
            save_to_notion(item["title"], summary, item["link"])
            html_parts.append(f"""
  <div class="item">
    <span class="headline"><a href="{item['link']}" target="_blank">{item['title']}</a></span>
    <div class="meta">{source_name} &nbsp;·&nbsp; {item['date']}</div>
    <div class="summary">{summary}</div>
  </div>""")

    html_parts.append("</div>")
    return "\n".join(html_parts)


# --- 7. Run ---
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
print("Fetching feeds and generating summaries...\n")
html_output = build_html(FEEDS, client)

display(HTML(html_output))

# Optional: save to file
with open("ai_news_digest.html", "w") as f:
    f.write(html_output)
print("\nSaved to ai_news_digest.html")
