from flask import Flask, request, jsonify
from models import db, migrate, User
import uuid
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate.init_app(app, db)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    new_user = User(
        id=uuid.uuid4(),
        email=email,
        password=password,
        confirmed_email=False,
        role='user',
        referral_code=None,
        created_at=datetime.utcnow()
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
