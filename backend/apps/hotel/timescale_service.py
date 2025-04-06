import csv
from io import StringIO
from django.db import connections, connection

SUBSYSTEM_DEVICE_MAP = {
    "ac": ["power_meter_1", "power_meter_2", "power_meter_3"],
    "lighting": ["power_meter_4", "power_meter_5"],
    "plug_load": ["power_meter_6"]
}

def get_energy_consumption_by_room(room_id, resolution, start_time=None, end_time=None, subsystem=None):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT device_id FROM hotel_device
            WHERE room_id = %s AND device_type = 'power_meter'
        """, [room_id])
        all_devices = [row[0] for row in cursor.fetchall()]

    if not all_devices:
        return "timestamp\n"

    # Filter devices by subsystem if provided
    filtered_devices = []
    if subsystem:
        keys = SUBSYSTEM_DEVICE_MAP.get(subsystem.lower())
        filtered_devices = [d for d in all_devices if any(k in d for k in keys)]
    else:
        filtered_devices = all_devices

    if not filtered_devices:
        return "timestamp\n"

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

    with connections["default"].cursor() as cursor:
        cursor.execute(query, sql_params)
        rows = cursor.fetchall()

    summary = {}
    for bucket, device_id, avg_kw in rows:
        ts = bucket.isoformat()
        energy = avg_kw * 1
        subsystem_type = next((k for k, v in SUBSYSTEM_DEVICE_MAP.items() if any(key in device_id for key in v)), None)
        if subsystem_type:
            summary.setdefault(ts, {}).setdefault(subsystem_type, 0.0)
            summary[ts][subsystem_type] += energy

    output = StringIO()
    writer = csv.writer(output)

    columns = [subsystem.lower()] if subsystem else list(SUBSYSTEM_DEVICE_MAP.keys())
    writer.writerow(["timestamp"] + columns)

    for ts in sorted(summary.keys()):
        row = [ts] + [round(summary[ts].get(col, 0.0), 2) for col in columns]
        writer.writerow(row)

    return output.getvalue()


def get_energy_consumption_by_hotel(hotel_id, resolution, start_time=None, end_time=None, subsystem=None):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT d.device_id
            FROM hotel_device d
            JOIN hotel_room r ON d.room_id = r.id
            JOIN hotel_floor f ON r.floor_id = f.id
            WHERE d.device_type = 'power_meter' AND f.hotel_id = %s
        """, [hotel_id])
        all_devices = [row[0] for row in cursor.fetchall()]

    if not all_devices:
        return "timestamp\n"

    filtered_devices = []
    if subsystem:
        keys = SUBSYSTEM_DEVICE_MAP.get(subsystem.lower())
        filtered_devices = [d for d in all_devices if any(k in d for k in keys)]
    else:
        filtered_devices = all_devices

    if not filtered_devices:
        return "timestamp\n"

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

    with connections["default"].cursor() as cursor:
        cursor.execute(query, sql_params)
        rows = cursor.fetchall()

    summary = {}
    for bucket, device_id, avg_kw in rows:
        ts = bucket.isoformat()
        energy = avg_kw * 1
        subsystem_type = next((k for k, v in SUBSYSTEM_DEVICE_MAP.items() if any(key in device_id for key in v)), None)
        if subsystem_type:
            summary.setdefault(ts, {}).setdefault(subsystem_type, 0.0)
            summary[ts][subsystem_type] += energy

    output = StringIO()
    writer = csv.writer(output)

    columns = [subsystem.lower()] if subsystem else list(SUBSYSTEM_DEVICE_MAP.keys())
    writer.writerow(["timestamp"] + columns)

    for ts in sorted(summary.keys()):
        row = [ts] + [round(summary[ts].get(col, 0.0), 2) for col in columns]
        writer.writerow(row)

    return output.getvalue()
