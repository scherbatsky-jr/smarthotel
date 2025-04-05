from django.db import models

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField()

    def __str__(self):
        return self.name

class Floor(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='floors')
    number = models.IntegerField()

    def __str__(self):
        return f"{self.hotel.name} - Floor {self.number}"

class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    number = models.CharField(max_length=10)

    def __str__(self):
        return f"Room {self.number} on {self.floor}"

class Device(models.Model):
    DEVICE_TYPES = [
        ("iaq", "IAQ Sensor"),
        ("life_being", "Life Being Sensor"),
        ("power_meter", "Power Meter"),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=50, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.device_type} ({self.device_id}) in {self.room}"


class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Reservation(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey('hotel.Room', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    passkey = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.guest} - {self.room.name}"
