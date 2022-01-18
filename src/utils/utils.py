import os
from dotenv import load_dotenv
from aiogram import types
from loguru import logger
from aiogram import types

def get_log_message(message: types.Message) -> str:
    result = f"User {message.from_user.id}, chat {message.chat.id} send message: '{message.text}'"
    return result

'''
def get_environment_variable(name: str) -> str:
    """Get environment variable value from .env file by input <name>

    Args:
        name (str): variable name

    Returns:
        str: variable values
    """
    # set .env file path and load in environments
    env_path = os.path.join("src/.env")
    load_dotenv(dotenv_path=env_path)
    # get value by name
    return os.environ.get(name)


def auth(func):
    async def wrapper(message: types.Message):
        user_id = str(message.from_user.id)
        logger.debug(f'User {user_id} send message')
        if not bool(int(get_environment_variable("IS_BOT_PRODUCTION"))):
            if user_id != get_environment_variable("TELEGRAM_ADMIN_USER_ID"):
                return await message.reply("Access denied", reply=False)
        return await func(message)
    
    return wrapper
'''