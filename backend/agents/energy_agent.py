import os
import time
import json
import glob
import pika
import pandas as pd
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

CSV_DIR = os.getenv("CSV_DIR", "agents/sample_data")
EXCHANGE_NAME = "iot_exchange"
ROUTING_KEY = "sensor.energy"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

def get_room_key_from_filename(filename):
    # Matches files like "power_meter_data_R1.csv"
    return filename.split("power_meter_data_")[-1].replace(".csv", "").strip()

def read_csv(filepath):
    df = pd.read_csv(filepath, parse_dates=["datetime"])
    df = df.sort_values("datetime")
    return df.to_dict(orient="records")

def run_energy_publisher(filepath):
    room_key = get_room_key_from_filename(filepath)
    rows = read_csv(filepath)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic")

    print(f"[EnergyAgent-{room_key}] Starting...")

    i = 0
    while True:
        row = rows[i % len(rows)]
        now = datetime.utcnow().isoformat()

        for meter_num in range(1, 7):
            meter_key = f"power_kw_power_meter_{meter_num}"
            device_id = f"power_meter_{meter_num}_{room_key}"

            payload = {
                "datetime": now,  # use current timestamp instead of original
                "device_id": device_id,
                "power": row[meter_key],
            }

            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=ROUTING_KEY,
                body=json.dumps(payload)
            )
            print(f"[EnergyAgent-{room_key}] Published → {payload}")

        i += 1
        time.sleep(5)

def start_energy_agents():
    csv_files = glob.glob(os.path.join(CSV_DIR, "power_meter_data_*.csv"))

    for filepath in csv_files:
        thread = Thread(target=run_energy_publisher, args=(filepath,), daemon=True)
        thread.start()
