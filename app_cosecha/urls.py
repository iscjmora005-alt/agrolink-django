from django.urls import path
from . import views  # Importaremos las vistas (lógica) en el siguiente paso

urlpatterns = [
  path('login/', views.login_view, name='login'),
    path('registrar/', views.registrar_cosecha_view, name='registrar_cosecha'),
    path('logout/', views.logout_view, name='logout'),

    # --- AÑADE ESTA LÍNEA ---
    path('dashboard/', views.dashboard_admin_view, name='dashboard'), 

    path('', views.index_view, name='index'), 
]