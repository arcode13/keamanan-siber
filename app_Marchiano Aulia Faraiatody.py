from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from markupsafe import escape

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    # Sebelumnya (Rentan)
    # students = db.session.execute(text('SELECT * FROM student')).fetchall()
    # return render_template('index.html', students=students)
    
    # Setelah Diperkuat
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    sanitized_students = [
        {'id': student.id, 'name': escape(student.name), 'age': student.age, 'grade': escape(student.grade)}
        for student in students
    ]
    return render_template('index.html', students=sanitized_students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']

    # Sebelumnya (Rentan)
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)

    # Setelah Diperkuat
    db.session.execute(
        text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
        {'name': name, 'age': age, 'grade': grade}
    )
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<string:id>')
def delete_student(id):
    # Sebelumnya (Rentan)
    # db.session.execute(text(f"DELETE FROM student WHERE id={id}"))

    # Setelah Diperkuat
    db.session.execute(
        text("DELETE FROM student WHERE id=:id"),
        {'id': id}
    )
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        # Sebelumnya (Rentan)
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))

        # Setelah Diperkuat
        db.session.execute(
            text("UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id"),
            {'name': name, 'age': age, 'grade': grade, 'id': id}
        )
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # Sebelumnya (Rentan)
        # student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()

        # Setelah Diperkuat
        student = db.session.execute(
            text("SELECT * FROM student WHERE id=:id"),
            {'id': id}
        ).fetchone()
        return render_template('edit.html', student=student)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
