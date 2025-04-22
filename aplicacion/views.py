from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

def index(request):
    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            # Login
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('index_admin')
                else:
                    return redirect('index_empleado')
            else:
                messages.error(request, 'Credenciales inválidas.')

        elif 'username' in request.POST and 'password1' in request.POST and 'password2' in request.POST:
            # Registro
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 == password2:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'El usuario ya existe.')
                else:
                    User.objects.create_user(username=username, password=password1)
                    messages.success(request, 'Cuenta creada correctamente. Ahora puedes iniciar sesión.')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')

    return render(request, 'index.html')

def index_admin(request):
    return render(request, 'index_admin.html')

def index_empleado(request):
    return render(request, 'index_empleado.html')
