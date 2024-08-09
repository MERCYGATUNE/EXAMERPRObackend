from flask import Flask, request, jsonify, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_cors import CORS
from models import db, migrate, User, Subscription,Questions,Answers,ExamCategory,SubCategory,Topic
import uuid
from datetime import datetime, timedelta
import bcrypt
import stripe
import logging
from dotenv import load_dotenv
import os
from uuid import UUID
from flask_mail import Mail, Message
from config import Config

from resources.student import student_bp
   

from resources.admin import admin_bp
    

from resources.examiner import examiner_bp


# Registering Blueprints

app.register_blueprint(student_bp)
app.register_blueprint(examiner_bp)
app.register_blueprint(admin_bp)





app = Flask(__name__)

app.config.from_object('config.Config')
load_dotenv()

SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'

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
def index():
    text='EXAMINER PRO'
    return text

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
    new_question = Questions(
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
    answer = Answers(
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
    questions = Questions.query.all()
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




    
    
    
    


if __name__ == '__main__':
    app.run(debug=True, port=5555)