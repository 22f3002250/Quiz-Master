from extensions import db
from sqlalchemy.sql import func
# --- MODIFIED: Ensure datetime and date are imported ---
from datetime import datetime, date 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # Stores hashed password
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    
    role = db.Column(db.String(20), default='user', nullable=False)

    scores_attempted = db.relationship('Score', backref='user', lazy=True, cascade="all, delete-orphan")
    user_answers = db.relationship('UserAnswer', backref='user', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f'<User {self.full_name}>'

    def as_dict(self):
        data = {c.key: getattr(self, c.key) for c in self.__table__.columns if c.key != 'password'}
        
        if isinstance(self.dob, date): 
            data['dob'] = self.dob.isoformat()
        else:
            data['dob'] = None
        return data


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) 
    def __repr__(self):
        return f'<Admin {self.username}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns if c.key != 'password'}


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    chapters = db.relationship('Chapter', back_populates='subject', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Subject {self.name}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    subject = db.relationship('Subject', back_populates='chapters')

    quizzes = db.relationship('Quiz', back_populates='chapter', cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint('subject_id', 'name', name='_subject_chapter_name_uc'),)


    def __repr__(self):
        return f'<Chapter {self.name}>'

    def as_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'name': self.name,
            'description': self.description
        }


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    time_duration = db.Column(db.Integer, nullable=False)  # in seconds
    date_of_quiz = db.Column(db.DateTime, server_default=func.now())

    chapter = db.relationship('Chapter', back_populates='quizzes')

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")
    user_answers = db.relationship('UserAnswer', backref='quiz', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Quiz {self.title}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False) 

    def __repr__(self):
        return f'<Question {self.question_text}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.Integer, nullable=False) # Stores 1, 2, 3, or 4
    attempt_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    question = db.relationship('Question', backref=db.backref('user_answers', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', 'question_id', name='_user_quiz_question_uc'),)

    def __repr__(self):
        return f'<UserAnswer User:{self.user_id} Quiz:{self.quiz_id} Q:{self.question_id} Opt:{self.selected_option}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    attempt_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Score {self.score} for User {self.user_id} on Quiz {self.quiz_id}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}
