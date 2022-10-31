from flask import Flask, make_response, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
api = Api(app)
# current_dir = os.path.abspath(os.path.dirname(__file__))
# noinspection DuplicatedCode
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqllite///home//mlop3n//PycharmProjects//WEEK5//database.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

enrollments = db.Table(
    'enrollments',
    db.Column('enrollment_id', db.Integer, primary_key=True, autoincrement=True),
    db.Column(
        'student_id',
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    ),
    db.Column(
        'course_id',
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )
)


class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(100), nullable=False)
    course_description = db.Column(db.String(100), nullable=True)


course_parser = reqparse.RequestParser()
course_parser.add_argument('course_code', type=str)
course_parser.add_argument('course_name', type=str)
course_parser.add_argument('course_description', type=str)


def json_course(course, message, code=200):
    course_details = {
        'course_id': course.course_id,
        'course_name': course.course_name,
        'course_code': course.course_code,
        'course_description': course.course_description
    }
    return make_response(jsonify(course_details), code, {'Content-Type': 'application/json',
                                                         'message': f'{message}'}, )


course_error_codes = {
    'COURSE001': {
        "error_code": "COURSE001",
        "error_message": "Course Name is Required"
    },
    'COURSE002': {
        "error_code": "COURSE002",
        "error_message": "Course Code is Required"
    }

}


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    courses = db.relationship(
        'Course', secondary=enrollments, backref='students', lazy=True)


student_error_codes = {
    'STUDENT001': {
        "error_code": "STUDENT001",
        "error_message": "Roll Number required"
    },
    'STUDENT002': {
        "error_code": "STUDENT002",
        "error_message": "First Name is required"
    }

}


def check_roll_exist(roll_number):
    if Student.query.filter_by(roll_number=roll_number).first():
        return True
    return False


def json_student(student, message, code=200):
    student_details = {
        'student_id': student.student_id,
        'roll_number': student.roll_number,
        'first_name': student.first_name,
        'last_name': student.last_name,
    }
    return make_response(jsonify(student_details), code, {'Content-Type': 'application/json',
                                                          'message': f'{message}'}, )


class Enrollments(db.Model):
    __table_args__ = {'extend_existing': True}
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    course_id = db.Column(
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )


class CourseCRUDApi(Resource):
    def get(self, course_id):
        course = Course.query.filter_by(course_id=course_id).first()
        if course:
            return json_course(course, 'Request Successful')
        return abort(404, message="Course not found")

    def put(self, course_id):
        course = Course.query.filter_by(course_id=course_id).first()
        if course:
            args = course_parser.parse_args()
            if args['course_code'] is None and args['course_name'] is None:
                return make_response(jsonify([course_error_codes['COURSE001'], course_error_codes['COURSE002']]), 400,
                                     {'Content-Type': 'application/json'}, )
            elif args['course_name'] is None:
                return make_response(jsonify(course_error_codes['COURSE001']), 400,
                                     {'Content-Type': 'application/json'}, )
            elif args['course_code'] is None:
                return make_response(jsonify(course_error_codes['COURSE002']), 400,
                                     {'Content-Type': 'application/json'}, )
            else:
                course.course_name = args['course_name']
                course.course_code = args['course_code']
                course.course_description = args['course_description']
                db.session.commit()
                return json_course(course, 'Successfully updated')
        return abort(404, message="Course not found")

    def delete(self, course_id):
        course = Course.query.filter_by(course_id=course_id).first()
        if course:
            db.session.delete(course)
            db.session.commit()
            return {'status': 'Successfully Deleted'}, 200
        return abort(404, message="Course not found")


def check_course_exist(course_code):
    if Course.query.filter_by(course_code=course_code).first():
        return True
    return False


class CourseCreateApi(Resource):
    def post(self):
        args = course_parser.parse_args()
        if args['course_code'] is None and args['course_name'] is None:
            return make_response(jsonify([course_error_codes['COURSE001'], course_error_codes['COURSE002']]), 400,
                                 {'Content-Type': 'application/json'}, )
        elif args['course_name'] is None:
            return make_response(jsonify(course_error_codes['COURSE001']), 400,
                                 {'Content-Type': 'application/json'}, )
        elif args['course_code'] is None:
            return make_response(jsonify(course_error_codes['COURSE002']), 400,
                                 {'Content-Type': 'application/json'}, )
        elif check_course_exist(args['course_code']):
            return abort(409, message="course_code already exist")
        else:
            course = Course(
                course_name=args['course_name'],
                course_code=args['course_code'],
                course_description=args['course_description']
            )
            db.session.add(course)
            db.session.commit()
            return json_course(course, 'Successfully Created', code=201)


class StudentCRUDApi(Resource):
    def get(self, student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            return json_student(student, 'Request Successful')
        return abort(404, message="Student not found")

    def put(self, student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            args = student_parser.parse_args()
            if args['roll_number'] is None and args['first_name'] is None:
                return make_response(jsonify([student_error_codes['STUDENT001'], student_error_codes['STUDENT002']]),
                                     400,
                                     {'Content-Type': 'application/json'}, )
            elif args['roll_number'] is None:
                return make_response(jsonify(student_error_codes['STUDENT001']), 400,
                                     {'Content-Type': 'application/json'}, )
            elif args['first_name'] is None:
                return make_response(jsonify(student_error_codes['STUDENT002']), 400,
                                     {'Content-Type': 'application/json'}, )
            else:
                student.roll_number = args['roll_number']
                student.first_name = args['first_name']
                student.last_name = args['last_name']
                db.session.commit()
                return json_student(student, 'Successfully updated')
        return abort(404, message="Student not found")

    def delete(self, student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            db.session.delete(student)
            db.session.commit()
            return {'status': 'Successfully Deleted'}, 200
        return abort(404, message="Student not found")


api.add_resource(CourseCRUDApi, '/api/course/<int:course_id>')
api.add_resource(CourseCreateApi, '/api/course')
api.add_resource(StudentCRUDApi, '/api/student/<int:student_id>')

with app.app_context():
    Student.__table__.create(bind=db.engine, checkfirst=True)
    Course.__table__.create(bind=db.engine, checkfirst=True)
    Enrollments.__table__.create(bind=db.engine, checkfirst=True)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
