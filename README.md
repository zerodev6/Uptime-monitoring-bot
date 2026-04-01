# ⏱️ Uptime Monitor Bot

A Pyrogram-based Telegram bot that keeps your apps and websites alive 24/7 with auto-pinging, premium subscriptions via Telegram Stars, MongoDB database, and broadcast tools.

**Developer:** [@Venuboyy](https://t.me/Venuboyy)

---

## 🚀 Features

- **Force Subscribe** to 2 channels before using the bot
- **Animated sticker** on welcome (auto-deletes after 2 sec)
- **Random welcome image** from API
- **Time-based greeting** (morning / afternoon / evening / night)
- **URL Monitoring** — pings every 5 minutes, notifies on up/down
- **Free users:** up to 5 apps | **Premium:** unlimited
- **Premium management** via admin commands + Telegram Stars payment
- **Admin broadcast** to all users or all groups (with pin option + cancel)
- **MongoDB** for persistent user, chat, app, and premium data
- **500 Pyrogram workers** for high throughput
- **/info** — user profile card with profile photo
- **/stats** — total users, groups, monitored apps

---

## 📋 Commands

| Command | Who | Description |
|---|---|---|
| `/start` | All | Welcome message |
| `/help` | All | Usage guide |
| `/about` | All | Bot info |
| `/add` | All | Add a URL to monitor |
| `/apps` | All | List your monitored URLs |
| `/info` | All | Your Telegram profile info |
| `/myplan` | All | Check premium status |
| `/plan` | All | View premium plans |
| `/stats` | Admin | Bot statistics |
| `/users` | Admin | User count |
| `/broadcast` | Admin | Broadcast to all users |
| `/grp_broadcast` | Admin | Broadcast to all groups |
| `/add_premium` | Admin | Grant premium to user |
| `/remove_premium` | Admin | Revoke premium |
| `/get_premium` | Admin | Check user's premium |
| `/premium_users` | Admin | List all premium users |
| `/clear_junk` | Admin | Remove blocked/deleted users |
| `/junk_group` | Admin | Leave dead groups |

---

## ⚙️ Setup

### Option A — Docker (recommended)

```bash
git clone <repo>
cd uptimebot
cp .env.example .env
# Edit .env with your values
docker compose up -d
```

This starts both the bot and a local MongoDB container automatically.  
To view logs: `docker compose logs -f bot`  
To stop: `docker compose down`

> **Note:** If you already have an external MongoDB (Atlas etc.), remove the `mongo` service from `docker-compose.yml` and set `MONGO_URI` in your `.env` to point to it.

### Option B — Manual

```bash
git clone <repo>
cd uptimebot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python bot.py
```

---

## 🌐 Heroku Deploy

Set all env vars from `.env.example` as Config Vars.  
Add buildpack: `heroku/python`  
Procfile:
```
worker: python bot.py
```

---

## 💎 Premium Plans (Telegram Stars)

Edit `STAR_PREMIUM_PLANS` in `config.py`:

```python
STAR_PREMIUM_PLANS = {
    100: "1 month",
    200: "3 months",
    500: "1 year",
}
```

---

## 📦 Project Structure

```
uptimebot/
├── bot.py          # Entry point
├── config.py       # All configuration
├── database.py     # MongoDB helper (motor)
├── script.py       # All message templates
├── utils.py        # Helpers (ping, broadcast, time)
├── scheduler.py    # Background ping loop
├── plugins/
│   ├── start.py    # /start, /help, /about, /info, force-sub
│   ├── monitor.py  # /add, /apps, URL management
│   ├── premium.py  # Premium commands + Stars payment
│   ├── broadcast.py# Broadcast + junk cleanup
│   └── admin.py    # /stats, /users
├── requirements.txt
└── .env.example
```
