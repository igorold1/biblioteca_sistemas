from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import db, Emprestimo, Livro, Multa

emprestimos = Blueprint('emprestimos', __name__)

@emprestimos.route('/meus-emprestimos')
@login_required
def meus_emprestimos():
    emprestimos_user = Emprestimo.query.filter_by(usuario_id=current_user.id).order_by(Emprestimo.data_emprestimo.desc()).all()
    return render_template('emprestimos/meus_emprestimos.html', emprestimos=emprestimos_user)

@emprestimos.route('/emprestar/<int:livro_id>', methods=['GET', 'POST'])
@login_required
def emprestar(livro_id):
    livro = Livro.query.get_or_404(livro_id)
    data_atual = datetime.utcnow()

    # Verificar se o livro está disponível
    if livro.quantidade_disponivel <= 0:
        flash('Este livro não está disponível para empréstimo no momento.', 'danger')
        return redirect(url_for('livros.detalhes', id=livro.id))
    
    # Verificar se o usuário já tem este livro emprestado
    emprestimo_existente = Emprestimo.query.filter_by(
        usuario_id=current_user.id,
        livro_id=livro.id,
        status='emprestado'
    ).first()
    
    if emprestimo_existente:
        flash('Você já possui um empréstimo ativo deste livro.', 'warning')
        return redirect(url_for('emprestimos.meus_emprestimos'))
    
    # Verificar se o usuário tem multas pendentes
    multas_pendentes = Multa.query.join(Emprestimo).filter(
        Emprestimo.usuario_id == current_user.id,
        Multa.pago == False
    ).all()
    
    if multas_pendentes:
        total_pendente = sum(multa.valor for multa in multas_pendentes)
        flash(f'Você possui R$ {total_pendente:.2f} em multas pendentes. Regularize sua situação para realizar novos empréstimos.', 'warning')
        return redirect(url_for('emprestimos.multas'))
    
    if request.method == 'POST':
        # Determinar a data de devolução (padrão: 14 dias)
        data_devolucao = datetime.utcnow() + timedelta(days=14)
        
        # Criar o empréstimo
        novo_emprestimo = Emprestimo(
            usuario_id=current_user.id,
            livro_id=livro.id,
            data_emprestimo=datetime.utcnow(),
            data_devolucao_prevista=data_devolucao,
            status='emprestado'
        )
        
        # Atualizar a quantidade disponível do livro
        livro.quantidade_disponivel -= 1
        
        db.session.add(novo_emprestimo)
        db.session.commit()
        
        flash(f'Empréstimo realizado com sucesso! A devolução deve ser feita até {data_devolucao.strftime("%d/%m/%Y")}.', 'success')
        return redirect(url_for('emprestimos.meus_emprestimos'))
    
    return render_template('emprestimos/emprestar.html', 
        livro=livro, 
        now=data_atual,
        timedelta=timedelta)

@emprestimos.route('/multas')
@login_required
def multas():
    multas_usuario = Multa.query.join(Emprestimo).filter(
        Emprestimo.usuario_id == current_user.id
    ).all()
    
    total_pendente = sum(multa.valor for multa in multas_usuario if not multa.pago)
    
    return render_template('emprestimos/multas.html', multas=multas_usuario, total_pendente=total_pendente)
@emprestimos.route('/devolver/<int:emprestimo_id>', methods=['POST'])
@login_required
def devolver(emprestimo_id):
    emprestimo = Emprestimo.query.get_or_404(emprestimo_id)
    
    # Verificar se o empréstimo pertence ao usuário atual
    if emprestimo.usuario_id != current_user.id and current_user.tipo_usuario != 'admin':
        flash('Acesso negado. Este empréstimo não pertence a você.', 'danger')
        return redirect(url_for('emprestimos.meus_emprestimos'))
    
    # Verificar se o livro já foi devolvido
    if emprestimo.status == 'devolvido':
        flash('Este livro já foi devolvido.', 'info')
        return redirect(url_for('emprestimos.meus_emprestimos'))
    
    # Atualizar status do empréstimo
    emprestimo.status = 'devolvido'
    emprestimo.data_devolucao_efetiva = datetime.utcnow()
    
    # Atualizar disponibilidade do livro
    livro = Livro.query.get(emprestimo.livro_id)
    livro.quantidade_disponivel += 1
    
    # Verificar atraso e calcular multa
    data_atual = datetime.utcnow()
    if data_atual > emprestimo.data_devolucao_prevista:
        dias_atraso = (data_atual - emprestimo.data_devolucao_prevista).days
        valor_multa = dias_atraso * 0.50  # R$ 0,50 por dia de atraso
        
        nova_multa = Multa(
            emprestimo_id=emprestimo.id,
            valor=valor_multa,
            pago=False
        )
        
        db.session.add(nova_multa)
        flash(f'Livro devolvido com atraso de {dias_atraso} dias. Multa de R$ {valor_multa:.2f} gerada.', 'warning')
    else:
        flash('Livro devolvido com sucesso!', 'success')
    
    db.session.commit()
    return redirect(url_for('emprestimos.meus_emprestimos'))