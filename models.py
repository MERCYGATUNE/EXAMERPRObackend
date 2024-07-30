from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    confirmed_email = Column(Boolean, default=False)
    role = Column(String)
    referral_code = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    scores = relationship("Score", back_populates="user")
    resources = relationship("Resource", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    user_answers = relationship("UserAnswers", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")

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

class AnswerMetadata(db.Model):
    __tablename__ = 'answermetadata'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    supporting_image = Column(String)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text)
    topic_id = Column(UUID(as_uuid=True))
    mode = Column(String)
    exam_mode = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    answers = relationship("Answers", back_populates="question")
    comments = relationship("Comment", back_populates="question")
    user_answers = relationship("UserAnswers", back_populates="question")

class Answers(db.Model):
    __tablename__ = 'answers'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    answer_type = Column(String)
    answer = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    question = relationship("Questions", back_populates="answers")

class UserAnswers(db.Model):
    __tablename__ = 'useranswers'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    answer_type = Column(String)
    answer = Column(Text)
    attempts = Column(Integer)
    
    question = relationship("Questions", back_populates="user_answers")
    user = relationship("User", back_populates="user_answers")

class UserParagraph(db.Model):
    __tablename__ = 'userparagraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))

class UserChoice(db.Model):
    __tablename__ = 'userchoice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))

class Topic(db.Model):
    __tablename__ = 'topic'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))
    sub_category_id = Column(UUID(as_uuid=True))

class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))
    exam_category_id = Column(UUID(as_uuid=True))

class ExamCategory(db.Model):
    __tablename__ = 'examcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))

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

class Comment(db.Model):
    __tablename__ = 'comment'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)

    question = relationship("Questions", back_populates="comments")
    user = relationship("User", back_populates="comments")

class PasswordReset(db.Model):
    __tablename__ = 'password_reset'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_triggered = Column(Boolean, nullable=False, default=False)
    request_satisfied = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    user = relationship("User", back_populates="password_resets")
