import os
import dotenv

# load environment variable from .env file
dotenv.load_dotenv(os.path.join("src", ".env"))

class Config:
    TELEGRAM_BOT_NAME=os.environ.get("TELEGRAM_BOT_NAME")
    TELEGRAM_BOT_USER_NAME=os.environ.get("TELEGRAM_BOT_USER_NAME")
    TELEGRAM_BOT_TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_ADMIN_USER_ID=os.environ.get("TELEGRAM_ADMIN_USER_ID")
    TELEGRAM_BOT_CHAT_ID=os.environ.get("TELEGRAM_BOT_CHAT_ID")
    DATABASE_COVID_NAME=os.environ.get("DATABASE_COVID_NAME")
    NAME=os.environ.get("NAME")
    DATABASE_COVID_REFRESH_TIME="09:30"
    SEND_COVID_MESSAGE_TIME="09:45"