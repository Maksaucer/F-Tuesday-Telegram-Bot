import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
E621_USERNAME = os.getenv("E621_USERNAME")
E621_API_KEY = os.getenv("E621_API_KEY")
USER_AGENT = 'FurryTuesdayBot/1.0 (by @maksaucer)'