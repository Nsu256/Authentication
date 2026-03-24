from flask import Flask, request, jsonfiy
from flask_cors import CORS
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json

    role = data.get('role')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash,password) and user.role == role:
        return jsonify({'message': 'Login successful', 'role': user.role}),200
    else:
        return jsonify({'error': 'Invalid credentials'}),401