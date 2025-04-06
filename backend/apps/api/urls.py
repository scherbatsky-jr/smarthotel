from django.urls import path
from . import views

urlpatterns = [
    path('login/guest', views.login_by_passkey),
    path('hotels/', views.get_hotels),
    path('hotels/<int:hotel_id>/floors/', views.get_floors_in_hotel),
    path('floors/<int:floor_id>/rooms/', views.get_rooms_on_floor),
    path('hotels/<int:hotel_id>/energy_summary/', views.energy_summary_by_hotel_view),
    path('rooms/<int:room_id>/energy_summary/', views.energy_summary_by_room_view),
    path('rooms/<int:room_id>/data/', views.get_latest_room_data),
    path('chat/', views.chat_view)
]
