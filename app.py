from flask import Flask, render_template, request, redirect, flash, session
from produto import Produto, validar_produto
import sqlite3

app = Flask(__name__)
app.secret_key = '123'


@app.route('/')
def index():

    if 'usuario' not in session:
        return redirect('/login')

    busca = request.args.get("busca")

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    if busca:
        cursor.execute(
            "SELECT * FROM produtos WHERE nome LIKE ?",
            ('%' + busca + '%',)
        )
    else:
        cursor.execute("SELECT * FROM produtos")

    produtos = cursor.fetchall()

    conexao.close()

    return render_template(
        'index.html',
        produtos=produtos
    )


@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():

    if request.method == 'POST':

        dados = validar_produto()

        if not dados:
            return redirect('/adicionar')

        nome, preco, quantidade = dados

        produto = Produto(nome, preco, quantidade)

        produto.cadastrar_produtos()
        
        flash('Produto cadastrado com sucesso!', 'certo')

        return redirect('/')

    return render_template('adicionar.html')


@app.route('/deletar/<int:id>')
def deletar(id):

    produto = Produto('', 0, 0)

    produto.deletar_produto(id)
    flash('Produto excluído com sucesso!', 'certo')

    return redirect('/')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    if request.method == 'POST':

        dados = validar_produto()

        if not dados:
            return redirect(f'/editar/{id}')

        nome, preco, quantidade = dados

        produto = Produto(nome, preco, quantidade)

        produto.editar_produto(id)
        
        flash('Produto editado com sucesso!', 'certo')

        return redirect('/')

    cursor.execute(
        "SELECT * FROM produtos WHERE id = ?",
        (id,)
    )

    produto = cursor.fetchone()

    conexao.close()

    return render_template(
        'editar.html',
        produto=produto
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        usuario = request.form['usuario']
        senha = request.form['senha']

        conexao = sqlite3.connect("database.db")
        cursor = conexao.cursor()

        cursor.execute(
            '''
            SELECT * FROM usuarios
            WHERE usuario = ? AND senha = ?
            ''',
            (usuario, senha)
        )
        usuario_encontrado = cursor.fetchone()
        
        if usuario_encontrado:
            
            session['usuario'] = usuario
            
            return redirect('/')

        flash('Usuário ou senha incorretos', 'erro')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    
    session.pop('usuario', None)
    
    return redirect('/login')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':

        usuario = request.form['usuario'].strip()
        senha = request.form['senha']

        conexao = sqlite3.connect("database.db")
        cursor = conexao.cursor()

        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                (usuario, senha)
            )

            conexao.commit()

            flash('Usuário cadastrado com sucesso!', 'certo')

            return redirect('/login')
        
        except sqlite3.IntegrityError:
            flash('Usuário já existe.', 'erro')
        
        finally:
            conexao.close()

    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)