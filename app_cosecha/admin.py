from django.contrib import admin
from .models import (
    Rol, 
    UsuarioPerfil, 
    Parcela, 
    Material, 
    ProductoTerminado,  # <-- Nuevo
    RecetaMaterial,     # <-- Nuevo
    RegistroCosecha, 
    MovimientoInventario
)

# Clase especial para mostrar la Receta "dentro" del Producto
class RecetaMaterialInline(admin.TabularInline):
    model = RecetaMaterial
    extra = 1  # Muestra 1 campo vacío para añadir

# Clase especial para el admin de Producto Terminado
class ProductoTerminadoAdmin(admin.ModelAdmin):
    inlines = [RecetaMaterialInline] # Pone la receta dentro del producto

# Registra tus modelos para que aparezcan en el panel de admin
admin.site.register(Rol)
admin.site.register(UsuarioPerfil)
admin.site.register(Parcela)
admin.site.register(Material)
admin.site.register(RegistroCosecha)
admin.site.register(MovimientoInventario)

# Registra los nuevos modelos con su admin especial
admin.site.register(ProductoTerminado, ProductoTerminadoAdmin)
admin.site.register(RecetaMaterial) # Opcional, para verlo por separado