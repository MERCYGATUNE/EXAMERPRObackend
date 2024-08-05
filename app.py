from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, migrate, User, Subscription
import uuid
from datetime import datetime, timedelta
import bcrypt
import stripe
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object('config.Config')

# Configure logging
if not app.debug:
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

# Initialize CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize database and migrations
db.init_app(app)
migrate.init_app(app, db)

# Load Stripe secret key from environment variable
stripe_api_key = os.getenv('STRIPE_SECRET_KEY')

if not stripe_api_key:
    app.logger.error('STRIPE_SECRET_KEY environment variable not set')
else:
    stripe.api_key = stripe_api_key
    app.logger.info('Stripe API key loaded successfully')

def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

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
            return jsonify({
                'message': 'Login successful',
                'user_id': str(user.id)  # Return user ID
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    app.logger.info(f'Received data: {data}')
    
    user_id = data.get('user_id')
    payment_method_id = data.get('payment_method_id')
    amount = data.get('amount')

    if not user_id:
        app.logger.error('Missing user_id.')
        return jsonify({'error': 'User ID is required'}), 400

    if not payment_method_id:
        app.logger.error('Missing payment_method_id.')
        return jsonify({'error': 'Payment method ID is required'}), 400

    if amount is None or amount < 50:  # Ensure minimum amount of 50 KSh
        app.logger.error('Amount must be at least 50 KSh.')
        return jsonify({'error': 'Amount must be at least 50 KSh'}), 400

    if not is_valid_uuid(user_id):
        app.logger.error(f'Invalid user ID: {user_id}')
        return jsonify({'error': 'Invalid user ID'}), 400

    try:
        user_id = uuid.UUID(user_id)
        user = User.query.get(user_id)
        
        if not user:
            app.logger.error('User not found.')
            return jsonify({'error': 'User not found'}), 404

        # Create PaymentIntent with automatic payment methods enabled
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert KSh to cents
            currency='kes',
            payment_method=payment_method_id,
            confirm=True,
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never',  # Change this to 'always' if needed
            }
        )
        app.logger.info(f'Payment Intent created: {payment_intent.id}')

        new_subscription = Subscription(
            id=uuid.uuid4(),
            user_id=user_id,
            type='premium',
            amount=amount,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(new_subscription)
        db.session.commit()

        return jsonify({'success': True, 'subscription_id': new_subscription.id}), 201
    except stripe.error.CardError as e:
        app.logger.error(f'Card error: {str(e)}')
        return jsonify({'success': False, 'error': f'Card error: {str(e)}'}), 400
    except stripe.error.StripeError as e:
        app.logger.error(f'Stripe error: {str(e)}')
        return jsonify({'success': False, 'error': 'Payment failed. Please try again.'}), 400
    except Exception as e:
        app.logger.error(f'Exception occurred: {str(e)}')
        return jsonify({'success': False, 'error': 'An error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
