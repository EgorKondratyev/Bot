import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TOKEN')
admins = list(map(int, os.getenv('ADMINS').split(',')))
bot_name = os.getenv('BOT_NAME')

token_admin = os.getenv('ADMIN_TOKEN')
