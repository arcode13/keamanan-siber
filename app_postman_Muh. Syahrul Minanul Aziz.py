from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

import jwt  # Ditambahkan untuk autentikasi JWT
from functools import wraps  # Ditambahkan untuk mendukung dekorator autentikasi
import os  # Ditambahkan untuk membaca environment variable
from datetime import datetime, timedelta  # Ditambahkan untuk membuat waktu kedaluwarsa JWT

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Membaca SECRET_KEY dari environment variable
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Ditambahkan: default untuk testing

# Fungsi dekorator untuk memeriksa token autentikasi
def token_required(f):  # Ditambahkan
    @wraps(f)  # Ditambahkan
    def decorated(*args, **kwargs):  # Ditambahkan
        token = request.headers.get('x-access-token')  # Ditambahkan
        if not token:  # Ditambahkan
            return jsonify({'message': 'Token is missing!'}), 401  # Ditambahkan
        try:  # Ditambahkan
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # Ditambahkan
        except:  # Ditambahkan
            return jsonify({'message': 'Token is invalid!'}), 401  # Ditambahkan
        return f(*args, **kwargs)  # Ditambahkan
    return decorated  # Ditambahkan

# Endpoint untuk login dan mendapatkan token
@app.route('/login', methods=['POST'])
def login():
    auth = request.form  # Ambil data dari form atau body request

    # Sederhana: hanya satu username dan password
    if auth.get('username') == 'admin' and auth.get('password') == 'admin123':
        token = jwt.encode(
            {'user': auth.get('username'), 'exp': datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY, 
            algorithm="HS256"
        )
        return jsonify({'token': token})  # Kirim token ke pengguna
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


# Model database untuk tabel Student
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
@token_required  # Ditambahkan autentikasi
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

@app.route('/delete/<string:id>', methods=['GET'])
@token_required  # Ditambahkan autentikasi
def delete_student(id):
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"}), 200  # Ditambahkan respon JSON

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@token_required  # Ditambahkan autentikasi
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
