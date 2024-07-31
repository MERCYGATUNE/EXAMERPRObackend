from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, migrate, User
import uuid
from datetime import datetime
import bcrypt  # Ensure bcrypt is installed: `pip install bcrypt`

app = Flask(__name__)
app.config.from_object('config.Config')

# Enable CORS
CORS(app)

db.init_app(app)
migrate.init_app(app, db)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Check if the email already exists
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
        try:
            # Check if the stored password is a valid bcrypt hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
        except ValueError:
            # If the stored password is not a valid bcrypt hash, rehash it
            hashed_password = bcrypt.hashpw(stored_password, bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')
            db.session.commit()
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
    return jsonify({'error': 'Invalid email or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)
