from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_mestra_123'

# Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vendas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)

# Criar banco ao iniciar
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('1234')))
        db.session.commit()

# --- ROTAS ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    produtos = Produto.query.all()
    return render_template('dashboard.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Login inválido!')
    return render_template('login.html')

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'user_id' in session:
        # Pega os dados do formulário
        novo_p = Produto(
            nome=request.form.get('nome'),
            preco=float(request.form.get('preco')),
            estoque=int(request.form.get('estoque'))
        )
        db.session.add(novo_p)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/vender/<int:id>')
def vender(id):
    if 'user_id' in session:
        p = Produto.query.get(id)
        if p and p.estoque > 0:
            p.estoque -= 1
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)