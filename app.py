from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
	student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	roll_number = db.Column(db.Integer, unique=True, nullable=False)
	first_name = db.Column(db.String(100), nullable=False)
	last_name = db.Column(db.String(100), nullable=True)


class Course(db.Model):
	course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	course_name = db.Column(db.String(100), nullable=False)
	course_code = db.Column(db.String(100), nullable=False)
	course_description = db.Column(db.String(100), nullable=True)


class Enrollments(db.Model):
	enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
	ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


if __name__ == '__main__':
	app.run(debug=True)
