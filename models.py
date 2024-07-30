from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    confirmed_email = Column(Boolean, default=False)
    role = Column(String)
    referral_code = Column(String)
    created_at = Column(DateTime)

    profile = relationship("Profile", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    scores = relationship("Score", back_populates="user")
    resources = relationship("Resource", back_populates="user")

class Profile(Base):
    __tablename__ = 'profile'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    first_name = Column(String)
    last_name = Column(String)
    photo_url = Column(String)
    title = Column(String)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="profile")

class Notification(Base):
    __tablename__ = 'notification'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    subject = Column(String)
    body = Column(Text)
    sender_id = Column(UUID(as_uuid=True))
    sender_name = Column(String)
    created_at = Column(DateTime)
    user = relationship("User", back_populates="notifications")

class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    subscription_id = Column(UUID(as_uuid=True))
    amount = Column(Float)
    expires_at = Column(DateTime)
    payment_type = Column(String)
    created_at = Column(DateTime)
    user = relationship("User", back_populates="payments")

class Score(Base):
    __tablename__ = 'score'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    topic_id = Column(UUID(as_uuid=True))
    possible_score = Column(Float)
    user_score = Column(Float)
    completion_rate = Column(Float)
    created_at = Column(DateTime)
    user = relationship("User", back_populates="scores")

class Resource(Base):
    __tablename__ = 'resource'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    resource_type = Column(String)
    short_desc = Column(String)
    details = Column(Text)
    created_at = Column(DateTime)
    user = relationship("User", back_populates="resources")

class Referral(Base):
    __tablename__ = 'referral'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_code = Column(String)
    points_earned = Column(Integer)
    redeemed = Column(Boolean)

class AnswerMetadata(Base):
    __tablename__ = 'answermetadata'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    supporting_image = Column(String)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Questions(Base):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text)
    topic_id = Column(UUID(as_uuid=True))
    mode = Column(String)
    exam_mode = Column(String)
    created_at = Column(DateTime)

class Answers(Base):
    __tablename__ = 'answers'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    answer_type = Column(String)
    answer = Column(Text)
    created_at = Column(DateTime)

class UserAnswers(Base):
    __tablename__ = 'useranswers'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    answer_type = Column(String)
    answer = Column(Text)
    attempts = Column(Integer)

class UserParagraph(Base):
    __tablename__ = 'userparagraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))

class UserChoice(Base):
    __tablename__ = 'userchoice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))

class Topic(Base):
    __tablename__ = 'topic'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))
    sub_category_id = Column(UUID(as_uuid=True))

class SubCategory(Base):
    __tablename__ = 'subcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))
    exam_category_id = Column(UUID(as_uuid=True))

class ExamCategory(Base):
    __tablename__ = 'examcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))

class Choice(Base):
    __tablename__ = 'choice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Paragraph(Base):
    __tablename__ = 'paragraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
class Comment(Base):
    __tablename__ = 'comment'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

class PasswordReset(Base):
    __tablename__ = 'password_reset'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_triggered = Column(Boolean, nullable=False, default=False)
    request_satisfied = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
