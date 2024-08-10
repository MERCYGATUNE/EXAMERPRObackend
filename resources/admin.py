from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import Column, DateTime, func
from flask import Blueprint, request,jsonify
from flask_restful import Api,Resource
from models import Profile,User, ExamCategory,Comment,SubCategory,Questions,UserAnswers,UserChoice,UserParagraph,Choice,Topic,Notification,AnswerMetadata,Score,Resource, Answers,Referral


db = SQLAlchemy()

# Define Blueprints
admin_bp=Blueprint('admin_bp',__name__,url_prefix='/admin')
admin_api=Api(admin_bp)

#  User

class UserList(Resource):
    def get(self):
        users = User.query.all()
        return [user.to_dict() for user in users], 200

    def post(self):
        data = request.get_json()

        # Ensure necessary fields are provided (you can add more validation if needed)
        if not data.get('email') or not data.get('password'):
            return {"error": "Email and password are required"}, 400

        new_user = User(
            email=data.get('email'),
            password=data.get('password'),  # Make sure to hash the password before saving in a real-world scenario
            confirmed_email=data.get('confirmed_email', False),
            role=data.get('role', 'user'),
            referral_code=data.get('referral_code'),
            created_at=data.get('created_at', datetime.utcnow())  # Use the current timestamp if not provided
        )
        
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict(), 201

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return user.to_dict(), 200
        return {"error": "User not found"}, 404

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
            return user.to_dict(), 200
        return {"error": "User not found"}, 404

    def delete(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted"}, 200
        return {"error": "User not found"}, 404

# Register the resources with the admin API
admin_api.add_resource(UserList, '/users')
admin_api.add_resource(UserResource, '/users/<uuid:user_id>')
    
    
    
    

#  Profile
class ProfileList(Resource):
    def get(self):
        profiles = Profile.query.all()
        return [profile.to_dict() for profile in profiles]

class ProfileResource(Resource):
    def get(self, profile_id):
        profile = Profile.query.get(profile_id)
        if profile:
            return profile.to_dict()
        return {"error": "Profile not found"}, 404

    def delete(self, profile_id):
        profile = Profile.query.get(profile_id)
        if profile:
            db.session.delete(profile)
            db.session.commit()
            return {"message": "Profile deleted"}
        return {"error": "Profile not found"}, 404

admin_api.add_resource(ProfileList, '/profiles')
admin_api.add_resource(ProfileResource, '/profiles/<uuid:profile_id>')

#  ExamCategory
class ExamCategoryResource(Resource):
    def get(self, exam_category_id=None):
        if exam_category_id:
            exam_category = ExamCategory.query.get(exam_category_id)
            if exam_category:
                return {
                    'id': str(exam_category.id),
                    'name': exam_category.name,
                    'description': exam_category.description,
                    'user_id': str(exam_category.user_id)
                }
            return {"error": "Exam category not found"}, 404
        else:
            exam_categories = ExamCategory.query.all()
            return [{
                'id': str(ec.id),
                'name': ec.name,
                'description': ec.description,
                'user_id': str(ec.user_id)
            } for ec in exam_categories],200

    def post(self):
        data = request.get_json()

        # Validate incoming data
        required_fields = ['name', 'description', 'user_id']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing {field}"}, 400

        try:
            user_id = uuid.UUID(data['user_id'])  # Ensure user_id is a valid UUID
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

        new_exam_category = ExamCategory(
            name=data['name'],
            description=data['description'],
            user_id=user_id
        )
        
        db.session.add(new_exam_category)
        try:
            db.session.commit()
            return {
                'id': str(new_exam_category.id),  # Convert UUID to string for JSON response
                'name': new_exam_category.name,
                'description': new_exam_category.description,
                'user_id': str(new_exam_category.user_id)  # Convert UUID to string for JSON response
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, exam_category_id):
        data = request.get_json()
        exam_category = ExamCategory.query.get(exam_category_id)
        if not exam_category:
            return {"error": "Exam category not found"}, 404

        exam_category.name = data.get('name', exam_category.name)
        exam_category.description = data.get('description', exam_category.description)
        exam_category.user_id = data.get('user_id', exam_category.user_id)

        try:
            db.session.commit()
            return {
                'id': str(exam_category.id),
                'name': exam_category.name,
                'description': exam_category.description,
                'user_id': str(exam_category.user_id)
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, exam_category_id):
        exam_category = ExamCategory.query.get(exam_category_id)
        if not exam_category:
            return {"error": "Exam category not found"}, 404

        db.session.delete(exam_category)
        try:
            db.session.commit()
            return {"message": "Exam category deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(ExamCategoryResource, '/examcategories', '/examcategories/<uuid:exam_category_id>')
   
   
# SubCategory 
class SubCategoryResource(Resource):
    def get(self, sub_category_id=None):
        if sub_category_id:
            sub_category = SubCategory.query.get(sub_category_id)
            if sub_category:
                return {
                    'id': str(sub_category.id),
                    'name': sub_category.name,
                    'description': sub_category.description,
                    'user_id': str(sub_category.user_id),
                    'exam_category_id': str(sub_category.exam_category_id)
                }
            return {"error": "Subcategory not found"}, 404
        else:
            subcategories = SubCategory.query.all()
            return [{
                'id': str(sc.id),
                'name': sc.name,
                'description': sc.description,
                'user_id': str(sc.user_id),
                'exam_category_id': str(sc.exam_category_id)
            } for sc in subcategories]

    def post(self):
        data = request.get_json()

        # Validate incoming data
        required_fields = ['name', 'description', 'user_id', 'exam_category_id']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing {field}"}, 400

        try:
            user_id = uuid.UUID(data['user_id'])  # Ensure user_id is a valid UUID
            exam_category_id = uuid.UUID(data['exam_category_id'])  # Ensure exam_category_id is a valid UUID
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

        new_subcategory = SubCategory(
            name=data['name'],
            description=data['description'],
            user_id=user_id,
            exam_category_id=exam_category_id
        )
        
        db.session.add(new_subcategory)
        try:
            db.session.commit()
            return {
                'id': str(new_subcategory.id),  # Convert UUID to string for JSON response
                'name': new_subcategory.name,
                'description': new_subcategory.description,
                'user_id': str(new_subcategory.user_id),  # Convert UUID to string for JSON response
                'exam_category_id': str(new_subcategory.exam_category_id)  # Convert UUID to string for JSON response
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, sub_category_id):
        data = request.get_json()
        sub_category = SubCategory.query.get(sub_category_id)
        if not sub_category:
            return {"error": "Subcategory not found"}, 404

        sub_category.name = data.get('name', sub_category.name)
        sub_category.description = data.get('description', sub_category.description)
        sub_category.user_id = data.get('user_id', sub_category.user_id)
        sub_category.exam_category_id = data.get('exam_category_id', sub_category.exam_category_id)

        try:
            db.session.commit()
            return {
                'id': str(sub_category.id),
                'name': sub_category.name,
                'description': sub_category.description,
                'user_id': str(sub_category.user_id),
                'exam_category_id': str(sub_category.exam_category_id)
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, sub_category_id):
        sub_category = SubCategory.query.get(sub_category_id)
        if not sub_category:
            return {"error": "Subcategory not found"}, 404

        db.session.delete(sub_category)
        try:
            db.session.commit()
            return {"message": "Subcategory deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(SubCategoryResource, '/subcategories', '/subcategories/<uuid:sub_category_id>')
    
#  QUESTIONS 
    
class QuestionsResource(Resource):
    def get(self, question_id=None):
        if question_id:
            question = Questions.query.get(question_id)
            if question:
                return jsonify({
                    'id': str(question.id),
                    'question': question.question,
                    'topic_id': str(question.topic_id),
                    'mode': question.mode,
                    'exam_mode': question.exam_mode,
                    'created_at': question.created_at.isoformat() if question.created_at else None
                })
            return {"error": "Question not found"}, 404
        else:
            questions = Questions.query.all()
            return jsonify([{
                'id': str(q.id),
                'question': q.question,
                'topic_id': str(q.topic_id),
                'mode': q.mode,
                'exam_mode': q.exam_mode,
                'created_at': q.created_at.isoformat() if q.created_at else None
            } for q in questions])

    def post(self):
        data = request.get_json()
        new_question = Questions(
            question=data['question'],
            topic_id=data['topic_id'],
            mode=data.get('mode'),
            exam_mode=data.get('exam_mode'),
            created_at=datetime.utcnow()
        )
        db.session.add(new_question)
        try:
            db.session.commit()
            return jsonify({
                'id': str(new_question.id),
                'question': new_question.question,
                'topic_id': str(new_question.topic_id),
                'mode': new_question.mode,
                'exam_mode': new_question.exam_mode,
                'created_at': new_question.created_at.isoformat() if new_question.created_at else None
            }), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, question_id):
        data = request.get_json()
        question = Questions.query.get(question_id)
        if not question:
            return {"error": "Question not found"}, 404

        question.question = data.get('question', question.question)
        question.topic_id = data.get('topic_id', question.topic_id)
        question.mode = data.get('mode', question.mode)
        question.exam_mode = data.get('exam_mode', question.exam_mode)

        try:
            db.session.commit()
            return jsonify({
                'id': str(question.id),
                'question': question.question,
                'topic_id': str(question.topic_id),
                'mode': question.mode,
                'exam_mode': question.exam_mode,
                'created_at': question.created_at.isoformat() if question.created_at else None
            })
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, question_id):
        question = Questions.query.get(question_id)
        if not question:
            return {"error": "Question not found"}, 404

        db.session.delete(question)
        try:
            db.session.commit()
            return jsonify({"message": "Question deleted"})
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(QuestionsResource, '/questions', '/questions/<uuid:question_id>')
    

# UserAnswers

class UserAnswersResource(Resource):
    def get(self, user_answer_id=None):
        if user_answer_id:
            user_answer = UserAnswers.query.get(user_answer_id)
            if user_answer:
                return user_answer.to_dict()
            return {"error": "User Answer not found"}, 404
        else:
            user_answers = UserAnswers.query.all()
            return [user_answer.to_dict() for user_answer in user_answers]

    def post(self):
        data = request.get_json()
        new_user_answer = UserAnswers(
            question_id=data['question_id'],
            user_id=data['user_id'],
            answer_type=data.get('answer_type'),
            answer=data.get('answer'),
            attempts=data.get('attempts', 1)
        )
        db.session.add(new_user_answer)
        try:
            db.session.commit()
            return new_user_answer.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, user_answer_id):
        data = request.get_json()
        user_answer = UserAnswers.query.get(user_answer_id)
        if not user_answer:
            return {"error": "User Answer not found"}, 404

        user_answer.answer_type = data.get('answer_type', user_answer.answer_type)
        user_answer.answer = data.get('answer', user_answer.answer)
        user_answer.attempts = data.get('attempts', user_answer.attempts)
        try:
            db.session.commit()
            return user_answer.to_dict()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, user_answer_id):
        user_answer = UserAnswers.query.get(user_answer_id)
        if not user_answer:
            return {"error": "User Answer not found"}, 404

        db.session.delete(user_answer)
        try:
            db.session.commit()
            return {"message": "User Answer deleted"}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(UserAnswersResource, '/useranswers', '/useranswers/<uuid:user_answer_id>')


#  NOTIFICATIONS

class NotificationResource(Resource):
    def get(self, notification_id=None):
        if notification_id:
            notification = Notification.query.get(notification_id)
            if notification:
                return jsonify(to_dict(notification))
            return {"error": "Notification not found"}, 404
        else:
            notifications = Notification.query.all()
            return jsonify([to_dict(notification) for notification in notifications])

    def post(self):
        data = request.get_json()
        new_notification = Notification(
            user_id=data['user_id'],
            subject=data.get('subject'),
            body=data.get('body'),
            sender_id=data.get('sender_id'),
            sender_name=data.get('sender_name')
        )
        db.session.add(new_notification)
        try:
            db.session.commit()
            return jsonify(to_dict(new_notification)), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, notification_id):
        data = request.get_json()
        notification = Notification.query.get(notification_id)
        if not notification:
            return {"error": "Notification not found"}, 404

        if 'subject' in data:
            notification.subject = data['subject']
        if 'body' in data:
            notification.body = data['body']
        if 'sender_id' in data:
            notification.sender_id = data['sender_id']
        if 'sender_name' in data:
            notification.sender_name = data['sender_name']

        try:
            db.session.commit()
            return jsonify(to_dict(notification))
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, notification_id):
        notification = Notification.query.get(notification_id)
        if not notification:
            return {"error": "Notification not found"}, 404

        db.session.delete(notification)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(NotificationResource, '/notifications', '/notifications/<uuid:notification_id>')
    

# Score CRUD Operations


class ScoreResource(Resource):
    def get(self, score_id=None):
        if score_id:
            score = Score.query.get(score_id)
            if score:
                return jsonify(to_dict(score))
            return {"error": "Score not found"}, 404
        else:
            scores = Score.query.all()
            return jsonify([to_dict(score) for score in scores])

    def post(self):
        data = request.get_json()
        new_score = Score(
            user_id=data['user_id'],
            topic_id=data.get('topic_id'),
            possible_score=data['possible_score'],
            user_score=data['user_score'],
            completion_rate=data.get('completion_rate')
        )
        db.session.add(new_score)
        try:
            db.session.commit()
            return jsonify(to_dict(new_score)), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, score_id):
        data = request.get_json()
        score = Score.query.get(score_id)
        if not score:
            return {"error": "Score not found"}, 404

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

        try:
            db.session.commit()
            return jsonify(to_dict(score))
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, score_id):
        score = Score.query.get(score_id)
        if not score:
            return {"error": "Score not found"}, 404

        db.session.delete(score)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(ScoreResource, '/scores', '/scores/<uuid:score_id>')



# Resource CRUD Operations

class ResourceResource(Resource):
    def get(self, resource_id=None):
        if resource_id:
            resource = Resource.query.get(resource_id)
            if resource:
                return jsonify(to_dict(resource))
            return {"error": "Resource not found"}, 404
        else:
            resources = Resource.query.all()
            return jsonify([to_dict(resource) for resource in resources])

    def post(self):
        data = request.get_json()
        new_resource = Resource(
            name=data['name'],
            description=data.get('description'),
            type=data.get('type'),
            url=data.get('url')
        )
        db.session.add(new_resource)
        try:
            db.session.commit()
            return jsonify(to_dict(new_resource)), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, resource_id):
        data = request.get_json()
        resource = Resource.query.get(resource_id)
        if not resource:
            return {"error": "Resource not found"}, 404

        if 'name' in data:
            resource.name = data['name']
        if 'description' in data:
            resource.description = data['description']
        if 'type' in data:
            resource.type = data['type']
        if 'url' in data:
            resource.url = data['url']

        try:
            db.session.commit()
            return jsonify(to_dict(resource))
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, resource_id):
        resource = Resource.query.get(resource_id)
        if not resource:
            return {"error": "Resource not found"}, 404

        db.session.delete(resource)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(ResourceResource, '/resources', '/resources/<uuid:resource_id>')


# UserParagraph

class UserParagraphResource(Resource):
    def get(self, user_paragraph_id=None):
        if user_paragraph_id:
            user_paragraph = UserParagraph.query.get(user_paragraph_id)
            if user_paragraph:
                return jsonify({
                    'id': str(user_paragraph.id),
                    'user_id': str(user_paragraph.user_id),
                    'paragraph_id': str(user_paragraph.paragraph_id),
                    'is_read': user_paragraph.is_read
                })
            return {"error": "UserParagraph not found"}, 404
        else:
            user_paragraphs = UserParagraph.query.all()
            return jsonify([{
                'id': str(up.id),
                'user_id': str(up.user_id),
                'paragraph_id': str(up.paragraph_id),
                'is_read': up.is_read
            } for up in user_paragraphs])

    def post(self):
        data = request.get_json()
        new_user_paragraph = UserParagraph(
            user_id=data['user_id'],
            paragraph_id=data['paragraph_id'],
            is_read=data.get('is_read', False)
        )
        db.session.add(new_user_paragraph)
        try:
            db.session.commit()
            return jsonify({
                'id': str(new_user_paragraph.id),
                'user_id': str(new_user_paragraph.user_id),
                'paragraph_id': str(new_user_paragraph.paragraph_id),
                'is_read': new_user_paragraph.is_read
            }), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, user_paragraph_id):
        data = request.get_json()
        user_paragraph = UserParagraph.query.get(user_paragraph_id)
        if not user_paragraph:
            return {"error": "UserParagraph not found"}, 404

        user_paragraph.user_id = data.get('user_id', user_paragraph.user_id)
        user_paragraph.paragraph_id = data.get('paragraph_id', user_paragraph.paragraph_id)
        user_paragraph.is_read = data.get('is_read', user_paragraph.is_read)

        try:
            db.session.commit()
            return jsonify({
                'id': str(user_paragraph.id),
                'user_id': str(user_paragraph.user_id),
                'paragraph_id': str(user_paragraph.paragraph_id),
                'is_read': user_paragraph.is_read
            })
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, user_paragraph_id):
        user_paragraph = UserParagraph.query.get(user_paragraph_id)
        if not user_paragraph:
            return {"error": "UserParagraph not found"}, 404

        db.session.delete(user_paragraph)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(UserParagraphResource, '/user_paragraphs', '/user_paragraphs/<uuid:user_paragraph_id>')


# UserChoice CRUD Operations

class UserChoiceResource(Resource):
    def get(self, user_choice_id=None):
        if user_choice_id:
            user_choice = UserChoice.query.get(user_choice_id)
            if user_choice:
                return jsonify({
                    'id': str(user_choice.id),
                    'user_id': str(user_choice.user_id),
                    'choice_id': str(user_choice.choice_id)
                })
            return {"error": "UserChoice not found"}, 404
        else:
            user_choices = UserChoice.query.all()
            return jsonify([{
                'id': str(uc.id),
                'user_id': str(uc.user_id),
                'choice_id': str(uc.choice_id)
            } for uc in user_choices])

    def post(self):
        data = request.get_json()
        new_user_choice = UserChoice(
            user_id=data['user_id'],
            choice_id=data['choice_id']
        )
        db.session.add(new_user_choice)
        try:
            db.session.commit()
            return jsonify({
                'id': str(new_user_choice.id),
                'user_id': str(new_user_choice.user_id),
                'choice_id': str(new_user_choice.choice_id)
            }), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, user_choice_id):
        data = request.get_json()
        user_choice = UserChoice.query.get(user_choice_id)
        if not user_choice:
            return {"error": "UserChoice not found"}, 404

        user_choice.user_id = data.get('user_id', user_choice.user_id)
        user_choice.choice_id = data.get('choice_id', user_choice.choice_id)

        try:
            db.session.commit()
            return jsonify({
                'id': str(user_choice.id),
                'user_id': str(user_choice.user_id),
                'choice_id': str(user_choice.choice_id)
            })
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, user_choice_id):
        user_choice = UserChoice.query.get(user_choice_id)
        if not user_choice:
            return {"error": "UserChoice not found"}, 404

        db.session.delete(user_choice)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(UserChoiceResource, '/user_choices', '/user_choices/<uuid:user_choice_id>')


# Choice CRUD Operations

class ChoiceResource(Resource):
    def get(self, choice_id=None):
        if choice_id:
            choice = Choice.query.get(choice_id)
            if choice:
                return jsonify(to_dict(choice))
            return {"error": "Choice not found"}, 404
        else:
            choices = Choice.query.all()
            return jsonify([to_dict(choice) for choice in choices])

    def post(self):
        data = request.get_json()
        new_choice = Choice(
            text=data['text'],
            question_id=data['question_id'],
            is_correct=data.get('is_correct', False)
        )
        db.session.add(new_choice)
        try:
            db.session.commit()
            return jsonify(to_dict(new_choice)), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, choice_id):
        data = request.get_json()
        choice = Choice.query.get(choice_id)
        if not choice:
            return {"error": "Choice not found"}, 404

        if 'text' in data:
            choice.text = data['text']
        if 'question_id' in data:
            choice.question_id = data['question_id']
        if 'is_correct' in data:
            choice.is_correct = data['is_correct']

        try:
            db.session.commit()
            return jsonify(to_dict(choice))
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, choice_id):
        choice = Choice.query.get(choice_id)
        if not choice:
            return {"error": "Choice not found"}, 404

        db.session.delete(choice)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(ChoiceResource, '/choices', '/choices/<uuid:choice_id>')

# AnswerMetadata CRUD Operations

class AnswerMetadataResource(Resource):
    def get(self, answer_metadata_id=None):
        if answer_metadata_id:
            answer_metadata = AnswerMetadata.query.get(answer_metadata_id)
            if answer_metadata:
                return jsonify(to_dict(answer_metadata))
            return {"error": "AnswerMetadata not found"}, 404
        else:
            answer_metadata_list = AnswerMetadata.query.all()
            return jsonify([to_dict(am) for am in answer_metadata_list])

    def post(self):
        data = request.get_json()
        new_answer_metadata = AnswerMetadata(
            question_id=data['question_id'],
            answer_id=data['answer_id'],
            metadata=data.get('metadata')
        )
        db.session.add(new_answer_metadata)
        try:
            db.session.commit()
            return jsonify(to_dict(new_answer_metadata)), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, answer_metadata_id):
        data = request.get_json()
        answer_metadata = AnswerMetadata.query.get(answer_metadata_id)
        if not answer_metadata:
            return {"error": "AnswerMetadata not found"}, 404

        if 'question_id' in data:
            answer_metadata.question_id = data['question_id']
        if 'answer_id' in data:
            answer_metadata.answer_id = data['answer_id']
        if 'metadata' in data:
            answer_metadata.metadata = data['metadata']

        try:
            db.session.commit()
            return jsonify(to_dict(answer_metadata))
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, answer_metadata_id):
        answer_metadata = AnswerMetadata.query.get(answer_metadata_id)
        if not answer_metadata:
            return {"error": "AnswerMetadata not found"}, 404

        db.session.delete(answer_metadata)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(AnswerMetadataResource, '/answer_metadata', '/answer_metadata/<uuid:answer_metadata_id>')


# TOPICS 
 
class TopicResource(Resource):
    def get(self, topic_id=None):
        if topic_id:
            topic = Topic.query.get(topic_id)
            if topic:
                return jsonify({
                    'id': str(topic.id),
                    'name': topic.name,
                    'description': topic.description,
                    'user_id': str(topic.user_id),
                    'sub_category_id': str(topic.sub_category_id)
                })
            return {"error": "Topic not found"}, 404
        else:
            topics = Topic.query.all()
            return jsonify([{
                'id': str(topic.id),
                'name': topic.name,
                'description': topic.description,
                'user_id': str(topic.user_id),
                'sub_category_id': str(topic.sub_category_id)
            } for topic in topics])

    def post(self):
        data = request.get_json()
        
        # Validate incoming data
        required_fields = ['name', 'description', 'user_id', 'sub_category_id']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing {field}"}, 400

        try:
            user_id = UUID(data['user_id'])  # Ensure user_id is a valid UUID
            sub_category_id = UUID(data['sub_category_id'])  # Ensure sub_category_id is a valid UUID
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

        new_topic = Topic(
            name=data['name'],
            description=data['description'],
            user_id=user_id,
            sub_category_id=sub_category_id
        )
        
        db.session.add(new_topic)
        try:
            db.session.commit()
            return jsonify({
                'id': str(new_topic.id),  # Convert UUID to string for JSON response
                'name': new_topic.name,
                'description': new_topic.description,
                'user_id': str(new_topic.user_id),  # Convert UUID to string for JSON response
                'sub_category_id': str(new_topic.sub_category_id)  # Convert UUID to string for JSON response
            }), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, topic_id):
        data = request.get_json()
        topic = Topic.query.get(topic_id)
        if not topic:
            return {"error": "Topic not found"}, 404

        if 'name' in data:
            topic.name = data['name']
        if 'description' in data:
            topic.description = data['description']
        if 'user_id' in data:
            try:
                topic.user_id = UUID(data['user_id'])  # Validate UUID
            except ValueError:
                return {"error": "Invalid UUID format"}, 400
        if 'sub_category_id' in data:
            try:
                topic.sub_category_id = UUID(data['sub_category_id'])  # Validate UUID
            except ValueError:
                return {"error": "Invalid UUID format"}, 400
        
        db.session.commit()
        return jsonify({
            'id': str(topic.id),
            'name': topic.name,
            'description': topic.description,
            'user_id': str(topic.user_id),
            'sub_category_id': str(topic.sub_category_id)
        })

    def delete(self, topic_id):
        topic = Topic.query.get(topic_id)
        if not topic:
            return {"error": "Topic not found"}, 404

        db.session.delete(topic)
        try:
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

admin_api.add_resource(TopicResource, '/topics', '/topics/<uuid:topic_id>')


# Comments

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

admin_api.add_resource(CommentResource, '/comments', '/comments/<uuid:comment_id>')


# Referral List Resource: Handles GET (list) and POST (create)
class ReferralListResource(Resource):
    def get(self):
        referrals = Referral.query.all()
        return jsonify([referral.to_dict() for referral in referrals])

    def post(self):
        data = request.get_json()
        new_referral = Referral(
            referral_code=data.get('referral_code'),
            points_earned=data.get('points_earned'),
            redeemed=data.get('redeemed')
        )
        try:
            db.session.add(new_referral)
            db.session.commit()
            return new_referral.to_dict(), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

# Referral Resource: Handles GET, PUT, DELETE for a single referral
class ReferralResource(Resource):
    def get(self, referral_id):
        try:
            uuid_obj = UUIDType(referral_id, version=4)
            referral = Referral.query.get(uuid_obj)
            if referral:
                return referral.to_dict()
            return {"error": "Referral not found"}, 404
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

    def put(self, referral_id):
        try:
            uuid_obj = UUIDType(referral_id, version=4)
            referral = Referral.query.get(uuid_obj)
            if not referral:
                return {"error": "Referral not found"}, 404
            
            data = request.get_json()
            referral.referral_code = data.get('referral_code', referral.referral_code)
            referral.points_earned = data.get('points_earned', referral.points_earned)
            referral.redeemed = data.get('redeemed', referral.redeemed)
            
            try:
                db.session.commit()
                return referral.to_dict()
            except SQLAlchemyError as e:
                db.session.rollback()
                return {"error": str(e)}, 400
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

    def delete(self, referral_id):
        try:
            uuid_obj = UUIDType(referral_id, version=4)
            referral = Referral.query.get(uuid_obj)
            if not referral:
                return {"error": "Referral not found"}, 404

            try:
                db.session.delete(referral)
                db.session.commit()
                return {"message": "Referral deleted"}
            except SQLAlchemyError as e:
                db.session.rollback()
                return {"error": str(e)}, 400
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

# Register the Resources with the API
admin_api.add_resource(ReferralListResource, '/referrals')
admin_api.add_resource(ReferralResource, '/referrals/<string:referral_id>')


# Answer List Resource: Handles GET (list) and POST (create)
class AnswerListResource(Resource):
    def get(self):
        answers = Answers.query.all()
        return jsonify([answer.to_dict() for answer in answers])

    def post(self):
        data = request.get_json()
        new_answer = Answers(
            question_id=data.get('question_id'),
            answer_type=data.get('answer_type'),
            answer=data.get('answer')
        )
        try:
            db.session.add(new_answer)
            db.session.commit()
            return new_answer.to_dict(), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

# Answer Resource: Handles GET, PUT, DELETE for a single answer
class AnswerResource(Resource):
    def get(self, answer_id):
        try:
            uuid_obj = UUIDType(answer_id, version=4)
            answer = Answers.query.get(uuid_obj)
            if answer:
                return answer.to_dict()
            return {"error": "Answer not found"}, 404
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

    def put(self, answer_id):
        try:
            uuid_obj = UUIDType(answer_id, version=4)
            answer = Answers.query.get(uuid_obj)
            if not answer:
                return {"error": "Answer not found"}, 404
            
            data = request.get_json()
            answer.answer_type = data.get('answer_type', answer.answer_type)
            answer.answer = data.get('answer', answer.answer)
            
            try:
                db.session.commit()
                return answer.to_dict()
            except SQLAlchemyError as e:
                db.session.rollback()
                return {"error": str(e)}, 400
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

    def delete(self, answer_id):
        try:
            uuid_obj = UUIDType(answer_id, version=4)
            answer = Answers.query.get(uuid_obj)
            if not answer:
                return {"error": "Answer not found"}, 404

            try:
                db.session.delete(answer)
                db.session.commit()
                return {"message": "Answer deleted"}
            except SQLAlchemyError as e:
                db.session.rollback()
                return {"error": str(e)}, 400
        except ValueError:
            return {"error": "Invalid UUID format"}, 400

# Register the Resources with the API
admin_api.add_resource(AnswerListResource, '/answers')
admin_api.add_resource(AnswerResource, '/answers/<string:answer_id>')




