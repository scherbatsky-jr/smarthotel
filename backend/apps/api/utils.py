from django.db import connection

def resolve_hotel_id_by_name(name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM hotel_hotel WHERE name ILIKE %s",
            [f"%{name}%"]
        )
        row = cursor.fetchone()
    return row[0] if row else None

def resolve_room_id_by_name(name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM hotel_room WHERE number ILIKE %s", [name])
        row = cursor.fetchone()
    return row[0] if row else None

def normalize_function_arguments(fn_name, args, user_context):
    def get_id(key):
        return str(user_context.get(key) or args.get(key))

    if fn_name in ["get_latest_sensor_data", "get_sensors_by_room"]:
        args["room_id"] = get_id("room_id")

    elif fn_name in ["get_hotel_summary", "get_floors_by_hotel", "download_energy_summary_csv"]:
        args["hotel_id"] = get_id("hotel_id")

    elif fn_name == "get_rooms_by_floor":
        args["floor_id"] = get_id("floor_id")

    return args
