from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from openai import OpenAI
import os
import json

from apps.hotel.models import Hotel, Floor, Room, Reservation
from .serializers import HotelSerializer, FloorSerializer, RoomSerializer
from .llm.functions import FUNCTIONS
from .resolvers import FUNCTION_RESOLVERS
from .utils import normalize_function_arguments
from .timescale_service import get_energy_consumption_by_room, get_energy_consumption_by_hotel
from .resolvers import fetch_latest_data_from_supabase

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

@api_view(['GET'])
def get_hotels(request):
    hotels = Hotel.objects.all()
    return Response(HotelSerializer(hotels, many=True).data)

@api_view(['GET'])
def get_floors_in_hotel(request, hotel_id):
    floors = Floor.objects.filter(hotel_id=hotel_id)
    return Response(FloorSerializer(floors, many=True).data)

@api_view(['GET'])
def get_rooms_on_floor(request, floor_id):
    rooms = Room.objects.filter(floor_id=floor_id)
    return Response(RoomSerializer(rooms, many=True).data)

@api_view(["POST"])
def login_by_passkey(request):
    passkey = request.data.get("passkey")
    reservation = Reservation.objects.select_related("guest", "room__floor__hotel").filter(passkey=passkey).first()

    if reservation:
        guest = reservation.guest
        return Response({
            "guest": {
                "first_name": guest.first_name,
                "last_name": guest.last_name,
                "contact": guest.contact,
                "address": guest.address,
            },
            "room_id": reservation.room.id,
            "room_name": reservation.room.number,
            "floor_id": reservation.room.floor.id,
            "floor_name": reservation.room.floor.number,
            "hotel_id": reservation.room.floor.hotel.id,
            "hotel_name": reservation.room.floor.hotel.name,
        })

    return Response({"error": "Invalid passkey"}, status=404)

@api_view(["POST"])
def chat_view(request):
    user_message = request.data.get("message", "")
    user_info = request.data.get("user_info", {})

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a smart hotel assistant. Use the available functions to answer guest queries based on their hotel, floor, and room."},
            {"role": "user", "content": user_message}
        ],
        functions=FUNCTIONS,
        function_call="auto"
    )

    msg = chat_response.choices[0].message

    if msg.function_call:
        fn_name = msg.function_call.name
        args = json.loads(msg.function_call.arguments)

        args = normalize_function_arguments(fn_name, args, user_info)

        resolver = FUNCTION_RESOLVERS.get(fn_name)
        if not resolver:
            return Response({"reply": f"Function {fn_name} is not yet implemented."})

        try:
            result = resolver(**args)
        except Exception as e:
            return Response({"reply": f"An error occurred while processing the function: {str(e)}"})

        second_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a smart hotel assistant."},
                {"role": "user", "content": user_message},
                msg,
                {"role": "function", "name": fn_name, "content": json.dumps(result)}
            ]
        )
        return Response({"reply": second_response.choices[0].message.content})

    return Response({"reply": msg.content})

@api_view(["GET"])
def get_latest_room_data(request, room_id):
    return Response(fetch_latest_data_from_supabase(room_id))

@api_view(["GET"])
def energy_summary_by_room_view(request, room_id):
    resolution = request.query_params.get("resolution")
    subsystem = request.query_params.get("subsystem")
    start_time = request.query_params.get("start_time")
    end_time = request.query_params.get("end_time")

    if not resolution:
        return Response({"error": "Missing required parameter: resolution"}, status=400)

    csv_data = get_energy_consumption_by_room(
        room_id=room_id,
        resolution=resolution,
        start_time=start_time,
        end_time=end_time,
        subsystem=subsystem
    )

    if isinstance(csv_data, dict) and "error" in csv_data:
        return Response(csv_data, status=400)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename=room_{room_id}_energy_summary.csv'
    return response

@api_view(["GET"])
def energy_summary_by_hotel_view(request, hotel_id):
    resolution = request.GET.get("resolution")
    start_time = request.GET.get("start_time")
    end_time = request.GET.get("end_time")
    subsystem = request.GET.get("subsystem")

    if not resolution:
        return Response({"error": "Missing required parameter: resolution"}, status=400)

    csv_data = get_energy_consumption_by_hotel(
        hotel_id=hotel_id,
        resolution=resolution,
        start_time=start_time,
        end_time=end_time,
        subsystem=subsystem
    )

    return HttpResponse(csv_data, content_type="text/csv")