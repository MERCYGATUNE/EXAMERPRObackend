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
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    confirmed_email = Column(Boolean, default=False)
    role = Column(String, default='user')
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
def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'password': self.password,  
            'confirmed_email': self.confirmed_email,
            'role': self.role,
            'referral_code': self.referral_code,
            'created_at': self.created_at.isoformat(),
            'profile': self.profile.to_dict() if self.profile else None,
            'notifications': [notification.to_dict() for notification in self.notifications],
            'subscriptions': [subscription.to_dict() for subscription in self.subscriptions],
            'payments': [payment.to_dict() for payment in self.payments],
            'scores': [score.to_dict() for score in self.scores],
            'resources': [resource.to_dict() for resource in self.resources],
            'comments': [comment.to_dict() for comment in self.comments],
            'user_answers': [user_answer.to_dict() for user_answer in self.user_answers],
            'password_resets': [password_reset.to_dict() for password_reset in self.password_resets]
        }
 
 
    
    
    
    
    
    

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
    
def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'photo_url': self.photo_url,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }    
    


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
    
def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'body': self.body,
            'sender_id': str(self.sender_id) if self.sender_id else None,
            'sender_name': self.sender_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }    
    

class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    user = relationship("User", back_populates="subscriptions")

def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'user_id': self.user_id
        }    
    
    
    
    

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
    
def to_dict(self):
        return {
            'id': self.id,  
            'user_id': self.user_id,  
            'subscription_id': self.subscription_id,  
            'amount': self.amount,  
            'expires_at': self.expires_at,  
            'payment_type': self.payment_type,  
            'created_at': self.created_at,  
        }    
    
    
    

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
    
def to_dict(self):
        return {
            'id': self.id,  
            'user_id': self.user_id,  
            'topic_id': self.topic_id,  
            'possible_score': self.possible_score,  
            'user_score': self.user_score,  
            'completion_rate': self.completion_rate,  
            'created_at': self.created_at  
        }    
    
    

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
    
def to_dict(self):
        return {
            'id': str(self.id),
            'topic_id': str(self.topic_id) if self.topic_id else None,
            'user_id': str(self.user_id),
            'resource_type': self.resource_type,
            'short_desc': self.short_desc,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None  # Assuming User has a to_dict method
        }    
    
    
    

class Referral(db.Model):
    __tablename__ = 'referral'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_code = Column(String)
    points_earned = Column(Integer)
    redeemed = Column(Boolean)
    
def to_dict(self):
        return {
            'id': str(self.id),
            'referral_code': self.referral_code,
            'points_earned': self.points_earned,
            'redeemed': self.redeemed
        }    
    

class AnswerMetadata(db.Model):
    __tablename__ = 'answermetadata'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    supporting_image = Column(String)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
def to_dict(self):
        return {
            'id': str(self.id),
            'description': self.description,
            'supporting_image': self.supporting_image,
            'answer_id': str(self.answer_id),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }    
    
    

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

    def to_dict(self):
        return {
            'id': str(self.id),
            'question': self.question,
            'topic_id': str(self.topic_id) if self.topic_id else None,
            'mode': self.mode,
            'exam_mode': self.exam_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            
        }



class Answers(db.Model):
    __tablename__ = 'answers'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    answer_type = Column(String)
    answer = Column(Text)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    question = relationship("Questions", back_populates="answers")

    def to_dict(self):
        return {
            'id': str(self.id),
            'question_id': str(self.question_id),
            'answer_type': self.answer_type,
            'answer': self.answer,
            'created_at': self.created_at.isoformat()
        }


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
    
    

def to_dict(self):
        return {
            'id': str(self.id),
            'question_id': str(self.question_id),
            'user_id': str(self.user_id),
            'answer_type': self.answer_type,
            'answer': self.answer,
            'attempts': self.attempts,
            'question': self.question.to_dict() if self.question else None,  # Assuming Questions has a to_dict method
            'user': self.user.to_dict() if self.user else None  # Assuming User has a to_dict method
        }    

class UserParagraph(db.Model):
    __tablename__ = 'userparagraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    
def to_dict(self):
        return {
            'id': str(self.id),
            'question_id': str(self.question_id),
            'paragraph': self.paragraph,
            'answer_id': str(self.answer_id) if self.answer_id else None
        }
    
    
    

class UserChoice(db.Model):
    __tablename__ = 'userchoice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    
def to_dict(self):
        return {
            'id': str(self.id),
            'question_id': str(self.question_id),
            'choice': self.choice,
            'answer_id': str(self.answer_id) if self.answer_id else None
        }    
    

class Topic(db.Model):
    __tablename__ = 'topic'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    sub_category_id = Column(UUID(as_uuid=True), nullable=False)
    
def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'user_id': str(self.user_id),
            'sub_category_id': str(self.sub_category_id)
        }    
    

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