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

def normalize_function_arguments(fn_name, args, user_info=None):
    if not user_info:
        return args

    if fn_name in ["get_latest_sensor_data", "get_sensors_by_room", "get_room_energy_summary"]:
        user_room_id = str(user_info.get("room_id"))
        requested_room_id = str(args.get("room_id", user_room_id))

        if requested_room_id != user_room_id:
            raise PermissionError("Access denied: You can only view your own room's data.")

        # Ensure room_id is injected if not provided
        args["room_id"] = user_room_id

    if fn_name in [
        "get_floors_by_hotel",
        "get_room_count_by_hotel",
        "get_all_rooms_by_hotel",
        "get_hotel_summary"
    ]:
        if "hotel_id" not in args and user_info.get("hotel_id"):
            args["hotel_id"] = user_info["hotel_id"]

    # ✅ Inject floor_id if missing
    if fn_name == "get_rooms_by_floor":
        if "floor_id" not in args and user_info.get("floor_id"):
            args["floor_id"] = user_info["floor_id"]

    return args
