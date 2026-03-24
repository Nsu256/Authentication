from flask import Flask, request, josnfiy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json

    role = data.get('role')
    email = data.get('email')
    password = data.get('password')