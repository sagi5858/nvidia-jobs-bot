import requests
import json
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

WORKDAY_URL = "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"

SEEN_FILE = "seen_jobs.json"

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    })

def main():
    payload = {
    "limit": 50,
    "offset": 0,
    "searchText": "Yokneam Israel"
}

    r = requests.post(WORKDAY_URL, json=payload)
    jobs = r.json().get("jobPostings", [])

    seen = load_seen()
    new = []

    for job in jobs:
        text = (job.get("title","") + " " + str(job.get("bulletFields",""))).lower()
if "israel" not in text or "yokneam" not in text:
    continue
        jid = job.get("externalPath")
        title = job.get("title")
        if jid and jid not in seen:
            url = f"https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite{jid}"
            new.append(f"{title}\n{url}")
            seen.add(jid)

    if new:
        send_telegram("משרות חדשות ב-NVIDIA:\n\n" + "\n\n".join(new))
    else:
        send_telegram("אין משרות חדשות היום ב-NVIDIA.")

    save_seen(seen)

if __name__ == "__main__":
    main()
