# spark_processor_hdfs.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import re

spark = SparkSession.builder.appName("AFD HDFS Writer").config("spark.sql.adaptive.enabled", "true").config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9001").getOrCreate()

# Schema definition 

schema = StructType([
    StructField("categories", StringType(), True),
    StructField("id_sirp", StringType(), True),
    StructField("unite_type", StringType(), True),
    StructField("libelle", StringType(), True),
    StructField("valeur_2012", StringType(), True),
    StructField("valeur_2013", StringType(), True),
    StructField("valeur_2014", StringType(), True),
    StructField("valeur_2015", StringType(), True),
    StructField("valeur_2016", StringType(), True),
    StructField("valeur_2017", StringType(), True),
    StructField("2018", StringType(), True),
    StructField("2019", StringType(), True),
    StructField("2020", StringType(), True),
    StructField("2021", StringType(), True),
    StructField("2022", StringType(), True),
])

# Reading data from Kafka

df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "afd_data_topic").option("startingOffsets", "earliest").load()

# Transforming data from JSON

parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")


# Selecting columns of the year 

year_columns = [col_name for col_name in parsed_df.columns if re.search(r'20\d{2}', col_name)]

#Unpivot 

unpivoted_df = parsed_df.select(
    "categories", "id_sirp", "unite_type", "libelle",
    explode(array([
        struct(lit(col_name.replace("valeur_", "")).alias("year"), col(col_name).alias("value"))
        for col_name in year_columns
    ])).alias("tmp")
).select(
    "categories", "id_sirp", "unite_type", "libelle",
    col("tmp.year"), col("tmp.value")
)

# Data cleaning

cleaned_df = unpivoted_df.filter(
    (col("value").isNotNull()) & (col("value") != "") & (col("value") != "null")
)


# Converting into double 

final_df = cleaned_df.withColumn(
    "value",
    when(col("value").cast("double").isNotNull(), col("value").cast("double"))
    .otherwise(lit(None).cast("double"))
).filter(col("value").isNotNull())

# Adding timestamp 

output_df = final_df.withColumn("processed_at", current_timestamp())

# Writing into parquet file into 

query = output_df.writeStream.format("parquet").option("path", "hdfs://localhost:9001/user/afd/processed_data").option("checkpointLocation", "/tmp/spark-checkpoint-hdfs").outputMode("append").start()

query.awaitTermination()
