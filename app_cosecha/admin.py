from django.contrib import admin
from .models import Rol, UsuarioPerfil, Parcela, Material, RegistroCosecha, MovimientoInventario

# Registra tus modelos para que aparezcan en el panel de admin
admin.site.register(Rol)
admin.site.register(UsuarioPerfil)
admin.site.register(Parcela)
admin.site.register(Material)
admin.site.register(RegistroCosecha)
admin.site.register(MovimientoInventario)