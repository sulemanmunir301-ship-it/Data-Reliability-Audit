-- Day-level counts miss intra-day gaps. Flags days with ZERO orders before 09:00 when the prior
-- 28 days averaged >= 5 such orders. Real Olist: Jun 21 and Jun 27, 2017 (Jun 27 had a normal day total).
select d, n, early_orders, round(early_baseline, 1) as early_baseline from {{ ref('daily_volume') }}
where early_baseline >= 5 and early_orders = 0
