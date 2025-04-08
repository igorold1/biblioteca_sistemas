from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Livro

livros = Blueprint('livros', __name__)

@livros.route('/')
@livros.route('/livros')
def listar():
    query = Livro.query
    
    # Lógica de pesquisa
    termo_busca = request.args.get('termo', '')
    disponibilidade = request.args.get('disponibilidade', 'todos')
    
    if termo_busca:
        query = query.filter(
            Livro.titulo.contains(termo_busca) | 
            Livro.autor.contains(termo_busca) | 
            Livro.isbn.contains(termo_busca)
        )
    
    if disponibilidade == 'disponiveis':
        query = query.filter(Livro.quantidade_disponivel > 0)
    elif disponibilidade == 'emprestados':
        query = query.filter(Livro.quantidade_disponivel < Livro.quantidade_total)
    
    livros = query.order_by(Livro.titulo).all()
    return render_template('livros/listar.html', livros=livros, termo=termo_busca, disponibilidade=disponibilidade)

@livros.route('/livros/<int:id>')
def detalhes(id):
    livro = Livro.query.get_or_404(id)
    return render_template('livros/detalhes.html', livro=livro)

@livros.route('/livros/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar():
    if current_user.tipo_usuario != 'admin':
        flash('Acesso negado. Apenas administradores podem adicionar livros.', 'danger')
        return redirect(url_for('livros.listar'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        editora = request.form.get('editora')
        ano_publicacao = request.form.get('ano_publicacao')
        isbn = request.form.get('isbn')
        categoria = request.form.get('categoria')
        quantidade = int(request.form.get('quantidade', 1))
        
        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            editora=editora,
            ano_publicacao=ano_publicacao,
            isbn=isbn,
            categoria=categoria,
            quantidade_total=quantidade,
            quantidade_disponivel=quantidade
        )
        
        db.session.add(novo_livro)
        db.session.commit()
        
        flash('Livro adicionado com sucesso!', 'success')
        return redirect(url_for('livros.listar'))
    
    return render_template('livros/adicionar.html')
