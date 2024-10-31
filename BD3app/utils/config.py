# BD3app/utils/config.py

import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    config = {
        "backend_url": os.getenv("FASTAPI_BACKEND_URL"),
    }
    return config
