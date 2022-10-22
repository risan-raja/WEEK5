import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask("WEEK5")

current_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
                                        os.path.join(current_dir, "database.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

enrollments = db.Table(
	'enrollments',
	db.Column('enrollment_id', db.Integer,
	          primary_key=True, autoincrement=True),
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


# with app.app_context():
#     Student.__table__.create(bind=db.engine, checkfirst=True)
#     Course.__table__.create(bind=db.engine, checkfirst=True)
#     Enrollments.__table__.create(bind=db.engine, checkfirst=True)

@app.route('/')
def main():
	return "HELLO WORLD"


if __name__ == "__main__":
	app.run(debug=True)
