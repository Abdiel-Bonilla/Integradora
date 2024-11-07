from flask_wtf import FlaskForm
from wtforms import StringField,SelectField, IntegerField, DecimalField,PasswordField, SubmitField,DateField,TimeField,FieldList,FormField
from wtforms.validators import DataRequired



class UsuariosForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    ape_pat = StringField('Apellido Paterno', validators=[DataRequired()])
    ape_mat = StringField('Apellido Materno', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('admin', 'Administrador'), ('cashier', 'Cajero')], validators=[DataRequired()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Agregar Usuario')

class ProductosForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    caducidad = DateField('Caducidad', format='%Y-%m-%d', validators=[DataRequired()])
    precio = DecimalField('Precio', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])  # Cambiado a StringField
    submit = SubmitField('Registrar Producto')
    cancel = SubmitField('Cancelar')

from wtforms import StringField, HiddenField

class VentaForm(FlaskForm):
    fecha = StringField('Fecha', render_kw={'readonly': True})
    hora = StringField('Hora', render_kw={'readonly': True})
    usuario = StringField('Usuario', render_kw={'readonly': True})  # Solo lectura
    producto = SelectField('Producto', choices=[], coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    submit = SubmitField('Registrar Venta')
    cancelar = SubmitField('Cancelar')

class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class CategoriaForm(FlaskForm):
    nombre_ca = StringField('Nombre de la Categoría', validators=[DataRequired()])
    submit = SubmitField('Guardar Categoría')