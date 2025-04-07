import os
import time
import json
import glob
import pika
import pandas as pd
from django.db import connection
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

def get_power_meter_device_ids_for_room(room_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, metadata
            FROM hotel_device
            WHERE room_id = %s AND device_type = 'power_meter'
        """, [room_id])
        rows = cursor.fetchall()
        cursor.close()

        result = {}
        for device_id, metadata in rows:
            try:
                meta = json.loads(metadata)
                name = meta.get("name")  # e.g., power_meter_1
                if name:
                    result[name] = device_id
            except Exception as e:
                print(f"[Warning] Could not parse metadata for device {device_id}: {e}")
        return result  # { "power_meter_1": 23, "power_meter_2": 24, ... }

def run_energy_publisher(filepath):
    room_key = get_room_key_from_filename(filepath)
    room_id = int(room_key[1:])  # remove 'R' and convert to int
    print(room_id)
    # Load device mapping from DB
    meter_name_to_id = get_power_meter_device_ids_for_room(room_id)
    if not meter_name_to_id:
        print(f"[EnergyAgent-{room_key}] No power meter devices found in DB for room ID {room_id}")
        return

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
            meter_name = f"power_meter_{meter_num}"
            device_id = meter_name_to_id.get(meter_name)
            if not device_id:
                continue

            meter_key = f"power_kw_{meter_name}"
            print(meter_key)
            if meter_key not in row:
                continue

            payload = {
                "datetime": now,
                "device_id": str(device_id),
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
