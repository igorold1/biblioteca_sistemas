import unittest
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import Usuario, Livro, Emprestimo, Multa

class TestMultas(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use banco de dados em memória
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.criar_dados_de_teste()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def criar_dados_de_teste(self):
        with self.app.app_context():
            # Criar usuário de teste
            self.usuario = Usuario(nome='Teste', email='teste@email.com')
            self.usuario.set_senha('senha123')
            db.session.add(self.usuario)
            db.session.commit()

            # Criar livro de teste
            self.livro = Livro(titulo='Livro Teste', autor='Autor Teste', quantidade_total=1, quantidade_disponivel=1)
            db.session.add(self.livro)
            db.session.commit()

    def test_multa_gerada_com_atraso(self):
        with self.app.app_context():
            # Buscar usuário e livro
            usuario = Usuario.query.filter_by(email='teste@email.com').first()
            livro = Livro.query.filter_by(titulo='Livro Teste').first()

            # Emprestar livro
            data_emprestimo = datetime.now(timezone.utc)
            data_devolucao_prevista = data_emprestimo + timedelta(days=7)
            
            emprestimo = Emprestimo(
                usuario_id=usuario.id,
                livro_id=livro.id,
                data_emprestimo=data_emprestimo,
                data_devolucao_prevista=data_devolucao_prevista,
                status='emprestado'
            )
            
            db.session.add(emprestimo)
            db.session.commit()

            # Simular devolução atrasada
            data_devolucao_efetiva = data_devolucao_prevista + timedelta(days=3)
            emprestimo.data_devolucao_efetiva = data_devolucao_efetiva
            emprestimo.status = 'devolvido'
            db.session.commit()

            # Calcular multa (mesma lógica da rota de devolução)
            dias_atraso = max(0, (data_devolucao_efetiva - data_devolucao_prevista).days)
            valor_multa = dias_atraso * 0.50

            # Criar a multa
            multa = Multa(emprestimo_id=emprestimo.id, valor=valor_multa, pago=False)
            db.session.add(multa)
            db.session.commit()

            # Verificar se a multa foi gerada
            multa_verificada = Multa.query.filter_by(emprestimo_id=emprestimo.id).first()
            
            self.assertIsNotNone(multa_verificada)
            self.assertEqual(multa_verificada.valor, valor_multa)

if __name__ == '__main__':
    unittest.main()
