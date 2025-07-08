import pandas as pd
import psycopg2

# Load the CSV
df = pd.read_csv("data/countries_metric.csv")

# Normalize column names
df.rename(columns={
    "Population (in millions)": "population",
    "Nominal Gross Domestic Product (in USD)": "nominal_gdp_usd",
    "Nominal GDP Per capita (in USD)": "nominal_gdp_per_capita_usd",
    "GDP Per capita PPP (in USD)": "gdp_per_capita_ppp_usd",
    "Human Development Index (HDI)": "hdi",
    "GINI": "gini",
    "AREA (in Sq km)": "area_sq_km"
}, inplace=True)



numeric_fields = ["population", "nominal_gdp_usd", "nominal_gdp_per_capita_usd",
                  "gdp_per_capita_ppp_usd", "hdi", "gini", "area_sq_km"]

#Convert strings to numbers
for col in numeric_fields:
    df[col] = df[col].astype(str).str.replace(",", "").str.strip()

#Parse currency values
def parse_currency(val):
    if isinstance(val, str):
        val = val.replace("$", "").replace(",", "").strip().lower()
        if "trillion" in val:
            return float(val.replace("trillion", "").strip()) * 1_000_000_000_000
        elif "billion" in val:
            return float(val.replace("billion", "").strip()) * 1_000_000_000
        elif "million" in val:
            return float(val.replace("million", "").strip()) * 1_000_000
        else:
            return float(val)
    return val


df["population"] = df["population"].astype(str).str.replace(",", "").astype(float)
df["hdi"] = pd.to_numeric(df["hdi"], errors="coerce")
df["gini"] = pd.to_numeric(df["gini"], errors="coerce")
df["area_sq_km"] = df["area_sq_km"].astype(str).str.replace(",", "").astype(float)
df["nominal_gdp_usd"] = df["nominal_gdp_usd"].apply(parse_currency)

# Connect to the source DB
conn = psycopg2.connect(
    dbname="source",
    user="postgres",
    password="password",
    host="localhost",
    port="5433"
)

cursor = conn.cursor()

# Insert rows
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO source_table (
            country_name,
            population,
            nominal_gdp_usd,
            nominal_gdp_per_capita_usd,
            gdp_per_capita_ppp_usd,
            hdi,
            gini,
            area_sq_km
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (country_name) DO NOTHING
    """, (
        row["country_name"],
        int(row["population"]),
        int(row["nominal_gdp_usd"]),
        float(row["nominal_gdp_per_capita_usd"]),
        float(row["gdp_per_capita_ppp_usd"]),
        float(row["hdi"]),
        float(row["gini"]),
        float(row["area_sq_km"])
    ))

conn.commit()
cursor.close()
conn.close()
