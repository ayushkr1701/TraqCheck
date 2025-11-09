from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    db.init_app(app)
    migrate = Migrate(app, db)

    from routes.candidates import candidates_bp
    app.register_blueprint(candidates_bp, url_prefix='/api/candidates')

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
