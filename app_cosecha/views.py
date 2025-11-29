from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.db import models
from .forms import LoginForm, CosechaForm, EntradaInventarioForm, ParcelaForm
from .models import (
    RegistroCosecha, Material, UsuarioPerfil, Rol, 
    MovimientoInventario, Parcela, ProductoTerminado, RecetaMaterial
)
from django.contrib.auth.models import User
from .forms import CrearUsuarioForm, UsuarioPerfilForm
from django.contrib import messages
# --- VISTA 4: PÁGINA DE INICIO (INDEX) ---

# Asegúrate de que UsuarioPerfil esté importado al inicio del archivo:
# from .models import UsuarioPerfil

def index_view(request):
    if request.user.is_authenticated:
        # --- Lógica de Redirección por Rol (SPRINT 5) ---
        try:
            # 1. Buscamos el perfil del usuario que inició sesión
            perfil = request.user.usuarioperfil
            rol_id = perfil.rol.id_rol

            # 2. Verificamos el ID del Rol
            # (Asumimos 1=Admin. Verifica el ID en tu /admin/ Rols)
            if rol_id == 1: 
                return redirect('admin_home')

            # (Asumimos 2=Supervisor. Verifica el ID)
            elif rol_id == 2: 
                return redirect('registrar_cosecha')

            # (Asumimos 3=Almacenista. Verifica el ID)
            elif rol_id == 3: 
                return redirect('registrar_entrada')

            else:
                # Si es otro rol (ej. 4=Jornalero), lo mandamos a registrar
                return redirect('registrar_cosecha')

        except UsuarioPerfil.DoesNotExist:
             # Si es superusuario pero no tiene perfil, lo mandamos al dashboard
             if request.user.is_superuser:
                 return redirect('dashboard')
             # Si es un usuario normal sin perfil, lo sacamos
             return redirect('login')
        except AttributeError:
             # Esto pasa si el usuario es superusuario pero no tiene perfil
             if request.user.is_superuser:
                 return redirect('dashboard')
             return redirect('login')

    # Si no está autenticado, siempre al login
    return redirect('login')

# --- VISTA 1: LOGIN (RF-1.1) ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('index') # Redirige al index, que decidirá a dónde ir
            else:
                form.add_error(None, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
        
    return render(request, 'app_cosecha/login.html', {'form': form})

# --- VISTA 3: LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- VISTA 2: REGISTRAR COSECHA (RF-2) ---
@login_required(login_url='login') 
def registrar_cosecha_view(request):
    if request.method == 'POST':
        form = CosechaForm(request.POST)
        if form.is_valid():

            # --- 1. DATOS DE LA COSECHA (PRODUCTO TERMINADO) ---
            producto_cosechado = form.cleaned_data['producto_terminado']
            cantidad_cosechada = form.cleaned_data['cantidad']

            # Guarda el registro principal de la cosecha
            registro = form.save(commit=False)
            registro.usuario = request.user 
            registro.save()

            # --- 2. LÓGICA DE RECETA (BOM) - (DESCUENTA MATERIALES POR COSECHA) ---
            # Busca la receta para este producto
            receta = RecetaMaterial.objects.filter(producto_terminado=producto_cosechado)

            for item_receta in receta:
                material = item_receta.material
                cantidad_a_descontar = item_receta.cantidad_requerida * cantidad_cosechada

                # Descuenta el stock del material
                material.stock_actual -= cantidad_a_descontar
                material.save()

                # Registra el movimiento de salida
                MovimientoInventario.objects.create(
                    tipo='SALIDA_COSECHA',
                    cantidad=cantidad_a_descontar,
                    material=material,
                    usuario=request.user
                )

            # --- 3. LÓGICA DE MERMA (DESCUENTA MATERIAL DE MERMA) ---
            merma_material = form.cleaned_data.get('merma_material')
            merma_cantidad = form.cleaned_data.get('merma_cantidad')

            if merma_material and merma_cantidad and merma_cantidad > 0:
                # Descuenta el stock del material de merma
                merma_material.stock_actual -= merma_cantidad
                merma_material.save()

                # Registra el movimiento de merma
                MovimientoInventario.objects.create(
                    tipo='SALIDA_MERMA',
                    cantidad=merma_cantidad,
                    material=merma_material,
                    usuario=request.user
                )
            messages.success(request, f'Cosecha de {registro.cantidad} cajas registrada correctamente.')
            return redirect('registrar_cosecha')
        
    else:
        form = CosechaForm()

    materiales = Material.objects.all()
    context = {
        'form': form,
        'materiales': materiales
    }
    return render(request, 'app_cosecha/registrar_cosecha.html', context)
# --- VISTA 5: DASHBOARD ADMIN ---
@login_required(login_url='login')
def dashboard_admin_view(request):
    try:
        # Asumimos 1=Admin. Verifica el ID en tu /admin/
        if not request.user.usuarioperfil.rol.id_rol == 1: 
            return redirect('registrar_cosecha')
    except UsuarioPerfil.DoesNotExist:
        return redirect('registrar_cosecha')
    except AttributeError:
        # Esto pasa si el usuario es superusuario pero no tiene perfil
        return redirect('registrar_cosecha')

    hoy = timezone.now().date()
    
    # KPI 1: Cajas cosechadas hoy (RF-4.2)
    cajas_hoy = RegistroCosecha.objects.filter(fecha_hora__date=hoy) \
                                      .aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    # KPI 2: Alertas de inventario (RF-3.7)
    alertas_stock = Material.objects.filter(stock_actual__lte=models.F('stock_minimo'))

    # KPI 3: Cosecha reciente
    cosechas_recientes = RegistroCosecha.objects.all().order_by('-fecha_hora')[:5] 

    context = {
        'cajas_cosechadas_hoy': cajas_hoy,
        'alertas_de_stock': alertas_stock,
        'cosechas_recientes': cosechas_recientes,
        'nombre_usuario': request.user.username,
    }
    return render(request, 'app_cosecha/dashboard.html', context)

# --- VISTA 6: REGISTRAR ENTRADA DE INVENTARIO (ALMACENISTA) ---
@login_required(login_url='login')
def registrar_entrada_view(request):
    # (Aquí falta la seguridad de rol, pero funcionará por ahora)
    
    if request.method == 'POST':
        form = EntradaInventarioForm(request.POST)
        if form.is_valid():
            material = form.cleaned_data['material']
            cantidad = form.cleaned_data['cantidad']
            
            # 1. Aumentar el stock
            material.stock_actual += cantidad
            material.save()
            
            # 2. Crear el registro del movimiento
            MovimientoInventario.objects.create(
                tipo='ENTRADA',
                cantidad=cantidad,
                material=material,
                usuario=request.user
            )
           
            return redirect('registrar_entrada')
    else:
        form = EntradaInventarioForm()

    movimientos_recientes = MovimientoInventario.objects.filter(tipo='ENTRADA').order_by('-fecha_hora')[:5]
    context = {
        'form': form,
        'movimientos_recientes': movimientos_recientes
    }
    return render(request, 'app_cosecha/registrar_entrada.html', context)
# ... (al final del archivo) ...

# --- VISTAS CRUD DE PARCELAS (SPRINT 5) ---
# (Aquí deberíamos añadir un decorador de seguridad @admin_required)
from django.shortcuts import get_object_or_404
# 1. READ (Listar)
@login_required(login_url='login')
def lista_parcelas_view(request):
    parcelas = Parcela.objects.all()
    return render(request, 'app_cosecha/admin_parcelas/lista_parcelas.html', {'parcelas': parcelas})

# 2. CREATE (Crear)
@login_required(login_url='login')
def crear_parcela_view(request):
    if request.method == 'POST':
        form = ParcelaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_parcelas')
    else:
        form = ParcelaForm()
    return render(request, 'app_cosecha/admin_parcelas/form_parcela.html', {'form': form, 'accion': 'Crear'})

# 3. UPDATE (Editar)
@login_required(login_url='login')
def editar_parcela_view(request, pk):
    parcela = get_object_or_404(Parcela, pk=pk)
    if request.method == 'POST':
        form = ParcelaForm(request.POST, instance=parcela)
        if form.is_valid():
            form.save()
            return redirect('lista_parcelas')
    else:
        form = ParcelaForm(instance=parcela)
    return render(request, 'app_cosecha/admin_parcelas/form_parcela.html', {'form': form, 'accion': 'Editar'})

# 4. DELETE (Borrar)
@login_required(login_url='login')
def borrar_parcela_view(request, pk):
    parcela = get_object_or_404(Parcela, pk=pk)
    if request.method == 'POST':
        parcela.delete()
        return redirect('lista_parcelas')
    # Si es GET, mostramos una confirmación
    return render(request, 'app_cosecha/admin_parcelas/confirmar_borrar.html', {'objeto': parcela})
# --- VISTAS CRUD DE USUARIOS (SPRINT 5) ---
# (Aquí también deberíamos añadir un decorador @admin_required)

# 1. READ (Listar)
@login_required(login_url='login')
def lista_usuarios_view(request):
    perfiles = UsuarioPerfil.objects.all()
    return render(request, 'app_cosecha/admin_usuarios/lista_usuarios.html', {'perfiles': perfiles})

# 2. CREATE (Crear)
@login_required(login_url='login')
def crear_usuario_view(request):
    if request.method == 'POST':
        user_form = CrearUsuarioForm(request.POST)
        perfil_form = UsuarioPerfilForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid():
            # --- Guardamos el User ---
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password']) # Encripta la contraseña
            user.save()
            
            # --- Guardamos el Perfil y lo conectamos al User ---
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user # ¡La conexión clave!
            perfil.save()
            
            return redirect('lista_usuarios')
    else:
        user_form = CrearUsuarioForm()
        perfil_form = UsuarioPerfilForm()
        
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'accion': 'Crear'
    }
    return render(request, 'app_cosecha/admin_usuarios/form_usuario.html', context)

# 3. UPDATE (Editar Rol)
@login_required(login_url='login')
def editar_usuario_view(request, pk):
    perfil = get_object_or_404(UsuarioPerfil, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios')
    else:
        form = UsuarioPerfilForm(instance=perfil)
        
    context = {
        'perfil_form': form, 
        'user_form': None, 
        'accion': 'Editar'
    }
    return render(request, 'app_cosecha/admin_usuarios/form_usuario.html', context)

# 4. DELETE (Borrar)
@login_required(login_url='login')
def borrar_usuario_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete() 
        return redirect('lista_usuarios')
    
    return render(request, 'app_cosecha/admin_usuarios/confirmar_borrar_usuario.html', {'objeto': user})

@login_required(login_url='login')
def rendimiento_parcelas_view(request):
    # --- LÓGICA PARA GRÁFICA (BI) ---
    # 1. Agrupamos por Parcela y sumamos cantidad
    datos_grafica = RegistroCosecha.objects.values('parcela__nombre').annotate(total=Sum('cantidad')).order_by('-total')

    # 2. Separamos en dos listas para Chart.js
    nombres_parcelas = []
    totales_cosecha = []

    for dato in datos_grafica:
        nombres_parcelas.append(dato['parcela__nombre'])
        totales_cosecha.append(dato['total'])

    # --- LÓGICA PARA TABLA DETALLADA ---
    # (La misma que tenías o una similar)
    rendimientos = RegistroCosecha.objects.values('parcela__nombre', 'fecha_hora__date').annotate(total_cajas=Sum('cantidad')).order_by('-fecha_hora__date')

    context = {
        'nombres_parcelas': nombres_parcelas, # Lista para el Eje X
        'totales_cosecha': totales_cosecha,   # Lista para el Eje Y
        'rendimientos': rendimientos
    }
    return render(request, 'app_cosecha/admin_reportes/rendimiento_parcelas.html', context)
@login_required(login_url='login')
def admin_home_view(request):
    # Seguridad básica
    if not request.user.usuarioperfil.rol.id_rol == 1:
        return redirect('index')

    return render(request, 'app_cosecha/admin_home.html')