import yfinance as yf
import requests
import datetime
import os

print("Agent starting...")

# ======================
# Config
# ======================

MOLTBOOK_API = "https://www.moltbook.com/api/v1/posts"
API_KEY = os.getenv("MOLTBOOK_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY"]

# ======================
# Fetch stock movement
# ======================

def get_daily_move(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")

    if len(hist) < 2:
        return None

    prev = hist.iloc[-2]["Close"]
    last = hist.iloc[-1]["Close"]
    pct = (last - prev) / prev * 100

    return {
        "price": round(last, 2),
        "pct": round(pct, 2),
        "volume": int(hist.iloc[-1]["Volume"])
    }

# ======================
# Generate discussion text
# ======================

def generate_commentary(ticker, data):
    direction = "rose" if data["pct"] > 0 else "fell"

    return (
        f"${ticker} {direction} {abs(data['pct'])}% today, "
        f"closing at ${data['price']}.\n\n"
        f"Volume was {data['volume']:,}, suggesting "
        f"{'heightened interest' if data['pct'] != 0 else 'muted trading activity'}.\n\n"
        "This move likely reflects short-term market positioning "
        "rather than a fundamental shift."
    )

# ======================
# Post to Moltbook
# ======================

def post_to_moltbook(text):
    payload = {
        "title": "Daily Stock Price Discussion",
        "content": text,
        "submolt": "stocks"
    }

    r = requests.post(MOLTBOOK_API, json=payload, headers=HEADERS)
    r.raise_for_status()

# ======================
# Main loop
# ======================

def run():
    print("Run loop entered")

    today = datetime.date.today().isoformat()
    posts = []

    for ticker in WATCHLIST:
        print(f"Fetching data for {ticker}")
        data = get_daily_move(ticker)

        if not data:
            print(f"No data for {ticker}")
            continue

        print(f"Data for {ticker}: {data}")
        posts.append(generate_commentary(ticker, data))

    print(f"Generated {len(posts)} post sections")

    if posts:
        print("Posting to Moltbook...")
        post_to_moltbook(
            f"📊 Market discussion for {today}\n\n"
            + "\n\n---\n\n".join(posts)
        )
        print("Post request sent")
    else:
        print("Nothing to post")

if __name__ == "__main__":
    print("About to call run()")
    run()
