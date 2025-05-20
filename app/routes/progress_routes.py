from flask import Blueprint, request, jsonify
from app.models import PlayerProgress, Player
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/progress', methods=['POST'])
@jwt_required()
def create_progress():
    data = request.get_json()
    
    if not data or 'player_id' not in data:
        return jsonify({'error': 'ID do jogador é obrigatório'}), 400
    
    player = Player.query.get(data['player_id'])
    if not player:
        return jsonify({'error': 'Jogador não encontrado'}), 404
    
    existing_progress = PlayerProgress.query.filter_by(player_id=data['player_id']).first()
    if existing_progress:
        return jsonify({'error': 'Progresso já existe para este jogador'}), 400
    
    progress = PlayerProgress(player_id=data['player_id'])
    db.session.add(progress)
    db.session.commit()
    
    return jsonify(progress.to_dict()), 201

@progress_bp.route('/progress/<int:player_id>', methods=['GET'])
@jwt_required()
def get_progress(player_id):
    progress = PlayerProgress.query.filter_by(player_id=player_id).first_or_404()
    return jsonify(progress.to_dict())

@progress_bp.route('/progress/<int:player_id>', methods=['PUT'])
@jwt_required()
def update_progress(player_id):
    progress = PlayerProgress.query.filter_by(player_id=player_id).first_or_404()
    data = request.get_json()
    
    if 'xp_amount' in data:
        progress.add_xp(data['xp_amount'])
    
    db.session.commit()
    return jsonify(progress.to_dict())

@progress_bp.route('/progress/<int:player_id>', methods=['DELETE'])
@jwt_required()
def delete_progress(player_id):
    progress = PlayerProgress.query.filter_by(player_id=player_id).first_or_404()
    db.session.delete(progress)
    db.session.commit()
    return '', 204

@progress_bp.route('/progress/<int:player_id>/reset', methods=['POST'])
@jwt_required()
def reset_progress(player_id):
    progress = PlayerProgress.query.filter_by(player_id=player_id).first_or_404()
    
    progress.current_level = 1
    progress.current_xp = 0
    progress.xp_to_next_level = 100
    
    db.session.commit()
    return jsonify(progress.to_dict()) 