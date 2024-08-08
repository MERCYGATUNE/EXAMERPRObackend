from sqlalchemy import Column, Text, UUID, DateTime
import uuid
from datetime import datetime


db = SQLAlchemy()

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
            'attempts': self.attempts
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



@app.route('/examcategories', methods=['POST'])

def create_exam_category():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['name', 'description', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        user_id = uuid.UUID(data['user_id'])  # Ensure user_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    new_exam_category = ExamCategory(
        name=data['name'],
        description=data['description'],
        user_id=user_id
    )
    
    db.session.add(new_exam_category)
    try:
        db.session.commit()
        return jsonify({
            'id': str(new_exam_category.id),  # Convert UUID to string for JSON response
            'name': new_exam_category.name,
            'description': new_exam_category.description,
            'user_id': str(new_exam_category.user_id)  # Convert UUID to string for JSON response
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/examcategories/<uuid:exam_category_id>', methods=['PUT'])

def update_exam_category(exam_category_id):
    data = request.get_json()
    exam_category = ExamCategory.query.get(exam_category_id)
    if not exam_category:
        return jsonify({"error": "Exam category not found"}), 404

    exam_category.name = data.get('name', exam_category.name)
    exam_category.description = data.get('description', exam_category.description)
    exam_category.user_id = data.get('user_id', exam_category.user_id)

    try:
        db.session.commit()
        return jsonify({
            'id': exam_category.id,
            'name': exam_category.name,
            'description': exam_category.description,
            'user_id': exam_category.user_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}),


@app.route('/examcategories/<uuid:exam_category_id>', methods=['DELETE'])

def delete_exam_category(exam_category_id):
    exam_category = ExamCategory.query.get(exam_category_id)
    if not exam_category:
        return jsonify({"error": "Exam category not found"}), 404

    db.session.delete(exam_category)
    try:
        db.session.commit()
        return jsonify({"message": "Exam category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/subcategories', methods=['GET'])

def get_subcategories():
    subcategories = SubCategory.query.all()
    return jsonify([{
        'id': sc.id,
        'name': sc.name,
        'description': sc.description,
        'user_id': sc.user_id,
        'exam_category_id': sc.exam_category_id
    } for sc in subcategories])
    
 @app.route('/subcategories', methods=['POST'])
 
def create_subcategory():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['name', 'description', 'user_id', 'exam_category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        user_id = UUID(data['user_id'])  # Ensure user_id is a valid UUID
        exam_category_id = UUID(data['exam_category_id'])  # Ensure exam_category_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    new_subcategory = SubCategory(
        name=data['name'],
        description=data['description'],
        user_id=user_id,
        exam_category_id=exam_category_id
    )
    
    db.session.add(new_subcategory)
    try:
        db.session.commit()
        return jsonify({
            'id': str(new_subcategory.id),  # Convert UUID to string for JSON response
            'name': new_subcategory.name,
            'description': new_subcategory.description,
            'user_id': str(new_subcategory.user_id),  # Convert UUID to string for JSON response
            'exam_category_id': str(new_subcategory.exam_category_id)  # Convert UUID to string for JSON response
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/subcategories/<uuid:sub_category_id>', methods=['PUT'])

def update_subcategory(sub_category_id):
    data = request.get_json()
    sub_category = SubCategory.query.get(sub_category_id)
    if not sub_category:
        return jsonify({"error": "Subcategory not found"}), 404

    sub_category.name = data.get('name', sub_category.name)
    sub_category.description = data.get('description', sub_category.description)
    sub_category.user_id = data.get('user_id', sub_category.user_id)
    sub_category.exam_category_id = data.get('exam_category_id', sub_category.exam_category_id)

    try:
        db.session.commit()
        return jsonify({
            'id': sub_category.id,
            'name': sub_category.name,
            'description': sub_category.description,
            'user_id': sub_category.user_,
            'exam_category_id': sub_category.exam_category_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/subcategories/<uuid:sub_category_id>', methods=['DELETE'])

def delete_subcategory(sub_category_id):
    sub_category = SubCategory.query.get(sub_category_id)
    if not sub_category:
        return jsonify({"error": "Subcategory not found"}), 404

    db.session.delete(sub_category)
    try:
        db.session.commit()
        return jsonify({"message": "Subcategory deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500  
    

 
@app.route('/topics', methods=['POST'])

def create_topic():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['name', 'description', 'user_id', 'sub_category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        user_id = UUID(data['user_id'])  # Ensure user_id is a valid UUID
        sub_category_id = UUID(data['sub_category_id'])  # Ensure sub_category_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

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
        return jsonify({"error": str(e)}), 500     
    
    
 @app.route('/questions', methods=['POST'])
 
def create_question():
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

@app.route('/questions/<uuid:question_id>', methods=['PUT'])

def update_question(question_id):
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
        return jsonify({"error": "Question not found"}), 404

@app.route('/questions/<uuid:question_id>', methods=['DELETE'])

def delete_question(question_id):
    question = Questions.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Question deleted"})
    else:
        return jsonify({"error": "Question not found"}), 404


# Routes for UserAnswers
@app.route('/useranswers', methods=['GET'])

def get_user_answers():
    user_answers = UserAnswers.query.all()
    return jsonify([user_answer.to_dict() for user_answer in user_answers])

@app.route('/useranswers/<uuid:user_answer_id>', methods=['GET'])

def get_user_answer(user_answer_id):
    user_answer = UserAnswers.query.get(user_answer_id)
    if user_answer:
        return jsonify(user_answer.to_dict())
    else:
        return jsonify({"error": "User Answer not found"}), 404

@app.route('/useranswers', methods=['POST'])

def create_user_answer():
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

@app.route('/useranswers/<uuid:user_answer_id>', methods=['PUT'])

def update_user_answer(user_answer_id):
    data = request.get_json()
    user_answer = UserAnswers.query.get(user_answer_id)
    if user_answer:
        user_answer.answer_type = data.get('answer_type', user_answer.answer_type)
        user_answer.answer = data.get('answer', user_answer.answer)
        user_answer.attempts = data.get('attempts', user_answer.attempts)
        db.session.commit()
        return jsonify(user_answer.to_dict())
    else:
        return jsonify({"error": "User Answer not found"}), 404

@app.route('/useranswers/<uuid:user_answer_id>', methods=['DELETE'])

def delete_user_answer(user_answer_id):
    user_answer = UserAnswers.query.get(user_answer_id)
    if user_answer:
        db.session.delete(user_answer)
        db.session.commit()
        return jsonify({"message": "User Answer deleted"})
    else:
        return jsonify({"error": "User Answer not found"}), 404


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

@app.route('/scores/<uuid:score_id>', methods=['DELETE'])

def delete_score(score_id):
    score = score.query.get_or_404(score_id)
    db.session.delete(score)
    db.session.commit()
    return '', 204

# Questions CRUD Operations
@app.route('/questions', methods=['POST'])

def create_question():
    data = request.get_json()
    new_question = Questions(
        text=data['text'],
        topic_id=data.get('topic_id')
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify(to_dict(new_question)), 201


@app.route('/questions/<uuid:question_id>', methods=['PUT'])

def update_question(question_id):
    data = request.get_json()
    question = Questions.query.get_or_404(question_id)
    if 'text' in data:
        question.text = data['text']
    if 'topic_id' in data:
        question.topic_id = data['topic_id']
    db.session.commit()
    return jsonify(to_dict(question)), 200

@app.route('/questions/<uuid:question_id>', methods=['DELETE'])

def delete_question(question_id):
    question = Questions.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return '', 204


# # UserAnswers CRUD Operations
# @app.route('/user_answers', methods=['POST'])
# def create_user_answer():
#     data = request.get_json()
#     new_user_answer = UserAnswers(
#         user_id=data['user_id'],
#         answer_id=data['answer_id']
#     )
#     db.session.add(new_user_answer)
#     db.session.commit()
#     return jsonify(to_dict(new_user_answer)), 201

# @app.route('/user_answers', methods=['GET'])
# def get_user_answers():
#     user_answers = UserAnswers.query.all()
#     return jsonify([to_dict(ua) for ua in user_answers]), 200

# @app.route('/user_answers/<uuid:user_answer_id>', methods=['GET'])
# def get_user_answer(user_answer_id):
#     user_answer = UserAnswers.query.get_or_404(user_answer_id)
#     return jsonify(to_dict(user_answer)), 200

# @app.route('/user_answers/<uuid:user_answer_id>', methods=['PUT'])
# def update_user_answer(user_answer_id):
#     data = request.get_json()
#     user_answer = UserAnswers.query.get_or_404(user_answer_id)
#     if 'user_id' in data:
#         user_answer.user_id = data['user_id']
#     if 'answer_id' in data:
#         user_answer.answer_id = data['answer_id']
#     db.session.commit()
#     return jsonify(to_dict(user_answer)), 200

# @app.route('/user_answers/<uuid:user_answer_id>', methods=['DELETE'])
# def delete_user_answer(user_answer_id):
#     user_answer = UserAnswers.query.get_or_404(user_answer_id)
#     db.session.delete(user_answer)
#     db.session.commit()
#     return '', 204


# Choice CRUD Operations
@app.route('/choices', methods=['POST'])

def create_choice():
    data = request.get_json()
    new_choice = Choice(
        text=data['text'],
        question_id=data['question_id'],
        is_correct=data.get('is_correct', False)
    )
    db.session.add(new_choice)
    db.session.commit()
    return jsonify(to_dict(new_choice)), 201


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

@app.route('/user_paragraphs', methods=['GET'])

def get_user_paragraphs():
    user_paragraphs = UserParagraph.query.all()
    return jsonify([to_dict(up) for up in user_paragraphs]), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['GET'])

def get_user_paragraph(user_paragraph_id):
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    return jsonify(to_dict(user_paragraph)), 200



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











    
    
    
    
    
    
    
    
    
    
    