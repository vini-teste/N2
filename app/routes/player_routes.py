from flask import Blueprint, request, jsonify
from app.models import Player
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

player_bp = Blueprint('player', __name__)

@player_bp.route('/players', methods=['POST'])
@jwt_required()
def create_player():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Nome do personagem é obrigatório'}), 400
    
    player = Player(name=data['name'])
    db.session.add(player)
    db.session.commit()
    
    return jsonify(player.to_dict()), 201

@player_bp.route('/players', methods=['GET'])
@jwt_required()
def get_players():
    players = Player.query.all()
    return jsonify([player.to_dict() for player in players])

@player_bp.route('/players/<int:player_id>', methods=['GET'])
@jwt_required()
def get_player(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify(player.to_dict())

@player_bp.route('/players/<int:player_id>', methods=['PUT'])
@jwt_required()
def update_player(player_id):
    player = Player.query.get_or_404(player_id)
    data = request.get_json()
    
    if 'name' in data:
        player.name = data['name']
    if 'hp' in data:
        player.hp = min(data['hp'], player.max_hp)
    if 'xp' in data:
        player.gain_xp(data['xp'])
    
    player.last_played = datetime.utcnow()
    db.session.commit()
    
    return jsonify(player.to_dict())

@player_bp.route('/players/<int:player_id>', methods=['DELETE'])
@jwt_required()
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)

    if player.spellbook:
        db.session.delete(player.spellbook)

    db.session.delete(player)
    db.session.commit()
    return '', 204

@player_bp.route('/players/<int:player_id>/reset', methods=['POST'])
@jwt_required()
def reset_player(player_id):
    player = Player.query.get_or_404(player_id)
    
    player.level = 1
    player.xp = 0
    player.hp = 100
    player.max_hp = 100
    
    player.spellbook.spells = ['Bola de Fogo']
    
    db.session.commit()
    return jsonify(player.to_dict()) 