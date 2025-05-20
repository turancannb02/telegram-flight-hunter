#!/usr/bin/env python3
"""
main.py

Telegram Flight Hunter Bot
--------------------------

A single-file Telegram bot that:
  • Loads secrets from .env
  • Retrieves an OAuth token from Amadeus
  • Searches flights BER/IST → Balkan cities
  • Sends Markdown alerts via Telegram
  • Schedules checks automatically
"""

import os
import asyncio
import requests
import schedule
from datetime import datetime
from dotenv import load_dotenv
import telegram
from telegram.ext import Application, CommandHandler
from telegram.helpers import escape_markdown

# ------------------------------------------------------------------------------
# 1. Load environment variables from .env
# ------------------------------------------------------------------------------
load_dotenv()
TELEGRAM_TOKEN     = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID            = os.getenv("CHAT_ID", "")
AMADEUS_API_KEY    = os.getenv("AMADEUS_API_KEY", "")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")

# ------------------------------------------------------------------------------
# 2. Amadeus API endpoints & search parameters
# ------------------------------------------------------------------------------
AMADEUS_TOKEN_URL  = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

ORIGINS = [
    {"code": "BER", "name": "Berlin"},
    {"code": "IST", "name": "Istanbul"},
]
DESTINATIONS = [
    {"code": "TGD", "name": "Podgorica"},
    {"code": "TIV", "name": "Tivat"},
    {"code": "BEG", "name": "Belgrade"},
    {"code": "TIA", "name": "Tirana"},
]
DATES = [
    {"departure": "2025-07-05", "return": "2025-07-12", "display": "5–12 Jul 2025"},
    {"departure": "2025-07-05", "return": "2025-07-13", "display": "5–13 Jul 2025"},
    # ...add more date windows...
]
ADULTS_PER_ORIGIN = 2
PRICE_THRESHOLD   = 1000  # EUR total for all travellers

# ------------------------------------------------------------------------------
# 3. Amadeus auth & search
# ------------------------------------------------------------------------------
def get_amadeus_token() -> str | None:
    resp = requests.post(
        AMADEUS_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": AMADEUS_API_KEY,
            "client_secret": AMADEUS_API_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    print(f"[{datetime.now()}] Amadeus error:", resp.text)
    return None

async def search_flights() -> bool:
    token = get_amadeus_token()
    if not token:
        return False
    headers = {"Authorization": f"Bearer {token}"}
    found = False

    for date in DATES:
        for dest in DESTINATIONS:
            prices = {}
            for origin in ORIGINS:
                params = {
                    "originLocationCode": origin["code"],
                    "destinationLocationCode": dest["code"],
                    "departureDate": date["departure"],
                    "returnDate": date["return"],
                    "adults": ADULTS_PER_ORIGIN,
                    "max": 10,
                }
                try:
                    r = requests.get(AMADEUS_FLIGHT_URL, headers=headers, params=params)
                    r.raise_for_status()
                    flights = r.json().get("data", [])
                    prices[origin["name"]] = (
                        min(float(f["price"]["total"]) for f in flights)
                        if flights else float("inf")
                    )
                except Exception as e:
                    print(f"[{datetime.now()}] {origin['code']}→{dest['code']} error:", e)
                    prices[origin["name"]] = float("inf")

            if all(p < float("inf") for p in prices.values()):
                total = sum(prices.values())
                if total < PRICE_THRESHOLD:
                    msg = [
                        f"🎉 *Deal!* {dest['name']}",
                        f"📅 Dates: *{date['display']}*",
                        f"💶 Total: *{total:.2f} €*",
                    ]
                    msg += [f"  – {o}: {p:.2f} €" for o,p in prices.items()]
                    await send_message("\n".join(msg))
                    found = True

    if not found:
        await send_message("🔎 No deals found – I'll keep trying!")
    return found

# ------------------------------------------------------------------------------
# 4. Telegram messaging
# ------------------------------------------------------------------------------
_bot = None
def get_bot() -> telegram.Bot:
    global _bot
    if _bot is None:
        _bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return _bot

async def send_message(text: str):
    safe = escape_markdown(text, version=2)
    await get_bot().send_message(chat_id=CHAT_ID, text=safe, parse_mode="MarkdownV2")

# ------------------------------------------------------------------------------
# 5. Command handlers
# ------------------------------------------------------------------------------
async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text("👋 Subscribed! I'll send deals here.")
    await send_message("✅ Bot is now active.")

async def manual_search(update, context):
    await update.message.reply_text("🔍 Running search…")
    await search_flights()
    await update.message.reply_text("✅ Done.")

# ------------------------------------------------------------------------------
# 6. Scheduler
# ------------------------------------------------------------------------------
def schedule_searches():
    for hh in (8, 11, 14, 17, 20):
        schedule.every().day.at(f"{hh:02d}:00").do(lambda: asyncio.run(search_flights()))
    schedule.every().day.at("22:00").do(lambda: asyncio.run(search_flights()))
    schedule.every().day.at("03:00").do(lambda: asyncio.run(search_flights()))

async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)

# ------------------------------------------------------------------------------
# 7. Main entrypoint
# ------------------------------------------------------------------------------
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", manual_search))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    schedule_searches()
    await run_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
