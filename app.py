from flask import Flask, make_response, jsonify
from flask_restful import Resource, Api, reqparse, abort, marshal, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

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
            return {'message': 'Successfully Deleted'}, 200
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


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
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


student_parser = reqparse.RequestParser()
student_parser.add_argument('roll_number', type=str)
student_parser.add_argument('first_name', type=str)
student_parser.add_argument('last_name', type=str)


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
            return {'message': 'Successfully Deleted'}, 200
        return abort(404, message="Student not found")


class StudentCreateApi(Resource):
    def post(self):
        args = student_parser.parse_args()
        if args['roll_number'] is None and args['first_name'] is None:
            return make_response(jsonify([student_error_codes['STUDENT001'], student_error_codes['STUDENT002']]), 400,
                                 {'Content-Type': 'application/json'}, )
        elif args['roll_number'] is None:
            return make_response(jsonify(student_error_codes['STUDENT001']), 400,
                                 {'Content-Type': 'application/json'}, )
        elif args['first_name'] is None:
            return make_response(jsonify(student_error_codes['STUDENT002']), 400,
                                 {'Content-Type': 'application/json'}, )
        elif check_roll_exist(args['roll_number']):
            return abort(409, message="Student already exist")
        else:
            student = Student(
                roll_number=args['roll_number'],
                first_name=args['first_name'],
                last_name=args['last_name']
            )
            db.session.add(student)
            db.session.commit()
            return json_student(student, 'Successfully Created', code=201)


class Enrollments(db.Model):
    __table_args__ = {'extend_existing': True}
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    course_id = db.Column(
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )


enrollment_error_codes = {
    'ENROLLMENT001': {
        "error_code": "ENROLLMENT001",
        "error_message": "Course does not exist"
    },
    'ENROLLMENT002': {
        "error_code": "ENROLLMENT002",
        "error_message": "Student does not exist"
    }

}


def enrollment_json(enrollment, message, code=200):
    enrollment_details = {
        'enrollment_id': enrollment.enrollment_id,
        'student_id': enrollment.student_id,
        'course_id': enrollment.course_id,
    }
    return make_response(jsonify(enrollment_details), code, {'Content-Type': 'application/json',
                                                             'message': f'{message}'}, )


enrollment_fields = {
    'enrollment_id': fields.Integer,
    'student_id': fields.Integer,
    'course_id': fields.Integer
}

enrollment_parser = reqparse.RequestParser()
enrollment_parser.add_argument('course_id', type=int)


def get_enrollments(enrollment_records):
    return marshal(enrollment_records, enrollment_fields)


class GetEnrollmentsApi(Resource):
    def get(self, student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            enrollment_records = Enrollments.query.filter_by(student_id=student_id).all()
            if enrollment_records:
                return make_response(jsonify(get_enrollments(enrollment_records)), 200,
                                     {'Content-Type': 'application/json'}, )
            return abort(404, message="Student is not enrolled in any course")
        return make_response(jsonify(enrollment_error_codes['ENROLLMENT002']), 400,
                             {'Content-Type': 'application/json'}, )

    def post(self, student_id):
        args = enrollment_parser.parse_args()
        course_id = args['course_id']
        course = Course.query.filter_by(course_id=course_id).first()
        if (course_id is not None) and course:
            student = Student.query.filter_by(student_id=student_id).first()
            if student:
                enrollment = Enrollments(
                    student_id=student_id,
                    course_id=course_id
                )
                db.session.add(enrollment)
                db.session.commit()
                enrollment_record = Enrollments.query.filter_by(enrollment_id=enrollment.enrollment_id).first()
                return make_response(jsonify(get_enrollments(enrollment_record)), 201,
                                     {'Content-Type': 'application/json'}, )
            return make_response(jsonify(enrollment_error_codes['ENROLLMENT002']), 400,
                                 {'Content-Type': 'application/json'}, )
        return make_response(jsonify(enrollment_error_codes['ENROLLMENT001']), 400,
                             {'Content-Type': 'application/json'}, )


class DeleteEnrollmentApi(Resource):
    def delete(self, student_id, course_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            course = Course.query.filter_by(course_id=course_id).first()
            if course:
                enrollment = Enrollments.query.filter_by(student_id=student_id, course_id=course_id).first()
                if enrollment:
                    db.session.delete(enrollment)
                    db.session.commit()
                    return make_response({'message': 'Successfully Deleted'}, 200)
                return abort(404, message="Enrollment for the student not found")
            return make_response(jsonify(enrollment_error_codes['ENROLLMENT001']), 400,
                                 {'Content-Type': 'application/json'}, )
        return make_response(jsonify(enrollment_error_codes['ENROLLMENT002']), 400,
                             {'Content-Type': 'application/json'}, )


api.add_resource(CourseCRUDApi, '/api/course/<int:course_id>')
api.add_resource(CourseCreateApi, '/api/course')
api.add_resource(StudentCRUDApi, '/api/student/<int:student_id>')
api.add_resource(StudentCreateApi, '/api/student')
api.add_resource(GetEnrollmentsApi, '/api/student/<int:student_id>/course')
api.add_resource(DeleteEnrollmentApi, '/api/student/<int:student_id>/course/<int:course_id>')

with app.app_context():
    Student.__table__.create(bind=db.engine, checkfirst=True)
    Course.__table__.create(bind=db.engine, checkfirst=True)
    Enrollments.__table__.create(bind=db.engine, checkfirst=True)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
