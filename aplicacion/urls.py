# aplicacion/urls.py
from django.urls import path
from aplicacion import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('index_admin/', views.index_admin, name='index_admin'),
    path('index_empleado/', views.index_empleado, name='index_empleado'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)