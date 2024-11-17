from flask import Flask, render_template, request , redirect, url_for, flash # importar Flask, render_template, request, redirect, url_for, flash
from forms import ContactForm # importar ContactForm de forms.py
from flask_login import  LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy # importar SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your secret key' # clave secreta para la aplicacion
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Usamos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar el seguimiento de modificaciones (para evitar advertencias)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) 
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')" # Representación de la clase User
    
    def set_password(self, password): 
        self.password_hash = generate_password_hash(password) # Generar hash de la contraseña
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Task('{self.title}', '{self.date_created}')" 

@app.route('/tasks', methods=['GET'])
def list_tasks(): # Listar todas las tareas
    tasks = Task.query.all() # Obtener todas las tareas
    return render_template('tasks.html', tasks=tasks)

@app.route('/tasks/add', methods=['GET', 'POST'])
def add_task(): # Añadir una tarea
    if request.method == 'POST' :
        title = request.form['title']
        description = request.form['description']
        new_task = Task(title=title, description= description)
        db.session.add(new_task)
        db.session.commit()
        flash('Tarea añadida correctamente!', "success")
        return redirect(url_for('list_tasks')) # Redirigir a la lista de tareas
    return render_template('add_task.html')

@app.route('/tasks/update/<int:task_id>', methods=['GET', 'POST']) # Actualizar una tarea
def update_task(task_id):
    if request.method == 'POST':
        "Actualizar tarea existente"
        task = Task.query.get(task_id)
        task.title = request.form['title']
        task.description = request.form['description']
        db.session.commit()# Guardar los cambios
        flash('Tarea actualizada correctamente!', 'success')
        return(redirect(url_for('list_tasks')))
    task = Task.query.get_or_404(task_id)# Obtener la tarea a actualizar
    return render_template('update_task.html', task=task) 
        
@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)# Obtener la tarea a eliminar
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada correctamente!', 'success')
    return redirect(url_for('list_tasks'))
        
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404  # Devolver una página personalizada 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500  # Página personalizada 500

@app.route('/')
def home():
    return "¡Hola, Flask! Soy harti."
 
@app.route('/about')
def about(): 
    return "Este es el about de mi aplicacion" # crear ruta hacia pagina about 

@app.route('/form', methods=['GET', 'POST']) #crear ruta hacia pagina form
def form():
    form = ContactForm() 
    if form.validate_on_submit():# si el formulario es valido
        name = form.name.data
        email = form.email.data
        flash(f'Hola {name}!, con correo {email} tu formulario ha sido enviado con éxito')
        return redirect(url_for('submit', name= name, email = email))# redirigir a la pagina submit con el nombre y el correo
    return render_template('form.html', form=form) # retornar el template form.html
@app.route('/submit', methods=['GET','POST']) # crear ruta hacia pagina submit
def submit():
    if request.method == 'POST': 
        name = request.form['name'] # Usamos POST si es un formulario
        email = request.form['email']
        return f'Hola {name}!, con correo {email} tu formulario ha sido enviado con éxito'
    else:
        name = request.args.get('name')  # Usamos GET si es una redirección
        email = request.args.get('email')
        return f'Hola {name}!, con correo {email} tu formulario ha sido enviado con éxito'



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
    
