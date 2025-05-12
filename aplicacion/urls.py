from django.urls import path
from aplicacion import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.index_admin, name='index_admin'),
    path('empleado/', views.index_empleado, name='index_empleado'),
    path('index_admin/', views.index_admin, name='index_admin'),
    path('index_empleado/', views.index_empleado, name='index_empleado'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    path('inventario/', views.inventario, name='inventario'),
    path('admin_empleado/', views.empleado, name='empleado'),

    # ✅ Rutas necesarias para funciones del inventario
    path('update_stock/', views.update_stock, name='update_stock'),
    path('eliminar_producto/', views.eliminar_producto, name='eliminar_producto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
