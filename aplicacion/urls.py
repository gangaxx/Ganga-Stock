from django.urls import path
from aplicacion import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.index_admin, name='index_admin'),  # Alias accesible como /admin/
    path('empleado/', views.index_empleado, name='index_empleado'),  # Alias accesible como /empleado/
    path('index_admin/', views.index_admin, name='index_admin'),  # Alias alternativo
    path('index_empleado/', views.index_empleado, name='index_empleado'),  # Alias alternativo
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
