from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.http import HttpResponse
from openai import OpenAI
import os
import json
from rest_framework_simplejwt.tokens import RefreshToken

from apps.hotel.models import Hotel, Floor, Room, Reservation
from .serializers import HotelSerializer, FloorSerializer, RoomSerializer
from .llm.functions import FUNCTIONS
from .resolvers import FUNCTION_RESOLVERS
from .utils import normalize_function_arguments
from .timescale_service import get_energy_consumption_by_room, get_energy_consumption_by_hotel
from .resolvers import fetch_latest_data_from_supabase

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_hotels(request):
    hotels = Hotel.objects.all()
    return Response(HotelSerializer(hotels, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_floors_in_hotel(request, hotel_id):
    floors = Floor.objects.filter(hotel_id=hotel_id)
    return Response(FloorSerializer(floors, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rooms_on_floor(request, floor_id):
    rooms = Room.objects.filter(floor_id=floor_id)
    return Response(RoomSerializer(rooms, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grouped_rooms_by_hotel(request, hotel_id):
    try:
        floors = Floor.objects.filter(hotel_id=hotel_id).prefetch_related(
            Prefetch(
            'rooms',
            queryset=Room.objects.prefetch_related('devices')
        )
        )

        result = []

        for floor in floors:
            rooms = floor.rooms.all()
            result.append({
                "floor": {
                    "id": floor.id,
                    "number": floor.number
                },
                "rooms": [
                    {
                        "id": room.id,
                        "number": room.number,
                        "devices": [
                        {
                            "id": device.id,
                            "device_type": device.device_type,
                        }
                        for device in room.devices.all()
                    ]
                    } for room in rooms
                ]
            })

        return Response(result)

    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"}, status=404)

@api_view(["POST"])
def admin_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user and user.is_staff:
        refresh = RefreshToken.for_user(user)
        request.session["user_id"] = user.id  # Store user ID in session
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user_info": {
                "username": user.username,
                "email": user.email,
                "role": "admin"
            }
        })
    return Response({"error": "Invalid credentials"}, status=401)

@api_view(["POST"])
def login_by_passkey(request):
    passkey = request.data.get("passkey")
    reservation = Reservation.objects.select_related(
        "guest", "room__floor__hotel"
    ).prefetch_related("room__devices").filter(passkey=passkey).first()

    if not reservation:
        return Response({"error": "Invalid passkey"}, status=404)

    room = reservation.room
    floor = room.floor
    hotel = floor.hotel
    guest = reservation.guest

    # Create or fetch a user account based on guest contact
    user, created = User.objects.get_or_create(username=guest.contact)
    refresh = RefreshToken.for_user(user)

    devices = [
        {
            "id": device.id,
            "device_type": device.device_type,
        }
        for device in room.devices.all()
    ]

    return Response({
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user_info": {
            "first_name": guest.first_name,
            "last_name": guest.last_name,
            "contact": guest.contact,
            "address": guest.address,
            "role": "guest"
        },
        "reservation": {
            "id": reservation.id,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "hotel": {
                "id": hotel.id,
                "name": hotel.name,
                "floor": {
                    "id": floor.id,
                    "number": floor.number,
                    "room": {
                        "id": room.id,
                        "name": room.number,
                        "devices": devices
                    }
                }
            }
        }
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_view(request):
    user_message = request.data.get("message", "")
    user_info = request.data.get("user_info", {})

    system_context = f"""
        You are a smart hotel assistant helping a guest.
        The guest is currently staying in:

        - Hotel ID: {user_info['hotel_id']}
        - Floor ID: {user_info['floor_id']}
        - Room ID: {user_info['room_id']}
        - Room Name: {user_info.get('room_name', '')}
        - Reservation ID: {user_info['reservation_id']}

        They are only allowed to access information related to **their own room**.
        If they ask about another room, you must politely deny the request.
        Use the functions responsibly and only for their room.
        """

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_message}
        ],
        functions=FUNCTIONS,
        function_call="auto"
    )

    msg = chat_response.choices[0].message

    if msg.function_call:
        fn_name = msg.function_call.name
        args = json.loads(msg.function_call.arguments)

        try:
            args = normalize_function_arguments(fn_name, args, user_info)
            resolver = FUNCTION_RESOLVERS.get(fn_name)
            if not resolver:
                return Response({"reply": f"Function {fn_name} is not yet implemented."})

            result = resolver(**args)

            second_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_message},
                    msg,
                    {"role": "function", "name": fn_name, "content": json.dumps(result)}
                ]
            )
            return Response({"reply": second_response.choices[0].message.content})

        except PermissionError as e:
            return Response({"reply": str(e)})
        except Exception as e:
            return Response({"reply": f"An error occurred while processing the function: {str(e)}"})

    return Response({"reply": msg.content})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_latest_room_data(request, room_id):
    return Response(fetch_latest_data_from_supabase(room_id))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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