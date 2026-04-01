import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot credentials
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")

    # MongoDB
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "uptimebot")

    # Admin
    ADMINS = list(map(int, os.environ.get("ADMINS", "").split())) if os.environ.get("ADMINS") else []
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))

    # Force Subscribe Channels
    FORCE_SUB_CHANNEL_1 = os.environ.get("FORCE_SUB_CHANNEL_1", "zerodev2")  # username or -100xxx id
    FORCE_SUB_CHANNEL_2 = os.environ.get("FORCE_SUB_CHANNEL_2", "mvxyoffcail")

    # Log Channel
    PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS", 0)) if os.environ.get("PREMIUM_LOGS") else None

    # Welcome Image API
    WELCOME_IMAGE = os.environ.get("WELCOME_IMAGE", "https://api.aniwallpaper.workers.dev/random?type=girl")

    # Force Sub Banner
    FORCE_SUB_IMAGE = os.environ.get("FORCE_SUB_IMAGE", "https://i.ibb.co/pr2H8cwT/img-8312532076.jpg")

    # Timezone
    TIMEZONE = "Asia/Kolkata"

    # Pyrogram workers
    WORKERS = int(os.environ.get("WORKERS", 500))

    # Premium plans via Telegram Stars: {stars_amount: "duration_string"}
    STAR_PREMIUM_PLANS = {
        100: "1 month",
        200: "3 months",
        500: "1 year",
    }

    # Free user app limit
    FREE_USER_LIMIT = 5
