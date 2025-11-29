from django.urls import path
from . import views 

urlpatterns = [
    # Vistas de autenticación y principales
    path('', views.index_view, name='index'), # La ruta raíz/index
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Vistas por Rol
    path('dashboard/', views.dashboard_admin_view, name='dashboard'), # Admin
    path('registrar/', views.registrar_cosecha_view, name='registrar_cosecha'), # Supervisor
    path('inventario/entrada/', views.registrar_entrada_view, name='registrar_entrada'), # Almacenista

    # Vistas de Gestión (CRUD) para Parcelas (Sprint 5)
    path('gestion/parcelas/', views.lista_parcelas_view, name='lista_parcelas'),
    path('gestion/parcelas/crear/', views.crear_parcela_view, name='crear_parcela'),
    path('gestion/parcelas/editar/<int:pk>/', views.editar_parcela_view, name='editar_parcela'),
    path('gestion/parcelas/borrar/<int:pk>/', views.borrar_parcela_view, name='borrar_parcela'),
    path('gestion/usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
path('gestion/usuarios/crear/', views.crear_usuario_view, name='crear_usuario'),
path('gestion/usuarios/editar/<int:pk>/', views.editar_usuario_view, name='editar_usuario'),
path('gestion/usuarios/borrar/<int:pk>/', views.borrar_usuario_view, name='borrar_usuario'),
path('gestion/rendimiento/', views.rendimiento_parcelas_view, name='rendimiento_parcelas'),

path('', views.index_view, name='index'), 

path('gestion/home/', views.admin_home_view, name='admin_home'),
]
