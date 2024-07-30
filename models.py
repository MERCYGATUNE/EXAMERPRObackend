from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    confirmed_email = db.Column(db.Boolean, default=False)
    role = db.Column(db.String)
    referral_code = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", back_populates="user", uselist=False)
    notifications = db.relationship("Notification", back_populates="user")
    subscriptions = db.relationship("Subscription", back_populates="user")
    payments = db.relationship("Payment", back_populates="user")
    scores = db.relationship("Score", back_populates="user")
    resources = db.relationship("Resource", back_populates="user")

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    photo_url = db.Column(db.String)
    title = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="profile")

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    subject = db.Column(db.String)
    body = db.Column(db.Text)
    sender_id = db.Column(UUID(as_uuid=True))
    sender_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.String)
    amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))

    user = db.relationship("User", back_populates="subscriptions")

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    subscription_id = db.Column(UUID(as_uuid=True))
    amount = db.Column(db.Float)
    expires_at = db.Column(db.DateTime)
    payment_type = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="payments")

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    topic_id = db.Column(UUID(as_uuid=True))
    possible_score = db.Column(db.Float)
    user_score = db.Column(db.Float)
    completion_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="scores")

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = db.Column(UUID(as_uuid=True))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    resource_type = db.Column(db.String)
    short_desc = db.Column(db.String)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="resources")

class Referral(db.Model):
    __tablename__ = 'referrals'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_code = db.Column(db.String, unique=True)
    points_earned = db.Column(db.Integer)
    redeemed = db.Column(db.Boolean, default=False)

class AnswerMetadata(db.Model):
    __tablename__ = 'answer_metadata'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = db.Column(db.Text)
    supporting_image = db.Column(db.String)
    answer_id = db.Column(UUID(as_uuid=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = db.Column(db.Text)
    topic_id = db.Column(UUID(as_uuid=True))
    mode = db.Column(db.String)
    exam_mode = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'))
    answer_type = db.Column(db.String)
    answer = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    answer_type = db.Column(db.String)
    answer = db.Column(db.Text)
    attempts = db.Column(db.Integer)

class UserParagraph(db.Model):
    __tablename__ = 'user_paragraphs'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'))
    paragraph = db.Column(db.Text)
    answer_id = db.Column(UUID(as_uuid=True))

class UserChoice(db.Model):
    __tablename__ = 'user_choices'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'))
    choice = db.Column(db.Text)
    answer_id = db.Column(UUID(as_uuid=True))

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    user_id = db.Column(UUID(as_uuid=True))
    sub_category_id = db.Column(UUID(as_uuid=True))

class SubCategory(db.Model):
    __tablename__ = 'sub_categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    user_id = db.Column(UUID(as_uuid=True))
    exam_category_id = db.Column(UUID(as_uuid=True))

class ExamCategory(db.Model):
    __tablename__ = 'exam_categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    user_id = db.Column(UUID(as_uuid=True))

class Choice(db.Model):
    __tablename__ = 'choices'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    choice = db.Column(db.Text)
    answer_id = db.Column(UUID(as_uuid=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Paragraph(db.Model):
    __tablename__ = 'paragraphs'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph = db.Column(db.Text)
    answer_id = db.Column(UUID(as_uuid=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_triggered = db.Column(db.Boolean, nullable=False, default=False)
    request_satisfied = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)