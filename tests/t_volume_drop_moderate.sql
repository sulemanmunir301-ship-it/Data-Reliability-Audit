{{ config(severity='warn') }}
-- WARN tier: 50-70% of baseline. Holidays, strikes and post-spike months land here, but so does a
-- partial loss (a 40% loss leaves 60%). A human has to look; this tier is for review, not paging.
select d, n, baseline, round(ratio, 2) as ratio from {{ ref('daily_volume') }}
where baseline > 20 and ratio >= 0.5 and ratio < 0.7
