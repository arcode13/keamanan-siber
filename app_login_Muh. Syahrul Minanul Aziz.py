from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super_secret_key"  # Secret key untuk session
db = SQLAlchemy(app)

SECRET_KEY = "your_secret_key"  # Secret key untuk JWT

# Model database untuk tabel Student
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# Fungsi dekorator untuk memeriksa token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))  # Arahkan ke login jika token tidak ada
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return redirect(url_for('login'))  # Arahkan ke login jika token tidak valid
        return f(*args, **kwargs)
    return decorated

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validasi username dan password (hardcoded)
        if username == 'admin' and password == 'admin123':
            token = jwt.encode(
                {'user': username, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                SECRET_KEY, 
                algorithm="HS256"
            )
            session['token'] = token  # Simpan token di session
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message="Invalid credentials")
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('token', None)  # Hapus token dari session
    return redirect(url_for('login'))

# Halaman utama
@app.route('/')
@token_required  # Proteksi dengan token
def index():
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

# Menambah data
@app.route('/add', methods=['POST'])
@token_required  # Proteksi dengan token
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

# Menghapus data
@app.route('/delete/<string:id>')
@token_required  # Proteksi dengan token
def delete_student(id):
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))

# Mengedit data
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@token_required  # Proteksi dengan token
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
