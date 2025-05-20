from app import db
from datetime import datetime

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    hp = db.Column(db.Integer, default=100)
    max_hp = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_played = db.Column(db.DateTime, default=datetime.utcnow)
    
    total_games_played = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)
    total_hordes_completed = db.Column(db.Integer, default=0)
    highest_horde_reached = db.Column(db.Integer, default=0)
    total_monsters_defeated = db.Column(db.Integer, default=0)
    total_play_time = db.Column(db.Integer, default=0) 
    
    spellbook = db.relationship('Spellbook', backref='player', uselist=False)
    game_sessions = db.relationship('GameSession', backref='player', lazy=True)
    
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0
        self.hp = 100
        self.max_hp = 100
        self.total_games_played = 0
        self.best_score = 0
        self.total_hordes_completed = 0
        self.highest_horde_reached = 0
        self.total_monsters_defeated = 0
        self.total_play_time = 0
        self.spellbook = Spellbook()
    
    def update_stats(self, game_session):
        if self.total_games_played is None:
            self.total_games_played = 0
        if self.total_hordes_completed is None:
            self.total_hordes_completed = 0
        if self.total_monsters_defeated is None:
            self.total_monsters_defeated = 0
        if self.total_play_time is None:
            self.total_play_time = 0
        if self.best_score is None:
            self.best_score = 0
        if self.highest_horde_reached is None:
            self.highest_horde_reached = 0
            
        self.total_games_played += 1
        self.total_hordes_completed += game_session.hordes_completed
        self.total_monsters_defeated += game_session.monsters_defeated
        self.total_play_time += game_session.play_time
        
        if game_session.final_score > self.best_score:
            self.best_score = game_session.final_score
        
        if game_session.highest_horde_reached > self.highest_horde_reached:
            self.highest_horde_reached = game_session.highest_horde_reached
        
        self.last_played = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'xp': self.xp,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'total_games_played': self.total_games_played,
            'best_score': self.best_score,
            'total_hordes_completed': self.total_hordes_completed,
            'highest_horde_reached': self.highest_horde_reached,
            'total_monsters_defeated': self.total_monsters_defeated,
            'total_play_time': self.total_play_time,
            'created_at': self.created_at.isoformat(),
            'last_played': self.last_played.isoformat(),
            'spellbook': self.spellbook.to_dict() if self.spellbook else None
        }

class Spellbook(db.Model):
    __tablename__ = 'spellbooks'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    spells = db.Column(db.JSON, default=list)
    current_power = db.Column(db.Integer, default=1)
    upgrade_level = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self):
        self.spells = ['Bola de Fogo']
        self.current_power = 1
        self.upgrade_level = 1
        self.is_active = True
    
    def reset(self):
        self.spells = ['Bola de Fogo']
        self.current_power = 1
        self.upgrade_level = 1
        self.is_active = True
    
    def upgrade(self):
        self.upgrade_level += 1
        self.current_power = int(self.current_power * 1.5)
        self.add_new_spell()
    
    def add_new_spell(self):
        available_spells = [
            'Raio de Gelo',
            'Explosão Arcana',
            'Tempestade de Energia',
            'Névoa Venenosa',
            'Projétil Mágico'
        ]
        new_spells = [spell for spell in available_spells if spell not in self.spells]
        if new_spells:
            self.spells.append(new_spells[0])
    
    def to_dict(self):
        return {
            'id': self.id,
            'spells': self.spells,
            'current_power': self.current_power,
            'upgrade_level': self.upgrade_level,
            'is_active': self.is_active
        }

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    final_score = db.Column(db.Integer, default=0)
    hordes_completed = db.Column(db.Integer, default=0)
    monsters_defeated = db.Column(db.Integer, default=0)
    highest_horde_reached = db.Column(db.Integer, default=0)
    highest_level_reached = db.Column(db.Integer, default=1)
    play_time = db.Column(db.Integer, default=0)  
    is_completed = db.Column(db.Boolean, default=False)
    
    def calculate_score(self):
        base_score = 1000 
        
        level_bonus = self.highest_level_reached * 500
        
        horde_bonus = self.hordes_completed * 200
        
        monster_bonus = self.monsters_defeated * 50
        
        time_bonus = (self.play_time // 300) * 100
        
        self.final_score = base_score + level_bonus + horde_bonus + monster_bonus + time_bonus
        return self.final_score
    
    def end_session(self):
        self.end_time = datetime.utcnow()
        self.play_time = int((self.end_time - self.start_time).total_seconds())
        self.calculate_score()
        self.is_completed = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'final_score': self.final_score,
            'hordes_completed': self.hordes_completed,
            'monsters_defeated': self.monsters_defeated,
            'highest_horde_reached': self.highest_horde_reached,
            'highest_level_reached': self.highest_level_reached,
            'play_time': self.play_time,
            'is_completed': self.is_completed
        }

class Horde(db.Model):
    __tablename__ = 'hordes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    math_subject = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)
    monster_count = db.Column(db.Integer, default=10)
    xp_reward = db.Column(db.Integer, nullable=False)
    is_boss_horde = db.Column(db.Boolean, default=False)
    required_hordes_completed = db.Column(db.Integer, default=0)
    difficulty_multiplier = db.Column(db.Float, default=1.0)
    time_limit = db.Column(db.Integer, nullable=True)  # em segundos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, math_subject, difficulty_level, monster_count=10, xp_reward=50):
        self.name = name
        self.math_subject = math_subject
        self.difficulty_level = difficulty_level
        self.monster_count = monster_count
        self.xp_reward = xp_reward
        self.difficulty_multiplier = 1.0 + (difficulty_level * 0.1) 
    
    def calculate_difficulty(self, player_level):
        level_difference = player_level - self.difficulty_level
        if level_difference > 0:
            return max(0.5, self.difficulty_multiplier * (1 - (level_difference * 0.05)))
        else:
            return self.difficulty_multiplier * (1 + (abs(level_difference) * 0.1))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'math_subject': self.math_subject,
            'difficulty_level': self.difficulty_level,
            'monster_count': self.monster_count,
            'xp_reward': self.xp_reward,
            'is_boss_horde': self.is_boss_horde,
            'required_hordes_completed': self.required_hordes_completed,
            'difficulty_multiplier': self.difficulty_multiplier,
            'time_limit': self.time_limit,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PlayerProgress(db.Model):
    __tablename__ = 'player_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    current_xp = db.Column(db.Integer, default=0)
    xp_to_next_level = db.Column(db.Integer, default=100)
    upgrade_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    player = db.relationship('Player', backref='progress')
    
    def __init__(self, player_id):
        self.player_id = player_id
        self.current_xp = 0
        self.xp_to_next_level = 100
        self.upgrade_level = 1
    
    def add_xp(self, amount):
        self.current_xp += amount
        
        while self.current_xp >= self.xp_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.player.level += 1
        
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        self.upgrade_level += 1
        
        if self.player.spellbook:
            self.player.spellbook.upgrade()
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'current_xp': self.current_xp,
            'xp_to_next_level': self.xp_to_next_level,
            'upgrade_level': self.upgrade_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class HordeProgress(db.Model):
    __tablename__ = 'horde_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    horde_id = db.Column(db.Integer, db.ForeignKey('hordes.id'), nullable=False)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    monsters_defeated = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    completion_time = db.Column(db.Integer, nullable=True)
    
    player = db.relationship('Player', backref='horde_progresses')
    horde = db.relationship('Horde', backref='progresses')
    game_session = db.relationship('GameSession', backref='horde_progresses')
    
    def __init__(self, player_id, horde_id, game_session_id):
        self.player_id = player_id
        self.horde_id = horde_id
        self.game_session_id = game_session_id
        self.monsters_defeated = 0
        self.is_completed = False
    
    def defeat_monster(self):
        self.monsters_defeated += 1
        if self.monsters_defeated >= self.horde.monster_count:
            self.complete_horde()
    
    def complete_horde(self):
        self.is_completed = True
        self.end_time = datetime.utcnow()
        self.completion_time = int((self.end_time - self.start_time).total_seconds())
        
        self.game_session.hordes_completed += 1
        self.game_session.monsters_defeated += self.monsters_defeated
        self.game_session.highest_horde_reached = max(
            self.game_session.highest_horde_reached,
            self.horde.difficulty_level
        )
        
        player_progress = PlayerProgress.query.filter_by(player_id=self.player_id).first()
        if player_progress:
            xp_reward = int(self.horde.xp_reward * self.horde.difficulty_multiplier)
            player_progress.add_xp(xp_reward)
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'horde_id': self.horde_id,
            'game_session_id': self.game_session_id,
            'monsters_defeated': self.monsters_defeated,
            'is_completed': self.is_completed,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'completion_time': self.completion_time,
            'horde': self.horde.to_dict() if self.horde else None
        } 