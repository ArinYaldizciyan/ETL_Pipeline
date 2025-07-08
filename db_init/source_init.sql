CREATE TABLE IF NOT EXISTS public.source_table (
    country_name TEXT PRIMARY KEY,
    population BIGINT,
    nominal_gdp_usd BIGINT,
    nominal_gdp_per_capita_usd DOUBLE PRECISION,
    gdp_per_capita_ppp_usd DOUBLE PRECISION,
    hdi DOUBLE PRECISION,
    gini DOUBLE PRECISION,
    area_sq_km DOUBLE PRECISION
);
