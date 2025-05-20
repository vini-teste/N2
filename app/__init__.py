from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes import clients_bp
    from app.auth import auth_bp
    from app.routes.player_routes import player_bp
    from app.routes.progress_routes import progress_bp
    from app.routes.horde_routes import horde_bp
    from app.routes.game_session_routes import game_session_bp
    
    app.register_blueprint(clients_bp, url_prefix='/clients')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(player_bp, url_prefix='/api')
    app.register_blueprint(progress_bp, url_prefix='/api')
    app.register_blueprint(horde_bp, url_prefix='/api')
    app.register_blueprint(game_session_bp, url_prefix='/api')

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Requisição inválida'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Não autorizado'}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erro interno do servidor'}), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({'error': 'Serviço indisponível'}), 503

    return app 