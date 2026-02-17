import requests
import csv
import re
from collections import defaultdict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- CONFIG ---

# Top US stock tickers (can expand or replace with full list)
VALID_TICKERS = {
    "TSLA", "NVDA", "GME", "AMC", "AAPL", "MSFT", "AMD", "NFLX",
    "BA", "BABA", "FB", "META", "GOOG", "GOOGL", "INTC", "AMD", "UBER"
}

# Words to ignore that match regex but aren't stocks
IGNORE_WORDS = {"CEO", "LOL", "YOLO", "FOMO"}

# Number of posts to scrape
POST_LIMIT = 100

# --- SCRAPE POSTS ---
url = f"https://www.reddit.com/r/wallstreetbets/hot.json?limit={POST_LIMIT}"

headers = {
    "User-Agent": "wsb_clean_scraper_v1"
}

response = requests.get(url, headers=headers)
data = response.json()

posts = data["data"]["children"]

# --- ANALYSIS SETUP ---
analyzer = SentimentIntensityAnalyzer()
ticker_counts = defaultdict(int)
ticker_sentiment = defaultdict(float)

ticker_pattern = r"\b[A-Z]{2,5}\b"

# --- PROCESS POSTS ---
for post in posts:
    post_data = post["data"]
    text = post_data["title"]

    # Find all uppercase words that look like tickers
    tickers = re.findall(ticker_pattern, text)

    if tickers:
        sentiment = analyzer.polarity_scores(text)["compound"]

        for ticker in tickers:
            # Only count valid tickers and ignore common words
            if ticker in VALID_TICKERS and ticker not in IGNORE_WORDS:
                ticker_counts[ticker] += 1
                ticker_sentiment[ticker] += sentiment

# --- COMPILE RESULTS ---
results = []

for ticker in ticker_counts:
    avg_sentiment = ticker_sentiment[ticker] / ticker_counts[ticker]
    results.append({
        "ticker": ticker,
        "mentions": ticker_counts[ticker],
        "average_sentiment": round(avg_sentiment, 3)
    })

# Sort by mentions
results.sort(key=lambda x: x["mentions"], reverse=True)

# --- SAVE TO CSV ---
with open("wsb_ticker_analysis.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["ticker", "mentions", "average_sentiment"])
    writer.writeheader()
    writer.writerows(results)

# --- PRINT TOP TRENDING ---
print("Top trending stocks on r/wallstreetbets:\n")
for r in results[:10]:
    print(r)
