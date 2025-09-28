# producer.py
from confluent_kafka import Producer
import requests
import json
import time

API_URL = "https://opendata.afd.fr/api/explore/v2.1/catalog/datasets/resultats-de-developpement-2012-2020/records?limit=20"

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

p = Producer({'bootstrap.servers': 'localhost:9092'})

def fetch_and_send():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        records = data.get('results', [])
        for record in records:
            p.produce('afd_data_topic', json.dumps(record).encode('utf-8'), callback=delivery_report)
        p.flush()  
        print("✅ All records sent to Kafka.")
    else:
        print("❌ Failed to fetch data from API.")

if __name__ == "__main__":
    fetch_and_send()
