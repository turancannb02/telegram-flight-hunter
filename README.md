# Telegram Flight Hunter ☀️✈️

A simple Telegram bot that periodically searches the Amadeus API for the cheapest round-trip flights  
from Berlin (BER) and Istanbul (IST) to a set of Balkan destinations, and notifies you on Telegram when  
a deal under your price threshold is found.

---

## Prerequisites

- You have Python 3.10 or newer installed.
- You can install Python packages with `pip`.

---

## 1. Get your Telegram bot token

1. Open Telegram and chat with **@BotFather**.  
2. Send the command `/newbot`.  
3. Follow the prompts:
   - Choose a **bot name** (e.g. “SummerFlightHunter”).  
   - Choose a **username** ending in “bot” (e.g. `summer_flight_hunter_bot`).  
4. BotFather replies with a token string (looks like `123456789:ABCDefGhIjKlmNoPQRsTUVwxyZ`).  
5. Copy that token—you’ll paste it into your `.env` in step 4.

---

## 2. Get your Amadeus API key & secret

1. Go to the Amadeus for Developers portal: https://developers.amadeus.com/  
2. Sign up for a free account or log in.  
3. In your dashboard, create a **New App**.  
4. In the App settings you will see two values:
   - **API Key** (also called “Client ID”)  
   - **API Secret** (also called “Client Secret”)  
5. Copy both values—you’ll paste them into your `.env` in step 4.

---

## 3. Prepare the repository

- Clone or download this repository to your computer.
- You will see two key files:
  - `README.md` (this file)  
  - `main.py` (the bot code)  
- There is also an example environment file named `.env.example`.

---

## 4. Configure your secrets

1. Make a copy of `.env.example` and name it `.env`.  
2. Open `.env` in your editor and fill in the four values:
   - `TELEGRAM_TOKEN` ← the token from BotFather  
   - `CHAT_ID` ← leave blank (the bot will fill this on `/start`)  
   - `AMADEUS_API_KEY` ← your Amadeus Client ID  
   - `AMADEUS_API_SECRET` ← your Amadeus Client Secret  

---

## 5. Install dependencies

1. From the repository folder, run:
```bash
pip install python-dotenv python-telegram-bot[asyncio] requests schedule
```

2. This will install:
- `python-dotenv` for loading `.env`
- `python-telegram-bot` for Telegram integration
- `requests` for HTTP calls
- `schedule` for periodic checks

---

## 6. Run the bot

1. In your terminal or command prompt, start the bot by running:
```bash
python main.py
```

2. In Telegram:
- Send `/start` to your new bot → it will confirm and save your chat ID.  
- Send `/search` anytime to trigger an immediate flight search.  
3. The bot will also automatically search:
- Five times per day at 08:00, 11:00, 14:00, 17:00, 20:00
- Twice per night at 22:00 and 03:00

---

## 7. Adjusting parameters

Inside `main.py` you can customize:

- `ORIGINS` and `DESTINATIONS` (airport codes + names)  
- `DATES` array (departure/return windows & display labels)  
- `ADULTS_PER_ORIGIN` (travellers per city)  
- `PRICE_THRESHOLD` (total EUR ceiling for the group)  

Simply edit those top-of-file constants to suit your needs.

---

## License

This project is released under the **MIT License**. See the `LICENSE` file for details.  
Feel free to fork, adapt, and improve!

