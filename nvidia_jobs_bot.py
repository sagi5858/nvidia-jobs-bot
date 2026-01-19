import requests
import os
import json
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEEN_FILE = "seen_jobs.json"

SEARCH_URL = (
    "https://nvidia.wd5.myworkdayjobs.com"
    "/en-US/NVIDIAExternalCareerSite"
    "?locations=Israel"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": msg[:3900],
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

def main():
    r = requests.get(SEARCH_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    job_links = soup.select("a[data-automation-id='jobTitle']")

    seen = load_seen()
    new_items = []

    for a in job_links:
        title = a.get_text(strip=True)
        href = a.get("href")

        if not href:
            continue

        url = "https://nvidia.wd5.myworkdayjobs.com" + href
        text = (title + " " + href).lower()

        # סינון יוקנעם / צפון
        if "yokneam" not in text and "north" not in text:
            continue

        if url not in seen:
            new_items.append(f"{title}\n{url}")
            seen.add(url)

    if not new_items:
        save_seen(seen)
        return

    send_telegram(
        "משרות חדשות ב-NVIDIA (Israel / Yokneam):\n\n"
        + "\n\n---\n\n".join(new_items)
    )
    save_seen(seen)

if __name__ == "__main__":
    main()
