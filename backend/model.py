from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    qualifications = db.Column(db.String(500), nullable=True)
    dob = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<Subject {self.name}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    subject = db.relationship('Subject', backref=db.backref('chapters', lazy=True))

    def __repr__(self):
        return f'<Chapter {self.title}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns} 


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)

    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy=True))

    def __repr__(self):
        return f'<Quiz {self.title}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(200), nullable=False)

    quiz = db.relationship('Quiz', backref=db.backref('questions', lazy=True))

    def __repr__(self):
        return f'<Question {self.question_text}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('scores', lazy=True))
    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True))

    def __repr__(self):
        return f'<Score {self.score} for User {self.user_id} on Quiz {self.quiz_id}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

