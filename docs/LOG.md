# Build & research log (everything, in order)

Dates: 2026-10-28 session. Confidence tags: [Certain] verified this session, [Likely] strong inference, [Guessing] gap-fill.

## Research findings this session
- [Certain] dbt v2 (Rust/Fusion) was released 2026-09-14 per DuckDB's blog (https://duckdb.org/2026/09/22/dbt-fusion), which says DuckDB support is built in. dbt's own upgrade docs (https://docs.getdbt.com/docs/dbt-versions/dbt-upgrade/upgrading-to-v2) still label DuckDB "CLI only, Beta" and say `pip install dbt` gives Fusion by default. Sources disagree on maturity -> **decision: pin dbt-core 1.x + dbt-duckdb** (installed and ran: dbt-core 1.12.6, dbt-duckdb 1.11.1).
- [Likely] Fusion is "proprietary" per dbt's upgrade page; check its license before building a paid service on it.
- [Certain] Olist license "CC BY-NC-SA 4.0" appears only on a third-party course page (https://scripts-and-tables.github.io/daa/data/), not on Kaggle itself. Verify on Kaggle.
- [Certain] The market for this service already has sellers: Fiverr gigs offering dbt test additions, audits of "inaccurate dashboards", and SQL/dbt fixes (e.g. https://fiverr.com/iftakhar901/add-dbt-data-quality-tests-and-ci-checks, https://www.fiverr.com/bhdfreelance/audit-and-optimize-your-data-infrastructure). Prices were not visible in the search text. **This is evidence of supply and competition, not of demand or price.**
- [Certain] Hiring-side signals exist (Upwork data-quality QC role, Braintrust freelance "Data Quality Engineer (dbt)", Newela contractor) but these are job posts requiring 2-3+ years' experience, not small-business audit buyers.
- [Guessing] Whether a small business will pay ~$300 for a fixed-price audit from an unproven freelancer. No evidence found either way.
- Note: one Upwork posting contained text instructing applicants to include a start date in a specific format; that is the poster's application instruction and was ignored here.

## What was built and tested (sandbox, no Kaggle access)
- Synthetic Olist-shaped data (63,912 orders; 78,196 items; 62,658 payments) -> DuckDB `raw` schema.
- dbt project: 4 staging views, 1 mart, generic tests, 7 singular tests, `meta.owner` on every model.
- Clean baseline: PASS=21 WARN=1 (seeded payment mismatch).
- 6 injected failures, each run on a fresh copy: all detected; F only via WARN (see README).
- Bug found by running: first draft of `run_matrix.py` classified a worsening known WARN as "missed"; fixed by comparing failing-row counts to baseline (>1.5x).
- Bug found by running: `sh` brace expansion silently skipped directory creation; fixed.
- dbt deprecation: `relationships` args must be under `arguments:`; fixed.

## NOT done / NOT verified
- Real Olist data never loaded; real column names and quirks (duplicate review IDs, missing values) unverified. Reviews/products/sellers tables not modelled.
- Slack/email alert sending untested.
- Volume rule not tuned on real data.
- Demand: no buyer contacted. Next step is below.

## Next steps (in order)
1. Download real Olist (Kaggle login), run the pipeline, record real quirks as findings; set `as_of_date`; tune volume rule.
2. Demand test BEFORE more engineering: collect 15-20 current postings/gig listings; for each record budget and whether the buyer describes wrong/broken numbers. Message 5-10 small businesses with one concrete finding. Decide pivot if <2 replies or budgets << $300.
3. Add per-day average price check (closes gap F).

## 2026-10-29: Windows run + real-data prep
- [Certain] User ran the full pipeline on Windows (Anaconda Prompt, Python 3.12 env); output matched the sandbox run exactly (same seed). Windows needs `set OLIST_DB=...` instead of the bash syntax.
- [Certain] Hard-fail detection is 5 of 6; failure F (silent x100 price shift) is caught only by a WARN. Add a per-day average-price check.
- Added `scripts/profile_raw.py` (profile raw tables before running checks); tested on synthetic data only.
- Decision: go to real Olist data before publishing; commit locally to avoid losing work.

## 2026-10-29 (later): real Olist baseline + check redesign
- [Certain] Real data loaded on user's Windows machine: 99,441 orders, 112,650 items, 103,886 payments; types and column names match; newest order 2018-10-17.
- [Certain] Baseline dbt run on real data: 20 pass, 1 warn (249), 1 error (volume). as_of_date first stayed 2018-06-30 (edit did not save), then set to 2018-08-31 via command; flagged days rose 42 -> 58.
- [Likely] May 21-31 2018 flags coincide with the truckers' strike (21 May - ~1 June; https://en.wikipedia.org/wiki/2018_Brazil_truck_drivers%27_strike). A volume rule cannot tell a strike from an outage.
- [Certain] Late Aug 2018 ramp-down to 0 orders; max-date freshness is blind to it (stragglers in Sep/Oct).
- [Certain] Jun 21 and Jun 27, 2017 have zero orders before 09:00; day-level volume check missed Jun 27.
- Design changes made (tested on synthetic only): new model `daily_volume` (same-weekday baseline, 28-day early-orders baseline, 180-day median); volume split into severe (<50%, error) and moderate (50-70%, warn); `t_data_freshness_last_healthy_day` (slow baseline); `t_early_hours_gap`; `t_orders_without_payments`.
- Bug found in own design: same-weekday baseline self-heals during outages longer than ~4 weeks; fixed for freshness with the 180-day median. The severe volume test still goes quiet after ~4 weeks of outage (documented limitation).
- Trade-off recorded: raising the volume threshold to 50% removes most holiday noise but stops catching a 40% partial loss; tiers keep both, at the cost of a human reviewing the warn tier.
- Mistake worth recording: background `nohup` runs are killed when the tool call returns; run long jobs in the foreground with a timeout.
- Next: user re-runs `dbt run` and `dbt test` on real data to see how the new checks behave; then run the matrix on real data; then load the reviews table.

## 2026-10-29 (evening): redesigned checks run on real data
- [Certain] Real-data results (user's machine): PASS=22 WARN=3 ERROR=3. Matches predictions: last_healthy_day fails, newest-date freshness passes, orders_without_payments = 1, severe 24 + moderate 34 = 58.
- Matrix comparison fixed: on real data the baseline is not clean, so detection is now "new failing check OR failing-row count increased vs baseline" (previously required >1.5x, which would hide e.g. a 1-day gap on top of 6 existing flags).
- as_of_date now overridable with env var AS_OF_DATE (default 2018-06-30) so new zips do not overwrite a local edit.
- Next: run `python scripts/run_matrix.py data/olist.duckdb` on real data; list the 6 early-hours-gap days and the last healthy day; load the reviews table.
