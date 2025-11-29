from django import forms
from django.contrib.auth.models import User
from .models import UsuarioPerfil, Rol
# Asegúrate de que todos estos modelos estén importados al inicio
from .models import RegistroCosecha, Parcela, ProductoTerminado, Material

# --- Formulario 1: Login (RF-1.1) ---
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nombre de Usuario'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Contraseña'
        })
    )

# --- Formulario 2: Registrar Cosecha (RF-2) - (VERSIÓN SPRINT 4) ---
class CosechaForm(forms.ModelForm):
    # --- Campos para la Cosecha (Producto Terminado) ---
    producto_terminado = forms.ModelChoiceField(
        queryset=ProductoTerminado.objects.all(),
        label="Producto Cosechado (Caja Armada)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # --- Campos EXTRA para la Merma (Materia Prima) ---
    # (Estos no están en el modelo 'RegistroCosecha', los manejaremos en la vista)
    merma_material = forms.ModelChoiceField(
        queryset=Material.objects.all(), # Muestra Clamshells, Charolas, etc.
        label="Material de Merma (Opcional)",
        required=False, # Hacemos que la merma sea opcional
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    merma_cantidad = forms.IntegerField(
        label="Cantidad de Merma (Opcional)",
        required=False,
        min_value=0,
        initial=0, # Valor por defecto
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RegistroCosecha
        # CAMBIAMOS 'tipo_fruta' por 'producto_terminado'
        # Solo incluimos los campos que SÍ están en el modelo
        fields = ['parcela', 'producto_terminado', 'cantidad']

        widgets = {
            'parcela': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. 600 (cajas armadas)'
            }),
        }

# --- Formulario 3: Entrada de Inventario (RF-3.2) ---
class EntradaInventarioForm(forms.Form):
    # Un dropdown para seleccionar el material
    material = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        label="Material que ingresa",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Un campo para la cantidad
    cantidad = forms.IntegerField(
        label="Cantidad que ingresa",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. 500'
        })
        
    )
    # --- Formulario 4: Gestión de Parcelas (Admin) ---
class ParcelaForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = ['nombre', 'ubicacion', 'hectareas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'hectareas': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# --- Formulario 5: Crear Usuario (Admin) ---
# Este formulario crea el User de Django
class CrearUsuarioForm(forms.ModelForm):
    # Hacemos que la contraseña use PasswordInput
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        # Pedimos los campos básicos para el login
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# --- Formulario 6: Asignar Rol (Admin) ---
# Este formulario crea/edita nuestro UsuarioPerfil
class UsuarioPerfilForm(forms.ModelForm):
    # Un dropdown para seleccionar el Rol (Admin, Supervisor, Almacenista)
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = UsuarioPerfil
        fields = ['rol', 'nombre_completo']
        widgets = {
             'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
        }