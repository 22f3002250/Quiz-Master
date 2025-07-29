import os
from datetime import datetime, timedelta, date 
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource
from functools import wraps
from flask_cors import cross_origin,CORS
import json
from extensions import db
from model import User, Quiz, Admin, Chapter, Subject, Question, Score, UserAnswer


# Create an admin user if it doesn't exist (renamed for consistency with call)
def create_admin_user():

    admin_username = "Tripti Jha"
    admin_password = "tripti123"
    admin_email = "tripti@gmail.com"
    print(f"DEBUG: Hashing admin password with key: {app.config['JWT_SECRET_KEY']}")
    # Check if admin already exists
    with db.session.no_autoflush:
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            hashed_password = generate_password_hash(admin_password)
            new_admin = Admin(username=admin_username,password=hashed_password,email=admin_email)
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

# Create Flask app and configure it
def create_app():
    app = Flask(__name__)
    api = Api(app)
    app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_SECRET_KEY"] = os.environ.get("FLASK_JWT_SECRET", "MY_PROJECT_SECRET_KEY_XYZ")
    print(f"DEBUG: Active JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

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

    return app, api, jwt

app, api, jwt = create_app()
print(f"DEBUG: Active JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")


@app.cli.command("create-db")
def create_db_command():
    """Create database tables and seed initial admin user."""
    with app.app_context():
        print("Creating database tables...")
        db.drop_all() # Added db.drop_all() for a clean start
        db.create_all()
        print("Database tables created.")
        create_admin_user() # Call the renamed function
        print("Admin user setup complete.")

# Custom decorator for admin-only endpoints
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
                    print("DEBUG: current_user is None or empty.")
                    return {'message': 'Admin access required (identity missing)'}, 403
                
                if current_user.get('role') != 'admin':
                    print(f"DEBUG: User role '{current_user.get('role')}' is not 'admin'.")
                    return {'message': 'Admin access required (role mismatch)'}, 403
                
                print("DEBUG: Admin role check passed. Proceeding to endpoint.")
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"DEBUG: Exception caught in admin_required decorator: {e}")
                import traceback
                traceback.print_exc()
                return {'message': 'Authentication error processing token internally: ' + str(e)}, 401
        return decorator
    return wrapper

# Test route
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

# Register Resource
class Register(Resource):
    def post(self):
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
        new_user = User(email=email,password=hashed_password,full_name=full_name,qualification=qualification,dob=dob,role='user')
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201




#Login Resource 
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
    def get(self):
        subjects = Subject.query.all()
        return [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects], 200


    @admin_required()
    def post(self):
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
    def get(self, subject_id):
        subject = db.session.get(Subject, subject_id) # Using db.session.get
        if not subject:
            return {'message': 'Subject not found'}, 404
        return {'id': subject.id, 'name': subject.name, 'description': subject.description}, 200

    @admin_required()
    def put(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')

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
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        
        db.session.delete(subject)
        db.session.commit()
        return {'message': 'Subject deleted successfully'}, 204


##_______________create chapter resource____________________##
class ChaptersBySubject(Resource):
    @admin_required()
    def get(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return [{
            'id': c.id,
            'subject_id': c.subject_id,
            'name': c.name,
            'description': c.description
        } for c in chapters], 200

    @admin_required()
    def post(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

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
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
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
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        db.session.delete(chapter)
        db.session.commit()
        return {'message': 'Chapter deleted successfully'}, 204


class QuizzesByChapter(Resource):
    @admin_required()
    def get(self, chapter_id):
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return [{
            'id': q.id,
            'chapter_id': q.chapter_id,
            'title': q.title,
            'description': q.description,
            'time_duration': q.time_duration,
            'date_of_quiz': q.date_of_quiz.isoformat()
        } for q in quizzes], 200

    @admin_required()
    def post(self, chapter_id):
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

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
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        time_duration = data.get('time_duration')
        date_of_quiz_str = data.get('date_of_quiz')
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
        return {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'title': quiz.title,
            'description': quiz.description,
            'time_duration': quiz.time_duration,
            'date_of_quiz': quiz.date_of_quiz.isoformat()
        }, 200

    @admin_required()
    def delete(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        db.session.delete(quiz)
        db.session.commit()
        return {'message': 'Quiz deleted successfully'}, 204

# --- NEW API RESOURCES FOR QUESTIONS ---

# Resource for fetching all questions for a specific quiz, or adding a new question
class QuestionsByQuiz(Resource):
    @admin_required()
    def get(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return [{
            'id': q.id,
            'quiz_id': q.quiz_id,
            'question_text': q.question_text,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4,
            'correct_option': q.correct_option
        } for q in questions], 200

    @admin_required()
    def post(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        data = request.get_json()
        question_text = data.get('question_text')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = data.get('correct_option')

        if not all([question_text, option1, option2, correct_option is not None]): # Check correct_option is provided
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

# Resource for operations on a single question by its ID
class QuestionResource(Resource):
    @admin_required()
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
        question = db.session.get(Question, question_id)
        if not question:
            return {'message': 'Question not found'}, 404

        data = request.get_json()
        question_text = data.get('question_text')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = data.get('correct_option')
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
    def delete(self, question_id):
        question = db.session.get(Question, question_id)
        if not question:
            return {'message': 'Question not found'}, 404
        
        db.session.delete(question)
        db.session.commit()
        return {'message': 'Question deleted successfully'}, 204

# --- Admin-only User Management Resource ---

class AdminUsers(Resource):
    @admin_required()
    def get(self):
        users = User.query.all()
        return [{'id': u.id,'email': u.email,'full_name': u.full_name,'qualification': u.qualification,'dob': u.dob.isoformat() if u.dob else None,'role': getattr(u, 'role', 'N/A') # Use getattr to safely get 'role', default to 'N/A' if not found
            } for u in users], 200
    def options(self):
        return {'Allow': 'GET, POST, PUT, DELETE, OPTIONS'}, 200 # Include all methods your resource supports

class AdminUserResource(Resource):
    @admin_required()
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        # Optionally, delete user's scores or related records here if needed
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User with ID {user_id} deleted successfully'}, 204


class UserAccessibleSubjects(Resource):
        @jwt_required()
        def get(self):
            subjects = Subject.query.all()
            return [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects], 200


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

    # Resource for fetching chapters for regular users (not admin_required)
class UserAccessibleChaptersBySubject(Resource):
    @jwt_required()
    def get(self, subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return [{
            'id': c.id,
            'subject_id': c.subject_id,
            'name': c.name,
            'description': c.description
        } for c in chapters], 200

    # Resource for fetching quizzes for regular users (not admin_required)
class UserAccessibleQuizzesByChapter(Resource):
    @jwt_required()
    def get(self, chapter_id):
        chapter = db.session.get(Chapter, chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return [{
            'id': q.id,
            'chapter_id': q.chapter_id,
            'title': q.title,
            'description': q.description,
            'time_duration': q.time_duration,
            'date_of_quiz': q.date_of_quiz.isoformat()
        } for q in quizzes], 200

    # Resource for fetching questions for regular users (not admin_required)
class UserAccessibleQuestionsByQuiz(Resource):
    @jwt_required()
    def get(self, quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        # IMPORTANT: Do NOT send correct_option to the frontend for users
        return [{
            'id': q.id,
            'quiz_id': q.quiz_id,
            'question_text': q.question_text,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4,
            # 'correct_option': q.correct_option # <--- DO NOT SEND THIS FOR USERS
        } for q in questions], 200


class QuizAttemptSubmit(Resource):
    @jwt_required()
    def post(self):
        raw_identity = get_jwt_identity()
        current_user_identity = json.loads(raw_identity)
        user_id = current_user_identity['id']

        data = request.get_json()
        quiz_id = data.get('quiz_id')
        answers = data.get('answers') # List of {'question_id': ..., 'selected_option': ...}

        if not all([quiz_id, answers]):
            return {'message': 'Quiz ID and answers are required'}, 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        # Fetch all correct answers for this quiz's questions from the backend
        quiz_questions = Question.query.filter_by(quiz_id=quiz_id).all()
        correct_answers_map = {q.id: q.correct_option for q in quiz_questions}

        calculated_score = 0
        correct_answers_count = 0
        
        # Process and save each user answer, and calculate score
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            selected_option = answer_data.get('selected_option')

            if question_id not in correct_answers_map:
                # Skip if question doesn't belong to this quiz or is invalid
                continue

            # Save/Update UserAnswer
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
            
            # Calculate score
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
    def post(self):
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
            db.session.commit()
            return {'message': 'User answer updated successfully', 'answer_id': existing_answer.id}, 200
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


if __name__ == "__main__":
    app.run(debug=True)