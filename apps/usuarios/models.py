from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    hotel = models.ForeignKey(
        'hoteles.Hotel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        help_text="Hotel al que pertenece el usuario"
    )
    fcm_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token FCM para notificaciones push de Firebase"
    )

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
