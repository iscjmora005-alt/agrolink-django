from django.db import models
from django.contrib.auth.models import User # Usaremos el User de Django

# Tu tabla 'roles'
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol

# Tu tabla 'usuarios', conectada al Rol
class UsuarioPerfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    nombre_completo = models.CharField(max_length=120)
    
    def __str__(self):
        return self.nombre_completo

# Tu tabla 'parcelas'
class Parcela(models.Model):
    id_parcela = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    hectareas = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nombre

# Tu tabla 'materiales'
class Material(models.Model):
    id_material = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

# Tu tabla 'registros_cosecha'
class RegistroCosecha(models.Model):
    id_registro = models.BigAutoField(primary_key=True)
    cantidad = models.IntegerField()
    tipo_fruta = models.CharField(max_length=60)
    fecha_hora = models.DateTimeField(auto_now_add=True) # auto_now_add pone la fecha actual
    usuario = models.ForeignKey(User, on_delete=models.PROTECT) # Relación con el Supervisor
    parcela = models.ForeignKey(Parcela, on_delete=models.PROTECT) # Relación con la Parcela

    def __str__(self):
        return f"Cosecha de {self.tipo_fruta} - {self.cantidad} - {self.fecha_hora.date()}"

# Tu tabla 'movimientos_inventario'
class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]
    id_movimiento = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.tipo} - {self.material.nombre} - {self.cantidad}"