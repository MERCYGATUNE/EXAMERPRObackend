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
from models import User,Profile,Topic,SubCategory,Paragraph,Comment,ExamCategory,Choice,Resource,Referral,PasswordReset,Payment,Questions,Answers,UserAnswers,AnswerMetadata


db = SQLAlchemy()
migrate = Migrate()


# Define Blueprints
student_bp=Blueprint('student_bp',__name__,url_prefix='/student')
student_api=Api(student_bp)




# Profile Resource
class ProfileResource(Resource):
    def get(self, profile_id=None):
        if profile_id:
            profile = Profile.query.get(profile_id)
            if profile:
                return jsonify(profile.to_dict())
            else:
                return jsonify({"error": "Profile not found"}), 404
        else:
            profiles = Profile.query.all()
            return jsonify([profile.to_dict() for profile in profiles])

    def post(self):
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

    def put(self, profile_id):
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

    def delete(self, profile_id):
        profile = Profile.query.get(profile_id)
        if profile:
            db.session.delete(profile)
            db.session.commit()
            return jsonify({"message": "Profile deleted"})
        else:
            return jsonify({"error": "Profile not found"}), 404

student_api.add_resource(ProfileResource, '/profiles', '/profiles/<uuid:profile_id>')

# User Resource
class UserResource(Resource):
    def post(self):
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

    def put(self, user_id):
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

student_api.add_resource(UserResource, '/users', '/users/<uuid:user_id>')

# ExamCategory Resource
class ExamCategoryResource(Resource):
    def get(self, exam_category_id=None):
        if exam_category_id:
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
        else:
            exam_categories = ExamCategory.query.all()
            return jsonify([{
                'id': ec.id,
                'name': ec.name,
                'description': ec.description,
                'user_id': ec.user_id
            } for ec in exam_categories])

student_api.add_resource(ExamCategoryResource, '/examcategories', '/examcategories/<uuid:exam_category_id>')

# SubCategory Resource
class SubCategoryResource(Resource):
    def get(self, sub_category_id):
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

student_api.add_resource(SubCategoryResource, '/subcategories/<uuid:sub_category_id>')

# Topic Resource
class TopicResource(Resource):
    def get(self, topic_id=None):
        if topic_id:
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
        else:
            topics = Topic.query.all()
            return jsonify([{
                'id': topic.id,
                'name': topic.name,
                'description': topic.description,
                'user_id': topic.user_id,
                'sub_category_id': topic.sub_category_id
            } for topic in topics])

student_api.add_resource(TopicResource, '/topics', '/topics/<uuid:topic_id>')

# Comment Resource
class CommentResource(Resource):
    def post(self):
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

    def put(self, comment_id):
        data = request.get_json()
        comment = Comment.query.get(comment_id)
        if comment:
            comment.description = data.get('description', comment.description)
            db.session.commit()
            return jsonify(comment.to_dict())
        else:
            return jsonify({"error": "Comment not found"}), 404

    def delete(self, comment_id):
        comment = Comment.query.get(comment_id)
        if comment:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({"message": "Comment deleted"})
        else:
            return jsonify({"error": "Comment not found"}), 404

student_api.add_resource(CommentResource, '/comments', '/comments/<uuid:comment_id>')

# Questions Resource
class QuestionResource(Resource):
    def get(self, question_id=None):
        if question_id:
            question = Questions.query.get(question_id)
            if question:
                return jsonify(question.to_dict())
            else:
                return jsonify({"error": "Question not found"}), 404
        else:
            questions = Questions.query.all()
            return jsonify([question.to_dict() for question in questions])

student_api.add_resource(QuestionResource, '/questions', '/questions/<uuid:question_id>')

# Answers Resource
class AnswerResource(Resource):
    def post(self):
        data = request.get_json()
        new_answer = Answers(
            text=data['text'],
            question_id=data['question_id'],
            is_correct=data.get('is_correct', False)
        )
        db.session.add(new_answer)
        db.session.commit()
        return jsonify(new_answer.to_dict()), 201

    def put(self, answer_id):
        data = request.get_json()
        answer = Answers.query.get(answer_id)
        if answer:
            answer.text = data.get('text', answer.text)
            answer.question_id = data.get('question_id', answer.question_id)
            answer.is_correct = data.get('is_correct', answer.is_correct)
            db.session.commit()
            return jsonify(answer.to_dict())
        else:
            return jsonify({"error": "Answer not found"}), 404

    def delete(self, answer_id):
        answer = Answers.query.get(answer_id)
        if answer:
            db.session.delete(answer)
            db.session.commit()
            return jsonify({"message": "Answer deleted"})
        else:
            return jsonify({"error": "Answer not found"}), 404

student_api.add_resource(AnswerResource, '/answers', '/answers/<uuid:answer_id>')

# Subscriptions Resource
class SubscriptionResource(Resource):
    def get(self, subscription_id=None):
        if subscription_id:
            subscription = Subscription.query.get(subscription_id)
            return jsonify(to_dict(subscription)), 200
        else:
            subscriptions = Subscription.query.all()
            return jsonify([to_dict(subscription) for subscription in subscriptions]), 200

student_api.add_resource(SubscriptionResource, '/subscriptions', '/subscriptions/<uuid:subscription_id>')

# Payment Resource
class PaymentResource(Resource):
    def post(self):
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

    def get(self, payment_id=None):
        if payment_id:
            payment = Payment.query.get(payment_id)
            return jsonify(to_dict(payment)), 200
        else:
            payments = Payment.query.all()
            return jsonify([to_dict(payment) for payment in payments]), 200

student_api.add_resource(PaymentResource, '/payments', '/payments/<uuid:payment_id>')

# Score Resource
class ScoreResource(Resource):
    def post(self):
        data = request.get_json()
        new_score = Score(
            user_id=data['user_id'],
            question_id=data['question_id'],
            score=data['score'],
            created_at=datetime.utcnow()
        )
        db.session.add(new_score)
        db.session.commit()
        return jsonify(new_score.to_dict()), 201

student_api.add_resource(ScoreResource, '/scores')




































    

    
    
    
    
    
    
    
    
    
     