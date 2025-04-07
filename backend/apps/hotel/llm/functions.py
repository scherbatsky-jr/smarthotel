FUNCTIONS = [
    {
        "name": "get_latest_sensor_data",
        "description": "Get the latest IAQ and LifeBeing data for the guest's current room only. Do not use for other rooms.",
        "parameters": {
            "type": "object",
            "properties": {
            "room_id": {
                "type": "string",
                "description": "Must be the room ID of the guest. No other rooms are allowed."
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
                "room_id": {
                    "type": "string",
                    "description": "Must be the room ID of the guest. No other rooms are allowed."
                },
                "reservation_id": {
                    "type": "string",
                    "description": "Must be the reservation id for the rooom reserved by the guest"
                },
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
            "required": ["resolution", "reservation_id", "room_id"]
        }
    },
    {
        "name": "get_room_historical_summary",
        "description": "Returns historical insights (average, max, min, last seen) for a specific datapoint in the guest's room.",
        "parameters": {
            "type": "object",
            "properties": {
                "room_id": {
                    "type": "string",
                    "description": "Room ID of the guest. Automatically resolved by the system."
                },
                "datapoint": {
                    "type": "string",
                    "description": "Datapoint to query (e.g., temperature, humidity, co2, presence_state)"
                },
                "stat": {
                    "type": "string",
                    "enum": ["average", "max", "min", "last_seen"],
                    "description": "Type of analysis to return"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time for the analysis range (ISO format, optional)"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time for the analysis range (ISO format, optional)"
                }
            },
            "required": ["room_id", "datapoint", "stat"]
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
