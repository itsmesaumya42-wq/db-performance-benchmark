"""
benchmark.py

The heart of the project. Defines a set of realistic payment-style
queries, runs each one BEFORE and AFTER adding a targeted index,
captures EXPLAIN (ANALYZE, BUFFERS) output, and records wall-clock
timing so you can produce a clear before/after comparison.

Usage:
    python scripts/benchmark.py
"""

import time
import json
import statistics
from pathlib import Path

from db_config import get_connection

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

RUNS_PER_QUERY = 5  # run each query multiple times and take the median


# Each scenario = a realistic query + the index that should speed it up.
# drop_sql runs first (idempotent) so re-running this script is always safe.
SCENARIOS = [
    {
        "name": "velocity_check_by_card",
        "description": "Count a card's transactions in the last 5 minutes (fraud velocity check)",
        "query": """
            SELECT COUNT(*) FROM transactions
            WHERE card_number = %s
              AND created_at > NOW() - INTERVAL '5 minutes';
        """,
        "params": ("4111111111111111",),
        "drop_sql": "DROP INDEX IF EXISTS idx_card_created;",
        "create_sql": "CREATE INDEX idx_card_created ON transactions (card_number, created_at);",
    },
    {
        "name": "category_spend_range",
        "description": "Sum spend for a merchant category over a date range",
        "query": """
            SELECT merchant_category, SUM(amount), COUNT(*)
            FROM transactions
            WHERE merchant_category = %s
              AND created_at BETWEEN NOW() - INTERVAL '30 days' AND NOW()
            GROUP BY merchant_category;
        """,
        "params": ("ELECTRONICS",),
        "drop_sql": "DROP INDEX IF EXISTS idx_category_created;",
        "create_sql": "CREATE INDEX idx_category_created ON transactions (merchant_category, created_at);",
    },
    {
        "name": "declined_by_country",
        "description": "Find declined transactions for a specific country (partial index)",
        "query": """
            SELECT transaction_id, card_number, amount, created_at
            FROM transactions
            WHERE status = 'DECLINED'
              AND country_code = %s
            ORDER BY created_at DESC
            LIMIT 100;
        """,
        "params": ("IN",),
        "drop_sql": "DROP INDEX IF EXISTS idx_declined_country;",
        "create_sql": """
            CREATE INDEX idx_declined_country
            ON transactions (country_code, created_at)
            WHERE status = 'DECLINED';
        """,
    },
    {
        "name": "merchant_join_report",
        "description": "Join merchants + transactions for a category report",
        "query": """
            SELECT m.merchant_name, COUNT(t.transaction_id), SUM(t.amount)
            FROM transactions t
            JOIN merchants m ON m.merchant_id = t.merchant_id
            WHERE m.category = %s
            GROUP BY m.merchant_name
            ORDER BY SUM(t.amount) DESC
            LIMIT 20;
        """,
        "params": ("DINING",),
        "drop_sql": "DROP INDEX IF EXISTS idx_txn_merchant_id;",
        "create_sql": "CREATE INDEX idx_txn_merchant_id ON transactions (merchant_id);",
    },
]


def run_query_timed(conn, query, params):
    """Run a query RUNS_PER_QUERY times, return the median wall-clock time in ms."""
    timings = []
    with conn.cursor() as cur:
        for _ in range(RUNS_PER_QUERY):
            start = time.perf_counter()
            cur.execute(query, params)
            cur.fetchall()
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)
    return statistics.median(timings), timings


def capture_explain(conn, query, params):
    """Capture EXPLAIN (ANALYZE, BUFFERS) output as text."""
    with conn.cursor() as cur:
        cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) " + query, params)
        rows = cur.fetchall()
    return "\n".join(row[0] for row in rows)


def main():
    conn = get_connection()
    conn.autocommit = True
    results = []

    for scenario in SCENARIOS:
        name = scenario["name"]
        print(f"\n=== {name} ===")
        print(scenario["description"])

        # --- BEFORE: make sure no relevant index exists ---
        with conn.cursor() as cur:
            cur.execute(scenario["drop_sql"])

        before_median, before_runs = run_query_timed(conn, scenario["query"], scenario["params"])
        before_explain = capture_explain(conn, scenario["query"], scenario["params"])
        print(f"BEFORE index -> median {before_median:.2f} ms")

        # --- AFTER: create the targeted index ---
        with conn.cursor() as cur:
            cur.execute(scenario["create_sql"])

        after_median, after_runs = run_query_timed(conn, scenario["query"], scenario["params"])
        after_explain = capture_explain(conn, scenario["query"], scenario["params"])
        print(f"AFTER index  -> median {after_median:.2f} ms")

        improvement_pct = (
            ((before_median - after_median) / before_median) * 100
            if before_median > 0 else 0
        )
        print(f"Improvement: {improvement_pct:.1f}%")

        # Save EXPLAIN output to files for your write-up / resume evidence
        (REPORTS_DIR / f"{name}_before_explain.txt").write_text(before_explain)
        (REPORTS_DIR / f"{name}_after_explain.txt").write_text(after_explain)

        results.append({
            "name": name,
            "description": scenario["description"],
            "before_ms": round(before_median, 2),
            "after_ms": round(after_median, 2),
            "improvement_pct": round(improvement_pct, 1),
            "before_runs_ms": [round(t, 2) for t in before_runs],
            "after_runs_ms": [round(t, 2) for t in after_runs],
        })

    conn.close()

    # Save raw results as JSON for the chart/report generator to consume
    results_path = REPORTS_DIR / "benchmark_results.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved results to {results_path}")
    print("Now run: python scripts/generate_report.py")


if __name__ == "__main__":
    main()
