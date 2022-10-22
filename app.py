from flask import Flask
import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask("WEEK5")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


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
    estudent_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    ecourse_id = db.Column(
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )


with app.app_context():
    Student.__table__.create(bind=db.engine, checkfirst=True)
    Course.__table__.create(bind=db.engine, checkfirst=True)
    Enrollments.__table__.create(bind=db.engine, checkfirst=True)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
