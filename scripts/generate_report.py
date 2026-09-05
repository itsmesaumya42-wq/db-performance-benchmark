"""
generate_report.py

Reads reports/benchmark_results.json (produced by benchmark.py) and
generates:
  1. A bar chart (before vs after latency) saved as reports/benchmark_chart.png
  2. A markdown summary report saved as reports/BENCHMARK_REPORT.md

This is the artifact you actually put in your resume/portfolio —
a clean visual + write-up of measurable query optimization.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
RESULTS_FILE = REPORTS_DIR / "benchmark_results.json"


def make_chart(results):
    names = [r["name"] for r in results]
    before = [r["before_ms"] for r in results]
    after = [r["after_ms"] for r in results]

    x = range(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - width / 2 for i in x], before, width, label="Before index", color="#d9534f")
    ax.bar([i + width / 2 for i in x], after, width, label="After index", color="#5cb85c")

    ax.set_ylabel("Median query latency (ms)")
    ax.set_title("Query Latency: Before vs After Indexing")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.legend()
    fig.tight_layout()

    chart_path = REPORTS_DIR / "benchmark_chart.png"
    fig.savefig(chart_path, dpi=150)
    print(f"Saved chart to {chart_path}")


def make_markdown_report(results):
    lines = [
        "# Database Performance Benchmark Report",
        "",
        "Comparison of query latency before and after adding targeted indexes,",
        "measured against a synthetic payments transactions dataset.",
        "",
        "| Query | Before (ms) | After (ms) | Improvement |",
        "|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['name']} | {r['before_ms']} | {r['after_ms']} | {r['improvement_pct']}% |"
        )

    lines.append("")
    lines.append("## Query details")
    for r in results:
        lines.append(f"\n### {r['name']}")
        lines.append(r["description"])
        lines.append(f"- Before: {r['before_ms']} ms (runs: {r['before_runs_ms']})")
        lines.append(f"- After: {r['after_ms']} ms (runs: {r['after_runs_ms']})")
        lines.append(
            f"- See `reports/{r['name']}_before_explain.txt` and "
            f"`reports/{r['name']}_after_explain.txt` for the full EXPLAIN ANALYZE output."
        )

    lines.append("\n![Benchmark Chart](benchmark_chart.png)")

    report_path = REPORTS_DIR / "BENCHMARK_REPORT.md"
    report_path.write_text("\n".join(lines))
    print(f"Saved report to {report_path}")


def main():
    if not RESULTS_FILE.exists():
        print("No results found — run benchmark.py first.")
        return

    results = json.loads(RESULTS_FILE.read_text())
    make_chart(results)
    make_markdown_report(results)


if __name__ == "__main__":
    main()
