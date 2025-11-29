from django.db import models
from django.contrib.auth.models import User

# --- Tablas de Catálogos (Se quedan igual) ---
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)
    def __str__(self): return self.nombre_rol

class UsuarioPerfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    nombre_completo = models.CharField(max_length=120)
    def __str__(self): return self.nombre_completo

class Parcela(models.Model):
    id_parcela = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    hectareas = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    def __str__(self): return self.nombre

# --- LÓGICA DE INVENTARIO (MODIFICADA SPRINT 4) ---

# 1. MATERIA PRIMA (Lo que compra el Almacenista)
class Material(models.Model):
    id_material = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120) # Ej. "Clamshell 6oz HEB", "Caja Cartón 12-pack", "Charola Merma"
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    def __str__(self): return self.nombre

# 2. PRODUCTO TERMINADO (Lo que cosecha el Supervisor)
class ProductoTerminado(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100) # Ej. "Caja Exportación 6oz (HEB)"
    def __str__(self): return self.nombre

# 3. RECETA (El "BOM" - La magia que conecta todo)
class RecetaMaterial(models.Model):
    # La "Caja Exportación 6oz" usa...
    producto_terminado = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE)
    # ... "Clamshell 6oz HEB"...
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    # ... en "cantidad 12".
    cantidad_requerida = models.IntegerField()

    def __str__(self):
        return f"{self.producto_terminado.nombre} usa {self.cantidad_requerida} de {self.material.nombre}"

# --- LÓGICA DE TRANSACCIONES ---

# 4. REGISTRO DE COSECHA (MODIFICADO)
class RegistroCosecha(models.Model):
    id_registro = models.BigAutoField(primary_key=True)
    # Se conecta al Producto Terminado
    producto_terminado = models.ForeignKey(ProductoTerminado, on_delete=models.PROTECT)
    cantidad = models.IntegerField() # Ej. 600 (cajas armadas)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    parcela = models.ForeignKey(Parcela, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.cantidad} de {self.producto_terminado.nombre} en {self.parcela.nombre}"

# 5. MOVIMIENTOS DE INVENTARIO (Se queda igual)
class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'), # Lo que hace el Almacenista
        ('SALIDA_COSECHA', 'Salida por Cosecha'), # Lo que calcula el sistema (BOM)
        ('SALIDA_MERMA', 'Salida por Merma'), # Lo que registra el Supervisor
    ]
    id_movimiento = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.tipo} - {self.material.nombre} - {self.cantidad}"
    
    