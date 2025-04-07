import os
import json
import time
import glob
import pika
import pandas as pd
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CSV_DIR = os.getenv("CSV_DIR", "agents/sample_data")
EXCHANGE_NAME = "iot_exchange"
ROUTING_KEY = "sensor.lifebeing"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

def get_device_id_from_filename(filename: str) -> int:
    """Extract device ID from filename like iaq_data_D1.csv"""
    base = os.path.basename(filename).replace(".csv", "")
    return int(base.split("_D")[-1])

def read_csv(filepath):
    df = pd.read_csv(filepath, parse_dates=["datetime"])
    df = df.sort_values("datetime")
    return df.to_dict(orient="records")

def run_lifebeing_publisher(filepath):
    device_id = get_device_id_from_filename(filepath)
    rows = read_csv(filepath)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

    print(f"[Lifebeing Thread - D{device_id}] Starting")

    i = 0
    while True:
        row = rows[i % len(rows)]
        payload = {
            "device_id": device_id,
            "datetime": datetime.utcnow().isoformat(),  # Use current UTC time
            "presence_state": row["presence_state"],
            "sensitivity": row["sensitivity"]
        }

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=json.dumps(payload)
        )

        print(f"[LifeBeing Thread - D{device_id}] Published → {payload}")
        time.sleep(5)
        i += 1

def start_lifebeing_agents():
    csv_files = glob.glob(os.path.join(CSV_DIR, "presence_sensor_data_D*.csv"))

    for filepath in csv_files:
        thread = Thread(target=run_lifebeing_publisher, args=(filepath,), daemon=True)
        thread.start()
