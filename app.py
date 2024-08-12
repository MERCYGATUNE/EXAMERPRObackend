from flask import Flask, request, jsonify, url_for
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


@app.route('/questions', methods=['POST'])
def create_question():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['question_text', 'exam_id', 'topic_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        exam_id = UUID(data['exam_id'])  # Ensure exam_id is a valid UUID
        topic_id = UUID(data['topic_id'])  # Ensure topic_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    question = Question(
        question_text=data['question_text'],
        choice1=data.get('choice1'),
        choice2=data.get('choice2'),
        choice3=data.get('choice3'),
        choice4=data.get('choice4'),
        isChoice=data.get('isChoice', False),
        answer=data.get('answer'),
        exam_id=exam_id,
        topic_id=topic_id
    )
    db.session.add(question)
    db.session.commit()

    return jsonify(question.to_dict()), 201

@app.route('/topics', methods=['POST'])
def create_topic():
    data = request.get_json()
    
  
    required_fields = ['name', 'sub_category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        
        sub_category_id = UUID(data['sub_category_id']) 
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    new_topic = Topic(
        name=data['name'],
        sub_category_id=sub_category_id
    )
    
    db.session.add(new_topic)
    try:
        db.session.commit()
        return jsonify({
            'id': str(new_topic.id),  
            'name': new_topic.name,
            'sub_category_id': str(new_topic.sub_category_id) 
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@app.route('/topics', methods=['GET'])
def get_topics():
    topics = Topic.query.all()
    return jsonify([{
        'id': str(topic.id),
        'name': topic.name,
        'sub_category_id': str(topic.sub_category_id)
    } for topic in topics])

@app.route('/topics/<uuid:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = Topic.query.get(topic_id)
    if topic is None:
        return jsonify({"error": "Topic not found"}), 404
    return jsonify({
        'id': str(topic.id),
        'name': topic.name,
        'sub_category_id': str(topic.sub_category_id)
    })

@app.route('/topics/<uuid:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    data = request.get_json()
    topic = Topic.query.get(topic_id)
    
    if topic is None:
        return jsonify({"error": "Topic not found"}), 404
    
    # Update topic fields
    topic.name = data.get('name', topic.name)
    topic.sub_category_id = UUID(data.get('sub_category_id', str(topic.sub_category_id)))

    db.session.commit()
    
    return jsonify({
        'id': str(topic.id),
        'name': topic.name,
        'sub_category_id': str(topic.sub_category_id)
    })
@app.route('/topics/<uuid:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    topic = Topic.query.get(topic_id)
    
    if topic is None:
        return jsonify({"error": "Topic not found"}), 404
    
    db.session.delete(topic)
    db.session.commit()
    
    return jsonify({"message": "Topic deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5555)