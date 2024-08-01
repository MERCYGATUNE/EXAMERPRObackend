from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, migrate, User, Subscription
import uuid
from datetime import datetime, timedelta
import bcrypt
import stripe

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

if __name__ == '__main__':
    app.run(debug=True)
