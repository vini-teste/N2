from flask import Blueprint, request, jsonify
from app.models import Horde, HordeProgress, Player, PlayerProgress, GameSession
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

horde_bp = Blueprint('horde', __name__)

@horde_bp.route('/hordes', methods=['POST'])
@jwt_required()
def create_horde():
    data = request.get_json()
    
    required_fields = ['name', 'math_subject', 'difficulty_level']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos obrigatórios: name, math_subject, difficulty_level'}), 400
    
    horde = Horde(
        name=data['name'],
        math_subject=data['math_subject'],
        difficulty_level=data['difficulty_level'],
        monster_count=data.get('monster_count', 10),
        xp_reward=data.get('xp_reward', 50)
    )
    
    db.session.add(horde)
    db.session.commit()
    
    return jsonify(horde.to_dict()), 201

@horde_bp.route('/hordes', methods=['GET'])
@jwt_required()
def get_hordes():
    hordes = Horde.query.all()
    return jsonify([horde.to_dict() for horde in hordes])

@horde_bp.route('/hordes/<int:horde_id>', methods=['GET'])
@jwt_required()
def get_horde(horde_id):
    horde = Horde.query.get_or_404(horde_id)
    return jsonify(horde.to_dict())

@horde_bp.route('/hordes/<int:horde_id>', methods=['PUT'])
@jwt_required()
def update_horde(horde_id):
    horde = Horde.query.get_or_404(horde_id)
    data = request.get_json()
    
    if 'name' in data:
        horde.name = data['name']
    if 'math_subject' in data:
        horde.math_subject = data['math_subject']
    if 'difficulty_level' in data:
        horde.difficulty_level = data['difficulty_level']
    if 'monster_count' in data:
        horde.monster_count = data['monster_count']
    if 'xp_reward' in data:
        horde.xp_reward = data['xp_reward']
    
    db.session.commit()
    return jsonify(horde.to_dict())

@horde_bp.route('/hordes/<int:horde_id>', methods=['DELETE'])
@jwt_required()
def delete_horde(horde_id):
    horde = Horde.query.get_or_404(horde_id)
    db.session.delete(horde)
    db.session.commit()
    return '', 204

@horde_bp.route('/hordes/<int:horde_id>/start', methods=['POST'])
@jwt_required()
def start_horde(horde_id):
    data = request.get_json()
    
    if not data or 'player_id' not in data:
        return jsonify({'error': 'ID do jogador é obrigatório'}), 400
    
    player = Player.query.get(data['player_id'])
    if not player:
        return jsonify({'error': 'Jogador não encontrado'}), 404
    
    horde = Horde.query.get_or_404(horde_id)
    
    if player.level < horde.difficulty_level:
        return jsonify({'error': 'Nível do jogador insuficiente para esta horda'}), 400
    
    active_horde = HordeProgress.query.filter_by(
        player_id=data['player_id'],
        is_completed=False
    ).first()
    
    if active_horde:
        return jsonify({'error': 'Jogador já está em uma horda ativa'}), 400
    
    active_session = GameSession.query.filter_by(
        player_id=data['player_id'],
        is_completed=False
    ).first()
    
    if not active_session:
        active_session = GameSession(player_id=data['player_id'])
        db.session.add(active_session)
        db.session.commit()
    
    horde_progress = HordeProgress(
        player_id=data['player_id'], 
        horde_id=horde_id,
        game_session_id=active_session.id
    )
    db.session.add(horde_progress)
    db.session.commit()
    
    return jsonify(horde_progress.to_dict()), 201

@horde_bp.route('/hordes/progress/<int:player_id>', methods=['GET'])
@jwt_required()
def get_player_horde_progress(player_id):
    progress = HordeProgress.query.filter_by(
        player_id=player_id,
        is_completed=False
    ).first()
    
    if not progress:
        return jsonify({'error': 'Nenhuma horda ativa encontrada'}), 404
    
    return jsonify(progress.to_dict())

@horde_bp.route('/hordes/progress/<int:player_id>/defeat', methods=['POST'])
@jwt_required()
def defeat_monster(player_id):
    progress = HordeProgress.query.filter_by(
        player_id=player_id,
        is_completed=False
    ).first_or_404()
    
    progress.defeat_monster()
    db.session.commit()
    
    return jsonify(progress.to_dict())

@horde_bp.route('/hordes/progress/<int:player_id>/history', methods=['GET'])
@jwt_required()
def get_horde_history(player_id):
    completed_hordes = HordeProgress.query.filter_by(
        player_id=player_id,
        is_completed=True
    ).order_by(HordeProgress.end_time.desc()).all()
    
    return jsonify([progress.to_dict() for progress in completed_hordes]) 