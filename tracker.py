# ===============================
# FINAL TCG TRACKER (BEGINNER)
# Pokemon + One Piece
# Prediction alerts (30 / 10 min)
# Discord alerts
# Cloud-ready (Railway)
# ===============================

import asyncio
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify

# -------------------------------
# CONFIG — EDIT ONLY THIS SECTION
# -------------------------------

DISCORD_WEBHOOKS = {
    "Pokemon": "https://discordapp.com/api/webhooks/1467793197647528141/fhTQQ6KvTVLv9UutC8jq4tza54d9eO3qz29sucV9YM8RmzB3Xl9nbwlOk1pNk_0mUaap",
    "One Piece": "https://discordapp.com/api/webhooks/1467793197647528141/fhTQQ6KvTVLv9UutC8jq4tza54d9eO3qz29sucV9YM8RmzB3Xl9nbwlOk1pNk_0mUaap"
}

# Simple keywords for auto-discovery
KEYWORDS = {
    "Pokemon": ["pokemon", "scarlet", "violet"],
    "One Piece": ["one piece", "op-", "bandai"]
}

# -------------------------------
# INTERNAL STORAGE
# -------------------------------

HISTORY_FILE = "drop_history.json"
last_hit = {}

app = Flask(__name__)

# -------------------------------
# HELPERS
# -------------------------------

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-200:], f)

def send_discord(game, message):
    url = DISCORD_WEBHOOKS.get(game)
    if url:
        requests.post(url, json={"content": message})

# -------------------------------
# FAKE STORE CHECK (PLACEHOLDER)
# This simulates a real drop.
# Replace later with real store logic.
# -------------------------------

def check_for_drops():
    # Example: simulate a drop once per day at a random minute
    now = datetime.utcnow()
    if now.minute == 0:  # simple trigger
        game = "Pokemon" if now.hour % 2 == 0 else "One Piece"
        drop = {
            "time": now.isoformat(),
            "game": game,
            "store": "Example Store",
            "set": "Auto Discovered Set",
            "link": "https://example.com"
        }
        return drop
    return None

# -------------------------------
# PREDICTION LOGIC
# -------------------------------

def prediction_check():
    history = load_history()
    now = datetime.utcnow()

    for game in ["Pokemon", "One Piece"]:
        times = [
            datetime.fromisoformat(h["time"])
            for h in history if h["game"] == game
        ]

        if len(times) < 3:
            continue

        avg_hour = sum(t.hour for t in times) // len(times)
        avg_min = sum(t.minute for t in times) // len(times)

        predicted = now.replace(hour=avg_hour, minute=avg_min, second=0)

        for mins in [30, 10]:
            alert_time = predicted - timedelta(minutes=mins)
            if abs((alert_time - now).total_seconds()) < 60:
                send_discord(
                    game,
                    f"⏰ **{mins} MIN WARNING** — Possible {game} TCG drop soon"
                )

# -------------------------------
# MAIN LOOP
# -------------------------------

async def main_loop():
    global last_hit
    while True:
        drop = check_for_drops()
        if drop:
            last_hit = drop
            save_history(drop)
            send_discord(
                drop["game"],
                f"🚨 **DROP DETECTED**\n{drop['game']} — {drop['set']}\n{drop['link']}"
            )

        prediction_check()
        await asyncio.sleep(60)

# -------------------------------
# API (FOR WIDGETS)
# -------------------------------

@app.route("/api/last-hit")
def api_last_hit():
    return jsonify(last_hit or {})

# -------------------------------
# START
# -------------------------------

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main_loop())
    app.run(host="0.0.0.0", port=8080)
