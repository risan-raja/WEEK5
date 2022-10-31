from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
    roll_number = db.Column(db.String, unique=True, nullable=False)
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


"""
STUDENT CRUD OPERATIONS
"""


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        roll_number = int(request.form['roll'])
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        if check_roll_exist(roll_number):
            return render_template("create_student_error.html.jinja", error="Roll number already exists")
        else:
            student = Student(
                roll_number=roll_number,
                first_name=first_name,
                last_name=last_name
            )
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
        db.session.commit()
        new_courses = request.form['course']
        curr_courses = [course.course_id for course in student.courses]
        for course in new_courses:
            if course not in curr_courses:
                student.courses.append(Course.query.filter_by(course_id=course).first())
        db.session.commit()
        return redirect(url_for('main'))

    if request.method == 'GET':
        courses = Course.query.all()
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


@app.route("/student/<int:student_id>/withdraw/<int:course_id>", methods=['GET', 'POST'])
def withdraw_course(student_id, course_id):
    student = Student.query.filter_by(student_id=student_id).first()
    course = Course.query.filter_by(course_id=course_id).first()
    student.courses.remove(course)
    db.session.commit()
    return redirect(url_for('main'))


"""
COURSE CRUD OPERATIONS
"""


def check_course_exist(course_code):
    if Course.query.filter_by(course_code=course_code).first():
        return True
    return False


@app.route('/courses', methods=['GET'])
def course_index():
    courses = Course.query.all()
    return render_template("course_index.html.jinja", courses=courses)


@app.route('/course/create', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        course_name = request.form['c_name']
        course_code = request.form['code']
        course_description = request.form['desc']
        if check_course_exist(course_code):
            return render_template("create_course_error.html.jinja", error="Course code already exists")
        else:
            course = Course(
                course_name=course_name,
                course_code=course_code,
                course_description=course_description
            )
            db.session.add(course)
            db.session.commit()
        return redirect(url_for('course_index'))
    if request.method == 'GET':
        return render_template("create_course.html.jinja")


@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def update_course(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if request.method == 'POST':
        course_name = request.form['c_name']
        # course_code = request.form['code']
        course_description = request.form['desc']
        course.course_name = course_name
        # course.course_code = course_code
        course.course_description = course_description
        db.session.commit()
        return redirect(url_for('course_index'))
    if request.method == 'GET':
        return render_template("update_course.html.jinja", course=course)


@app.route('/course/<int:course_id>/delete', methods=['GET'])
def delete_course(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if request.method == 'GET':
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for('main'))


@app.route('/course/<int:course_id>', methods=['GET'])
def course_detail(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if request.method == 'GET':
        return render_template("course_details.html.jinja", course=course)


with app.app_context():
    Student.__table__.create(bind=db.engine, checkfirst=True)
    Course.__table__.create(bind=db.engine, checkfirst=True)
    Enrollments.__table__.create(bind=db.engine, checkfirst=True)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
