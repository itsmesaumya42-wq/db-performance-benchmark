# Database Performance Benchmark Report

Comparison of query latency before and after adding targeted indexes,
measured against a synthetic payments transactions dataset.

| Query | Before (ms) | After (ms) | Improvement |
|---|---:|---:|---:|
| velocity_check_by_card | 95.66 | 0.61 | 99.4% |
| category_spend_range | 105.75 | 13.53 | 87.2% |
| declined_by_country | 129.5 | 1.07 | 99.2% |
| merchant_join_report | 122.78 | 133.75 | -8.9% |

## Query details

### velocity_check_by_card
Count a card's transactions in the last 5 minutes (fraud velocity check)
- Before: 95.66 ms (runs: [205.53, 92.35, 87.92, 95.66, 96.45])
- After: 0.61 ms (runs: [4.69, 0.7, 0.42, 0.48, 0.61])
- See `reports/velocity_check_by_card_before_explain.txt` and `reports/velocity_check_by_card_after_explain.txt` for the full EXPLAIN ANALYZE output.

### category_spend_range
Sum spend for a merchant category over a date range
- Before: 105.75 ms (runs: [107.67, 109.64, 105.31, 105.75, 104.22])
- After: 13.53 ms (runs: [16.26, 13.53, 12.95, 14.78, 13.09])
- See `reports/category_spend_range_before_explain.txt` and `reports/category_spend_range_after_explain.txt` for the full EXPLAIN ANALYZE output.

### declined_by_country
Find declined transactions for a specific country (partial index)
- Before: 129.5 ms (runs: [113.05, 129.5, 124.43, 137.9, 197.68])
- After: 1.07 ms (runs: [4.98, 1.18, 0.92, 1.07, 0.98])
- See `reports/declined_by_country_before_explain.txt` and `reports/declined_by_country_after_explain.txt` for the full EXPLAIN ANALYZE output.

### merchant_join_report
Join merchants + transactions for a category report
- Before: 122.78 ms (runs: [148.39, 115.98, 102.21, 122.78, 161.49])
- After: 133.75 ms (runs: [110.26, 127.1, 148.38, 147.99, 133.75])
- See `reports/merchant_join_report_before_explain.txt` and `reports/merchant_join_report_after_explain.txt` for the full EXPLAIN ANALYZE output.

![Benchmark Chart](benchmark_chart.png)