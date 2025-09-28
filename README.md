# AgenceFran-aisedeD-veloppement-DataPipeline
# AFD Data Pipeline

A streaming data pipeline that fetches development results from the AFD API, processes them using Apache Spark, and stores them as Parquet in HDFS.

## Overview
This project demonstrates a simple ETL pipeline:
- Fetch data from a public API using Python and send it to Kafka.
- Process the data in real-time using PySpark (unpivot, clean, and add timestamp).
- Store the processed data in HDFS as Parquet files.

**Note:** All components (Apache Spark, Kafka, and HDFS) are running locally on Ubuntu in this setup. This is ideal for development and testing. For production, consider deploying on a cluster (e.g., via Docker, Kubernetes, or cloud services like AWS EMR).

## Prerequisites
- Ubuntu OS (tested on Ubuntu 20.04 or later).
- Python 3.10.
- Apache Spark 3.4.4 (installed locally).
- Apache Kafka (Confluent client recommended, running locally on port 9092).
- Hadoop (with HDFS enabled, running locally on port 9001).
- Basic libraries: requests, confluent_kafka, pyspark.

Install Spark, Kafka, and Hadoop locally on Ubuntu using official guides:
- Spark: Download from https://spark.apache.org/downloads.html and set SPARK_HOME.
- Kafka: Follow https://kafka.apache.org/quickstart.
- Hadoop: Install single-node setup from https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html.

## Environment Variables
Set these in your terminal or .env file:
- `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`
- `HDFS_PATH=hdfs://localhost:9001/user/afd/processed_data`
- `CHECKPOINT_PATH=/tmp/spark-checkpoint-hdfs`

## Setup
1. Start Zookeeper and Kafka locally:
   bin/zookeeper-server-start.sh config/zookeeper.properties
   bin/kafka-server-start.sh config/server.properties
   Create the topic: `bin/kafka-topics.sh --create --topic afd_data_topic --bootstrap-server localhost:9092`.

2. Start Hadoop (HDFS):
   start-dfs.sh
   Create directories: `hdfs dfs -mkdir /user/afd/processed_data`.

3. Run the producer to fetch and send data to Kafka:
   python3 API_kafka.py

4. Submit the Spark job for processing:
   spark-submit --master local[*] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.4 spark_processor.py

## Output
Processed data is stored in `hdfs://localhost:9001/user/afd/processed_data`. View it with:
   hdfs dfs -ls /user/afd/processed_data

## Troubleshooting
- Ensure all services are running locally on Ubuntu.
- If ports conflict, update the configs in Kafka/Hadoop.
- For non-Ubuntu setups, adjust paths and installations accordingly.

## License
MIT License.
