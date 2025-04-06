from django.contrib import admin
from .models import Hotel, Room, Floor, Reservation, Guest, Device

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Floor)
admin.site.register(Reservation)
admin.site.register(Guest)
admin.site.register(Device)
