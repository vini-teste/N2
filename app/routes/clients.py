from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Client

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/', methods=['GET'])
@jwt_required()
def get_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients]), 200

@clients_bp.route('/', methods=['POST'])
@jwt_required()
def create_client():
    if not request.is_json:
        return jsonify({'error': 'Dados devem ser enviados em formato JSON'}), 400

    data = request.get_json()
    
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400

    if Client.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Nome já existe'}), 400

    if Client.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já existe'}), 400

    client = Client(name=data['name'], email=data['email'])
    db.session.add(client)
    
    try:
        db.session.commit()
        return jsonify(client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar cliente'}), 500

@clients_bp.route('/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    if not request.is_json:
        return jsonify({'error': 'Dados devem ser enviados em formato JSON'}), 400

    client = Client.query.get_or_404(client_id)
    data = request.get_json()

    if 'name' in data:
        if Client.query.filter_by(name=data['name']).first() and client.name != data['name']:
            return jsonify({'error': 'Nome já existe'}), 400
        client.name = data['name']

    if 'email' in data:
        if Client.query.filter_by(email=data['email']).first() and client.email != data['email']:
            return jsonify({'error': 'Email já existe'}), 400
        client.email = data['email']

    try:
        db.session.commit()
        return jsonify(client.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar cliente'}), 500

@clients_bp.route('/<int:client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao excluir cliente'}), 500 