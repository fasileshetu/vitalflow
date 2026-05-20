import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, substring

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET = "raw"
TABLE = "brfss_2023"
BQ_TABLE = f"{PROJECT_ID}.{DATASET}.{TABLE}"

spark = SparkSession.builder \
    .appName("VitalFlow - BRFSS Ingestion") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("Reading BRFSS 2023 fixed-width data...")

# Read as raw text lines
raw_df = spark.read.text("data/raw/LLCP2023.ASC")

# Extract columns by character position (1-indexed from official CDC BRFSS variable layout)
# Source: https://www.cdc.gov/brfss/annual_data/2023/files/2023-BRFSS-Variable-Layout.pdf
brfss_df = raw_df.select(
    substring(col("value"), 1, 2).alias("state_code"),
    substring(col("value"), 23, 4).alias("interview_year"),
    substring(col("value"), 88, 1).alias("sex"),
    substring(col("value"), 101, 1).alias("general_health"),
    substring(col("value"), 102, 2).alias("physical_health_days"),
    substring(col("value"), 104, 2).alias("mental_health_days"),
    substring(col("value"), 113, 1).alias("exercise"),
    substring(col("value"), 138, 1).alias("heart_disease"),
    substring(col("value"), 141, 1).alias("asthma"),
    substring(col("value"), 149, 1).alias("diabetes"),
    substring(col("value"), 187, 1).alias("education"),
    substring(col("value"), 204, 2).alias("income"),
    substring(col("value"), 225, 1).alias("smoking_status"),
    substring(col("value"), 2060, 1).alias("race"),
    substring(col("value"), 2065, 2).alias("age_group"),
    substring(col("value"), 2082, 4).alias("bmi"),
    substring(col("value"), 2086, 1).alias("bmi_category"),
)

# Light cleaning
brfss_clean = brfss_df \
    .withColumn("state_code", trim(col("state_code"))) \
    .withColumn("interview_year", trim(col("interview_year")))

print(f"Raw record count: {brfss_clean.count()}")
print(f"Writing to BigQuery: {BQ_TABLE}")

brfss_clean.write \
    .format("bigquery") \
    .option("table", BQ_TABLE) \
    .option("credentialsFile", "./gcp-key.json") \
    .option("writeMethod", "direct") \
    .mode("overwrite") \
    .save()

print("BRFSS data successfully loaded to BigQuery.")
spark.stop()