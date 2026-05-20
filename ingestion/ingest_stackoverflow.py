import os
import re
from dotenv import load_dotenv
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import col, trim, when

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET = "raw"
TABLE = "stackoverflow_survey"
BQ_TABLE = f"{PROJECT_ID}.{DATASET}.{TABLE}"

spark = SparkSession.builder \
    .appName("VitalFlow - StackOverflow Ingestion") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("Reading Stack Overflow survey data...")

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("multiLine", "true") \
    .option("escape", '"') \
    .csv("data/raw/survey_results_public.csv")

print(f"Raw record count: {df.count()}")
print(f"Columns: {len(df.columns)}")

# Light cleaning
df_clean = df \
    .withColumn("Employment", trim(col("Employment"))) \
    .withColumn("Country", trim(col("Country"))) \
    .withColumn("EdLevel", trim(col("EdLevel"))) \
    .withColumn("DevType", trim(col("DevType"))) \
    .withColumn("YearsCodePro", when(col("YearsCodePro") == "Less than 1 year", "0")
                                .when(col("YearsCodePro") == "More than 50 years", "51")
                                .otherwise(col("YearsCodePro"))) \
    .dropDuplicates()

print(f"Clean record count: {df_clean.count()}")

# Sanitize column names - replace spaces and special characters with underscores
def clean_column_name(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

df_clean = df_clean.toDF(*[clean_column_name(c) for c in df_clean.columns])

print(f"Writing to BigQuery: {BQ_TABLE}")

df_clean.write \
    .format("bigquery") \
    .option("table", BQ_TABLE) \
    .option("credentialsFile", "./gcp-key.json") \
    .option("writeMethod", "direct") \
    .mode("overwrite") \
    .save()

print("Stack Overflow data successfully loaded to BigQuery.")
spark.stop()