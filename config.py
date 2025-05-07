import dotenv
import os

from dotenv import load_dotenv
load_dotenv()

telegram_api_key=os.getenv("telegram_api_key")
exchange_api_key=os.getenv("exchange_api_key")
