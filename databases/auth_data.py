import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')
db_name = os.getenv('DB_NAME')
