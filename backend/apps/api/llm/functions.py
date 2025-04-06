FUNCTIONS = [
    {
        "name": "get_latest_sensor_data",
        "description": "Get the latest IAQ and LifeBeing data for the guest's room.",
        "parameters": {
            "type": "object",
            "properties": {
                "room_id": {
                    "type": "string",
                    "description": "The ID of the room (auto-resolved from guest login)"
                }
            },
            "required": ["room_id"]
        }
    },
    {
        "name": "get_room_energy_summary",
        "description": "Download energy consumption summary CSV for the guest's room over the reservation period.",
        "parameters": {
            "type": "object",
            "properties": {
                "resolution": {
                    "type": "string",
                    "enum": ["1hour", "1day", "1month"],
                    "description": "Time resolution for grouping energy data."
                },
                "subsystem": {
                    "type": "string",
                    "enum": ["ac", "lighting", "plug_load"],
                    "description": "Filter by specific subsystem (optional)"
                }
            },
            "required": ["resolution"]
        }
    },
    {
        "name": "get_sensors_by_room",
        "description": "List all sensors installed in the guest's room.",
        "parameters": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string"}
            },
            "required": ["room_id"]
        }
    },
    {
        "name": "get_hotel_summary",
        "description": "Get total number of floors and rooms in the guest's hotel.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"}
            },
            "required": ["hotel_id"]
        }
    },
    {
        "name": "get_floors_by_hotel",
        "description": "Get all floors in the guest's hotel with number of rooms per floor.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"}
            },
            "required": ["hotel_id"]
        }
    },
    {
        "name": "get_rooms_by_floor",
        "description": "Get list of rooms on the guest's floor.",
        "parameters": {
            "type": "object",
            "properties": {
                "floor_id": {"type": "string"}
            },
            "required": ["floor_id"]
        }
    }
]
