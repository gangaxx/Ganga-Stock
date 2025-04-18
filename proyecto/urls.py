"""
URL configuration for proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('aplicacion.urls')),
    path('', TemplateView.as_view(template_name="aplicacion/index.html")),
    path('placamadre/', TemplateView.as_view(template_name="placamadre.html")),
    path('index_empleado/', TemplateView.as_view(template_name="index_empleado.html")),
]

## borrar si no sirve para las imagenes
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    ##respaldo  16/4/2025   urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)