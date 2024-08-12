from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import Column, DateTime, func

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    confirmed_email = Column(Boolean, default=False)
    role = Column(String, default='user')
    referral_code = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="user", cascade='all, delete')
    exams = relationship("Exams", backref="user")

class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    user = relationship("User", back_populates="subscriptions")

class Topic(db.Model):
    __tablename__ = 'topics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    sub_category_id = Column(UUID(as_uuid=True), ForeignKey('subcategory.id'),nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'sub_category': str(self.sub_category)
        }
    
    questions = relationship('Question', backref='topic')

class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    exam_category_id = Column(UUID(as_uuid=True), ForeignKey('examcategory.id'), nullable=False)

    topics = relationship('Topic', backref='subcategory')

class ExamCategory(db.Model):
    __tablename__ = 'examcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)

    subcategories = relationship('SubCategory', backref='examcategory')

class Exams(db.Model):
    __tablename__ = 'exams'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    createdBy = Column(String, nullable=False)
    createdOn = Column(String, nullable=False)
    exam_duration = Column(Integer)
    examiner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), default=uuid.uuid4)

    questions = relationship('Question', backref='exams')

class Question(db.Model):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_text = Column(String, nullable=False)
    choice1 = Column(String)
    choice2 = Column(String)
    choice3 = Column(String)
    choice4 = Column(String)
    isChoice = Column(Boolean)
    answer = Column(String)

    exam_id = Column(UUID(as_uuid=True), ForeignKey('exams.id'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('topics.id') ,default=uuid.uuid4)

class UserExamResult(db.Model):
    __tablename__ = 'user_exam_result'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    exam_id = Column(UUID(as_uuid=True), ForeignKey('exams.id'), nullable=False)
    grade = Column(Float)
