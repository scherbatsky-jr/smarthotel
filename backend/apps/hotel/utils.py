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

    # Protect room-specific data
    if fn_name in ["get_latest_sensor_data", "get_sensors_by_room", "get_room_energy_summary"]:
        user_room_id = str(user_info.get("room_id"))
        requested_room_id = str(args.get("room_id"))
        print(args)

        if requested_room_id and requested_room_id != user_room_id:
            raise PermissionError("Access denied: You can only view your own room's data.")
        args["room_id"] = int(user_room_id)

    # Hotel-specific data
    if fn_name in [
        "get_floors_by_hotel", "get_room_count_by_hotel",
        "get_all_rooms_by_hotel", "get_hotel_summary"
    ]:
        user_hotel_id = str(user_info.get("hotel_id"))
        requested_hotel_id = str(args.get("hotel_id"))

        if requested_hotel_id and requested_hotel_id != user_hotel_id:
            raise PermissionError("Access denied: You can only view your own hotel's data.")
        args["hotel_id"] = user_hotel_id

    # Floor-specific
    if fn_name == "get_rooms_by_floor":
        user_floor_id = str(user_info.get("floor_id"))
        requested_floor_id = str(args.get("floor_id"))

        if requested_floor_id and requested_floor_id != user_floor_id:
            raise PermissionError("Access denied: You can only view your own floor's data.")
        args["floor_id"] = user_floor_id

    return args
