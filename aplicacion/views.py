from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive  # ✅ IMPORTANTE

import json
from datetime import timedelta

from .models import (
    Producto,
    Movimiento,
    PerfilUsuario,
    EmpleadoEliminado,
    VentaCajero,
    MovimientoBodega,
    BoletaCliente,
    BoletaItem
)

carritos_guardados = {}

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
                    # 👇 Esto limpia automáticamente el rol temporal si ya venció
                    rol = perfil.get_rol_actual()

                    if rol == 'vendedor':
                        return redirect('vendedor')
                    elif rol == 'bodeguero':
                        return redirect('bodeguero')
                    elif rol == 'cajero':
                        return redirect('cajero')
                    else:
                        logout(request)
                        messages.error(request, "Rol no válido.")
                        return redirect('index')
                except PerfilUsuario.DoesNotExist:
                    messages.error(request, 'Perfil de usuario no encontrado.')
                    logout(request)
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
    movimientos_queryset = Movimiento.objects.select_related('producto', 'empleado').order_by('-fecha', '-hora')
    ventas_cajero = VentaCajero.objects.select_related('producto', 'cajero').order_by('-fecha', '-hora')
    movimientos_bodega_queryset = MovimientoBodega.objects.select_related('producto', 'empleado').order_by('-fecha', '-hora')

    movimientos = [{
        'producto': m.producto,
        'cantidad_vendida': m.cantidad_vendida,
        'fecha': m.fecha,
        'hora': m.hora,
        'nombre_empleado': m.empleado.get_full_name() or m.empleado.username
    } for m in movimientos_queryset]

    movimientos_bodega = [{
        'producto': b.producto,
        'agregado': b.agregado,
        'eliminado': b.eliminado,
        'fecha': b.fecha,
        'hora': b.hora,
        'nombre_empleado': b.empleado.get_full_name() or b.empleado.username
    } for b in movimientos_bodega_queryset]

    return render(request, 'index_admin.html', {
        'movimientos': movimientos,
        'ventas_cajero': ventas_cajero,
        'movimientos_bodega': movimientos_bodega
    })

def cerrar_sesion(request):
    logout(request)
    return redirect('index')

@login_required
def procesar_compra(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito = data.get('carrito', [])
            perfil = PerfilUsuario.objects.filter(user=request.user).first()

            for item in carrito:
                producto = Producto.objects.get(id=item['id'])
                cantidad = item['cantidad']

                if producto.cantidad >= cantidad:
                    producto.cantidad -= cantidad
                    producto.save()

                    if perfil and perfil.get_rol_actual() == 'vendedor':
                        Movimiento.objects.create(
                            producto=producto,
                            cantidad_vendida=cantidad,
                            empleado=request.user
                        )
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
        imagen = request.FILES.get('imagen')
        precio = request.POST.get('precio')
        cantidad = request.POST.get('cantidad')

        if nombre and imagen and precio and cantidad:
            Producto.objects.create(nombre=nombre, imagen=imagen, precio=precio, cantidad=cantidad)
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
@login_required
def update_stock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = int(data.get('cantidad', 0))

            producto = Producto.objects.get(id=producto_id)

            # Verifica si el usuario es superusuario
            if request.user.is_superuser:
                producto.cantidad += cantidad
                producto.save()
                return JsonResponse({'success': True, 'nuevo_stock': producto.cantidad})

            # Si no es superusuario, asume que es bodeguero
            perfil = PerfilUsuario.objects.get(user=request.user)
            if cantidad > 0:
                producto.cantidad += cantidad
                MovimientoBodega.objects.create(
                    producto=producto,
                    agregado=cantidad,
                    eliminado=0,
                    empleado=request.user
                )
            elif cantidad < 0 and producto.cantidad >= abs(cantidad):
                producto.cantidad += cantidad
                MovimientoBodega.objects.create(
                    producto=producto,
                    agregado=0,
                    eliminado=abs(cantidad),
                    empleado=request.user
                )
            else:
                return JsonResponse({'success': False, 'error': 'Cantidad inválida o insuficiente.'})

            producto.save()
            return JsonResponse({'success': True, 'nuevo_stock': producto.cantidad})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@csrf_exempt
@login_required
def eliminar_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto = Producto.objects.get(id=data['id'])
            perfil = PerfilUsuario.objects.filter(user=request.user, rol='bodeguero').first()
            if perfil:
                MovimientoBodega.objects.create(
                    producto=producto,
                    agregado=0,
                    eliminado=producto.cantidad,
                    empleado=request.user
                )
            producto.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def cajero(request):
    codigo = request.GET.get("codigo")
    carrito = []
    total_general = 0

    if codigo and codigo != 'None':
        session = carritos_guardados.get(codigo, {})
        carrito = session.get('carrito', []) if isinstance(session, dict) else []
        total_general = sum(item['precio'] * item['cantidad'] for item in carrito)
        for item in carrito:
            item['total'] = item['precio'] * item['cantidad']
            item['nombre'] = item.get('nombre', item.get('name'))
            item['imagen_url'] = item.get('imagen_url', item.get('img'))

    return render(request, 'cajero.html', {
        'carrito': carrito,
        'total_general': total_general,
        'codigo': codigo
    })


@login_required
@user_passes_test(lambda u: PerfilUsuario.objects.filter(user=u, rol='bodeguero').exists())
def bodeguero(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        imagen = request.FILES.get('imagen')
        precio = request.POST.get('precio')
        cantidad = request.POST.get('cantidad')

        if nombre and imagen and precio and cantidad:
            Producto.objects.create(nombre=nombre, imagen=imagen, precio=precio, cantidad=cantidad)
            messages.success(request, "Producto agregado correctamente.")
            return redirect('bodeguero')

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

@csrf_exempt
@login_required
def guardar_carrito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = str(data.get('codigo'))
            carrito = data.get('carrito', [])

            # Guardar también el ID del vendedor actual
            carritos_guardados[codigo] = {
                'carrito': carrito,
                'vendedor_id': request.user.id
            }
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def boleta(request, codigo):
    session = carritos_guardados.get(codigo, {})
    carrito = session.get('carrito', []) if isinstance(session, dict) else []
    for item in carrito:
        item['nombre'] = item.get('nombre', item.get('name'))
        item['imagen_url'] = item.get('imagen_url', item.get('img'))
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render(request, 'boleta.html', {
        'carrito': carrito,
        'codigo': codigo,
        'total': total
    })


@login_required
def confirmar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo')
            session = carritos_guardados.pop(codigo, None)

            if not session:
                return JsonResponse({'success': False, 'error': 'Carrito no encontrado'})

            carrito = session['carrito']
            vendedor_id = session.get('vendedor_id')
            vendedor_user = User.objects.filter(id=vendedor_id).first()
            perfil = PerfilUsuario.objects.filter(user=request.user).first()

            total = 0
            for item in carrito:
                total += item['precio'] * item['cantidad']

            boleta = BoletaCliente.objects.create(
                codigo=codigo,
                total=total,
                cajero=request.user if perfil and perfil.get_rol_actual() == 'cajero' else None
            )

            for item in carrito:
                producto = Producto.objects.get(id=item['id'])
                cantidad = item['cantidad']

                if producto.cantidad < cantidad:
                    return JsonResponse({'success': False, 'error': f'Stock insuficiente para {producto.nombre}'})

                producto.cantidad -= cantidad
                producto.save()

                if perfil and perfil.get_rol_actual() == 'cajero' and vendedor_user:
                    Movimiento.objects.create(
                        producto=producto,
                        cantidad_vendida=cantidad,
                        empleado=vendedor_user
                    )
                    VentaCajero.objects.create(
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=item['precio'],
                        total_venta=item['precio'] * cantidad,
                        cajero=request.user
                    )

                BoletaItem.objects.create(
                    boleta=boleta,
                    producto=producto,
                    nombre=item.get('nombre', producto.nombre),
                    precio=item['precio'],
                    cantidad=cantidad
                )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def boleta_cliente(request, codigo):
    try:
        boleta = BoletaCliente.objects.get(codigo=codigo)
        items = BoletaItem.objects.filter(boleta=boleta)
        return render(request, 'boleta_cliente.html', {
            'carrito': items,
            'codigo': boleta.codigo,
            'total': boleta.total
        })
    except BoletaCliente.DoesNotExist:
        return render(request, 'boleta_cliente.html', {
            'carrito': [],
            'codigo': codigo,
            'total': 0
        })



@login_required
@user_passes_test(lambda u: u.is_superuser)
def modificar_rol(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        nuevo_rol = request.POST.get('rol')
        try:
            usuario = User.objects.get(id=user_id)
            perfil = PerfilUsuario.objects.get(user=usuario)
            perfil.rol = nuevo_rol
            perfil.save()
            messages.success(request, 'Rol actualizado correctamente.')
        except (User.DoesNotExist, PerfilUsuario.DoesNotExist):
            messages.error(request, 'Error al actualizar el rol.')

    usuarios = User.objects.filter(is_superuser=False)
    perfiles = PerfilUsuario.objects.filter(user__in=usuarios)
    empleados_info = []
    for usuario in usuarios:
        perfil = perfiles.filter(user=usuario).first()
        empleados_info.append({
            'id': usuario.id,
            'username': usuario.username,
            'nombre': usuario.first_name,
            'rol': perfil.rol if perfil else 'Sin rol'
        })

    return render(request, 'modificar_rol.html', {'empleados': empleados_info})


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser)
def modificar_rol_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("usuario")
            nuevo_rol = data.get("nuevo_rol")
            es_temporal = data.get("temporal", False)

            user = User.objects.get(username=username)
            perfil = PerfilUsuario.objects.get(user=user)

            if es_temporal:
                inicio = parse_datetime(data.get("inicio"))
                fin = parse_datetime(data.get("fin"))

                if not inicio or not fin or inicio >= fin:
                    return JsonResponse({"success": False, "error": "Fechas inválidas"})

                if is_naive(inicio):
                    inicio = make_aware(inicio)
                if is_naive(fin):
                    fin = make_aware(fin)

                perfil.rol_temporal = nuevo_rol
                perfil.inicio_temporal = inicio
                perfil.fin_temporal = fin
            else:
                perfil.rol = nuevo_rol
                perfil.rol_temporal = None
                perfil.inicio_temporal = None
                perfil.fin_temporal = None

            perfil.save()
            return JsonResponse({"success": True})

        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Usuario no encontrado"})
        except PerfilUsuario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Perfil de usuario no encontrado"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser)
def modificar_rol_lista_usuarios(request):
    if request.method == "GET":
        rol = request.GET.get("rol")
        if rol not in ["vendedor", "bodeguero", "cajero"]:
            return JsonResponse({"success": False, "error": "Rol no válido"})

        perfiles = PerfilUsuario.objects.filter(rol=rol).select_related('user')
        usuarios = [{
            "username": p.user.username,
            "nombre": p.user.first_name or p.user.username,
            "rol": p.rol
        } for p in perfiles]

        return JsonResponse({"success": True, "usuarios": usuarios})

    return JsonResponse({"success": False, "error": "Método no permitido"})


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser)
def asignar_rol_temporal(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("usuario")
            nuevo_rol = data.get("nuevo_rol")
            duracion = int(data.get("duracion"))  # en horas

            user = User.objects.get(username=username)
            perfil = PerfilUsuario.objects.get(user=user)

            perfil.rol_temporal = nuevo_rol
            perfil.vencimiento_rol_temporal = timezone.now() + timedelta(hours=duracion)
            perfil.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Método no permitido"})



@csrf_exempt
@login_required
def modificar_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            nuevo_nombre = data.get('nuevo_nombre')
            nuevo_precio = data.get('nuevo_precio')
            nuevo_cantidad = data.get('nuevo_cantidad')

            if not producto_id:
                return JsonResponse({'success': False, 'error': 'ID de producto no proporcionado'})

            producto = Producto.objects.get(id=producto_id)
            cantidad_anterior = producto.cantidad

            # Actualiza campos si vienen
            if nuevo_nombre:
                producto.nombre = nuevo_nombre
            if nuevo_precio:
                producto.precio = float(nuevo_precio)
            if nuevo_cantidad is not None:
                producto.cantidad = int(nuevo_cantidad)

            producto.save()

            # Registra movimiento de bodega solo si cambia la cantidad
            if nuevo_cantidad is not None and int(nuevo_cantidad) != cantidad_anterior:
                diferencia = int(nuevo_cantidad) - cantidad_anterior
                agregado = diferencia if diferencia > 0 else 0
                eliminado = abs(diferencia) if diferencia < 0 else 0

                # ✅ Solo registrar movimiento si es superuser o bodeguero
                if request.user.is_superuser or PerfilUsuario.objects.filter(user=request.user, rol='bodeguero').exists():
                    MovimientoBodega.objects.create(
                        producto=producto,
                        agregado=agregado,
                        eliminado=eliminado,
                        fecha=timezone.now().date(),
                        hora=timezone.now().time(),
                        empleado=request.user
                    )

            return JsonResponse({'success': True})

        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'})