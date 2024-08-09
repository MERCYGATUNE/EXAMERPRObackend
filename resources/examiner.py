from flask import Flask, request, jsonify,Blueprint
from flask_restful import Resource, Api
from models import db, ExamCategory, SubCategory, Topic, Questions, UserAnswers, Score, Choice, AnswerMetadata
import uuid
from datetime import datetime

app = Flask(__name__)



# Define Blueprints
examiner_bp=Blueprint('examiner_bp',__name__,url_prefix='/examiner')
examiner_api=Api(examiner_bp)



# ExamCategory Resource
class ExamCategoryResource(Resource):
    def post(self):
        data = request.get_json()
        required_fields = ['name', 'description', 'user_id']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing {field}"}, 400

        try:
            user_id = uuid.UUID(data['user_id'])
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
                'id': str(new_exam_category.id),
                'name': new_exam_category.name,
                'description': new_exam_category.description,
                'user_id': str(new_exam_category.user_id)
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
                'id': exam_category.id,
                'name': exam_category.name,
                'description': exam_category.description,
                'user_id': exam_category.user_id
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

# SubCategory Resource
class SubCategoryResource(Resource):
    def get(self):
        subcategories = SubCategory.query.all()
        return [{
            'id': sc.id,
            'name': sc.name,
            'description': sc.description,
            'user_id': sc.user_id,
            'exam_category_id': sc.exam_category_id
        } for sc in subcategories]

    def post(self):
        data = request.get_json()
        required_fields = ['name', 'description', 'user_id', 'exam_category_id']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing {field}"}, 400

        try:
            user_id = uuid.UUID(data['user_id'])
            exam_category_id = uuid.UUID(data['exam_category_id'])
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
                'id': str(new_subcategory.id),
                'name': new_subcategory.name,
                'description': new_subcategory.description,
                'user_id': str(new_subcategory.user_id),
                'exam_category_id': str(new_subcategory.exam_category_id)
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# Topic Resource
class TopicResource(Resource):
    def post(self):
        data = request.get_json()
        required_fields = ['name', 'description', 'user_id', 'sub_category_id']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing {field}"}, 400

        try:
            user_id = uuid.UUID(data['user_id'])
            sub_category_id = uuid.UUID(data['sub_category_id'])
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
            return {
                'id': str(new_topic.id),
                'name': new_topic.name,
                'description': new_topic.description,
                'user_id': str(new_topic.user_id),
                'sub_category_id': str(new_topic.sub_category_id)
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# Questions Resource
class QuestionResource(Resource):
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
        db.session.commit()
        return jsonify(new_question.to_dict()), 201

    def put(self, question_id):
        data = request.get_json()
        question = Questions.query.get(question_id)
        if question:
            question.question = data.get('question', question.question)
            question.topic_id = data.get('topic_id', question.topic_id)
            question.mode = data.get('mode', question.mode)
            question.exam_mode = data.get('exam_mode', question.exam_mode)
            db.session.commit()
            return jsonify(question.to_dict())
        else:
            return {"error": "Question not found"}, 404

    def delete(self, question_id):
        question = Questions.query.get(question_id)
        if question:
            db.session.delete(question)
            db.session.commit()
            return {"message": "Question deleted"}
        else:
            return {"error": "Question not found"}, 404

# UserAnswers Resource
class UserAnswerResource(Resource):
    def get(self):
        user_answers = UserAnswers.query.all()
        return jsonify([user_answer.to_dict() for user_answer in user_answers])

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
        db.session.commit()
        return jsonify(new_user_answer.to_dict()), 201

    def put(self, user_answer_id):
        data = request.get_json()
        user_answer = UserAnswers.query.get(user_answer_id)
        if user_answer:
            user_answer.answer_type = data.get('answer_type', user_answer.answer_type)
            user_answer.answer = data.get('answer', user_answer.answer)
            user_answer.attempts = data.get('attempts', user_answer.attempts)
            db.session.commit()
            return jsonify(user_answer.to_dict())
        else:
            return {"error": "User Answer not found"}, 404

    def delete(self, user_answer_id):
        user_answer = UserAnswers.query.get(user_answer_id)
        if user_answer:
            db.session.delete(user_answer)
            db.session.commit()
            return {"message": "User Answer deleted"}
        else:
            return {"error": "User Answer not found"}, 404

# Score Resource
class ScoreResource(Resource):
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
        db.session.commit()
        return jsonify(new_score.to_dict()), 201

    def get(self):
        scores = Score.query.all()
        return jsonify([score.to_dict() for score in scores])

    def put(self, score_id):
        data = request.get_json()
        score = Score.query.get(score_id)
        if score:
            score.user_id = data.get('user_id', score.user_id)
            score.topic_id = data.get('topic_id', score.topic_id)
            score.possible_score = data.get('possible_score', score.possible_score)
            score.user_score = data.get('user_score', score.user_score)
            score.completion_rate = data.get('completion_rate', score.completion_rate)
            db.session.commit()
            return jsonify(score.to_dict())
        else:
            return {"error": "Score not found"}, 404

    def delete(self, score_id):
        score = Score.query.get(score_id)
        if score:
            db.session.delete(score)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Score not found"}, 404

# Choice Resource
class ChoiceResource(Resource):
    def post(self):
        data = request.get_json()
        new_choice = Choice(
            question_id=data['question_id'],
            choice=data['choice'],
            is_correct=data.get('is_correct', False)
        )
        db.session.add(new_choice)
        db.session.commit()
        return jsonify(new_choice.to_dict()), 201

    def get(self):
        choices = Choice.query.all()
        return jsonify([choice.to_dict() for choice in choices])

    def put(self, choice_id):
        data = request.get_json()
        choice = Choice.query.get(choice_id)
        if choice:
            choice.choice = data.get('choice', choice.choice)
            choice.is_correct = data.get('is_correct', choice.is_correct)
            db.session.commit()
            return jsonify(choice.to_dict())
        else:
            return {"error": "Choice not found"}, 404

    def delete(self, choice_id):
        choice = Choice.query.get(choice_id)
        if choice:
            db.session.delete(choice)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Choice not found"}, 404

# AnswerMetadata Resource
class AnswerMetadataResource(Resource):
    def post(self):
        data = request.get_json()
        new_answer_metadata = AnswerMetadata(
            user_id=data['user_id'],
            question_id=data['question_id'],
            answer=data.get('answer'),
            attempts=data.get('attempts', 1)
        )
        db.session.add(new_answer_metadata)
        db.session.commit()
        return jsonify(new_answer_metadata.to_dict()), 201

    def get(self):
        metadata = AnswerMetadata.query.all()
        return jsonify([meta.to_dict() for meta in metadata])

    def put(self, metadata_id):
        data = request.get_json()
        metadata = AnswerMetadata.query.get(metadata_id)
        if metadata:
            metadata.answer = data.get('answer', metadata.answer)
            metadata.attempts = data.get('attempts', metadata.attempts)
            db.session.commit()
            return jsonify(metadata.to_dict())
        else:
            return {"error": "Answer metadata not found"}, 404

    def delete(self, metadata_id):
        metadata = AnswerMetadata.query.get(metadata_id)
        if metadata:
            db.session.delete(metadata)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Answer metadata not found"}, 404

# API Resource Routing
examiner_api.add_resource(ExamCategoryResource, '/exam-category', '/exam-category/<uuid:exam_category_id>')
examiner_api.add_resource(SubCategoryResource, '/subcategory', '/subcategory/<uuid:subcategory_id>')
examiner_api.add_resource(TopicResource, '/topic', '/topic/<uuid:topic_id>')
examiner_api.add_resource(QuestionResource, '/question', '/question/<uuid:question_id>')
examiner_api.add_resource(UserAnswerResource, '/user-answer', '/user-answer/<uuid:user_answer_id>')
examiner_api.add_resource(ScoreResource, '/score', '/score/<uuid:score_id>')
examiner_api.add_resource(ChoiceResource, '/choice', '/choice/<uuid:choice_id>')
examiner_api.add_resource(AnswerMetadataResource, '/answer-metadata', '/answer-metadata/<uuid:metadata_id>')


