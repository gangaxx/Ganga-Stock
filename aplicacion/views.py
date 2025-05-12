from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Producto, Movimiento

def index(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session['nombre_usuario'] = user.username
                return redirect('index_admin' if user.is_superuser else 'index_empleado')
            else:
                messages.error(request, 'Credenciales incorrectas.')

        elif 'registro' in request.POST:
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']

            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Ese usuario ya existe.')
            else:
                User.objects.create_user(username=username, password=password1)
                messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')

    return render(request, 'index.html')

@user_passes_test(lambda u: u.is_superuser)
def index_admin(request):
    movimientos = Movimiento.objects.select_related('producto', 'empleado').order_by('-fecha', '-hora')
    return render(request, 'index_admin.html', {'movimientos': movimientos})

def is_empleado(user):
    return user.is_authenticated and not user.is_superuser

@login_required
@user_passes_test(is_empleado)
def index_empleado(request):
    productos = Producto.objects.all()
    return render(request, 'index_empleado.html', {'productos': productos})

def cerrar_sesion(request):
    logout(request)
    return redirect('index')

@login_required
def procesar_compra(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito = data.get('carrito', [])
            for item in carrito:
                producto = Producto.objects.get(id=item['id'])
                cantidad = item['cantidad']
                if producto.cantidad >= cantidad:
                    producto.cantidad -= cantidad
                    producto.save()
                    Movimiento.objects.create(producto=producto, cantidad_vendida=cantidad, empleado=request.user)
                else:
                    return JsonResponse({'success': False, 'error': f'Stock insuficiente para {producto.nombre}'})
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@user_passes_test(lambda u: u.is_superuser)
def inventario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        imagen = request.POST.get('imagen')  # Ruta relativa desde static/
        precio = request.POST.get('precio')
        cantidad = request.POST.get('cantidad')

        if nombre and imagen and precio and cantidad:
            Producto.objects.create(
                nombre=nombre,
                imagen=imagen,
                precio=precio,
                cantidad=cantidad
            )
            messages.success(request, "Producto agregado correctamente.")
            return redirect('inventario')

    productos = Producto.objects.all()
    return render(request, 'inventario.html', {'productos': productos})

@user_passes_test(lambda u: u.is_superuser)
def empleado(request):
    if request.method == 'POST' and 'registro' in request.POST:
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe.')
        else:
            User.objects.create_user(username=username, password=password1)
            messages.success(request, 'Empleado registrado correctamente.')

    empleados = User.objects.filter(is_superuser=False)
    return render(request, 'empleado.html', {'empleados': empleados})

# ✅ Agregado: actualizar stock
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def update_stock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto = Producto.objects.get(id=data['id'])
            if data['action'] == 'add':
                producto.cantidad += 1
            elif data['action'] == 'remove' and producto.cantidad > 0:
                producto.cantidad -= 1
            producto.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ✅ Agregado: eliminar producto
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def eliminar_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto = Producto.objects.get(id=data['id'])
            producto.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
