from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    ROLES = (
        ('vendedor', 'Vendedor'),
        ('bodeguero', 'Bodeguero'),
        ('cajero', 'Cajero'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=10, choices=ROLES)
    rut = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username} - {self.rol}"


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')  # Ahora usa ImageField
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_vendida = models.PositiveIntegerField(default=0)
    cantidad_devuelta = models.PositiveIntegerField(default=0)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto.nombre} - {self.empleado.username} - {self.fecha}"


class EmpleadoEliminado(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=12)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=20)

    def __str__(self):
        return self.username


class CarritoTemporal(models.Model):
    codigo = models.CharField(max_length=6, unique=True)
    productos = models.JSONField()  # [{id, nombre, cantidad, precio, imagen_url}]
    total = models.DecimalField(max_digits=10, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)
