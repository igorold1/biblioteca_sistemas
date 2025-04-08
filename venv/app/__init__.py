from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, Usuario
from datetime import datetime, timedelta

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'chave-secreta-para-desenvolvimento'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints
    from .routes.auth import auth
    from .routes.livros import livros
    from .routes.emprestimos import emprestimos
    
    app.register_blueprint(auth)
    app.register_blueprint(livros)
    app.register_blueprint(emprestimos)

    # Adicionar filtros de template aqui
    @app.template_filter('now')
    def now_filter(format='%d/%m/%Y'):
        return datetime.utcnow().strftime(format)
    
    @app.template_filter('timedelta')
    def filter_timedelta(date, days=0):
        from datetime import timedelta
        return date + timedelta(days=days)
  
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app