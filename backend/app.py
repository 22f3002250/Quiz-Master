import os
from datetime import datetime, timedelta, date
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource
from functools import wraps
from flask_cors import cross_origin,CORS
import json
from io import BytesIO

from extensions import db
from model import User, Quiz, Admin, Chapter, Subject, Question, Score, UserAnswer
from celery_worker import celery, export_users_csv, generate_monthly_report
from flask_caching import Cache

def create_admin_user():
    admin_username = "Tripti Jha"
    admin_password = "tripti123"
    admin_email = "tripti@gmail.com"
    print(f"DEBUG: Hashing admin password with key: {app.config['JWT_SECRET_KEY']}")
    with db.session.no_autoflush:
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            hashed_password = generate_password_hash(admin_password)
            new_admin = Admin(
                username=admin_username,
                password=hashed_password,
                email=admin_email
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

cache = Cache()

def create_app():
    app = Flask(__name__)
    api = Api(app)
    app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_SECRET_KEY"] = os.environ.get("FLASK_JWT_SECRET", "MY_PROJECT_SECRET_KEY_XYZ")
    print(f"DEBUG: Active JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_REDIS_DB'] = 1
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/1'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app) 
    
    @jwt.user_identity_loader
    def user_identity_lookup(user_data):
        return json.dumps(user_data)

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"message": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"message": "Signature verification failed or token is invalid"}), 403

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({"message": "Token has expired"}), 401

    cache.init_app(app)
    return app, api, jwt

app, api, jwt = create_app()
print(f"DEBUG: Active JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

@app.cli.command("create-db")
def create_db_command():
    """Create database tables and seed initial admin user."""
    with app.app_context():
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        print("Database tables created.")
        create_admin_user()
        print("Admin user setup complete.")

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                raw_identity = get_jwt_identity()
                current_user = json.loads(raw_identity)
                print(f"DEBUG: current_user identity within decorator: {current_user}")

                if not current_user:
                    return {'message': 'Admin access required (identity missing)'}, 403
                
                if current_user.get('role') != 'admin':
                    return {'message': 'Admin access required (role mismatch)'}, 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {'message': 'Authentication error processing token internally: ' + str(e)}, 401
        return decorator
    return wrapper

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Register(Resource):
    def post(self):
        cache.clear() # Registration affects overall user count, so clear cache
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        qualification = data.get('qualification')
        dob_str = data.get('dob')

        if not all([email, password, full_name, qualification, dob_str]):
            return {'message': 'Missing fields'}, 400

        if User.query.filter_by(email=email).first():
            return {'message': 'Email already registered'}, 400

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format for DOB. Use YYYY-MM-DD.'}, 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_password,
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Email and password required'}, 400
       
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity={'id': user.id, 'role': user.role})
            return {'access_token': access_token, 'role': user.role, 'message': 'Login successful'}, 200

        admin = Admin.query.filter((Admin.email == email) | (Admin.username == email)).first()
        if admin and check_password_hash(admin.password, password):
            access_token = create_access_token(identity={'id': admin.id, 'role': 'admin'})
            return {'access_token': access_token, 'role': 'admin', 'message': 'Admin login successful'}, 200
        return {'message': 'Invalid credentials'}, 401


class Subjects(Resource):
    @admin_required()
    @cache.cached(timeout=60, query_string=True)
    def get(self):
        search_query = request.args.get('query', type=str, default='').strip()
        
        if search_query:
            subjects = Subject.query.filter(
                (Subject.name.ilike(f'%{search_query}%')) |
                (Subject.description.ilike(f'%{search_query}%'))
            ).all()
        else:
            subjects = Subject.query.all()

        return [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects], 200


    @admin_required()
    def post(self):
        cache.clear() # Clears ALL cache in the configured DB (DB 1 for Flask-Caching)
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        if not name:
            return {'message': 'Subject name is required'}, 400
        if Subject.query.filter_by(name=name).first():
            return {'message': 'Subject with this name already exists'}, 409

        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        return {'id': subject.id, 'name': subject.name, 'description': subject.description}, 201

class SubjectResource(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        return {'id': subject.id, 'name': subject.name, 'description': subject.description}, 200

    @admin_required()
    def put(self, subject_id):
        cache.clear() # Clears ALL cache after modification
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        data = request.get_json()
        name = data.get('name', subject.name)
        description = data.get('description', subject.description)

        if not name:
            return {'message': 'Subject name is required'}, 400

        if Subject.query.filter(Subject.name == name, Subject.id != subject_id).first():
            return {'message': 'Subject with this name already exists'}, 409

        subject.name = name
        subject.description = description
        db.session.commit()
        return {'id': subject.id, 'name': subject.name, 'description': subject.description}, 200

    @admin_required()
    def delete(self, subject_id):
        cache.clear() # Clears ALL cache after deletion
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        
        db.session.delete(subject)
        db.session.commit()
        return {'message': 'Subject deleted successfully'}, 204


class ChaptersBySubject(Resource):
    @admin_required()
    @cache.cached(timeout=60, query_string=True)
    def get(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        search_query = request.args.get('query', type=str, default='').strip()
        
        if search_query:
            chapters = Chapter.query.filter(
                Chapter.subject_id == subject_id,
                (Chapter.name.ilike(f'%{search_query}%')) |
                (Chapter.description.ilike(f'%{search_query}%'))
            ).all()
        else:
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()

        return [{'id': c.id, 'subject_id': c.subject_id, 'name': c.name, 'description': c.description} for c in chapters], 200

    @admin_required()
    def post(self, subject_id):
        cache.clear() # Clears ALL cache after modification
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return {'message': 'Chapter name is required'}, 400

        if Chapter.query.filter_by(subject_id=subject_id, name=name).first():
            return {'message': f'Chapter with name "{name}" already exists under this subject'}, 409

        new_chapter = Chapter(
            subject_id=subject_id,
            name=name,
            description=description
        )
        db.session.add(new_chapter)
        db.session.commit()
        return {
            'id': new_chapter.id,
            'subject_id': new_chapter.subject_id,
            'name': new_chapter.name,
            'description': new_chapter.description
        }, 201

class ChapterResource(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, chapter_id):
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404
        return {
            'id': chapter.id,
            'subject_id': chapter.subject_id,
            'name': chapter.name,
            'description': chapter.description
        }, 200

    @admin_required()
    def put(self, chapter_id):
        cache.clear() # Clears ALL cache after modification
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404
        data = request.get_json()
        name = data.get('name', chapter.name)
        description = data.get('description', chapter.description)
        subject_id = data.get('subject_id', chapter.subject_id)

        if not name:
            return {'message': 'Chapter name is required'}, 400
        
        if (name != chapter.name or subject_id != chapter.subject_id) and \
           Chapter.query.filter_by(subject_id=subject_id, name=name).first():
            return {'message': f'Chapter with name "{name}" already exists under the selected subject'}, 409

        chapter.name = name
        chapter.description = description
        chapter.subject_id = subject_id
        db.session.commit()
        return {
            'id': chapter.id,
            'subject_id': chapter.subject_id,
            'name': chapter.name,
            'description': chapter.description
        }, 200

    @admin_required()
    def delete(self, chapter_id):
        cache.clear() # Clears ALL cache after deletion
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        db.session.delete(chapter)
        db.session.commit()
        return {'message': 'Chapter deleted successfully'}, 204


class QuizzesByChapter(Resource):
    @admin_required()
    @cache.cached(timeout=60, query_string=True)
    def get(self, chapter_id):
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        search_query = request.args.get('query', type=str, default='').strip()
        
        if search_query:
            quizzes = Quiz.query.filter(
                Quiz.chapter_id == chapter_id,
                (Quiz.title.ilike(f'%{search_query}%')) |
                (Quiz.description.ilike(f'%{search_query}%'))
            ).all()
        else:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

        return [{'id': q.id, 'chapter_id': q.chapter_id, 'title': q.title, 'description': q.description, 'time_duration': q.time_duration, 'date_of_quiz': q.date_of_quiz.isoformat()} for q in quizzes], 200

    @admin_required()
    def post(self, chapter_id):
        cache.clear()
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        time_duration = data.get('time_duration')
        date_of_quiz_str = data.get('date_of_quiz')

        if not all([title, time_duration, date_of_quiz_str]):
            return {'message': 'Quiz title, duration, and date are required'}, 400
        
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format for date_of_quiz. Use YYYY-MM-DD.'}, 400

        if Quiz.query.filter_by(chapter_id=chapter_id, title=title).first():
            return {'message': f'Quiz with title "{title}" already exists under this chapter'}, 409

        new_quiz = Quiz(
            chapter_id=chapter_id,
            title=title,
            description=description,
            time_duration=time_duration,
            date_of_quiz=date_of_quiz
        )
        db.session.add(new_quiz)
        db.session.commit()
        return {
            'id': new_quiz.id,
            'chapter_id': new_quiz.chapter_id,
            'title': new_quiz.title,
            'description': new_quiz.description,
            'time_duration': new_quiz.time_duration,
            'date_of_quiz': new_quiz.date_of_quiz.isoformat()
        }, 201

class QuizResource(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        return {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'title': quiz.title,
            'description': quiz.description,
            'time_duration': quiz.time_duration,
            'date_of_quiz': quiz.date_of_quiz.isoformat()
        }, 200

    @admin_required()
    def put(self, quiz_id):
        cache.clear()
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        data = request.get_json()
        title = data.get('title', quiz.title)
        description = data.get('description', quiz.description)
        time_duration = data.get('time_duration', quiz.time_duration)
        date_of_quiz_str = data.get('date_of_quiz', quiz.date_of_quiz.isoformat())
        chapter_id = data.get('chapter_id', quiz.chapter_id)

        if not all([title, time_duration, date_of_quiz_str]):
            return {'message': 'Quiz title, duration, and date are required'}, 400
        
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format for date_of_quiz. Use YYYY-MM-DD.'}, 400

        if (title != quiz.title or chapter_id != quiz.chapter_id) and \
           Quiz.query.filter_by(chapter_id=chapter_id, title=title).first():
            return {'message': f'Quiz with title "{title}" already exists under the selected chapter'}, 409

        quiz.title = title
        quiz.description = description
        quiz.time_duration = time_duration
        quiz.date_of_quiz = date_of_quiz
        quiz.chapter_id = chapter_id
        db.session.commit()
        return {'id': quiz.id, 'chapter_id': quiz.chapter_id, 'title': quiz.title, 'description': quiz.description, 'time_duration': quiz.time_duration, 'date_of_quiz': quiz.date_of_quiz.isoformat()}, 200

    @admin_required()
    def delete(self, quiz_id):
        cache.clear()
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        db.session.delete(quiz)
        db.session.commit()
        return {'message': 'Quiz deleted successfully'}, 204

class QuestionsByQuiz(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return [{'id': q.id, 'quiz_id': q.quiz_id, 'question_text': q.question_text, 'option1': q.option1, 'option2': q.option2, 'option3': q.option3, 'option4': q.option4, 'correct_option': q.correct_option} for q in questions], 200

    @admin_required()
    def post(self, quiz_id):
        cache.clear()
        data = request.get_json()
        question_text = data.get('question_text')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = data.get('correct_option')

        if not all([question_text, option1, option2, correct_option is not None]):
            return {'message': 'Question text, option1, option2, and correct option are required'}, 400
        
        if correct_option not in [1, 2, 3, 4]:
            return {'message': 'Correct option must be 1, 2, 3, or 4'}, 400

        new_question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        db.session.add(new_question)
        db.session.commit()
        return {
            'id': new_question.id,
            'quiz_id': new_question.quiz_id,
            'question_text': new_question.question_text,
            'option1': new_question.option1,
            'option2': new_question.option2,
            'option3': new_question.option3,
            'option4': new_question.option4,
            'correct_option': new_question.correct_option
        }, 201

class QuestionResource(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, question_id):
        question = db.session.get(Question, question_id)
        if not question:
            return {'message': 'Question not found'}, 404
        return {
            'id': question.id,
            'quiz_id': question.quiz_id,
            'question_text': question.question_text,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'correct_option': question.correct_option
        }, 200

    @admin_required()
    def put(self, question_id):
        cache.clear()
        question = db.session.get(Question, question_id)
        if not question:
            return {'message': 'Question not found'}, 404
        data = request.get_json()
        question_text = data.get('question_text', question.question_text)
        option1 = data.get('option1', question.option1)
        option2 = data.get('option2', question.option2)
        option3 = data.get('option3', question.option3)
        option4 = data.get('option4', question.option4)
        correct_option = data.get('correct_option', question.correct_option)
        quiz_id = data.get('quiz_id', question.quiz_id)

        if not all([question_text, option1, option2, correct_option is not None]):
            return {'message': 'Question text, option1, option2, and correct option are required'}, 400
        
        if correct_option not in [1, 2, 3, 4]:
            return {'message': 'Correct option must be 1, 2, 3, or 4'}, 400

        question.question_text = question_text
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = correct_option
        question.quiz_id = quiz_id
        db.session.commit()
        return {'id': question.id, 'quiz_id': question.quiz_id, 'question_text': question.question_text, 'option1': question.option1, 'option2': question.option2, 'option3': question.option3, 'option4': question.option4, 'correct_option': question.correct_option}, 200

    @admin_required()
    def delete(self, question_id):
        cache.clear()
        question = db.session.get(Question, question_id)
        if not question:
            return {'message': 'Question not found'}, 404
        
        db.session.delete(question)
        db.session.commit()
        return {'message': 'Question deleted successfully'}, 204

class AdminUsers(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self):
        users = User.query.all()
        return [{'id': u.id,'email': u.email,'full_name': u.full_name,'qualification': u.qualification,'dob': u.dob.isoformat() if u.dob else None,'role': getattr(u, 'role', 'N/A')
            } for u in users], 200
    def options(self):
        return {'Allow': 'GET, POST, PUT, DELETE, OPTIONS'}, 200

class AdminUserResource(Resource):
    @admin_required()
    def delete(self, user_id):
        cache.clear()
        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User with ID {user_id} deleted successfully'}, 204


class AdminDashboardStats(Resource):
    @admin_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self):
        total_users = User.query.count()
        total_subjects = Subject.query.count()
        total_chapters = Chapter.query.count()
        total_quizzes = Quiz.query.count()
        total_questions = Question.query.count()
        total_scores = Score.query.count()

        all_scores = [s.score for s in Score.query.all()]
        average_score = sum(all_scores) / len(all_scores) if all_scores else 0

        return {
            'total_users': total_users,
            'total_subjects': total_subjects,
            'total_chapters': total_chapters,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'total_scores': total_scores,
            'average_score': round(average_score, 2)
        }, 200

    def options(self):
        return {'Allow': 'GET, OPTIONS'}, 200


class AdminReportExport(Resource):
    @admin_required()
    def post(self):
        cache.clear()
        try:
            result = export_users_csv.apply_async()
            csv_content = result.get(timeout=60)

            if isinstance(csv_content, dict) and csv_content.get('status') == 'error':
                return {'message': csv_content.get('message', 'Failed to generate CSV report')}, 500

            buffer = BytesIO(csv_content.encode('utf-8'))
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name='users_report.csv'
            )

        except TimeoutError:
            print("ERROR: Celery task timed out.")
            return {'message': 'CSV export task timed out. Please try again later.'}, 504
        except Exception as e:
            print(f"ERROR: Failed to initiate CSV export: {e}")
            import traceback
            traceback.print_exc()
            return {'message': 'Failed to initiate CSV export or process result'}, 500

    def options(self):
        return {'Allow': 'POST, OPTIONS'}, 200


class AdminMonthlyReportTrigger(Resource):
    @admin_required()
    def post(self):
        cache.clear()
        try:
            result = generate_monthly_report.apply_async()
            report_html_content = result.get(timeout=60)

            if isinstance(report_html_content, dict) and report_html_content.get('status') == 'error':
                return {'message': report_html_content.get('message', 'Failed to generate monthly report')}, 500

            buffer = BytesIO(report_html_content.encode('utf-8'))
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype='text/html',
                as_attachment=True,
                download_name=f'monthly_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            )

        except TimeoutError:
            print("ERROR: Celery task timed out.")
            return {'message': 'Monthly report task timed out. Please try again later.'}, 504
        except Exception as e:
            print(f"ERROR: Failed to initiate monthly report: {e}")
            import traceback
            traceback.print_exc()
            return {'message': 'Failed to initiate monthly report generation or process result'}, 500

    def options(self):
        return {'Allow': 'POST, OPTIONS'}, 200

class UserAccessibleSubjects(Resource):
        @jwt_required()
        @cache.cached(timeout=60) # Cache for 60 seconds
        def get(self):
            subjects = Subject.query.all()
            return [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects], 200

        def options(self):
            return {'Allow': 'GET, OPTIONS'}, 200

class UserProfileResource(Resource):
    @jwt_required() # Protected, but not necessarily admin_required
    def get(self, user_id):
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)

        # Ensure user can only access their own profile unless they are admin
        if current_user_identity['role'] == 'user' and current_user_identity['id'] != user_id:
            return {'message': 'Unauthorized access to user profile'}, 403
        
        user = db.session.get(User, user_id) # Using db.session.get for SQLAlchemy 2.0 style
        if not user:
            return {'message': 'User not found'}, 404
        
        return user.as_dict(), 200

    @jwt_required() # Protected, but not necessarily admin_required
    def put(self, user_id):
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)

        # Ensure user can only update their own profile unless they are admin
        if current_user_identity['role'] == 'user' and current_user_identity['id'] != user_id:
            return {'message': 'Unauthorized to update this profile'}, 403
        
        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'User not found'}, 404

        data = request.get_json()
        full_name = data.get('full_name', user.full_name)
        qualification = data.get('qualification', user.qualification)
        # Ensure dob_str is correctly handled, especially if user.dob is None
        dob_str = data.get('dob', user.dob.isoformat() if user.dob else None)

        if not all([full_name, qualification, dob_str]):
            return {'message': 'Full name, qualification, and DOB are required'}, 400
        
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid DOB format. Use YYYY-MM-DD'}, 400
        
        user.full_name = full_name
        user.qualification = qualification
        user.dob = dob
        db.session.commit()
        return user.as_dict(), 200

    # --- NEW: Add OPTIONS method for CORS preflight ---
    def options(self, user_id): # user_id is passed but not used for OPTIONS
        return {'Allow': 'GET, PUT, OPTIONS'}, 200 # Include methods this resource supports



class UserAccessibleChaptersBySubject(Resource):
    @jwt_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return [{'id': c.id, 'subject_id': c.subject_id, 'name': c.name, 'description': c.description} for c in chapters], 200

    def options(self, subject_id):
        return {'Allow': 'GET, OPTIONS'}, 200

class UserAccessibleQuizzesByChapter(Resource):
    @jwt_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, chapter_id):
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return [{'id': q.id, 'chapter_id': q.chapter_id, 'title': q.title, 'description': q.description, 'time_duration': q.time_duration, 'date_of_quiz': q.date_of_quiz.isoformat()} for q in quizzes], 200

    def options(self, chapter_id):
        return {'Allow': 'GET, OPTIONS'}, 200

class UserAccessibleQuestionsByQuiz(Resource):
    @jwt_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return [{'id': q.id, 'quiz_id': q.quiz_id, 'question_text': q.question_text, 'option1': q.option1, 'option2': q.option2, 'option3': q.option3, 'option4': q.option4, 'correct_option': q.correct_option} for q in questions], 200

    def options(self, quiz_id):
        return {'Allow': 'GET, OPTIONS'}, 200


class QuizAttemptSubmit(Resource):
    @jwt_required()
    def post(self):
        cache.clear() # Clears ALL cache after modification
        try:
            raw_identity = get_jwt_identity()
            current_user_identity = json.loads(raw_identity)
            user_id = current_user_identity['id']

            data = request.get_json()
            quiz_id = data.get('quiz_id')
            answers = data.get('answers')

            if not all([quiz_id, answers]):
                return {'message': 'Quiz ID and answers are required'}, 400

            quiz = db.session.get(Quiz, quiz_id)
            if not quiz:
                return {'message': 'Quiz not found'}, 404

            quiz_questions = Question.query.filter_by(quiz_id=quiz_id).all()
            correct_answers_map = {q.id: q.correct_option for q in quiz_questions}

            calculated_score = 0
            correct_answers_count = 0
            
            for answer_data in answers:
                question_id = answer_data.get('question_id')
                selected_option = answer_data.get('selected_option')

                if question_id not in correct_answers_map:
                    continue

                existing_user_answer = UserAnswer.query.filter_by(
                    user_id=user_id,
                    quiz_id=quiz_id,
                    question_id=question_id
                ).first()

                if existing_user_answer:
                    existing_user_answer.selected_option = selected_option
                    existing_user_answer.attempt_timestamp = datetime.utcnow()
                else:
                    new_user_answer = UserAnswer(
                        user_id=user_id,
                        quiz_id=quiz_id,
                        question_id=question_id,
                        selected_option=selected_option,
                        attempt_timestamp=datetime.utcnow()
                    )
                    db.session.add(new_user_answer)
                
                if selected_option == correct_answers_map[question_id]:
                    calculated_score += 1
                    correct_answers_count += 1
            
            db.session.commit()
            new_score_entry = Score(
                user_id=user_id,
                quiz_id=quiz_id,
                score=calculated_score,
                attempt_timestamp=datetime.utcnow()
            )
            db.session.add(new_score_entry)
            db.session.commit()

            return {
                'message': 'Quiz submitted successfully!',
                'final_score': calculated_score,
                'correct_answers_count': correct_answers_count,
                'total_questions': len(quiz_questions)
            }, 200
        except Exception as e:
            print(f"ERROR: Quiz submission failed: {e}")
            import traceback
            traceback.print_exc()
            return {'message': 'Quiz submission failed internally'}, 500

    def options(self):
        return {'Allow': 'POST, OPTIONS'}, 200


class UserScores(Resource):
    @jwt_required()
    def get(self):
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)
        user_id = current_user_identity['id']
        
        scores = Score.query.filter_by(user_id=user_id).all()
        all_quizzes = Quiz.query.all()
        quiz_titles = {q.id: q.title for q in all_quizzes}

        return [{
            'id': s.id,
            'user_id': s.user_id,
            'quiz_id': s.quiz_id,
            'score': s.score,
            'attempt_timestamp': s.attempt_timestamp.isoformat(),
            'quiz_title': quiz_titles.get(s.quiz_id, 'Unknown Quiz')
        } for s in scores], 200

    @jwt_required()
    def post(self):
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)
        user_id = current_user_identity['id']

        data = request.get_json()
        quiz_id = data.get('quiz_id')
        score_value = data.get('score')

        if not all([quiz_id, score_value is not None]):
            return {'message': 'Quiz ID and score are required'}, 400
        
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        new_score = Score(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score_value,
            attempt_timestamp=datetime.utcnow()
        )
        db.session.add(new_score)
        db.session.commit()
        return {'message': 'Score saved successfully', 'score_id': new_score.id}, 201


class UserAnswers(Resource):
    @jwt_required()
    @cache.cached(timeout=60, key_prefix='user_answers', make_cache_key=lambda *args, **kwargs: str(json.loads(get_jwt_identity())['id']) + str(kwargs['quiz_id']) + str(kwargs['question_id']))
    def get(self, quiz_id, question_id): # This GET method is not used in frontend, but good for completeness
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)
        user_id = current_user_identity['id']

        user_answer = UserAnswer.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id,
            question_id=question_id
        ).first()

        if not user_answer:
            return {'message': 'Answer not found'}, 404
        return user_answer.as_dict(), 200

    @jwt_required()
    def post(self):
        cache.clear() # Clears ALL cache after modification
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)
        user_id = current_user_identity['id']

        data = request.get_json()
        quiz_id = data.get('quiz_id')
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')

        if not all([quiz_id, question_id, selected_option is not None]):
            return {'message': 'Quiz ID, Question ID, and selected option are required'}, 400
        
        quiz = db.session.get(Quiz, quiz_id)
        question = db.session.get(Question, question_id)
        if not quiz or not question:
            return {'message': 'Quiz or Question not found'}, 404

        existing_answer = UserAnswer.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id,
            question_id=question_id
        ).first()

        if existing_answer:
            existing_answer.selected_option = selected_option
            existing_answer.attempt_timestamp = datetime.utcnow()
        else:
            new_answer = UserAnswer(
                user_id=user_id,
                quiz_id=quiz_id,
                question_id=question_id,
                selected_option=selected_option,
                attempt_timestamp=datetime.utcnow()
            )
            db.session.add(new_answer)
        
        db.session.commit()
        return {'message': 'User answer saved successfully', 'answer_id': new_answer.id}, 201

    def options(self):
        return {'Allow': 'POST, OPTIONS'}, 200

class UserAccessibleAllQuizzes(Resource):
    @jwt_required()
    @cache.cached(timeout=60) # Cache for 60 seconds
    def get(self):
        quizzes = Quiz.query.all()
        return [{'id': q.id, 'chapter_id': q.chapter_id, 'title': q.title, 'description': q.description, 'time_duration': q.time_duration, 'date_of_quiz': q.date_of_quiz.isoformat()} for q in quizzes], 200

    def options(self):
        return {'Allow': 'GET, OPTIONS'}, 200

class UserDashboardStats(Resource):
    @jwt_required()
    @cache.cached(timeout=60, key_prefix='user_dashboard_stats', make_cache_key=lambda *args, **kwargs: str(json.loads(get_jwt_identity())['id']))
    def get(self):
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)
        user_id = current_user_identity['id']

        total_quizzes_attempted = Score.query.filter_by(user_id=user_id).count()
        user_scores = Score.query.filter_by(user_id=user_id).all()
        average_user_score = sum(s.score for s in user_scores) / len(user_scores) if user_scores else 0

        return {
            'total_quizzes_attempted': total_quizzes_attempted,
            'average_user_score': round(average_user_score, 2)
        }, 200

    def options(self):
        return {'Allow': 'GET, OPTIONS'}, 200

# Register the resource with the API
api.add_resource(HelloWorld, '/')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Subjects, '/api/subjects')
api.add_resource(SubjectResource, '/api/subjects/<int:subject_id>')
api.add_resource(ChaptersBySubject, '/api/subjects/<int:subject_id>/chapters')
api.add_resource(ChapterResource, '/api/chapters/<int:chapter_id>')
api.add_resource(QuizzesByChapter, '/api/chapters/<int:chapter_id>/quizzes')
api.add_resource(QuizResource, '/api/quizzes/<int:quiz_id>')
api.add_resource(QuestionsByQuiz, '/api/quizzes/<int:quiz_id>/questions')
api.add_resource(QuestionResource, '/api/questions/<int:question_id>')
api.add_resource(UserAccessibleSubjects, '/api/user/subjects')
api.add_resource(UserAccessibleChaptersBySubject, '/api/user/subjects/<int:subject_id>/chapters')
api.add_resource(UserAccessibleQuizzesByChapter, '/api/user/chapters/<int:chapter_id>/quizzes')
api.add_resource(UserAccessibleQuestionsByQuiz, '/api/user/quizzes/<int:quiz_id>/questions')
api.add_resource(QuizAttemptSubmit, '/api/quiz_attempt_submit')
api.add_resource(AdminUsers, '/api/admin/users')
api.add_resource(AdminUserResource, '/api/admin/users/<int:user_id>')
api.add_resource(UserProfileResource, '/api/users/<int:user_id>')
api.add_resource(UserScores, '/api/scores')
api.add_resource(UserAnswers, '/api/user_answers')
api.add_resource(UserAccessibleAllQuizzes, '/api/quizzes/all')
api.add_resource(AdminDashboardStats, '/api/admin/dashboard/stats')
api.add_resource(UserDashboardStats, '/api/user/dashboard/stats')
api.add_resource(AdminReportExport, '/api/admin/reports/export-csv')
api.add_resource(AdminMonthlyReportTrigger, '/api/admin/reports/generate-monthly')


if __name__ == "__main__":
    app.run(debug=True)
