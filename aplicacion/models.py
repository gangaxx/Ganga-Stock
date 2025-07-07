from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

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

    # NUEVOS CAMPOS PARA ROL TEMPORAL
    rol_temporal = models.CharField(max_length=10, choices=ROLES, null=True, blank=True)
    inicio_temporal = models.DateTimeField(null=True, blank=True)
    fin_temporal = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_actual_display()}"

    def get_rol_actual(self):
        """Devuelve el rol activo, considerando si hay un rol temporal vigente."""
        now = timezone.now()
        if self.rol_temporal and self.inicio_temporal and self.fin_temporal:
            if self.inicio_temporal <= now <= self.fin_temporal:
                return self.rol_temporal
            else:
                # Limpiar si está vencido
                self.rol_temporal = None
                self.inicio_temporal = None
                self.fin_temporal = None
                self.save()
        return self.rol

    def get_rol_actual_display(self):
        actual = self.get_rol_actual()
        return dict(self.ROLES).get(actual, actual)


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)

    # ✅ Campos de oferta bien definidos
    descuento = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Porcentaje de descuento, por ejemplo: 15 para 15%"
    )
    fecha_inicio_oferta = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha y hora de inicio de la oferta"
    )
    fecha_fin_oferta = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha y hora de fin de la oferta"
    )

    def __str__(self):
        return self.nombre

    def precio_oferta(self):
        """
        Calcula el precio final con descuento si está vigente.
        """
        from django.utils import timezone
        ahora = timezone.now()
        if (
            self.descuento > 0 and
            self.fecha_inicio_oferta and
            self.fecha_fin_oferta and
            self.fecha_inicio_oferta <= ahora <= self.fecha_fin_oferta
        ):
            return self.precio * (1 - self.descuento / 100)
        return self.precio


class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_vendida = models.PositiveIntegerField(default=0)
    cantidad_devuelta = models.PositiveIntegerField(default=0)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto.nombre} - {self.empleado.username} - {self.fecha}"


class MovimientoBodega(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    agregado = models.PositiveIntegerField(default=0)
    eliminado = models.PositiveIntegerField(default=0)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    empleado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.producto.nombre} - Agregado: {self.agregado} - Eliminado: {self.eliminado}"


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
    productos = models.JSONField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)


class VentaCajero(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    cajero = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Venta {self.producto.nombre} - {self.fecha} - {self.total_venta}"


class BoletaCliente(models.Model):
    codigo = models.CharField(max_length=6, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Boleta {self.codigo} - ${self.total}"


class BoletaItem(models.Model):
    boleta = models.ForeignKey(BoletaCliente, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nombre} x{self.cantidad}"
