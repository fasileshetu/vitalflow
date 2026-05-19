import os
import re
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

# Extract columns by character position (1-indexed from BRFSS codebook)
# Format: substring(col, start_position, length)
brfss_df = raw_df.select(
    substring(col("value"), 1, 2).alias("state_code"),
    substring(col("value"), 18, 4).alias("interview_year"),
    substring(col("value"), 30, 1).alias("sex"),
    substring(col("value"), 31, 2).alias("age_group"),
    substring(col("value"), 33, 1).alias("race"),
    substring(col("value"), 38, 2).alias("education"),
    substring(col("value"), 40, 2).alias("income"),
    substring(col("value"), 50, 1).alias("general_health"),
    substring(col("value"), 51, 1).alias("physical_health_days"),
    substring(col("value"), 52, 1).alias("mental_health_days"),
    substring(col("value"), 55, 1).alias("exercise"),
    substring(col("value"), 56, 1).alias("smoking_status"),
    substring(col("value"), 60, 1).alias("bmi_category"),
    substring(col("value"), 65, 1).alias("diabetes"),
    substring(col("value"), 66, 1).alias("heart_disease"),
    substring(col("value"), 67, 1).alias("asthma"),
)

# Light cleaning
brfss_clean = brfss_df \
    .withColumn("state_code", trim(col("state_code"))) \
    .withColumn("interview_year", trim(col("interview_year"))) \

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