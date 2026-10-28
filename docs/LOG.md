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
