import os
import dotenv

dotenv.load_dotenv(os.path.join("src", ".env"))

class Config:
    TELEGRAM_BOT_NAME=os.environ.get("TELEGRAM_BOT_NAME")
    TELEGRAM_BOT_USER_NAME=os.environ.get("TELEGRAM_BOT_USER_NAME")
    TELEGRAM_BOT_TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_ADMIN_USER_ID=os.environ.get("TELEGRAM_ADMIN_USER_ID")
    TELEGRAM_BOT_CHAT_ID=os.environ.get("TELEGRAM_BOT_CHAT_ID")
    DATABASE_COVID_NAME=os.environ.get("DATABASE_COVID_NAME")
    NAME=os.environ.get("NAME")