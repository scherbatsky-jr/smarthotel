from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os
from . import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

urlpatterns = [
    path('login/guest/', views.login_by_passkey),
    path("login/admin/", views.admin_login),
    path('hotels/', permission_classes([IsAuthenticated])(views.get_hotels)),
    path('hotels/<int:hotel_id>/floors/', permission_classes([IsAuthenticated])(views.get_floors_in_hotel)),
    path('floors/<int:floor_id>/rooms/', permission_classes([IsAuthenticated])(views.get_rooms_on_floor)),
    path('hotels/<int:hotel_id>/rooms/', permission_classes([IsAuthenticated])(views.grouped_rooms_by_hotel)),
    path('hotels/<int:hotel_id>/energy_summary/', permission_classes([IsAuthenticated])(views.energy_summary_by_hotel_view)),
    path('rooms/<int:room_id>/energy_summary/', permission_classes([IsAuthenticated])(views.energy_summary_by_room_view)),
    path('rooms/<int:room_id>/data/', permission_classes([IsAuthenticated])(views.get_latest_room_data)),
    path('chat/', permission_classes([IsAuthenticated])(views.chat_view)),
    path("api/downloads/<path:path>", serve, {
        "document_root": os.path.join(settings.MEDIA_ROOT, "exports"),
    }),
]
