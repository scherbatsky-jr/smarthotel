import os
import psycopg2
import pandas as pd
from io import StringIO

def get_timescale_connection():
    return psycopg2.connect(
        host=os.getenv("TS_DB_HOST"),
        port=os.getenv("TS_DB_PORT"),
        dbname=os.getenv("TS_DB_NAME"),
        user=os.getenv("TS_DB_USER"),
        password=os.getenv("TS_DB_PASS")
    )

def insert_raw_data_row(device_id, datapoint, value, timestamp, datetime):
    conn = get_timescale_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO raw_data (timestamp, datetime, device_id, datapoint, value)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (timestamp, datetime, device_id, datapoint, str(value))
    )
    conn.commit()
    cur.close()
    conn.close()

def get_energy_consumption(subsystems, resolution, start_time=None, end_time=None):
    meters = []
    from .constants import SUBSYSTEM_METERS

    for subsystem in subsystems:
        meters += SUBSYSTEM_METERS.get(subsystem, [])

    if not meters:
        return pd.DataFrame()

    meters_sql = ",".join(f"'{m}'" for m in meters)

    if resolution == "1hour":
        time_bucket = "1 hour"
    elif resolution == "1day":
        time_bucket = "1 day"
    elif resolution == "1month":
        time_bucket = "1 month"
    else:
        raise ValueError("Invalid resolution")

    where_clause = f"WHERE datapoint = 'kW' AND device_id IN ({meters_sql})"
    if start_time:
        where_clause += f" AND datetime >= '{start_time}'"
    if end_time:
        where_clause += f" AND datetime <= '{end_time}'"

    query = f"""
        SELECT
            time_bucket('{time_bucket}', datetime) AS bucket,
            device_id,
            AVG(CAST(value AS FLOAT)) AS avg_kw,
            COUNT(*) * EXTRACT(EPOCH FROM INTERVAL '5 seconds') / 3600 AS run_hours
        FROM raw_data
        {where_clause}
        GROUP BY bucket, device_id
        ORDER BY bucket ASC;
    """

    conn = get_timescale_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    df["energy_kwh"] = df["avg_kw"] * df["run_hours"]

    result = df.groupby("bucket")["energy_kwh"].sum().reset_index()

    return result
