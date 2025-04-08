from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, Usuario
from werkzeug.security import generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/criar_admin', methods=['GET', 'POST'])
def criar_admin():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Este email já está em uso.', 'danger')
            return redirect(url_for('auth.criar_admin'))
        
        novo_admin = Usuario(nome=nome, email=email, tipo_usuario='admin')
        novo_admin.set_senha(senha)
        
        db.session.add(novo_admin)
        db.session.commit()
        
        flash('Administrador criado com sucesso!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/criar_admin.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('livros.listar'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('livros.listar'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('livros.listar'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Este email já está em uso.', 'danger')
            return redirect(url_for('auth.registro'))
        
        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))