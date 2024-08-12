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

    profile = relationship("Profile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user", cascade='all, delete')
    payments = relationship("Payment", back_populates="user")
    scores = relationship("Score", back_populates="user")
    resources = relationship("Resource", back_populates="user")
    exams = relationship("Exams", backref="user")

class Profile(db.Model):
    __tablename__ = 'profile'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    photo_url = Column(String)
    title = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class Notification(db.Model):
    __tablename__ = 'notification'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    subject = Column(String)
    body = Column(Text)
    sender_id = Column(UUID(as_uuid=True))
    sender_name = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")

class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    user = relationship("User", back_populates="subscriptions")

class Payment(db.Model):
    __tablename__ = 'payment'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    subscription_id = Column(UUID(as_uuid=True))
    amount = Column(Float)
    expires_at = Column(DateTime)
    payment_type = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    user = relationship("User", back_populates="payments")

class Score(db.Model):
    __tablename__ = 'score'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    topic_id = Column(UUID(as_uuid=True))
    possible_score = Column(Float)
    user_score = Column(Float)
    completion_rate = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    user = relationship("User", back_populates="scores")

class Resource(db.Model):
    __tablename__ = 'resource'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    resource_type = Column(String)
    short_desc = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    user = relationship("User", back_populates="resources")

class Referral(db.Model):
    __tablename__ = 'referral'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_code = Column(String)
    points_earned = Column(Integer)
    redeemed = Column(Boolean)

# class AnswerMetadata(db.Model):
#     __tablename__ = 'answermetadata'
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     description = Column(Text)
#     supporting_image = Column(String)
#     answer_id = Column(UUID(as_uuid=True))
#     created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
#     updated_at = Column(DateTime)

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


# class Answers(db.Model):
#     __tablename__ = 'answers'
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
#     answer_type = Column(String)
#     answer = Column(Text)
#     created_at = Column(DateTime, default=func.now(), nullable=False)

#     question = relationship("Questions", back_populates="answers")

#     def to_dict(self):
#         return {
#             'id': str(self.id),
#             'question_id': str(self.question_id),
#             'answer_type': self.answer_type,
#             'answer': self.answer,
#             'created_at': self.created_at.isoformat()
#         }


class UserChoice(db.Model):
    __tablename__ = 'userchoice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))


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
    # user_id = Column(UUID(as_uuid=True))

    subcategories = relationship('SubCategory', backref='examcategory')

class Choice(db.Model):
    __tablename__ = 'choice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)

class Paragraph(db.Model):
    __tablename__ = 'paragraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)


class Exams(db.Model):
    __tablename__ = 'exams'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    createdBy = Column(String, nullable=False)
    createdOn = Column(String, nullable=False)
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
