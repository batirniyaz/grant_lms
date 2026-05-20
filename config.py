import os
from dotenv import load_dotenv
import pytz
import datetime

TASHKENT_TZ = pytz.timezone("Asia/Tashkent")

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

SECRET = os.getenv("SECRET", "YOUR_SUPER_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def now_tashkent():
    return datetime.datetime.now(TASHKENT_TZ)




