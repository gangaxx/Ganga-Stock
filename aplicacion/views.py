from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Producto, Movimiento, PerfilUsuario, EmpleadoEliminado

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
                try:
                    perfil = PerfilUsuario.objects.get(user=user)
                    if perfil.rol == 'vendedor':
                        return redirect('vendedor')
                    elif perfil.rol == 'bodeguero':
                        return redirect('bodeguero')
                    elif perfil.rol == 'cajero':
                        return redirect('cajero')
                except PerfilUsuario.DoesNotExist:
                    messages.error(request, 'Perfil de usuario no encontrado.')
                    return redirect('index')
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
        imagen = request.POST.get('imagen')
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
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        genero = request.POST.get('genero')
        rol = request.POST.get('rol')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe.')
        else:
            user = User.objects.create_user(username=username, password=password1, email=email, first_name=nombre)
            PerfilUsuario.objects.create(user=user, rol=rol, rut=rut, fecha_nacimiento=fecha_nacimiento, genero=genero)
            messages.success(request, f'{rol.capitalize()} registrado correctamente.')

    empleados = User.objects.filter(is_superuser=False)
    perfiles = PerfilUsuario.objects.filter(user__in=empleados)
    empleados_info = [
        {
            'username': e.username,
            'email': e.email,
            'nombre': e.first_name,
            'rut': perfiles.get(user=e).rut if perfiles.filter(user=e).exists() else '',
            'fecha_nacimiento': perfiles.get(user=e).fecha_nacimiento if perfiles.filter(user=e).exists() else '',
            'genero': perfiles.get(user=e).genero if perfiles.filter(user=e).exists() else '',
            'rol': perfiles.get(user=e).rol if perfiles.filter(user=e).exists() else '',
            'id': e.id,
        } for e in empleados
    ]

    eliminados = EmpleadoEliminado.objects.all()

    return render(request, 'empleado.html', {
        'empleados': empleados_info,
        'empleados_eliminados': eliminados
    })

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

@login_required
def cajero(request):
    productos = Producto.objects.all()
    return render(request, 'cajero.html', {'productos': productos})

@login_required
def bodeguero(request):
    productos = Producto.objects.all()
    return render(request, 'bodega.html', {'productos': productos})

@login_required
def vendedor(request):
    productos = Producto.objects.all()
    return render(request, 'vendedor.html', {'productos': productos})

@csrf_exempt
def eliminar_empleado(request, id):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            user = User.objects.get(id=id)
            perfil = PerfilUsuario.objects.get(user=user)

            EmpleadoEliminado.objects.create(
                username=user.username,
                email=user.email,
                nombre=perfil.user.first_name + " " + perfil.user.last_name,
                rut=perfil.rut,
                fecha_nacimiento=perfil.fecha_nacimiento,
                genero=perfil.genero,
            )

            perfil.delete()
            user.delete()

            return JsonResponse({
                'success': True,
                'usuario': {
                    'username': user.username,
                    'email': user.email,
                    'nombre': perfil.user.first_name + " " + perfil.user.last_name,
                    'rut': perfil.rut,
                    'fecha_nacimiento': perfil.fecha_nacimiento.strftime('%d/%m/%Y'),
                    'genero': perfil.genero,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido o cabecera incorrecta'}, status=400)
