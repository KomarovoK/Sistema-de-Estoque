from flask import Flask, render_template, request, redirect, flash
from produto import Produto, validar_produto
import sqlite3

app = Flask(__name__)
app.secret_key = '123'


@app.route('/')
def index():

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

        return redirect('/')

    return render_template('adicionar.html')


@app.route('/deletar/<int:id>')
def deletar(id):

    produto = Produto('', 0, 0)

    produto.deletar_produto(id)

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



if __name__ == '__main__':
    app.run(debug=True)