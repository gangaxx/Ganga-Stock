from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
import json

from .forms import RegistroEmpleadoForm
from .models import Producto

def index(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session['nombre_usuario'] = user.username
                if user.is_superuser:
                    return redirect('index_admin')
                else:
                    return redirect('index_empleado')
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
    return render(request, 'index_admin.html')

def is_empleado(user):
    return user.is_authenticated and not user.is_superuser

@login_required
@user_passes_test(is_empleado)
def index_empleado(request):
    productos = Producto.objects.all()
    return render(request, 'index_empleado.html', {'productos': productos})

def registro_empleado(request):
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('index')
    else:
        form = RegistroEmpleadoForm()
    return render(request, 'index.html', {'form': form})

def login_empleado(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.is_superuser:
            login(request, user)
            request.session['nombre_usuario'] = user.username
            return redirect('index_empleado')
        else:
            messages.error(request, 'Credenciales inválidas o acceso no autorizado.')
    return render(request, 'index.html')

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
                producto_id = item.get('id')
                cantidad = item.get('cantidad', 0)
                producto = Producto.objects.get(id=producto_id)
                if producto.cantidad >= cantidad:  # Usar `cantidad` en lugar de `stock`
                    producto.cantidad -= cantidad
                    producto.save()
                else:
                    return JsonResponse({'success': False, 'error': f'Stock insuficiente para {producto.nombre}'})
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@user_passes_test(lambda u: u.is_superuser)
def inventario(request):
    return render(request, 'inventario.html')

@user_passes_test(lambda u: u.is_superuser)
def empleado(request):
    return render(request, 'empleado.html')


