from flask import Flask, request, jsonify

from flask_cors import CORS
from models import db, migrate, User, Subscription,Questions,Answers,ExamCategory,SubCategory,Topic
import uuid
from datetime import datetime, timedelta
import bcrypt
import stripe
from uuid import UUID


app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app)

db.init_app(app)
migrate.init_app(app, db)

stripe.api_key = 'your-secret-key-here'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already in use'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        id=uuid.uuid4(),
        email=email,
        password=hashed_password.decode('utf-8'),
        confirmed_email=False,
        role='user',
        referral_code=None,
        created_at=datetime.utcnow()
    )
    db.session.add(new_user)
    db.session.commit()

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
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    return jsonify({'error': 'Invalid email or password'}), 401


@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    user_id = data.get('user_id')
    payment_method_id = data.get('payment_method_id')
    amount = data.get('amount')

    if not user_id or not payment_method_id or not amount:
        return jsonify({'error': 'User ID, payment method, and amount are required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        # Create a Payment Intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe expects the amount in cents
            currency='kes',  # Use 'kes' for Kenyan Shilling
            payment_method=payment_method_id,
            confirm=True,
        )

        # Create a new subscription
        new_subscription = Subscription(
            id=uuid.uuid4(),
            user_id=user_id,
            type='premium',  # Adjust based on your subscription types
            amount=amount,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(new_subscription)
        db.session.commit()

        return jsonify({'success': True, 'subscription_id': new_subscription.id}), 201
    except stripe.error.CardError as e:
        return jsonify({'success': False, 'error': f'Card error: {str(e)}'}), 400
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
