import os
from typing import Final
from dotenv import load_dotenv

load_dotenv(override=True)

token: Final = os.getenv("BOT_TOKEN")
mongo_uri: Final = os.getenv("MONGODB_URI")
db_name: Final = os.getenv("DB_NAME")