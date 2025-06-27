from flask import Flask, render_template, session, request, redirect, url_for, make_response, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from  modelos import User

login_manager = LoginManager() 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'OS7BELOSSS_FC'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Página Inicial
@app.route('/')
def index():
    if 'usuarios' not in session:
        usuarios = {}
        session['usuarios'] = usuarios
    return render_template('index.html')

# Sessão de Cadastro, Login e Logout
@app.route('/cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        usuarios = session.get('usuarios')
        hash_senha = generate_password_hash(senha)
        
        if usuarios == {} or email not in usuarios:
            usuarios[email] = hash_senha
            session['usuarios'] = usuarios
            user = User(email, hash_senha)
            user.id = email
            login_user(user)
            return redirect(url_for('login'))
        
        
    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        redirecionar = redirect(url_for('produtos'))
        response = make_response(redirecionar)
        response.set_cookie('nome', email)

        l_usuarios = session.get('usuarios')
        if email in l_usuarios and check_password_hash(l_usuarios[email], senha):
            # logar o usuário
            user = User(nome=email, senha=senha)
            user.id = email
            login_user(user)
            return response
        
        flash('Erro ao realizar cadastro', category='error')
        return redirect(url_for('register'))

    return render_template('login.html')

@login_required
@app.route('/logout')
def logout():
    if 'nome' in request.cookies:
        redirecionar = redirect(url_for('index'))
        response = make_response(redirecionar)
        response.delete_cookie('nome')
    else:
        response = make_response(redirect(url_for('index')))
        session.pop('usuario')
        logout_user()

    return response

# Processo de Produtos e Carrinho
@app.route('/produtos', methods=['GET'])
def produtos():
    if 'usuarios' not in session:
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
    if 'usuarios' not in session:
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


@login_required
@app.route('/carrinho')
def carrinho():
    if 'usuarios' not in session:
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
