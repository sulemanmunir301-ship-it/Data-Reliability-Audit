-- ERROR tier: day has < 50% of the same-weekday baseline (4 prior weeks). Baseline must exceed 20 items.
-- On real Olist data, ~15 of 42 flagged days at the old 70% rule fell below 50%.
select d, n, baseline, round(ratio, 2) as ratio from {{ ref('daily_volume') }}
where baseline > 20 and ratio < 0.5
