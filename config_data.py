# config_data.py
from decouple import config
config.read(.env.template)

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
RAPIDAPI_KEY = config('RAPIDAPI_KEY')
RAPIDAPI_HOST = config('RAPIDAPI_HOST')
