from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    tipo_usuario = db.Column(db.String(20), default='usuario')  # 'admin' ou 'usuario'
    emprestimos = db.relationship('Emprestimo', backref='usuario', lazy=True)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
        
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(100))
    ano_publicacao = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    categoria = db.Column(db.String(50))
    quantidade_total = db.Column(db.Integer, default=1)
    quantidade_disponivel = db.Column(db.Integer, default=1)
    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True)
    
    def __repr__(self):
        return f'<Livro {self.titulo}>'

class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    data_emprestimo = db.Column(db.DateTime, default=datetime.utcnow)
    data_devolucao_prevista = db.Column(db.DateTime, nullable=False)
    data_devolucao_efetiva = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='emprestado')  # 'emprestado', 'devolvido', 'atrasado'
    multa = db.relationship('Multa', backref='emprestimo', lazy=True, uselist=False)
    
    def __repr__(self):
        return f'<Emprestimo {self.id}>'

class Multa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emprestimo_id = db.Column(db.Integer, db.ForeignKey('emprestimo.id'), nullable=False)
    valor = db.Column(db.Float, default=0.0)
    pago = db.Column(db.Boolean, default=False)
    data_pagamento = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Multa {self.id}>'