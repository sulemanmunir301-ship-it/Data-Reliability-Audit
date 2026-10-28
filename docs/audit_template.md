# Data Reliability Audit — template (one page)

**Client / stack:** ______ (Postgres / BigQuery / Sheets)   **Access needed:** read-only
**Fixed price / timeline:** ______ / ______ days   **Status:** UNTESTED OFFER — no client has bought this yet

## What I check
1. Row-count / volume per key table per day vs same-weekday baseline (incl. missing days)
2. Freshness: newest record vs expected; loader timestamp vs expected
3. Keys: duplicates, nulls, orphans in both directions (child->parent AND parent without children)
4. Reconciliation of 2+ sources for the metrics that drive decisions (e.g. revenue vs payments)
5. Schema drift on raw inputs (type/column changes)
6. Ownership: who is named for each table/dashboard

## What you receive
- Findings list: each issue, rows affected, business impact guess (marked as a guess)
- Checks implemented (dbt tests or SQL) + how to run them
- Alert route (email/Slack) for failures
- One-page ownership map: table/dashboard -> named owner -> who to tell when it breaks

## What I do NOT do
Guarantee upstream correctness, fix business definitions I wasn't given, or monitor continuously.
