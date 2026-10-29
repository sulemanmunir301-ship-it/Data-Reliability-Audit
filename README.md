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

## Results (synthetic data) — see `results/detection_matrix.md`
Clean baseline: 21 pass, 1 warn (seeded ~1% payment mismatch). All six injected failures were detected,
**but F (silent price x100) was caught only by a WARN-level cross-source reconciliation**, which does not
trigger an alert in `run_checks.py` (exit code 0). That is the real finding: value-level corruption with
unchanged counts and keys has no hard-fail check here, and it is only visible because payments exist as an
independent source to reconcile against. Next check to add: per-day average price vs baseline.
Also: the first volume rule in the original plan (flag <60% of average) would have missed a 40% drop,
because 40% loss leaves exactly 60%. The rule here is <70% of the same-weekday 4-week average.

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
