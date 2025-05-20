from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import Client

auth_bp = Blueprint('auth', __name__)

TEST_USER = {
    'username': 'user',
    'password': generate_password_hash('user123')
}

@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'error': 'Dados devem ser enviados em formato JSON'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400

    if username != TEST_USER['username'] or not check_password_hash(TEST_USER['password'], password):
        return jsonify({'error': 'Credenciais inválidas'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200 