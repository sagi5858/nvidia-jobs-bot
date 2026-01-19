import requests
import json
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEEN_FILE = "seen_jobs.json"

# JSON ציבורי של NVIDIA (GET – לא נחסם)
JOBS_URL = (
    "https://nvidia.wd5.myworkdayjobs.com"
    "/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"
    "?limit=50&offset=0"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
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
    r = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": msg[:3900],
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
    r.raise_for_status()

def is_israel_yokneam(job):
    text = (
        job.get("title", "")
        + " "
        + str(job.get("locations", ""))
        + " "
        + str(job.get("externalPath", ""))
    ).lower()

    return "israel" in text and ("yokneam" in text or "north" in text)

def main():
    r = requests.get(JOBS_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    jobs = r.json().get("jobPostings", [])

    seen = load_seen()
    new_items = []

    for job in jobs:
        if not is_israel_yokneam(job):
            continue

        path = job.get("externalPath")
        title = job.get("title", "NVIDIA Job")

        if path and path not in seen:
            url = (
                "https://nvidia.wd5.myworkdayjobs.com"
                "/en-US/NVIDIAExternalCareerSite"
                + path
            )
            new_items.append(f"{title}\n{url}")
            seen.add(path)

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
