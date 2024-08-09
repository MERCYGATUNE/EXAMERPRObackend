from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import Column, DateTime, func
from flask import Blueprint, request,jsonify
from flask_restful import Api
from models import User,Profile,Topic,SubCategory,Paragraph,


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
    
    

class Topic(db.Model):
    __tablename__ = 'topic'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    sub_category_id = Column(UUID(as_uuid=True), nullable=False)
   
def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'sub_category_id': self.sub_category_id
        }    
     

class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))
    exam_category_id = Column(UUID(as_uuid=True))  
    
def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'exam_category_id': self.exam_category_id
        }    
    
class Paragraph(db.Model):
    __tablename__ = 'paragraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
def to_dict(self):
        return {
            'id': self.id,
            'paragraph': self.paragraph,
            'answer_id': self.answer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }    
    
    
    

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
   
def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question': self.question.to_dict() if self.question else None,
            'user': self.user.to_dict() if self.user else None
        }    
    
class ExamCategory(db.Model):
    __tablename__ = 'examcategory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True))
    
def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        } 

class Choice(db.Model):
    __tablename__ = 'choice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)  
    
def to_dict(self):
        return {
            'id': self.id,
            'choice': self.choice,
            'answer_id': self.answer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
            'id': self.id,
            'topic_id': self.topic_id,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'short_desc': self.short_desc,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }    

class PasswordReset(db.Model):
    __tablename__ = 'password_reset'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_triggered = Column(Boolean, nullable=False, default=False)
    request_satisfied = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    user = relationship("User", back_populates="password_resets")
    
def to_dict(self):
        return {
            'id': self.id,
            'request_triggered': self.request_triggered,
            'request_satisfied': self.request_satisfied,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None
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
            'id': self.id,
            'description': self.description,
            'supporting_image': self.supporting_image,
            'answer_id': self.answer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
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
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'answer_type': self.answer_type,
            'answer': self.answer,
            'attempts': self.attempts,
            'question': self.question.to_dict() if self.question else None,
            'user': self.user.to_dict() if self.user else None
        }    
    
    
class UserParagraph(db.Model):
    __tablename__ = 'userparagraph'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    paragraph = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    
    
def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'paragraph': self.paragraph,
            'answer_id': self.answer_id
        }    

class UserChoice(db.Model):
    __tablename__ = 'userchoice'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'), nullable=False)
    choice = Column(Text)
    answer_id = Column(UUID(as_uuid=True))
    
def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'choice': self.choice,
            'answer_id': self.answer_id
        }

# Routes for Profile
@app.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = Profile.query.all()
    return jsonify([profile.to_dict() for profile in profiles])

@app.route('/profiles/<uuid:profile_id>', methods=['GET'])
def get_profile(profile_id):
    profile = Profile.query.get(profile_id)
    if profile:
        return jsonify(profile.to_dict())
    else:
        return jsonify({"error": "Profile not found"}), 404

@app.route('/profiles', methods=['POST'])
def create_profile():
    data = request.get_json()
    new_profile = Profile(
        user_id=data['user_id'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        photo_url=data.get('photo_url'),
        title=data.get('title'),
        created_at=datetime.utcnow()
    )
    db.session.add(new_profile)
    db.session.commit()
    return jsonify(new_profile.to_dict()), 201

@app.route('/profiles/<uuid:profile_id>', methods=['PUT'])

def update_profile(profile_id):
    data = request.get_json()
    profile = Profile.query.get(profile_id)
    if profile:
        profile.first_name = data.get('first_name', profile.first_name)
        profile.last_name = data.get('last_name', profile.last_name)
        profile.photo_url = data.get('photo_url', profile.photo_url)
        profile.title = data.get('title', profile.title)
        db.session.commit()
        return jsonify(profile.to_dict())
    else:
        return jsonify({"error": "Profile not found"}), 404

@app.route('/profiles/<uuid:profile_id>', methods=['DELETE'])

def delete_profile(profile_id):
    profile = Profile.query.get(profile_id)
    if profile:
        db.session.delete(profile)
        db.session.commit()
        return jsonify({"message": "Profile deleted"})
    else:
        return jsonify({"error": "Profile not found"}), 404



@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        email=data['email'],
        password=data['password'],
        confirmed_email=data.get('confirmed_email', False),
        role=data.get('role', 'user'),
        referral_code=data.get('referral_code'),
        created_at=datetime.utcnow()
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/users/<uuid:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user:
        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        user.confirmed_email = data.get('confirmed_email', user.confirmed_email)
        user.role = data.get('role', user.role)
        user.referral_code = data.get('referral_code', user.referral_code)
        db.session.commit()
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404






    
@app.route('/examcategories', methods=['GET'])
def get_exam_categories():
    exam_categories = ExamCategory.query.all()
    return jsonify([{
        'id': ec.id,
        'name': ec.name,
        'description': ec.description,
        'user_id': ec.user_id
    } for ec in exam_categories])
    
@app.route('/examcategories/<uuid:exam_category_id>', methods=['GET'])
def get_exam_category(exam_category_id):
    exam_category = ExamCategory.query.get(exam_category_id)
    if exam_category:
        return jsonify({
            'id': exam_category.id,
            'name': exam_category.name,
            'description': exam_category.description,
            'user_id': exam_category.user_id
        })
    else:
        return jsonify({"error": "Exam category not found"}), 404
    
    


@app.route('/subcategories/<uuid:sub_category_id>', methods=['GET'])
def get_subcategory(sub_category_id):
    sub_category = SubCategory.query.get(sub_category_id)
    if sub_category:
        return jsonify({
            'id': sub_category.id,
            'name': sub_category.name,
            'description': sub_category.description,
            'user_id': sub_category.user_id,
            'exam_category_id': sub_category.exam_category_id
        })
    else:
        return jsonify({"error": "Subcategory not found"}), 404


    
@app.route('/topics', methods=['GET'])
def get_topics():
    topics = Topic.query.all()
    return jsonify([{
        'id': topic.id,
        'name': topic.name,
        'description': topic.description,
        'user_id': topic.user_id,
        'sub_category_id': topic.sub_category_id
    } for topic in topics])

@app.route('/topics/<uuid:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = Topic.query.get(topic_id)
    if topic:
        return jsonify({
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'user_id': topic.user_id,
            'sub_category_id': topic.sub_category_id
        })
    else:
        return jsonify({"error": "Topic not found"}), 404
    
@app.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    new_comment = Comment(
        question_id=data['question_id'],
        user_id=data['user_id'],
        description=data['description'],
        created_at=datetime.utcnow()
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.to_dict()), 201

@app.route('/comments/<uuid:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.get_json()
    comment = Comment.query.get(comment_id)
    if comment:
        comment.description = data.get('description', comment.description)
        db.session.commit()
        return jsonify(comment.to_dict())
    else:
        return jsonify({"error": "Comment not found"}), 404

@app.route('/comments/<uuid:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted"})
    else:
        return jsonify({"error": "Comment not found"}), 404
  
#  Routes for Questions
@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Questions.query.all()
    return jsonify([question.to_dict() for question in questions])

@app.route('/questions/<uuid:question_id>', methods=['GET'])
def get_question(question_id):
    question = Questions.query.get(question_id)
    if question:
        return jsonify(question.to_dict())
    else:
        return jsonify({"error": "Question not found"}), 404


@app.route('/answers', methods=['POST'])
def create_answer():
    data = request.get_json()
    new_answer = Answers(
        question_id=data['question_id'],
        answer_type=data.get('answer_type'),
        answer=data.get('answer'),
        created_at=datetime.utcnow()
    )
    db.session.add(new_answer)
    db.session.commit()
    return jsonify(new_answer.to_dict()), 201

@app.route('/answers/<uuid:answer_id>', methods=['PUT'])
def update_answer(answer_id):
    data = request.get_json()
    answer = Answers.query.get(answer_id)
    if answer:
        answer.answer_type = data.get('answer_type', answer.answer_type)
        answer.answer = data.get('answer', answer.answer)
        db.session.commit()
        return jsonify(answer.to_dict())
    else:
        return jsonify({"error": "Answer not found"}), 404

@app.route('/answers/<uuid:answer_id>', methods=['DELETE'])
def delete_answer(answer_id):
    answer = Answers.query.get(answer_id)
    if answer:
        db.session.delete(answer)
        db.session.commit()
        return jsonify({"message": "Answer deleted"})
    else:
        return jsonify({"error": "Answer not found"}), 404
    
@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    subscriptions = Subscription.query.all()
    return jsonify([to_dict(subscription) for subscription in subscriptions]), 200

@app.route('/subscriptions/<uuid:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    return jsonify(to_dict(subscription)), 200


# Payment CRUD Operations
@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    new_payment = payment(
        user_id=data['user_id'],
        subscription_id=data.get('subscription_id'),
        amount=data['amount'],
        expires_at=data.get('expires_at'),
        payment_type=data.get('payment_type')
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(to_dict(new_payment)), 201

@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([to_dict(payment) for payment in payments]), 200

@app.route('/payments/<uuid:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.get_json()
    payment = Payment.query.get_or_404(payment_id)
    if 'user_id' in data:
        payment.user_id = data['user_id']
    if 'subscription_id' in data:
        payment.subscription_id = data['subscription_id']
    if 'amount' in data:
        payment.amount = data['amount']
    if 'expires_at' in data:
        payment.expires_at = data['expires_at']
    if 'payment_type' in data:
        payment.payment_type = data['payment_type']
    db.session.commit()
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    return '', 204

# Score CRUD Operations
@app.route('/scores', methods=['POST'])
def create_score():
    data = request.get_json()
    new_score = Score(
        user_id=data['user_id'],
        topic_id=data.get('topic_id'),
        possible_score=data['possible_score'],
        user_score=data['user_score'],
        completion_rate=data.get('completion_rate')
    )
    db.session.add(new_score)
    db.session.commit()
    return jsonify(to_dict(new_score)), 201


@app.route('/scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    return jsonify([to_dict(score) for score in scores]), 200

@app.route('/scores/<uuid:score_id>', methods=['GET'])
def get_score(score_id):
    score = Score.query.get_or_404(score_id)
    return jsonify(to_dict(score)), 200

@app.route('/scores/<uuid:score_id>', methods=['PUT'])
def update_score(score_id):
    data = request.get_json()
    score = Score.query.get_or_404(score_id)
    if 'user_id' in data:
        score.user_id = data['user_id']
    if 'topic_id' in data:
        score.topic_id = data['topic_id']
    if 'possible_score' in data:
        score.possible_score = data['possible_score']
    if 'user_score' in data:
        score.user_score = data['user_score']
    if 'completion_rate' in data:
        score.completion_rate = data['completion_rate']
    db.session.commit()
    return jsonify(to_dict(score)), 200


@app.route('/resources', methods=['GET'])
def get_resources():
    resources = Resource.query.all()
    return jsonify([to_dict(resource) for resource in resources]), 200

@app.route('/resources/<uuid:resource_id>', methods=['GET'])
def get_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    return jsonify(to_dict(resource)), 200


# Referral CRUD Operations
@app.route('/referrals', methods=['POST'])
def create_referral():
    data = request.get_json()
    new_referral = Referral(
        user_id=data['user_id'],
        referred_user_email=data['referred_user_email'],
        status=data.get('status', 'pending')
    )
    db.session.add(new_referral)
    db.session.commit()
    return jsonify(to_dict(new_referral)), 201


@app.route('/referrals', methods=['GET'])
def get_referrals():
    referrals = Referral.query.all()
    return jsonify([to_dict(referral) for referral in referrals]), 200

@app.route('/referrals/<uuid:referral_id>', methods=['GET'])
def get_referral(referral_id):
    referral = Referral.query.get_or_404(referral_id)
    return jsonify(to_dict(referral)), 200

@app.route('/referrals/<uuid:referral_id>', methods=['PUT'])
def update_referral(referral_id):
    data = request.get_json()
    referral = Referral.query.get_or_404(referral_id)
    if 'user_id' in data:
        referral.user_id = data['user_id']
    if 'referred_user_email' in data:
        referral.referred_user_email = data['referred_user_email']
    if 'status' in data:
        referral.status = data['status']
    db.session.commit()
    return jsonify(to_dict(referral)), 200

@app.route('/referrals/<uuid:referral_id>', methods=['DELETE'])
def delete_referral(referral_id):
    referral = Referral.query.get_or_404(referral_id)
    db.session.delete(referral)
    db.session.commit()
    return '', 204


# AnswerMetadata CRUD Operations
@app.route('/answer_metadata', methods=['POST'])
def create_answer_metadata():
    data = request.get_json()
    new_answer_metadata = AnswerMetadata(
        question_id=data['question_id'],
        answer_id=data['answer_id'],
        metadata=data.get('metadata')
    )
    db.session.add(new_answer_metadata)
    db.session.commit()
    return jsonify(to_dict(new_answer_metadata)), 


@app.route('/answer_metadata', methods=['GET'])
def get_answer_metadata():
    answer_metadata = AnswerMetadata.query.all()
    return jsonify([to_dict(am) for am in answer_metadata]), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['GET'])
def get_answer_metadata_by_id(answer_metadata_id):
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    return jsonify(to_dict(answer_metadata)), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['PUT'])
def update_answer_metadata(answer_metadata_id):
    data = request.get_json()
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    if 'question_id' in data:
        answer_metadata.question_id = data['question_id']
    if 'answer_id' in data:
        answer_metadata.answer_id = data['answer_id']
    if 'metadata' in data:
        answer_metadata.metadata = data['metadata']
    db.session.commit()
    return jsonify(to_dict(answer_metadata)), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['DELETE'])
def delete_answer_metadata(answer_metadata_id):
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    db.session.delete(answer_metadata)
    db.session.commit()
    return '', 204


@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Questions.query.all()
    return jsonify([to_dict(question) for question in questions]), 200

@app.route('/questions/<uuid:question_id>', methods=['GET'])
def get_question(question_id):
    question = Questions.query.get_or_404(question_id)
    return jsonify(to_dict(question)), 200


# Answers CRUD Operations
@app.route('/answers', methods=['POST'])
def create_answer():
    data = request.get_json()
    new_answer = Answers(
        text=data['text'],
        question_id=data['question_id'],
        is_correct=data.get('is_correct', False)
    )
    db.session.add(new_answer)
    db.session.commit()
    return jsonify(to_dict(new_answer)), 201

@app.route('/answers', methods=['GET'])
def get_answers():
    answers = Answers.query.all()
    return jsonify([to_dict(answer) for answer in answers]), 200

@app.route('/answers/<uuid:answer_id>', methods=['GET'])
def get_answer(answer_id):
    answer = Answers.query.get_or_404(answer_id)
    return jsonify(to_dict(answer)), 200

@app.route('/answers/<uuid:answer_id>', methods=['PUT'])
def update_answer(answer_id):
    data = request.get_json()
    answer = Answers.query.get_or_404(answer_id)
    if 'text' in data:
        answer.text = data['text']
    if 'question_id' in data:
        answer.question_id = data['question_id']
    if 'is_correct' in data:
        answer.is_correct = data['is_correct']
    db.session.commit()
    return jsonify(to_dict(answer)), 200

@app.route('/answers/<uuid:answer_id>', methods=['DELETE'])
def delete_answer(answer_id):
    answer = Answers.query.get_or_404(answer_id)
    db.session.delete(answer)
    db.session.commit()
    return '', 204

# UserParagraph CRUD Operations
@app.route('/user_paragraphs', methods=['POST'])
def create_user_paragraph():
    data = request.get_json()
    new_user_paragraph = UserParagraph(
        user_id=data['user_id'],
        paragraph_id=data['paragraph_id'],
        is_read=data.get('is_read', False)
    )
    db.session.add(new_user_paragraph)
    db.session.commit()
    return jsonify(to_dict(new_user_paragraph)), 201

@app.route('/user_paragraphs', methods=['GET'])
def get_user_paragraphs():
    user_paragraphs = UserParagraph.query.all()
    return jsonify([to_dict(up) for up in user_paragraphs]), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['GET'])
def get_user_paragraph(user_paragraph_id):
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    return jsonify(to_dict(user_paragraph)), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['PUT'])
def update_user_paragraph(user_paragraph_id):
    data = request.get_json()
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    if 'user_id' in data:
        user_paragraph.user_id = data['user_id']
    if 'paragraph_id' in data:
        user_paragraph.paragraph_id = data['paragraph_id']
    if 'is_read' in data:
        user_paragraph.is_read = data['is_read']
    db.session.commit()
    return jsonify(to_dict(user_paragraph)), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['DELETE'])
def delete_user_paragraph(user_paragraph_id):
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    db.session.delete(user_paragraph)
    db.session.commit()
    return '', 204

# Payment CRUD Operations
@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    new_payment = Payment(
        user_id=data['user_id'],
        subscription_id=data.get('subscription_id'),
        amount=data['amount'],
        expires_at=data.get('expires_at'),
        payment_type=data.get('payment_type')
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(to_dict(new_payment)), 201

@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([to_dict(payment) for payment in payments]), 200

@app.route('/payments/<uuid:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.get_json()
    payment = Payment.query.get_or_404(payment_id)
    if 'user_id' in data:
        payment.user_id = data['user_id']
    if 'subscription_id' in data:
        payment.subscription_id = data['subscription_id']
    if 'amount' in data:
        payment.amount = data['amount']
    if 'expires_at' in data:
        payment.expires_at = data['expires_at']
    if 'payment_type' in data:
        payment.payment_type = data['payment_type']
    db.session.commit()
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    return '', 204

@app.route('/choices', methods=['GET'])
def get_choices():
    choices = Choice.query.all()
    return jsonify([to_dict(choice) for choice in choices]), 200

@app.route('/choices/<uuid:choice_id>', methods=['GET'])
def get_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    return jsonify(to_dict(choice)), 200

@app.route('/choices/<uuid:choice_id>', methods=['PUT'])
def update_choice(choice_id):
    data = request.get_json()
    choice = Choice.query.get_or_404(choice_id)
    if 'text' in data:
        choice.text = data['text']
    if 'question_id' in data:
        choice.question_id = data['question_id']
    if 'is_correct' in data:
        choice.is_correct = data['is_correct']
    db.session.commit()
    return jsonify(to_dict(choice)), 200

@app.route('/choices/<uuid:choice_id>', methods=['DELETE'])
def delete_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    db.session.delete(choice)
    db.session.commit()
    return '', 204

# AnswerMetadata CRUD Operations
@app.route('/answer_metadata', methods=['POST'])
def create_answer_metadata():
    data = request.get_json()
    new_answer_metadata = AnswerMetadata(
        question_id=data['question_id'],
        answer_id=data['answer_id'],
        metadata=data.get('metadata')
    )
    db.session.add(new_answer_metadata)
    db.session.commit()
    return jsonify(to_dict(new_answer_metadata)), 201

@app.route('/answer_metadata', methods=['GET'])
def get_answer_metadata():
    answer_metadata = AnswerMetadata.query.all()
    return jsonify([to_dict(am) for am in answer_metadata]), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['GET'])
def get_answer_metadata_by_id(answer_metadata_id):
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    return jsonify(to_dict(answer_metadata)), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['PUT'])
def update_answer_metadata(answer_metadata_id):
    data = request.get_json()
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    if 'question_id' in data:
        answer_metadata.question_id = data['question_id']
    if 'answer_id' in data:
        answer_metadata.answer_id = data['answer_id']
    if 'metadata' in data:
        answer_metadata.metadata = data['metadata']
    db.session.commit()
    return jsonify(to_dict(answer_metadata)), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['DELETE'])
def delete_answer_metadata(answer_metadata_id):
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    db.session.delete(answer_metadata)
    db.session.commit()
    return '', 204


# Define Blueprints

profile_bp = Blueprint('profile', __name__ ,url_prefix='/profiles' )
user_bp = Blueprint('user', __name__ ,url_prefix='/users')
exam_category_bp = Blueprint('exam_category', __name__ ,url_prefix='/examcategories')
subcategory_bp = Blueprint('subcategory', __name__ url_prefix='/subcategories')
topic_bp = Blueprint('topic', __name__ ,url_prefix='/topics')
comment_bp = Blueprint('comment', __name__ ,url_prefix='/comments')
question_bp = Blueprint('question', __name__ ,url_prefix='/questions')
answer_bp = Blueprint('answer', __name__ ,url_prefix='/answers')
subscription_bp = Blueprint('subscription', __name__, url_prefix='/subscriptions')
payment_bp = Blueprint('payment', __name__ ,url_prefix='/payments')
score_bp = Blueprint('score', __name__ ,url_prefix='/scores')
resource_bp = Blueprint('resource', __name__ ,url_prefix='/resources')
referral_bp = Blueprint('referral', __name__ ,url_prefix='/referrals')
answer_metadata_bp = Blueprint('answer_metadata', __name__, url_prefix='/answermetadata')
choice_bp = Blueprint('choice', __name__ ,url_prefix='/choices')
user_paragraph_bp = Blueprint('user_paragraph', __name__ ,url_prefix='/userparagraphs')

profile_api=Api(profile_bp)




























    

    
    
    
    
    
    
    
    
    
     