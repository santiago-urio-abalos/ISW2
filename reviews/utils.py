from django.contrib.auth.models import User
from relecloud.models import Cruise
from .models import Review

def user_has_purchased(user: User, cruise: Cruise) -> bool:
    """
    Devuelve True si el usuario ha comprado un cruise.
    Aquí puedes conectar con tu modelo de ventas o reservas.
    """
    # Este es un ejemplo: supongamos que tienes un modelo Purchase
    from relecloud.models import Purchase
    return Purchase.objects.filter(user=user, cruise=cruise).exists()
