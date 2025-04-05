import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_realtime_data(device_id, datapoint, value):
    data = {
        "device_id": device_id,
        "datapoint": datapoint,
        "value": str(value)
    }

    # Update if exists, insert otherwise
    response = supabase.table("realtime_data").upsert(data, on_conflict=["device_id", "datapoint"]).execute()

    return response
