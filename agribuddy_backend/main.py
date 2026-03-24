from flask import Flask, request, josnfiy
from flask_cors import CORS
from werkzeug.security import check-password_harsh

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
        