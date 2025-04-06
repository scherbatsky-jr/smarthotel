import os
import json
import pika
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from django.db import connections

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "iot_exchange"

def insert_timescale(device_id, datapoint, value, dt):
    timestamp = int(dt.timestamp())
    with connections['default'].cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO raw_data (timestamp, datetime, device_id, datapoint, value)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (timestamp, dt, device_id, datapoint, str(value))
        )

def upsert_supabase(device_id, datapoint, value):
    try:
        data = {
            "device_id": device_id,
            "datapoint": datapoint,
            "value": str(value)
        }
        print(f"[Supabase] Upserting: {data}")
        supabase.table("realtime_data").upsert(data, on_conflict="device_id, datapoint").execute()
    except Exception as e:
        print(f"[Supabase ERROR] Failed to upsert {device_id}:{datapoint} → {e}")

def process_message(body):
    data = json.loads(body)
    device_id = data["device_id"]
    dt = datetime.fromisoformat(data["datetime"])

    for key in data:
        if key in ["device_id", "datetime", "room_id"]:
            continue

        value = data[key]
        print(f"[Datalogger] → {device_id}, {key}: {value}")
        insert_timescale(device_id, key, value, dt)
        upsert_supabase(device_id, key, value)

def callback(ch, method, properties, body):
    print(f"[← {method.routing_key}] Message received")
    process_message(body)

def start_datalogger():
    print("[✓] Datalogger Agent started")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic")

    queue = channel.queue_declare(queue='', exclusive=True).method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue, routing_key="sensor.iaq")
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue, routing_key="sensor.lifebeing")
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue, routing_key="sensor.energy")

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
