from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-taskmonitor-pro-2'
    
    # Registra apenas o blueprint principal (que já tem todas as rotas)
    from .routes import main
    app.register_blueprint(main)
    
    return app
