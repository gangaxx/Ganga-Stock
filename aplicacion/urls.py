from django.urls import path
from aplicacion import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.index_admin, name='index_admin'),
    path('empleado/', views.vendedor, name='vendedor'),
    path('index_admin/', views.index_admin, name='index_admin'),
    path('index_empleado/', views.vendedor, name='vendedor'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    path('inventario/', views.inventario, name='inventario'),
    path('admin_empleado/', views.empleado, name='empleado'),

    path('cajero/', views.cajero, name='cajero'),
    path('bodega/', views.bodeguero, name='bodega'),

    path('update_stock/', views.update_stock, name='update_stock'),
    path('eliminar_producto/', views.eliminar_producto, name='eliminar_producto'),

    # Nueva ruta para eliminar empleados
    path('eliminar_empleado/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
