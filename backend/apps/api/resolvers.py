from django.db import connection
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_latest_data_from_supabase(room_id):
    # Fetch device IDs from hotel_device table
    with connection.cursor() as cursor:
        cursor.execute("SELECT device_type, device_id FROM hotel_device WHERE room_id = %s", [room_id])
        devices = cursor.fetchall()

    device_map = {"iaq_sensor": [], "presence_sensor": []}
    for dtype, did in devices:
        if dtype in device_map:
            device_map[dtype].append(did)

    def fetch_device_data(device_ids):
        data_map = {}
        for dev_id in device_ids:
            res = supabase.table("realtime_data").select("*").eq("device_id", dev_id).execute()
            for row in res.data:
                data_map[row["datapoint"]] = row
        return data_map

    iaq = fetch_device_data(device_map["iaq_sensor"])
    lb = fetch_device_data(device_map["presence_sensor"])

    return {
        "room_id": room_id,
        "iaq": {
            "temperature": iaq.get("temperature", {}).get("value"),
            "humidity": iaq.get("humidity", {}).get("value"),
            "co2": iaq.get("co2", {}).get("value"),
            "timestamp": iaq.get("temperature", {}).get("timestamp"),
        },
        "life_being": {
            "presence_state": lb.get("presence_state", {}).get("value"),
            "sensitivity": lb.get("sensitivity", {}).get("value"),
            "timestamp": lb.get("presence_state", {}).get("timestamp"),
        }
    }

def get_hotels():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM hotel_hotel")
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1]} for r in rows]


def get_floors_by_hotel(hotel_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.id, f.name, COUNT(r.id) as room_count
            FROM hotel_floor f
            LEFT JOIN hotel_room r ON r.floor_id = f.id
            WHERE f.hotel_id = %s
            GROUP BY f.id
        """, [hotel_id])
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "room_count": r[2]} for r in rows]


def get_rooms_by_floor(floor_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM hotel_room WHERE floor_id = %s", [floor_id])
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1]} for r in rows]


def get_room_count_by_hotel(hotel_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM hotel_room
            WHERE floor_id IN (
                SELECT id FROM hotel_floor WHERE hotel_id = %s
            )
        """, [hotel_id])
        count = cursor.fetchone()[0]
    return {"hotel_id": hotel_id, "room_count": count}


def get_all_rooms_by_hotel(hotel_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.id, r.name, f.id as floor_id, f.name as floor_name
            FROM hotel_room r
            JOIN hotel_floor f ON r.floor_id = f.id
            WHERE f.hotel_id = %s
        """, [hotel_id])
        rows = cursor.fetchall()
    return [
        {"id": r[0], "name": r[1], "floor_id": r[2], "floor_name": r[3]}
        for r in rows
    ]


def get_sensors_by_room(room_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, device_id, device_type
            FROM hotel_device
            WHERE room_id = %s
        """, [room_id])
        rows = cursor.fetchall()
    return [
        {"id": r[0], "device_id": r[1], "device_type": r[2]}
        for r in rows
    ]

FUNCTION_RESOLVERS = {
    "get_latest_sensor_data": fetch_latest_data_from_supabase,
    "get_sensors_by_room": get_sensors_by_room,
    "get_floors_by_hotel": get_floors_by_hotel,
    "get_rooms_by_floor": get_rooms_by_floor,
}
