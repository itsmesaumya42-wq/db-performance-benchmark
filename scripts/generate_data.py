"""
generate_data.py

Populates the `merchants` and `transactions` tables with synthetic data
so you have a large enough dataset (default 500,000 rows) to make
indexing differences actually visible.

Usage:
    python scripts/generate_data.py --rows 500000
"""

import argparse
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

from db_config import get_connection

fake = Faker()

CATEGORIES = ["GROCERY", "TRAVEL", "ELECTRONICS", "DINING", "FUEL", "PHARMACY", "ONLINE_RETAIL"]
COUNTRIES = ["US", "IN", "GB", "CA", "AU", "DE", "SG"]
STATUSES = ["APPROVED", "DECLINED", "REVERSED"]
STATUS_WEIGHTS = [0.85, 0.12, 0.03]  # realistic skew — most transactions approve


def seed_merchants(conn, count=500):
    rows = [
        (fake.company(), random.choice(CATEGORIES), random.choice(COUNTRIES))
        for _ in range(count)
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO merchants (merchant_name, category, country_code) VALUES %s",
            rows,
        )
    conn.commit()
    print(f"Inserted {count} merchants.")


def seed_transactions(conn, total_rows, batch_size=10000):
    with conn.cursor() as cur:
        cur.execute("SELECT merchant_id, category, country_code FROM merchants")
        merchants = cur.fetchall()

    start_date = datetime.now() - timedelta(days=180)
    inserted = 0

    while inserted < total_rows:
        batch = []
        current_batch_size = min(batch_size, total_rows - inserted)

        for _ in range(current_batch_size):
            merchant_id, category, country = random.choice(merchants)
            card_number = fake.credit_card_number(card_type="visa")
            amount = round(random.uniform(1.0, 2500.0), 2)
            created_at = start_date + timedelta(
                seconds=random.randint(0, 180 * 24 * 3600)
            )
            status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

            batch.append(
                (
                    card_number,
                    merchant_id,
                    category,
                    amount,
                    "USD",
                    country,
                    status,
                    created_at,
                )
            )

        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO transactions
                (card_number, merchant_id, merchant_category, amount,
                 currency, country_code, status, created_at)
                VALUES %s
                """,
                batch,
            )
        conn.commit()
        inserted += current_batch_size
        print(f"Inserted {inserted}/{total_rows} transactions...")

    print("Done seeding transactions.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=500_000, help="Number of transaction rows to generate")
    parser.add_argument("--merchants", type=int, default=500, help="Number of merchants to generate")
    args = parser.parse_args()

    conn = get_connection()
    try:
        seed_merchants(conn, args.merchants)
        seed_transactions(conn, args.rows)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
