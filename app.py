from sqlite3 import IntegrityError
from flask import Flask, request, jsonify, abort
from itsdangerous import URLSafeTimedSerializer
from flask_cors import CORS
from models import db, migrate, User, Subscription,ExamCategory,SubCategory,Topic, Exams, Question, UserExamResult
import uuid
from datetime import datetime, timedelta
import bcrypt
import stripe
import logging
from dotenv import load_dotenv
import os
from uuid import UUID
import json

from flask_mail import Mail, Message


app = Flask(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder
app.config.from_object('config.Config')
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')

# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == 'false'


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USERNAME'] = 'examerpro@gmail.com'
app.config['MAIL_PASSWORD'] = 'aghu rdsk jxqa encf'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

def send_email(to, subject, body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = body
    mail.send(msg)

CORS(app)

db.init_app(app)
migrate.init_app(app, db)

stripe.api_key = os.getenv('STRIPE_API_KEY')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index ():
    return "EXAMER PRO"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password or not username:
        return jsonify({'error': 'Email, Username and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already in use'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        id=uuid.uuid4(),
        email=email,
        password=hashed_password.decode('utf-8'),
        username=username,
        confirmed_email=False,
        role='user',
        referral_code=None,
        created_at=datetime.utcnow()
    )
    db.session.add(new_user)
    db.session.commit()
    send_email(email, 'ExamerPro™ - Successful Sign Up', 'Thank you for signing up!')
    

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        stored_password = user.password.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            send_email(email, 'Login Notification', 'You have logged in successfully!')
            return jsonify({
                'message': 'Login successful',
                "user_id": user.id,
                "role": user.role,
                "email": user.email,
                "username": user.username}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    return jsonify({'error': 'Invalid email or password'}), 401


@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    user_id = data.get('user_id')
    payment_method_id = data.get('payment_method_id')
    amount = data.get('amount')

    if user_id == 'undefined':
        return jsonify({'error': 'Invalid User ID'}), 400
    if not user_id or not payment_method_id or not amount:
        return jsonify({'error': 'User ID, payment method, and amount are required'}), 400

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid User ID format'}), 400

    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        amount_cents = int(float(amount) * 100)



        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents, 
            currency='kes',  
            payment_method=payment_method_id,
            confirm=True,
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never'
            }
        )

        # Create a new subscription
        new_subscription = Subscription(
            id=uuid.uuid4(),
            user_id=user_uuid,
            type='premium',  # Adjust based on your subscription types
            amount=amount_cents,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        if amount == 65:
            user.role = 'student'
            user.referral_code = str(uuid.uuid4())
            send_email(user.email, 'ExamerPro™ - Your Student Account', 'Congratulations! You have successfully created a student account.')
        if amount == 150:
            user.role = 'examiner'
            user.referral_code = str(uuid.uuid4())
            send_email(user.email, 'ExamerPro™ - Your Examiner Account', 'Congratulations! You have successfully created an examiner account.')
        
        db.session.add(new_subscription)
        db.session.commit()

        return jsonify({'success': True, 'subscription_id': str(new_subscription.id)}), 201

    except stripe.error.CardError as e:
        return jsonify({'success': False, 'error': f'Card error: {e.user_message}'}), 400
    except stripe.error.RateLimitError as e:
        return jsonify({'success': False, 'error': 'Too many requests to the API. Please try again later.'}), 429
    except stripe.error.InvalidRequestError as e:
        return jsonify({'success': False, 'error': 'Invalid parameters. Please check your input and try again.'}), 400
    except stripe.error.AuthenticationError as e:
        return jsonify({'success': False, 'error': 'Authentication with Stripe API failed. Please try again later.'}), 401
    except stripe.error.APIConnectionError as e:
        return jsonify({'success': False, 'error': 'Network communication with Stripe failed. Please try again later.'}), 502
    except stripe.error.StripeError as e:
        return jsonify({'success': False, 'error': 'Payment failed. Please try again.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'An error occurred. Please try again later.'}), 500
    
@app.route('/all_users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([{
        'id': str(user.id),
        'email': user.email,
        'username': user.username,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
    } for user in users])

@app.route('/update-subscription', methods=['POST'])
def update_subscription():
    data = request.get_json()
    subscription_id = data.get('subscription_id')
    user_id = data.get('user_id')
    amount = data.get('amount')

    if not subscription_id or not user_id or not amount:
        return jsonify({'error': 'Subscription ID, user ID, and amount are required'}), 400

    subscription = Subscription.query.get(subscription_id)
    if not subscription or subscription.user_id!= user_id:
        return jsonify({'error': 'Invalid subscription or user ID'}), 404

    subscription.amount = amount
    subscription.expires_at = datetime.utcnow() + timedelta(days=30)

    db.session.commit()

    return jsonify({'success': True}), 200

@app.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    data = request.get_json()
    subscription_id = data.get('subscription_id')
    user_id = data.get('user_id')

    if not subscription_id or not user_id:
        return jsonify({'error': 'Subscription ID and user ID are required'}), 400

    subscription = Subscription.query.get(subscription_id)
    if not subscription or subscription.user_id!= user_id:
        return jsonify({'error': 'Invalid subscription or user ID'}), 404

    try:
        # Cancel the subscription
        stripe.Subscription.cancel(subscription.id, at_period_end=True)

        # Update the subscription status in the database
        subscription.status = 'cancelled'
        db.session.commit()

        return jsonify({'success': True}), 200
    except stripe.error.InvalidRequestError as e:
        return jsonify({'success': False, 'error': f'Invalid request'}, 400)
    except stripe.error.RateLimitError as e:
        return jsonify({'success': False, 'error': f'Rate limit exceeded'}, 429)
    except stripe.error.AuthenticationError as e:
        return jsonify({'success': False, 'error': 'Authentication error'}, 401)
    
    
@app.route('/create_question', methods=['POST'])
def create_question():
    data = request.get_json()

    # Validate data
    question_text = data.get('question')
    topic_id = data.get('topic_id')  # Expect UUID or None
    mode = data.get('mode')
    exam_mode = data.get('exam_mode')

    if not question_text:
        return jsonify({"error": "Question text is required"}), 400

    # Convert topic_id to UUID if not None
    if topic_id:
        if isinstance(topic_id, int):
            topic_id = str(topic_id)  # Convert integer to string
        try:
            topic_id = uuid.UUID(topic_id)
        except ValueError:
            return jsonify({"error": "Invalid topic_id format"}), 400

    # Create new question instance
    new_question = Question(
        question=question_text,
        topic_id=topic_id,  # Should be a UUID or None
        mode=mode,
        exam_mode=exam_mode
    )

    # Add to session and commit
    db.session.add(new_question)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Question created successfully", "question_id": str(new_question.id)}), 201

@app.route('/questions/<uuid:question_id>/answers', methods=['POST'])
def create_answer(question_id):
    data = request.get_json()
    answer = answer(
        question_id=question_id,
        answer_type=data['answer_type'],
        answer=data['answer']
    )
    db.session.add(answer)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify(answer.to_dict()), 201

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = questions.query.all()
    return jsonify([question.to_dict() for question in questions])

# @app.route('/questions/<uuid:question_id>', methods=['DELETE'])
# def delete_question(question_id):
#     # Ensure user is logged in
#     if not current_user.is_authenticated:
#         return jsonify({"error": "Unauthorized"}), 401

#     # Check if the user is an admin
#     if not current_user.is_admin:
#         return jsonify({"error": "Forbidden"}), 403

#     # Find the question to delete
#     question = Questions.query.get(question_id)
#     if not question:
#         return jsonify({"error": "Question not found"}), 404

#     # Delete the question
#     db.session.delete(question)
#     try:
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500

#     return jsonify({"message": "Question deleted successfully"}), 200







       #  EXAM CATEGORIES   
@app.route('/examcategories', methods=['POST'])
def create_exam_category():
    data = request.json

    if not data or not 'name' in data:
        abort(400, description="Name is required")
    
    new_category = ExamCategory(
        name=data.get('name'),
        description=data.get('description')
    )
    
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({"id": new_category.id, "name": new_category.name, "description": new_category.description}), 201

# Get all Exam Categories
@app.route('/examcategories', methods=['GET'])
def get_exam_categories():
    categories = ExamCategory.query.all()
    return jsonify([
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "subcategories": [{"id": sub.id, "name": sub.name} for sub in category.subcategories]
        } for category in categories
    ]), 200

# Get a Single Exam Category by ID
@app.route('/examcategories/<uuid:id>', methods=['GET'])
def get_exam_category(id):
    category = ExamCategory.query.get_or_404(id)
    return jsonify({
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "subcategories": [{"id": sub.id, "name": sub.name} for sub in category.subcategories]
    }), 200

# Update Exam Category
@app.route('/examcategories/<uuid:id>', methods=['PUT'])
def update_exam_category(id):
    category = ExamCategory.query.get_or_404(id)
    data = request.json

    category.name = data.get('name', category.name)
    category.description = data.get('description', category.description)
    
    db.session.commit()

    return jsonify({"id": category.id, "name": category.name, "description": category.description}), 200

# Delete Exam Category
@app.route('/examcategories/<uuid:id>', methods=['DELETE'])
def delete_exam_category(id):
    category = ExamCategory.query.get_or_404(id)
    
    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "Category deleted successfully"}), 200





    
    
    
       # SUBCATEGORIES    
@app.route('/subcategory', methods=['POST'])
def create_subcategory():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('exam_category_id'):
        abort(400, "Missing required fields: 'name', 'exam_category_id'")

    try:
        exam_category_id = UUID(data['exam_category_id'])  # Convert to UUID
    except ValueError:
        abort(400, "Invalid 'exam_category_id' format")

    subcategory = SubCategory(
        name=data['name'],
        exam_category_id=exam_category_id
    )
    db.session.add(subcategory)
    db.session.commit()

    return jsonify({"message": "SubCategory created", "id": str(subcategory.id)}), 201




# Read a single SubCategory by ID
@app.route('/subcategory/<uuid:id>', methods=['GET'])
def get_subcategory(id):
    subcategory = SubCategory.query.get(id)
    if not subcategory:
        abort(404, "SubCategory not found")

    return jsonify({
        'id': str(subcategory.id),
        'name': subcategory.name,
        'exam_category_id': str(subcategory.exam_category_id)
    })

# Read all SubCategories
@app.route('/subcategories', methods=['GET'])
def get_subcategories():
    subcategories = SubCategory.query.all()
    return jsonify([
        {
            'id': str(subcategory.id),
            'name': subcategory.name,
            'exam_category_id': str(subcategory.exam_category_id)
        } for subcategory in subcategories
    ])

# Update an existing SubCategory
@app.route('/subcategory/<uuid:id>', methods=['PUT'])
def update_subcategory(id):
    data = request.get_json()
    subcategory = SubCategory.query.get(id)
    if not subcategory:
        abort(404, "SubCategory not found")

    if 'name' in data:
        subcategory.name = data['name']
    if 'exam_category_id' in data:
        subcategory.exam_category_id = data['exam_category_id']

    db.session.commit()
    return jsonify({"message": "SubCategory updated"})

# Delete a SubCategory
@app.route('/subcategory/<uuid:id>', methods=['DELETE'])
def delete_subcategory(id):
    subcategory = SubCategory.query.get(id)
    if not subcategory:
        abort(404, "SubCategory not found")

    db.session.delete(subcategory)
    db.session.commit()
    return jsonify({"message": "SubCategory deleted"})    

    
    
    
    
    # TOPICS
    
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

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def verify_reset_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except:
        return None
    return email

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    token = generate_reset_token(email)
    reset_url = reset_url = f"http://localhost:3000/reset-password/{token}"
    send_email(email, 'Password Reset Request', f'Click the link to reset your password: {reset_url} \n \n You have exactly 1 hour to reset this password \n \n Ignore this email if you did not initialize this.')

    return jsonify({"message": "Password reset email sent."}), 200

@app.route('/reset_password/<token>', methods=['POST'])
def reset_with_token(token):
    email = verify_reset_token(token)
    if not email:
        return jsonify({"message": "Invalid or expired token"}), 400
    
    data = request.get_json()
    new_password = data['new_password']
    user = User.query.filter_by(email=email).first()
    if user:
        new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = new_hashed_password.decode('utf-8')
        db.session.commit()
        return jsonify({"message": "Password has been reset."}), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
@app.route('/change_username', methods=['POST'])
def change_username():
    data = request.get_json()
    current_user_id = data['user_id']
    current_user_uuid = uuid.UUID(current_user_id)
    new_username = data['new_username']
    user = User.query.filter_by(id=current_user_uuid).first()
    if user:
        user.username = new_username
        db.session.commit()
        return jsonify({"message": "Username has been changed."}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/change_email', methods=['POST'])
def change_email():
    data = request.get_json()
    current_user_id = data['user_id']
    current_user_uuid = uuid.UUID(current_user_id)
    new_email = data['new_email']
    if User.query.filter_by(email=new_email).first():
        return jsonify({'error': 'Email already in use'}), 400
    user = User.query.filter_by(id=current_user_uuid).first()
    if user:
        user.email = new_email
        db.session.commit()
        return jsonify({"message": "Email has been changed."}), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/delete_account', methods=['POST'])
def delete_account():
    data = request.get_json()
    current_user_id = data['user_id']
    current_user_uuid = uuid.UUID(current_user_id)
    user = User.query.filter_by(id=current_user_uuid).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Account has been deleted."}), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.get_json()
    user_id = data.get('id')
    username = data.get('username')
    email = data.get('email')
    role = data.get('role')
    new_password = data.get('password')

    userUUID = uuid.UUID(user_id) 

    user = User.query.get(userUUID)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if username:
        user.username = username
    if email:
        user.email = email
    if role:
        user.role = role
    if new_password:
        new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = new_hashed_password.decode('utf-8')

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    data = request.json
    exam_id = data['exam_id']
    user_answers = data['user_answers']  # This is a dictionary of question IDs and selected answers
    
    # Fetch the exam from the database
    exam = Exams.query.get(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404
    
    # Initialize variables to calculate the score
    total_questions = len(exam.questions)
    correct_answers = 0

    # Compare user answers with correct answers
    for question in exam.questions:
        question_id = question.id
        correct_answer = question.answer
        user_answer = user_answers.get(question_id)
        
        if user_answer and user_answer == correct_answer:
            correct_answers += 1
    
    # Calculate grade as a percentage
    grade = (correct_answers / total_questions) * 100
    
    result = UserExamResult(user_id=user_id, exam_id=exam_id, grade=grade)
    db.session.add(result)
    db.session.commit()
    return jsonify({'grade': grade})



     # UserExamResult
     
# @app.route('/user_exam_result', methods=['POST'])
# def create_user_exam_result():
#     data = request.get_json()
#     user_exam_result = UserExamResult(
#         id=uuid.uuid4(),
#         user_id=uuid.UUID(data.get('user_id')),
#         exam_id=uuid.UUID(data.get('exam_id')),
#         grade=data.get('grade')
#     )
#     db.session.add(user_exam_result)
#     db.session.commit()
#     return jsonify({'message': 'UserExamResult created successfully', 'user_exam_result': user_exam_result.id}), 201



# @app.route('/user_exam_result', methods=['GET'])
# def get_user_exam_results():
#     print("Route accessed") 
#     user_exam_results = UserExamResult.query.all()
#     results = []
#     for result in user_exam_results:
#         results.append({
#             'id': str(result.id),
#             'user_id': str(result.user_id),
#             'exam_id': str(result.exam_id),
#             'grade': result.grade
#         })
#     return jsonify(results), 200
     
# @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['GET'])
# def get_user_exam_result(user_exam_result_id):
#     user_exam_result = UserExamResult.query.get_or_404(user_exam_result_id)
#     result = {
#         'id': str(user_exam_result.id),
#         'user_id': str(user_exam_result.user_id),
#         'exam_id': str(user_exam_result.exam_id),
#         'grade': user_exam_result.grade
#     }
#     return jsonify(result), 200
     
# @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['PUT'])
# def update_user_exam_result(user_exam_result_id):
#     user_exam_result = UserExamResult.query.get_or_404(user_exam_result_id)
#     data = request.get_json()
#     user_exam_result.user_id = data.get('user_id', user_exam_result.user_id)
#     user_exam_result.exam_id = data.get('exam_id', user_exam_result.exam_id)
#     user_exam_result.grade = data.get('grade', user_exam_result.grade)
#     db.session.commit()
#     return jsonify({'message': 'UserExamResult updated successfully'}), 200


# @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['DELETE'])
# def delete_user_exam_result(user_exam_result_id):
#     user_exam_result = UserExamResult.query.get_or_404(user_exam_result_id)
#     db.session.delete(user_exam_result)
#     db.session.commit()
#     return jsonify({'message': 'UserExamResult deleted successfully'}), 200

# @app.route('/user_exam_result', methods=['POST'])

# def create_user_exam_result():
    
#     data = request.get_json()
    
#     user_id = uuid.UUID(data.get('user_id'))
#     exam_id = uuid.UUID(data.get('exam_id'))
    
    
#     user_exam_result = UserExamResult(
#         user_id=user_id,
#         exam_id=exam_id,
#         grade=data.get('grade')
#     )
#     db.session.add(user_exam_result)
#     db.session.commit()
#     return jsonify({'message': 'UserExamResult created successfully', 'user_exam_result': user_exam_result.id}), 201




# @app.route('/user_exam_result', methods=['GET'])

# def get_user_exam_results():
#     user_exam_results = UserExamResult.query.all()
#     results = []
#     for result in user_exam_results:
#         results.append({
#             'id': result.id,
#             'user_id': result.user_id,
#             'exam_id': result.exam_id,
#             'grade': result.grade
#         })
#     return jsonify(results), 200





# # @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['GET'])
# # def get_user_exam_result(user_exam_result_id):
# #     user_exam_result = UserExamResult.query.get_or_404(str(user_exam_result_id))
# #     result = {
# #         'id': user_exam_result.id,
# #         'user_id': user_exam_result.user_id,
# #         'exam_id': user_exam_result.exam_id,
# #         'grade': user_exam_result.grade
# #     }
# #     return jsonify(result), 200

# @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['GET'])
# def get_user_exam_result(user_exam_result_id):
#     # Directly use user_exam_result_id as it is already a UUID object
#     user_exam_result = UserExamResult.query.get_or_404(user_exam_result_id)
#     result = {
#         'id': str(user_exam_result.id),  # Convert UUID to string for JSON response
#         'user_id': str(user_exam_result.user_id),  # Convert UUID to string
#         'exam_id': str(user_exam_result.exam_id),  # Convert UUID to string
#         'grade': user_exam_result.grade
#     }
#     return jsonify(result), 200





# # @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['PUT'])
# # def update_user_exam_result(user_exam_result_id):
# #     user_exam_result = UserExamResult.query.get_or_404(str(user_exam_result_id))
# #     data = request.get_json()
# #     user_exam_result.user_id = str(uuid.UUID(data.get('user_id', user_exam_result.user_id)))
# #     user_exam_result.exam_id = str(uuid.UUID(data.get('exam_id', user_exam_result.exam_id)))
# #     user_exam_result.grade = data.get('grade', user_exam_result.grade)
# #     db.session.commit()
# #     return jsonify({'message': 'UserExamResult updated successfully'}), 200
# @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['PUT'])
# def update_user_exam_result(user_exam_result_id):
#     user_exam_result = UserExamResult.query.get_or_404(user_exam_result_id)
#     data = request.get_json()
    
#     # Convert UUID strings to UUID objects only if present in the request data
#     if 'user_id' in data:
#         user_exam_result.user_id = uuid.UUID(data['user_id'])  # Convert string to UUID if provided
#     if 'exam_id' in data:
#         user_exam_result.exam_id = uuid.UUID(data['exam_id'])  # Convert string to UUID if provided
#     if 'grade' in data:
#         user_exam_result.grade = data['grade']
    
#     db.session.commit()
#     return jsonify({'message': 'UserExamResult updated successfully'}), 200







# # @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['DELETE'])
# # def delete_user_exam_result(user_exam_result_id):
# #     user_exam_result = UserExamResult.query.get_or_404(str(user_exam_result_id))
# #     db.session.delete(user_exam_result)
# #     db.session.commit()
# #     return jsonify({'message': 'UserExamResult created successfully', 'user_exam_result': user_exam_result.id}), 201

# @app.route('/user_exam_result/<uuid:user_exam_result_id>', methods=['DELETE'])
# def delete_user_exam_result(user_exam_result_id):
#     user_exam_result = UserExamResult.query.get_or_404(user_exam_result_id)
#     db.session.delete(user_exam_result)
#     db.session.commit()
#     return jsonify({'message': 'UserExamResult deleted successfully', 'user_exam_result': str(user_exam_result.id)}), 200

@app.route('/user_exam_result', methods=['POST'])
def create_user_exam_result():
    data = request.json
    try:
        new_result = UserExamResult(
            id=uuid.uuid4(),
            user_id=data['user_id'],
            exam_id=data['exam_id'],
            grade=data['grade']
        )
        db.session.add(new_result)
        db.session.commit()
        return jsonify({'message': 'UserExamResult created', 'id': str(new_result.id)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/user_exam_result/<uuid:id>', methods=['GET'])
def get_user_exam_result(id):
 try:
    result = UserExamResult.query.get(uuid.UUID(id))
    if result:
        return jsonify({
            'id': str(result.id),
            'user_id': str(result.user_id),
            'exam_id': str(result.exam_id),
            'grade': result.grade
        })
    return jsonify({'message': 'UserExamResult not found'}), 404
 except ValueError:
    return jsonify({'message': 'Invalid UUID format'}), 400


@app.route('/user_exam_result/<uuid:id>', methods=['PUT'])
def update_user_exam_result(id):
    data = request.json
    try:
        result = UserExamResult.query.get(uuid.UUID(id))
        
        if result:
            result.user_id = uuid.UUID(data.get('user_id', result.user_id))
            result.exam_id = uuid.UUID(data.get('exam_id', result.exam_id))
            result.grade = data.get('grade', result.grade)
            db.session.commit()
            return jsonify({'message': 'UserExamResult updated'})
        return jsonify({'message': 'UserExamResult not found'}), 404
    except ValueError:
        return jsonify({'message': 'Invalid UUID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/user_exam_result/<uuid:id>', methods=['DELETE'])
def delete_user_exam_result(id):
    try:
        result = UserExamResult.query.get(uuid.UUID(id))
        if result:
            db.session.delete(result)
            db.session.commit()
            return jsonify({'message': 'UserExamResult deleted'})
        return jsonify({'message': 'UserExamResult not found'}), 404
    except ValueError:
        return jsonify({'message': 'Invalid UUID format'}), 400

     
     
     
     
         






# http://127.0.0.1:5000/examcategories , it works!!1.
# http://127.0.0.1:5000/subcategories  , it works

if __name__ == '__main__':
    app.run(debug=True, port=5555)