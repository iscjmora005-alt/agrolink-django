from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, CosechaForm # Crearemos estos formularios después
from .models import RegistroCosecha, Parcela, Material
from django.utils import timezone
from django.db.models import Sum
from .models import RegistroCosecha, Material, UsuarioPerfil, Rol
from django.db import models
# (Asegúrate de que 'Sum' esté importado de django.db.models al inicio del archivo)

@login_required(login_url='login')
def dashboard_admin_view(request):
    # 1. Asegurarnos de que solo el admin entre (¡Mejora de seguridad!)
    #    (Asumimos que el 'rol_id' 1 es Administrador, ajústalo si es necesario)
    try:
        # Revisa si el usuario logueado tiene un perfil y si su rol es el 1
        if not request.user.usuarioperfil.rol.id_rol == 1:
            # Si no es admin, lo sacamos al login
            return redirect('login')
    except:
         # Si tiene un error (ej. no tiene perfil), lo sacamos
        return redirect('login')

    hoy = timezone.now().date()

   # 2. KPI 1: Cajas cosechadas hoy (RF-4.2)
    cajas_hoy = RegistroCosecha.objects.filter(fecha_hora__date=hoy) \
                                  .aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    # 3. KPI 2: Alertas de inventario (RF-3.7)
    alertas_stock = Material.objects.filter(stock_actual__lte=models.F('stock_minimo'))

    # 4. KPI 3: Cosecha reciente
    cosechas_recientes = RegistroCosecha.objects.all().order_by('-fecha_hora')[:5] # Últimas 5

    context = {
       'cajas_cosechadas_hoy': cajas_hoy,
        'alertas_de_stock': alertas_stock,
        'cosechas_recientes': cosechas_recientes,
        'nombre_usuario': request.user.username, # Para saludarlo
    }
    return render(request, 'app_cosecha/dashboard.html', context)
# --- VISTA 4: PÁGINA DE INICIO (INDEX) ---
# La vista más simple, solo muestra una página de bienvenida o redirige.
def index_view(request):
    # Si el usuario está logueado, lo mandamos a registrar cosecha.
    if request.user.is_authenticated:
        return redirect('registrar_cosecha')
    # Si no, lo mandamos al login.
    return redirect('login')

# --- VISTA 1: LOGIN (RF-1.1) ---
# Esta es la 'login_view' que faltaba y causaba el error.
def login_view(request):
    # Si el usuario ya está logueado, que no vea el login de nuevo
    if request.user.is_authenticated:
        return redirect('registrar_cosecha')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Redirigir al supervisor a la página de registro
                return redirect('registrar_cosecha')
            else:
                # Si el usuario es nulo, el login falló
                form.add_error(None, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
        
    return render(request, 'app_cosecha/login.html', {'form': form})

# --- VISTA 3: LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- VISTA 2: REGISTRAR COSECHA (RF-2) ---
# Esta es la 'registrar_cosecha_view' que también faltaba.
@login_required(login_url='login') # Protege la vista, si no estás logueado, te manda a 'login'
def registrar_cosecha_view(request):
    if request.method == 'POST':
        form = CosechaForm(request.POST)
        if form.is_valid():
            # El formulario es válido, guardamos la cosecha
            registro = form.save(commit=False)
            registro.usuario = request.user # Asigna el supervisor que está logueado
            registro.save()
            
            # (Aquí iría la lógica para descontar de inventario RF-3.4)
            # ...
            
            # Redirigimos a la misma página para que pueda registrar de nuevo
            return redirect('registrar_cosecha')
    else:
        # Si no es POST, es un GET, así que solo mostramos el formulario vacío
        form = CosechaForm()
        
    # También obtenemos los materiales para mostrarlos (RF-3.5)
    materiales = Material.objects.all()
    
    context = {
        'form': form,
        'materiales': materiales
    }
    
    return render(request, 'app_cosecha/registrar_cosecha.html', context)