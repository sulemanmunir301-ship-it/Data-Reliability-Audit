# Data Reliability Case Study (dbt + DuckDB)

A reproducible case study of **silent data failures**: pipelines that "succeed" while the numbers
are wrong. It injects realistic failures into an e-commerce dataset, runs open-source checks, and
reports **which failures were caught and which were missed**.

> Status: built and run end-to-end on **synthetic Olist-shaped data** and on the **real Olist dataset** (4 of its 9 tables). Results for both are below. Demand for a paid audit service based on this is **not validated**.

## Purpose
Show, with evidence, how common data checks (row counts, freshness, key tests) behave on real data, where they raise false alarms, and where they stay silent while the numbers are wrong. It is a portfolio case study in data-quality thinking, not a monitoring product.

## Best use cases
- **Portfolio / interview material:** every finding below is reproducible and the weaknesses are written down.
- **Template for a small "data health check":** the dbt checks, the failure-injection script and the detection matrix can be adapted to a small team's Postgres/BigQuery/Sheets reporting (demand untested).
- **Teaching example:** shows why "newest record date" freshness, same-weekday baselines and day-level volume checks each fail in specific ways.
- **Not for:** production monitoring, or replacing dedicated observability tools.

## How this was built
Built by Suleman Munir **with AI assistance (Claude, Anthropic)**. The AI wrote the initial code, tests and analysis drafts. The author chose the topic direction, downloaded the Olist data, ran every step on their own machine, supplied the real-data outputs the findings come from, decided to test on real data first, and published the repository. Real-data numbers in this README come from the author's runs; interpretations marked "likely" or "unverified" are hypotheses.

## Why this problem (evidence, with caveats)
| Claim | Source | Caveat |
|---|---|---|
| ~53% of data-engineering capacity goes to pipeline maintenance; ~4.7 failures/month, ~13 h each | [Fivetran 2026 benchmark](https://www.fivetran.com/blog/the-enterprise-data-infrastructure-benchmark-report-2026) | Vendor survey, 500 leaders at 5,000+ employee firms; leader estimates, not measured time |
| 72% prioritise AI-assisted coding vs 24% AI-assisted testing/observability; 71% worry wrong outputs reach stakeholders; 41% cite unclear ownership | [dbt Labs State of Analytics Engineering 2026](https://www.getdbt.com/resources/state-of-analytics-engineering-2026) | Vendor survey, n=363 |
| ~89-90% report a data-modeling pain point; top causes: speed pressure (59%), unclear ownership (51%) | [Practical Data Community survey](https://joereis.github.io/practical_data_data_eng_survey) | n=1,101, sponsored by a modeling-tool vendor |

None of these samples are small businesses. **Small-business willingness to pay is unvalidated.**

## Quickstart
Windows (Anaconda Prompt):
```
conda create -n reliability python=3.12 -y
conda activate reliability
pip install -r requirements.txt                       # dbt-core 1.x pinned on purpose
python scripts/make_synthetic_olist.py data/synthetic # or put real Olist CSVs in data/olist
python scripts/load_raw.py data/synthetic data/clean.duckdb
set OLIST_DB=data/clean.duckdb
dbt run --profiles-dir .
dbt test --profiles-dir .
python scripts/run_matrix.py data/clean.duckdb        # injects failures, writes results/detection_matrix_clean.md
```
Mac/Linux: replace `set NAME=value` with `export NAME=value`.

Alerts: `python scripts/run_checks.py --slack` (needs `SLACK_WEBHOOK_URL`) or `--email` (needs `SMTP_*`). **Slack and email sending are untested**; the report and exit-code logic is tested.

## What is checked
28 dbt tests: generic tests (unique, not_null, accepted_values, relationships) and these singular tests in `tests/`:
- `t_volume_drop_severe` (error, below 50% of the same-weekday 4-week baseline) and `t_volume_drop_moderate` (warn, 50-70%), using a full date spine so empty days count
- `t_data_freshness_orders` (newest order date) and `t_data_freshness_last_healthy_day` (last day with at least 50% of a slow 180-day median baseline)
- `t_early_hours_gap` (zero orders before 09:00 when ~5+ are normal)
- `t_delivered_orders_without_items`, `t_duplicate_payment_rows`, `t_orders_without_payments` (warn), `t_payment_vs_item_total` (warn), `t_raw_schema_drift`, `t_model_ownership` (`meta.owner`)
Plus loader-level `dbt source freshness`.

## Results on synthetic data (see `results/detection_matrix_clean.md`)
Clean baseline: 26 pass, 2 warn (seeded payment mismatch; canceled orders without payments).
Eight failures injected one at a time (A-H). All eight were detected, but read how:
- A (40% item loss) is caught by a hard-fail check only because of `t_delivered_orders_without_items`; the volume rule sees it only at WARN tier.
- F (silent price x100) is caught only by a WARN-level reconciliation. No hard-fail check exists for value corruption with unchanged counts and keys.
- H (feed stalls but ~1% stragglers keep arriving) is NOT caught by the newest-order-date freshness check. Only the 180-day-baseline check catches it.
- A same-weekday baseline adapts to an outage: after ~4 weeks the broken state looks normal. The freshness check therefore uses a slow 180-day median.
Synthetic scenarios were written after the checks, so "all detected" is a plumbing test, not evidence of quality.

## Findings on the real Olist data (4 tables only; as_of_date 2018-08-31)
Full matrix: `results/detection_matrix_olist.md`. Profile: `results/profile.md`.
Redesigned checks on real data: 22 pass, 3 warn, 3 error (24 severe + 34 moderate volume flags = 58 days; 249 payment mismatches; 1 order without payment; 6 early-hours-gap days; last healthy day 2018-08-23).

How to read the real-data matrix (this is the honest part):
- **Clean detections (5 of 8):** A, B, C, D, E are caught by checks that pass on the real baseline.
- **Warn-only (1):** F (silent price x100) is caught only by the payment-mismatch warning (249 -> 2,143 rows). No hard-fail check exists.
- **Visible only as a jump in an already-red count (2):** H (severe volume 24 -> 43, early-hours 6 -> 19) is visible if someone tracks the counts; G (partial-day gap) moves two counts by +1 each and is effectively buried.
- The real baseline is already red on three error-level checks. Monitoring that is always red hides new problems; the standard fix (not built here) is an acknowledged-events list so only unexplained days stay red.

Real-data observations:
- Late Aug 2018: daily items fall 216 -> 0 over Aug 22-30; September has 16 orders, October 4. Newest-order-date freshness passes anyway because of those stragglers.
- Nov 20, 2017 and Aug 2, 2018: no orders before 10:00 and 12:00 respectively, then a burst (Aug 2: 104 orders in the 12:00 hour vs 16-28 in neighbouring hours; Nov 20: 52 in the 11:00 hour vs 13 and 29 around it). Daily totals look normal or high, so the day-level volume check misses them. Consistent with a delayed-ingestion backlog; cause not confirmed.
- Jun 21, 2017: 35 orders vs 72-156 on other June days, none before 09:00, no catch-up burst (a low day, a different pattern). Jun 27, 2017: normal total, none before 09:00.
- 58 volume-flag days: Dec 2017-Jan 1 (21, post-Black-Friday baseline plus holidays), May 21-31 2018 (11, coincides with the national truckers' strike), Easter/Carnival/Independence-Day days, July 6-12 2018 (6, unexplained), Aug 22-31 2018 (10, end-of-data ramp-down), 4 unexplained 2017 days.
- 1 delivered order (Sept 2016) has no payment row; 3 payments typed `not_defined`; 249 payment-vs-item mismatches, 232 of them overpayments (median +6.98 BRL), consistent with installment interest (not verified); November 2016 has no orders.
- 96,096 unique customers across 99,441 customer_ids.
- Not examined: reviews, products, sellers, geolocation tables. Demand for a paid audit is NOT validated.

## Limitations (read these)
- Failures are **synthetic**; this shows what the checks can catch, not how often failures occur in practice.
- The synthetic data is generated to look like Olist. For the real data, column names and types were verified for four tables only (orders, customers, order_items, order_payments).
- Real Olist data effectively ends in late Aug 2018; set `AS_OF_DATE` accordingly (see below). The volume rule is noisy on real data (holidays, a national strike, post-Black-Friday baselines) and was NOT tuned to hide that.
- Olist is reportedly CC BY-NC-SA 4.0 (non-commercial). Verify on Kaggle; do not redistribute the data. This repo's `.gitignore` excludes `data/`.
- `dbt run` + `dbt test` is used instead of `dbt build` because build skips downstream nodes after an upstream test failure (good for gating, worse for detection).

## Running on the real Olist data
1. Download from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce (free account) and extract the CSVs into `data/olist/`.
2. `python scripts/load_raw.py data/olist data/olist.duckdb`
3. `python scripts/profile_raw.py data/olist.duckdb` and READ `results/profile.md` (types, nulls, date range, duplicates).
4. Set the reference date for this session: `set AS_OF_DATE=2018-08-31` (Windows cmd) or `export AS_OF_DATE=2018-08-31`. Choose it from the profile; real Olist volume collapses after late Aug 2018. Default (synthetic data) is 2018-06-30.
5. `set OLIST_DB=data/olist.duckdb` (Windows cmd) then `dbt run --profiles-dir .` and `dbt test --profiles-dir .`
6. Record every failure/warn on the REAL data as a finding, and tune the volume rule only after looking at the flagged days.
