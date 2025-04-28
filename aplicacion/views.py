from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegistroEmpleadoForm


def index(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                ## lo que esta abajo en la linea de request fue agregago el 28/4/2025 es para que el nombre de usuario se guarde en la sesion y se pueda usar en el index_empleado (sea visible) eso xd
                request.session['nombre_usuario'] = user.username  # 👈 AGREGADO
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
    return render(request, 'index_empleado.html')


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
            ## lo que esta abajo en la linea de request fue agregago el 28/4/2025 es para que el nombre de usuario se guarde en la sesion y se pueda usar en el index_empleado (sea visible) eso xd
            request.session['nombre_usuario'] = user.username  # 👈 AGREGADO AQUÍ TAMBIÉN
            return redirect('index_empleado')
        else:
            messages.error(request, 'Credenciales inválidas o acceso no autorizado.')
    return render(request, 'index.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('index')
