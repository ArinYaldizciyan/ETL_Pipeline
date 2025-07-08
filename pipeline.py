from pyspark.sql import functions as F
from pyspark.sql import SparkSession
import os

os.environ["HADOOP_HOME"] = "C:/hadoop/hadoop-3.3.4"

spark = SparkSession.builder \
  .appName("ETL Pipeline") \
  .config("spark.jars", "jdbc_drivers/postgresql-42.7.7.jar") \
  .getOrCreate()

# Read from source
source_df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5433/source") \
    .option("driver", "org.postgresql.Driver") \
    .option("user", "postgres") \
    .option("password", "password") \
    .option("dbtable", "source_table") \
    .load()

cleaned_df = source_df.na.drop(subset=["nominal_gdp_per_capita_usd", "hdi"])

# Compute stats
stats = cleaned_df.select(
    F.mean("nominal_gdp_per_capita_usd").alias("gdp_mean"),
    F.stddev("nominal_gdp_per_capita_usd").alias("gdp_std"),
    F.mean("hdi").alias("hdi_mean"),
    F.stddev("hdi").alias("hdi_std")
).collect()[0]

# Print stats
print("Stats:") 
print(stats)

# Apply filters using the collected stats
filtered = cleaned_df.filter(
    (F.col("nominal_gdp_per_capita_usd") > stats["gdp_mean"] + stats["gdp_std"]) 
    & (F.col("hdi") > stats["hdi_mean"] + 1.2*stats["hdi_std"])
)

output_df = filtered.select("country_name", "nominal_gdp_per_capita_usd", "hdi")
print(output_df.show())
print(f"Number of rows: {output_df.count()}")

output_df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5434/target") \
    .option("driver", "org.postgresql.Driver") \
    .option("dbtable", "target_table") \
    .option("user", "postgres") \
    .option("password", "password") \
    .mode("overwrite") \
    .save()
