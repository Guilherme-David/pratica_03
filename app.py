from flask import Flask, render_template, session, request, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'OS7BELOSSS_FC'

usuarios_cadastrados = {}

# Página Inicial
@app.route('/')
def index():
    if 'nome' in request.cookies:
        nome = request.cookies.get('nome')
        return render_template('index.html', nome=nome)
    return render_template('index.html')

# Sessão de Cadastro, Login e Logout
@app.route('/cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        session['carrinho'] = []

        hash_senha = generate_password_hash(senha)

        if nome not in usuarios_cadastrados:
            usuarios_cadastrados[nome] = hash_senha
            return redirect(url_for('login'))
        
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        redirecionar = redirect(url_for('produtos'))
        response = make_response(redirecionar)
        response.set_cookie('nome', nome)

        if nome in usuarios_cadastrados.keys() and check_password_hash(usuarios_cadastrados[usuario], senha):
            # logar o usuário
            session['usuario'] = nome
            session['password'] = senha
            return response

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'nome' in request.cookies:
        redirecionar = redirect(url_for('index'))
        response = make_response(redirecionar)
        response.delete_cookie('nome')
    else:
        response = make_response(redirect(url_for('index')))
    session.pop('usuario')
    return response

# Processo de Produtos e Carrinho
@app.route('/produtos', methods=['GET'])
def produtos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    return render_template('produtos.html', produtos=get_produtos())

def get_produtos():
    produtos = [
        {'nome': 'Air Jordan', 'preco': 1232.50, 'id': 1}, 
        {'nome': 'Air Max', 'preco': 982, 'id': 2}, 
        {'nome': 'Air Novak', 'preco': 1282.50, 'id': 3}
    ] 

    return produtos

@app.route("/add_to_cart/<int:produto_id>")
def adicionar_carrinho(produto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if 'carrinho' not in session:
        session['carrinho'] = []

    carrinho = session['carrinho']

    if produto_id not in carrinho:
        carrinho.append(produto_id)

    session['carrinho'] = carrinho
    return redirect(url_for('produtos'))

@app.route("/empty_cart")
def esvaziar_carrinho():
    session['carrinho'] = []
    return redirect(url_for("produtos"))

@app.route('/carrinho')
def carrinho():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    carrinho_ids = session.get('carrinho', [])
    produtos_disponiveis = get_produtos()

    # Montar lista de produtos reais com base nos IDs no carrinho
    carrinho_real = []
    for produto_id in carrinho_ids:
        for produto in produtos_disponiveis:
            if produto['id'] == produto_id:
                carrinho_real.append(produto)
                break

    return render_template('carrinho.html', carrinho=carrinho_real)
