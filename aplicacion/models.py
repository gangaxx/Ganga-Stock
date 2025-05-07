from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.rol}"
    


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.CharField(max_length=255)  # Ruta relativa a la carpeta static
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
