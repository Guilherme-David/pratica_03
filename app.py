from flask import Flask, render_template, session, request, redirect, url_for, make_response, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from modelos import User
import json
import os

login_manager = LoginManager() 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'OS7BELOSSS_FC'
login_manager.init_app(app)

# Caminho para arquivos JSON
PRODUTOS_FILE = 'produtos.json'
COMPRAS_FILE = 'compras.json'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Página Inicial
@app.route('/')
def index():
    if 'usuarios' not in session:
        session['usuarios'] = {}
    return render_template('index.html')

# Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        usuarios = session.get('usuarios')
        if usuarios is None:
            usuarios = {}

        hash_senha = generate_password_hash(senha)

        if email not in usuarios:
            usuarios[email] = hash_senha
            session['usuarios'] = usuarios
            user = User(email, hash_senha)
            user.id = email
            login_user(user)
            return redirect(url_for('login'))
        else:
            flash('Usuário já cadastrado', category='error')

    return render_template('cadastro.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        l_usuarios = session.get('usuarios')
        if l_usuarios is None:
            l_usuarios = {}

        if email in l_usuarios and check_password_hash(l_usuarios[email], senha):
            user = User(nome=email, senha=senha)
            user.id = email
            login_user(user)

            response = make_response(redirect(url_for('produtos')))
            response.set_cookie('nome', email)
            return response
        
        flash('Usuário ou senha inválidos', category='error')
        return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@login_required
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    if 'nome' in request.cookies:
        response.delete_cookie('nome')
    if 'usuario' in session:
        session.pop('usuario')
    logout_user()
    return response

# Produtos
@app.route('/produtos')
def produtos():
    if 'usuarios' not in session:
        return redirect(url_for('login'))

    produtos = carregar_produtos()
    return render_template('produtos.html', produtos=produtos)

def carregar_produtos():
    # Se o arquivo json não existir, cria com produtos padrão
    if not os.path.exists(PRODUTOS_FILE):
        produtos_padrao = [
            {'nome': 'Air Jordan', 'preco': 1232.50, 'id': 1}, 
            {'nome': 'Air Max', 'preco': 982, 'id': 2}, 
            {'nome': 'Air Novak', 'preco': 1282.50, 'id': 3}
        ]
        with open(PRODUTOS_FILE, 'w') as f:
            json.dump(produtos_padrao, f)
        return produtos_padrao

    with open(PRODUTOS_FILE, 'r') as f:
        return json.load(f)

# Adicionar ao carrinho
@app.route('/add_to_cart/<int:produto_id>')
def adicionar_carrinho(produto_id):
    if 'usuarios' not in session:
        return redirect(url_for('login'))

    if 'carrinho' not in session:
        session['carrinho'] = []

    carrinho = session['carrinho']
    if produto_id not in carrinho:
        carrinho.append(produto_id)

    session['carrinho'] = carrinho
    return redirect(url_for('produtos'))

# Esvaziar carrinho
@app.route('/empty_cart')
def esvaziar_carrinho():
    session['carrinho'] = []
    return redirect(url_for('produtos'))

# Visualizar carrinho
@login_required
@app.route('/carrinho')
def carrinho():
    if 'usuarios' not in session:
        return redirect(url_for('login'))

    carrinho_ids = session.get('carrinho', [])
    produtos_disponiveis = carregar_produtos()

    carrinho_real = []
    for produto_id in carrinho_ids:
        for produto in produtos_disponiveis:
            if produto['id'] == produto_id:
                carrinho_real.append(produto)
                break

    return render_template('carrinho.html', carrinho=carrinho_real)

# Finalizar compra: salva compra em JSON e limpa carrinho
@login_required
@app.route('/fechar_compra', methods=['POST'])
def fechar_compra():
    usuario = request.cookies.get('nome')
    if not usuario:
        flash('Usuário não autenticado', category='error')
        return redirect(url_for('login'))

    carrinho_ids = session.get('carrinho', [])
    if not carrinho_ids:
        flash('Carrinho vazio', category='error')
        return redirect(url_for('carrinho'))

    produtos_disponiveis = carregar_produtos()
    compra_real = []
    total = 0

    for pid in carrinho_ids:
        for produto in produtos_disponiveis:
            if produto['id'] == pid:
                compra_real.append(produto)
                total += produto['preco']
                break

    compra_salvar = {
        'usuario': usuario,
        'produtos': compra_real,
        'total': total
    }

    # Lê arquivo compras.json existente ou cria lista vazia
    if os.path.exists(COMPRAS_FILE):
        with open(COMPRAS_FILE, 'r') as f:
            compras = json.load(f)
    else:
        compras = []

    compras.append(compra_salvar)

    with open(COMPRAS_FILE, 'w') as f:
        json.dump(compras, f, indent=4, ensure_ascii=False)

    session['carrinho'] = []
    flash('Compra finalizada com sucesso!', category='success')
    return redirect(url_for('produtos'))

if __name__ == '__main__':
    app.run(debug=True)
