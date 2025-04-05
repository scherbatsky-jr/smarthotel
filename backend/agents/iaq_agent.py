import os
import json
import time
import glob
import pika
import pandas as pd
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

CSV_DIR = os.getenv("CSV_DIR", "agents/sample_data")
EXCHANGE_NAME = "iot_exchange"
ROUTING_KEY = "sensor.iaq"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

def parse_room_info_from_filename(filename: str):
    """
    Extract hotel_id, floor_id, and room_id from a filename like:
    iaq_data_H1_F2_R12.csv
    Returns (hotel_id, floor_id, room_id) as strings
    """
    base = os.path.basename(filename).replace(".csv", "")
    parts = base.split("_")
    h_id = [p for p in parts if p.startswith("H")][0][1:]
    f_id = [p for p in parts if p.startswith("F")][0][1:]
    r_id = [p for p in parts if p.startswith("R")][0][1:]
    return h_id, f_id, r_id

def read_csv(filepath):
    df = pd.read_csv(filepath, parse_dates=["datetime"])
    return df.to_dict(orient="records")

def run_iaq_publisher(filepath):
    hotel_id, floor_id, room_id = parse_room_info_from_filename(filepath)
    device_id = f"iaq_sensor_H{hotel_id}_F{floor_id}_R{room_id}"
    rows = read_csv(filepath)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

    print(f"[IAQ Thread - H{hotel_id}F{floor_id}R{room_id}] Starting")

    i = 0
    while True:
        row = rows[i % len(rows)]
        payload = {
            "device_id": device_id,
            "datetime": row["datetime"].isoformat(),
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "co2": row["co2"]
        }

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=json.dumps(payload)
        )

        print(f"[IAQ Thread - H{hotel_id}F{floor_id}R{room_id}] Published → {payload}")
        time.sleep(5)
        i += 1

def start_iaq_agents():
    csv_files = glob.glob(os.path.join(CSV_DIR, "iaq_data_H*_F*_R*.csv"))

    for filepath in csv_files:
        thread = Thread(target=run_iaq_publisher, args=(filepath,), daemon=True)
        thread.start()