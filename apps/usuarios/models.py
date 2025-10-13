from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        permissions = [
            ("can_manage_hotels", "Can manage hotels"),
            ("can_manage_rooms", "Can manage rooms"),
            ("can_view_reports", "Can view reports"),
            ("can_manage_bookings", "Can manage bookings"),
            ("can_manage_users", "Can manage users"),
        ]

    def __str__(self):
        return self.username
