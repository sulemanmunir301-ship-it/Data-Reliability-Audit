# Data Reliability Case Study (dbt + DuckDB)

A reproducible case study of **silent data failures**: pipelines that "succeed" while the numbers
are wrong. It injects realistic failures into an e-commerce dataset, runs open-source checks, and
reports **which failures were caught and which were missed**.

> Status: tested end-to-end on **synthetic Olist-shaped data** (see Limitations). Not yet run on
> the real Kaggle dataset.

## Why this problem (evidence, with caveats)
| Claim | Source | Caveat |
|---|---|---|
| ~53% of data-engineering capacity goes to pipeline maintenance; ~4.7 failures/month, ~13 h each | [Fivetran 2026 benchmark](https://www.fivetran.com/blog/the-enterprise-data-infrastructure-benchmark-report-2026) | Vendor survey, 500 leaders at 5,000+ employee firms; leader estimates, not measured time |
| 72% prioritise AI-assisted coding vs 24% AI-assisted testing/observability; 71% worry wrong outputs reach stakeholders; 41% cite unclear ownership | [dbt Labs State of Analytics Engineering 2026](https://www.getdbt.com/resources/state-of-analytics-engineering-2026) | Vendor survey, n=363 |
| ~89-90% report a data-modeling pain point; top causes: speed pressure (59%), unclear ownership (51%) | [Practical Data Community survey](https://joereis.github.io/practical_data_data_eng_survey) | n=1,101, sponsored by a modeling-tool vendor |

None of these samples are small businesses. **Small-business willingness to pay is unvalidated.**

## Quickstart
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt                       # dbt-core 1.x pinned on purpose
python scripts/make_synthetic_olist.py data/synthetic # or put real Olist CSVs in data/olist
python scripts/load_raw.py data/synthetic data/clean.duckdb
OLIST_DB=data/clean.duckdb dbt run  --profiles-dir . && OLIST_DB=data/clean.duckdb dbt test --profiles-dir .
python scripts/run_matrix.py data/clean.duckdb        # injects failures, writes results/detection_matrix.md
```
Alerts: `python scripts/run_checks.py --slack` (needs `SLACK_WEBHOOK_URL`) or `--email` (needs `SMTP_*`).
**Slack and email sending are untested** (no network in the build sandbox); the report/exit-code logic is tested.

## What is checked
Generic tests (unique, not_null, accepted_values, relationships) plus singular tests in `tests/`:
volume drop vs same-weekday baseline (with date spine), delivered orders without items, duplicate
payments, payment-vs-item reconciliation (warn), data freshness, raw schema drift, model ownership
(`meta.owner`), and loader-level source freshness.

## Results on synthetic data (see `results/detection_matrix.md`)
Clean baseline: 26 pass, 2 warn (seeded payment mismatch; canceled orders without payments).
Eight failures injected one at a time (A-H). All eight were detected, but read how:
- A (40% item loss) is caught by a hard-fail check only because of `t_delivered_orders_without_items`; the volume rule sees it only at WARN tier.
- F (silent price x100) is caught only by a WARN-level reconciliation. No hard-fail check exists for value corruption with unchanged counts and keys.
- H (feed stalls but ~1% stragglers keep arriving) is NOT caught by the newest-order-date freshness check. Only the 180-day-baseline check catches it.
- A same-weekday baseline adapts to an outage: after ~4 weeks the broken state looks normal. The freshness check therefore uses a slow 180-day median.
Synthetic scenarios were written after the checks, so "all detected" is a plumbing test, not evidence of quality.

## Findings on the real Olist data (baseline run, 4 tables only; new checks not yet run on real data)
- 20 of 22 original checks pass; types, keys and orphans are clean in orders, customers, items, payments.
- Volume rule at 70%: 58 flagged days through 2018-08-31 (about 8% of days). Groups: Dec 2017-Jan 1 (21, post-Black-Friday baseline plus holidays), May 21-31 2018 (11, coincides with the national truckers' strike), Easter/Carnival/Independence-Day days, July 6-12 2018 (6, unexplained), Aug 22-31 2018 (10, ramp-down to zero), and 4 unexplained 2017 days.
- Late Aug 2018: daily items fall 216 -> 0 over Aug 22-30; September has 16 orders and October 4. Newest-order-date freshness passes anyway because of those stragglers.
- Jun 21 and Jun 27, 2017: zero orders before 09:00 (Jun 21 total: 35 orders vs 72-156 on other June days). Candidate partial-day gaps; cause unknown.
- November 2016 has no orders; December 2016 has 1.
- 249 payment-vs-item mismatches: 232 are overpayments (median +6.98 BRL, range -51.62 to +182.81), consistent with installment interest (not verified).
- 1 order without a payment row; 3 payments typed `not_defined`; 96,096 unique customers across 99,441 customer_ids.
- Not examined: reviews, products, sellers, geolocation tables.

## Limitations (read these)
- Failures are **synthetic**; this shows what the checks can catch, not how often failures occur in practice.
- Data is generated to look like Olist; table/column names follow Kaggle's schema from secondary sources, not verified against the real files.
- Real Olist data ends in 2018; set `as_of_date` in `dbt_project.yml` accordingly and expect to **tune the volume rule** (sparse 2016, Black Friday 2017).
- Olist is reportedly CC BY-NC-SA 4.0 (non-commercial). Verify on Kaggle; do not redistribute the data. This repo's `.gitignore` excludes `data/`.
- `dbt run` + `dbt test` is used instead of `dbt build` because build skips downstream nodes after an upstream test failure (good for gating, worse for detection).

## Running on the real Olist data
1. Download from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce (free account) and extract the CSVs into `data/olist/`.
2. `python scripts/load_raw.py data/olist data/olist.duckdb`
3. `python scripts/profile_raw.py data/olist.duckdb` and READ `results/profile.md` (types, nulls, date range, duplicates).
4. Set `as_of_date` in `dbt_project.yml` near the newest order date from the profile.
5. `set OLIST_DB=data/olist.duckdb` (Windows cmd) then `dbt run --profiles-dir .` and `dbt test --profiles-dir .`
6. Record every failure/warn on the REAL data as a finding, and tune the volume rule only after looking at the flagged days.
