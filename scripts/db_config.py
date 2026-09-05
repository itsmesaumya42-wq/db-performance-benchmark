"""
db_config.py
Central place to configure and open the database connection.
Swap in your real credentials, or set them via environment variables.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "db_perf_benchmark"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)
