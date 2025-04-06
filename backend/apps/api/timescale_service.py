import os
import psycopg2
import csv
import pandas as pd
from io import StringIO
from django.db import connection, connections

SUBSYSTEM_DEVICE_MAP = {
    "ac": ["power_meter_1", "power_meter_2", "power_meter_3"],
    "lighting": ["power_meter_4", "power_meter_5"],
    "plug_load": ["power_meter_6"]
}

def get_timescale_connection():
    return psycopg2.connect(
        host=os.getenv("TS_DB_HOST"),
        port=os.getenv("TS_DB_PORT"),
        dbname=os.getenv("TS_DB_NAME"),
        user=os.getenv("TS_DB_USER"),
        password=os.getenv("TS_DB_PASS")
    )

SUBSYSTEM_DEVICE_MAP = {
    "ac": ["power_meter_1", "power_meter_2", "power_meter_3"],
    "lighting": ["power_meter_4", "power_meter_5"],
    "plug_load": ["power_meter_6"]
}

def get_energy_consumption_by_room(room_id, resolution, start_time=None, end_time=None, subsystem=None):
    # Step 1: Fetch power_meter device_ids from default DB (Postgres)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT device_id FROM hotel_device
            WHERE room_id = %s AND device_type = 'power_meter'
        """, [room_id])
        all_devices = [row[0] for row in cursor.fetchall()]

    # Step 2: Subsystem filter
    filtered_devices = []
    if subsystem:
        keys = SUBSYSTEM_DEVICE_MAP.get(subsystem.lower())
        if keys:
            for d in all_devices:
                if any(k in d for k in keys):
                    filtered_devices.append(d)
    else:
        filtered_devices = all_devices

    if not filtered_devices:
        return {"error": "No matching devices found for the room and subsystem."}

    # Step 3: Prepare time_bucket resolution
    time_bucket_interval = {
        "1hour": "1 hour",
        "1day": "1 day",
        "1month": "1 month"
    }.get(resolution, "1 hour")

    placeholders = ",".join(["%s"] * len(filtered_devices))
    sql_params = [time_bucket_interval] + filtered_devices

    query = f"""
        SELECT time_bucket(%s::interval, datetime) as bucket,
            device_id,
            AVG(value::FLOAT) as avg_kw
        FROM raw_data
        WHERE device_id IN ({placeholders})
        AND datapoint = 'power'
    """
    if start_time:
        query += " AND datetime >= %s"
        sql_params.append(start_time)
    if end_time:
        query += " AND datetime <= %s"
        sql_params.append(end_time)

    query += " GROUP BY bucket, device_id ORDER BY bucket"

    # Step 4: Run the query using the timescale DB
    with connections["timescale"].cursor() as cursor:
        cursor.execute(query, sql_params)
        rows = cursor.fetchall()

    # 5. Aggregate energy (kWh) per subsystem
    summary = {}
    for bucket, device_id, avg_kw in rows:
        ts = bucket.isoformat()
        energy = avg_kw * 1  # assuming 1 hour duration

        subsystem_type = None
        for sys, keys in SUBSYSTEM_DEVICE_MAP.items():
            if any(k in device_id for k in keys):
                subsystem_type = sys
                break

        if subsystem_type:
            if ts not in summary:
                summary[ts] = {}
            summary[ts].setdefault(subsystem_type, 0.0)
            summary[ts][subsystem_type] += energy

    # Step 6: Format CSV
    output = StringIO()
    writer = csv.writer(output)

    # Determine which subsystems to show
    columns = []
    if subsystem:
        columns = [subsystem.lower()]
    else:
        columns = ["ac", "lighting", "plug_load"]

    writer.writerow(["timestamp"] + columns)

    for ts in sorted(summary.keys()):
        row = [ts]
        for col in columns:
            row.append(round(summary[ts].get(col, 0.0), 2))
        writer.writerow(row)

    return output.getvalue()
