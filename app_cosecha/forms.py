from django import forms
from .models import RegistroCosecha, Parcela

# --- Formulario 1: Login (RF-1.1) ---
# Este es un formulario simple, no está conectado a un modelo.
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

# --- Formulario 2: Registrar Cosecha (RF-2) ---
# Este es un ModelForm, Django lo construye automáticamente
# a partir de tu modelo 'RegistroCosecha'.
class CosechaForm(forms.ModelForm):

    # Hacemos que el campo 'parcela' sea un dropdown (select)
    # que se llena con las parcelas de la base de datos.
    parcela = forms.ModelChoiceField(
        queryset=Parcela.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RegistroCosecha

        # Especifica los campos del modelo que queremos en el formulario
        fields = ['parcela', 'tipo_fruta', 'cantidad']

        # Añade atributos HTML (como clases de Bootstrap) para que se vea bien
        widgets = {
            'tipo_fruta': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. Frambuesa Exportación'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. 150'
            }),
        }