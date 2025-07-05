from django.urls import path
from aplicacion import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Página principal y autenticación
    path('', views.index, name='index'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),

    # Vistas principales según rol
    path('admin/', views.index_admin, name='index_admin'),
    path('index_admin/', views.index_admin, name='index_admin'),
    path('empleado/', views.vendedor, name='vendedor'),
    path('index_empleado/', views.vendedor, name='vendedor'),
    path('cajero/', views.cajero, name='cajero'),
    path('bodega/', views.bodeguero, name='bodeguero'),
    path('inventario/', views.inventario, name='inventario'),

    # Inventario y stock
    path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    path('update_stock/', views.update_stock, name='update_stock'),
    path('eliminar_producto/', views.eliminar_producto, name='eliminar_producto'),
    path('modificar_producto/', views.modificar_producto, name='modificar_producto'),  # ✅ Ruta para modificar producto

    # Empleados
    path('admin_empleado/', views.empleado, name='empleado'),
    path('eliminar_empleado/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),

    # Carrito y ventas
    path('guardar_carrito/', views.guardar_carrito, name='guardar_carrito'),
    path('boleta/<str:codigo>/', views.boleta, name='boleta'),
    path('confirmar_venta/', views.confirmar_venta, name='confirmar_venta'),
    path('boleta_cliente/<str:codigo>/', views.boleta_cliente, name='boleta_cliente'),

    # Roles
    path('modificar_rol/', views.modificar_rol, name='modificar_rol'),
    path('api/lista_usuarios_por_rol/', views.modificar_rol_lista_usuarios, name='modificar_rol_lista_usuarios'),
    path('api/modificar_rol/', views.modificar_rol_api, name='modificar_rol_api'),
    path('api/asignar_rol_temporal/', views.asignar_rol_temporal, name='asignar_rol_temporal'),

    path('exportar_excel/<str:tipo>/', views.exportar_excel, name='exportar_excel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
