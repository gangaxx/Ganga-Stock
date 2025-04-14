from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def index_admin(request):
    return render(request, 'index_admin.html')

# Create your views here.
