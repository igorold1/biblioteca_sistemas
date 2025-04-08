Based on the code analysis, here's a comprehensive README.md for your biblioteca_sistemas project:

# Biblioteca Sistemas

A library management system built with Flask that handles book loans, user management, and late return fines.

## Features

- **User Management**
  - Authentication system (login/logout)
  - User roles (admin/regular users)
  - Password encryption

- **Book Management**
  - Book inventory tracking
  - Book details (title, author, ISBN, publisher)
  - Availability status
  - Stock management

- **Loan System**
  - Book borrowing
  - Return tracking
  - Due date management
  - Automated fine calculation

- **Fine Management**
  - Automatic fine calculation for late returns
  - Fine payment tracking
  - R$0.50 per day late fee

## Technical Stack

- **Backend:** Python 3.x + Flask
- **Database:** SQLAlchemy with SQLite
- **Authentication:** Flask-Login
- **Frontend:** Bootstrap 5
- **Testing:** Python unittest

## Project Structure

```
biblioteca_sistemas/
├── venv/
│   └── app/
│       ├── __init__.py
│       ├── models/
│       │   └── __init__.py (Usuario, Livro, Emprestimo, Multa models)
│       ├── routes/
│       │   ├── auth.py
│       │   ├── livros.py
│       │   └── emprestimos.py
│       └── templates/
│           ├── base.html
│           ├── livros/
│           └── auth/
├── tests/
│   └── test_multas.py
└── requirements.txt
```

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
python run.py
```

## Testing

Run the test suite:
```bash
python -m unittest discover tests
```

## Database Models

- **Usuario (User)**
  - nome (name)
  - email
  - senha_hash (password hash)
  - tipo_usuario (user type)

- **Livro (Book)**
  - titulo (title)
  - autor (author)
  - isbn
  - quantidade_total (total quantity)
  - quantidade_disponivel (available quantity)

- **Emprestimo (Loan)**
  - usuario_id
  - livro_id
  - data_emprestimo (loan date)
  - data_devolucao_prevista (expected return date)
  - data_devolucao_efetiva (actual return date)
  - status

- **Multa (Fine)**
  - emprestimo_id
  - valor (amount)
  - pago (paid status)

## Contributors

- Igor Oliveira

## License

This project is licensed under the MIT License.