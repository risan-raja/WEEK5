from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# current_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

enrollments = db.Table(
    'enrollments',
    db.Column('enrollment_id', db.Integer, primary_key=True, autoincrement=True),
    db.Column(
        'estudent_id',
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    ),
    db.Column(
        'ecourse_id',
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )
)


class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(100), nullable=False)
    course_description = db.Column(db.String(100), nullable=True)


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    courses = db.relationship(
        'Course', secondary=enrollments, backref='students', lazy=True)


class Enrollments(db.Model):
    __table_args__ = {'extend_existing': True}
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    ecourse_id = db.Column(
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )


def check_roll_exist(roll_number):
    if Student.query.filter_by(roll_number=roll_number).first():
        return True
    return False


@app.route('/')
def main():
    students = Student.query.all()
    return render_template("index.html.jinja", students=students)


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        roll_number = int(request.form['roll'])
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        if check_roll_exist(roll_number):
            return render_template("create.html.jinja", error="Roll number already exists")
        else:
            student = Student(
                roll_number=roll_number,
                first_name=first_name,
                last_name=last_name
            )
            selected_courses = request.form.getlist('courses')
            for course_id in selected_courses:
                course = Course.query.filter_by(course_id=int(course_id[-1])).first()
                student.courses.append(course)

            db.session.add(student)
            db.session.commit()
        return redirect(url_for('main'))
    if request.method == 'GET':
        return render_template("create_student.html.jinja")


@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if request.method == 'POST':
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        student.first_name = first_name
        student.last_name = last_name
        student.courses = []
        db.session.commit()
        selected_courses = request.form.getlist('courses')
        for course_id in selected_courses:
            course = Course.query.filter_by(course_id=int(course_id[-1])).first()
            student.courses.append(course)
        db.session.commit()
        return redirect(url_for('main'))

    if request.method == 'GET':
        courses = [""] * 4
        for course in student.courses:
            courses[course.course_id - 1] = "checked=true"

        return render_template("update_student.html.jinja", student=student, courses=courses)


@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if request.method == 'GET':
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for('main'))


@app.route('/student/<int:student_id>', methods=['GET'])
def student_detail(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if request.method == 'GET':
        return render_template("student_details.html.jinja", student=student)



with app.app_context():
    Student.__table__.create(bind=db.engine, checkfirst=True)
    Course.__table__.create(bind=db.engine, checkfirst=True)
    Enrollments.__table__.create(bind=db.engine, checkfirst=True)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
