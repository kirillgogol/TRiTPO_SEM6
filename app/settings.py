from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv('USER')
DB_PASSWORD = os.getenv('PASSWORD')
DB_HOST = os.getenv('HOST')
DB_NAME = os.getenv('DB_NAME')