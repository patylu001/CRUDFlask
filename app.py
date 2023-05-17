from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'mysecretkey'

## Set up the database
DATABASE_USER = 'root'
DATABASE_PASSWORD = '123456'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3307'
DATABASE_NAME = 'calificaciones'

DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?charset=utf8mb4"



app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#app.run(host='0.0.0.0', port=5555)

##Create the Account model
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False, default='password')
    email = db.Column(db.String(100), unique=True, nullable=False)
    def __repr__(self):
        return f"<Account(username='{self.username}', password='{self.password}', email='{self.email}')>"

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    second_name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.Float, default=0.0, nullable=False)

    def __repr__(self):
        return f"<Student(name='{self.name}', second_name='{self.second_name}', grade='{self.grade}')>"

#


#@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = Account.query.filter_by(username=username, password=password).first()
        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)




#@app.route('/crudflask/logout')
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


#@app.route('/crudflask/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = Account.query.filter_by(username=username).first()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            new_account = Account(username=username, password=password, email=email)
            db.session.add(new_account)
            db.session.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)



#@app.route('/crudflask/home')
@app.route('/home')
def home():
    title = "Teacher's Grading Dashboard"
    if 'loggedin' in session:
        students = Student.query.all()  # Obtén todos los registros de la base de datos
        alumnos_reprobando = Student.query.filter(Student.grade <= 59.99).all()  # Filtra los alumnos reprobando
        return render_template('home.html', username=session['username'], students=students, alumnos_reprobando=alumnos_reprobando, title=title)
    return redirect(url_for('login'))


#@app.route('/crudflask/profile')
@app.route('/profile')
def profile():
    if 'loggedin' in session:
        account = Account.query.filter_by(id=session['id']).first()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))



#@app.route('/crudflask/create', methods=['POST'])
@app.route('/create', methods=['POST'])
def create_student():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        second_name = request.form['second_name']
        grade = request.form['grade']

        student = Student.query.filter_by(name=name).first()
        if student:
            flash('Student already exists!')
        elif not name or not second_name or not grade:

            flash('Please fill out all the fields!')

        else:
            new_student = Student(name=name, second_name=second_name, grade=grade)
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully!')
    students = all_students()
    alumnos_reprobando = donkeys()
    return render_template('home.html', msg=msg, students=students, alumnos_reprobando=alumnos_reprobando)

# @app.route('/crudflask/edit/<id_username>', methods=['GET', 'POST'])
@app.route('/edit/<id_username>', methods=['GET', 'POST'])
def edit_student(id_username):
    msg='Alumno actualizado exitosamente'
    alumno = Student.query.filter_by(id=id_username).first()

    if not alumno:
        return "No se encontró el alumno"

    if request.method == 'POST':
        alumno.name = request.form['name']
        alumno.second_name = request.form['second_name']
        alumno.grade = request.form['grade']
        db.session.commit()
        students = all_students()
        alumnos_reprobando = donkeys()
        return render_template('home.html', msg=msg, students=students, alumnos_reprobando=alumnos_reprobando)

    students = all_students()
    alumnos_reprobando = donkeys()
    return render_template('edit_student.html', alumno=alumno, students=students, alumnos_reprobando=alumnos_reprobando)


#@app.route('/crudflask/delete/<id_username>', methods=['GET', 'POST'])
@app.route('/delete/<id_username>', methods=['GET', 'POST'])
def delete_student(id_username):

    msg='Alumno eliminado exitosamente'
    account = Student.query.get(id_username)

    if not account:
        return "No se encontró el alumno"

    if request.method == 'POST':
        db.session.delete(account)
        db.session.commit()
        alumnos_reprobando = donkeys()
        students = all_students()
        return render_template('home.html', msg=msg, students=students, alumnos_reprobando=alumnos_reprobando)

    alumnos_reprobando = donkeys()
    students = all_students()
    return render_template('delete_student.html', alumno=account, students=students, alumnos_reprobando=alumnos_reprobando)


def donkeys():
    donkeys_students = Student.query.filter(Student.grade <= 59.99).all()
    return donkeys_students

def all_students():
    students = Student.query.all()
    return students



