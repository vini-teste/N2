from flask import Blueprint, request, jsonify
from app.models import GameSession, Player, Horde, HordeProgress, Spellbook
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

game_session_bp = Blueprint('game_session', __name__)

@game_session_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    data = request.get_json()
    
    if not data or 'player_id' not in data:
        return jsonify({'error': 'ID do jogador é obrigatório'}), 400
    
    player = Player.query.get(data['player_id'])
    if not player:
        return jsonify({'error': 'Jogador não encontrado'}), 404
    
    active_session = GameSession.query.filter_by(
        player_id=data['player_id'],
        is_completed=False
    ).first()
    
    if active_session:
        return jsonify({'error': 'Jogador já possui uma sessão ativa'}), 400
    
    session = GameSession(player_id=data['player_id'])
    
    player.spellbook.reset()
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201

@game_session_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    session = GameSession.query.get_or_404(session_id)
    return jsonify(session.to_dict())

@game_session_bp.route('/sessions/<int:session_id>/end', methods=['POST'])
@jwt_required()
def end_session(session_id):
    session = GameSession.query.get_or_404(session_id)
    
    if session.is_completed:
        return jsonify({'error': 'Sessão já foi finalizada'}), 400
    
    session.end_session()
    
    session.player.update_stats(session)
    
    db.session.commit()
    return jsonify(session.to_dict())

@game_session_bp.route('/sessions/player/<int:player_id>/active', methods=['GET'])
@jwt_required()
def get_active_session(player_id):
    session = GameSession.query.filter_by(
        player_id=player_id,
        is_completed=False
    ).first()
    
    if not session:
        return jsonify({'error': 'Nenhuma sessão ativa encontrada'}), 404
    
    return jsonify(session.to_dict())

@game_session_bp.route('/sessions/player/<int:player_id>/history', methods=['GET'])
@jwt_required()
def get_session_history(player_id):
    sessions = GameSession.query.filter_by(
        player_id=player_id,
        is_completed=True
    ).order_by(GameSession.end_time.desc()).all()
    
    return jsonify([session.to_dict() for session in sessions])

@game_session_bp.route('/sessions/player/<int:player_id>/stats', methods=['GET'])
@jwt_required()
def get_player_stats(player_id):
    player = Player.query.get_or_404(player_id)
    
    total_sessions = GameSession.query.filter_by(player_id=player_id).count()
    completed_sessions = GameSession.query.filter_by(
        player_id=player_id,
        is_completed=True
    ).count()
    
    avg_score = 0
    if completed_sessions > 0:
        avg_score = db.session.query(db.func.avg(GameSession.final_score))\
            .filter_by(player_id=player_id, is_completed=True)\
            .scalar() or 0
    
    stats = {
        'player': player.to_dict(),
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'average_score': round(avg_score, 2),
        'best_score': player.best_score,
        'highest_horde_reached': player.highest_horde_reached,
        'total_play_time': player.total_play_time,
        'total_monsters_defeated': player.total_monsters_defeated
    }
    
    return jsonify(stats) 