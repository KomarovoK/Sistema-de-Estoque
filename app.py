from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, flash, session
from produto import Produto, validar_produto
from cliente import Cliente
from pedidos import Pedido
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
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':

        dados = validar_produto()

        if not dados:
            return redirect('/adicionar')

        nome, preco, quantidade = dados

        produto = Produto(nome, preco, quantidade)

        if produto.cadastrar_produtos():
            flash('Produto cadastrado com sucesso!', 'certo')
        else:
            flash('Produto já cadastrado!', 'erro')
        
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
        WHERE usuario = ?
        ''',
        (usuario,)
        )
        
        usuario_encontrado = cursor.fetchone()
        
        if usuario_encontrado and check_password_hash(usuario_encontrado[2], senha):
            
            conexao.close()

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
            senha_hash = generate_password_hash(senha)
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                (usuario, senha_hash)
            )

            conexao.commit()

            flash('Usuário cadastrado com sucesso!', 'certo')

            return redirect('/login')
        
        except sqlite3.IntegrityError:
            flash('Usuário já existe.', 'erro')
        
        finally:
            conexao.close()

    return render_template('cadastro.html')

@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if 'usuario' not in session:
        return redirect('/login')
    
    if request.method == 'POST':

        nome = request.form['nome']
        telefone = request.form['telefone']

        cliente = Cliente(nome, telefone)

        if cliente.cadastrar_cliente():
            flash('Cliente cadastrado com sucesso!', 'certo')
        else:
            flash('Cliente já cadastrado!', 'erro')

        return redirect('/clientes')

    return render_template('adicionar_cliente.html')


@app.route('/clientes')
def clientes():
    if 'usuario' not in session:
        return redirect('/login')

    busca = request.args.get('busca')

    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    if busca:
        cursor.execute(
            "SELECT * FROM clientes WHERE nome LIKE ?",
            ('%' + busca + '%',)
        )
    else:
        cursor.execute("SELECT * FROM clientes")

    clientes = cursor.fetchall()

    conexao.close()

    return render_template(
        'clientes.html',
        clientes=clientes
        )

@app.route('/deletar_cliente/<int:id_cliente>')
def deletar_cliente(id_cliente):
    if 'usuario' not in session:
        return redirect('/login')

    cliente = Cliente('', '')
    cliente.deletar_cliente(id_cliente)

    flash('Cliente removido com sucesso!', 'certo')

    return redirect('/clientes')


@app.route('/editar_cliente/<int:id_cliente>', methods=['GET', 'POST'])
def editar_cliente(id_cliente):
    if 'usuario' not in session:
        return redirect('/login')

    cliente = Cliente('', '')

    if request.method == 'POST':

        nome = request.form['nome']
        telefone = request.form['telefone']

        cliente = Cliente(nome, telefone)

        if cliente.editar_cliente(id_cliente):
            flash('Cliente atualizado com sucesso!', 'certo')
        else:
            flash('Telefone já cadastrado!', 'erro')

        return redirect('/clientes')

    dados_cliente = cliente.buscar_cliente(id_cliente)

    return render_template(
        'editar_cliente.html',
        cliente=dados_cliente
    )

@app.route('/pedido_cliente/<int:id_cliente>')
def pedido_cliente(id_cliente):
    if 'usuario' not in session:
        return redirect('/login')

    cliente = Cliente('', '')
    dados_cliente = cliente.buscar_cliente(id_cliente)

    pedido = Pedido(id_cliente)

    pedido_existente = pedido.buscar_pedido_cliente(id_cliente)

    if pedido_existente is None:
        pedido_id = pedido.criar_pedido()   
        status = 'aberto'
    else:
        pedido_id = pedido_existente[0]
        status = pedido_existente[1]

    itens = pedido.listar_itens(pedido_id)

    return render_template(
        'pedido_cliente.html',
        cliente=dados_cliente,
        itens=itens,
        pedido_id=pedido_id,
        status=status
    )

@app.route('/adicionar_item_pedido/<int:pedido_id>', methods=['GET', 'POST'])
def adicionar_item_pedido(pedido_id):
    if 'usuario' not in session:
        return redirect('/login')

    pedido = Pedido(0)

    if request.method == 'POST':

        produto_id = int(request.form['produto_id'])
        quantidade = int(request.form['quantidade'])

        estoque = pedido.verificar_estoque(produto_id)

        if quantidade > estoque:

            flash('Quantidade maior que o estoque!', 'erro')

            return redirect(f'/adicionar_item_pedido/{pedido_id}')

        pedido.adicionar_item_pedido(
            pedido_id,
            produto_id,
            quantidade
        )   

        cliente_id = pedido.buscar_cliente_pedido(pedido_id)

        flash('Produto adicionado ao pedido!', 'certo')

        return redirect(f'/pedido_cliente/{cliente_id}')

    produtos = pedido.listar_produtos_disponiveis()

    cliente_id = pedido.buscar_cliente_pedido(pedido_id)

    return render_template(
        'adicionar_item_pedido.html',
        produtos=produtos,
        cliente_id=cliente_id
    )

@app.route('/excluir_item/<int:item_id>')
def excluir_item(item_id):
    if 'usuario' not in session:
        return redirect('/login')

    pedido = Pedido(0)

    sucesso = pedido.excluir_item_pedido(item_id)

    if sucesso:
        flash('Item removido do pedido!', 'certo')
    else:
        flash('Item não encontrado!', 'erro')

    return redirect(request.referrer or '/')

@app.route('/itens/editar/<int:item_id>', methods=['GET', 'POST'])
def editar_item(item_id):

    pedido = Pedido(0)

    item = pedido.buscar_item(item_id)

    if not item:
        flash('Item não encontrado!', 'erro')
        return redirect(request.referrer or '/')

    pedido_id = item[4]
    cliente_id = pedido.buscar_cliente_pedido(pedido_id)

    if request.method == 'POST':

        nova_quantidade = int(request.form['quantidade'])

        sucesso = pedido.editar_item(item_id, nova_quantidade)

        if sucesso:
            flash('Item atualizado com sucesso!', 'certo')
        else:
            flash('Erro: estoque insuficiente ou item inválido.', 'erro')

        return redirect(f'/pedido_cliente/{cliente_id}')

    return render_template(
        'editar_item.html',
        item=item,
        cliente_id=cliente_id
    )


@app.route('/finalizar_pedido/<int:pedido_id>')
def finalizar_pedido(pedido_id):

    if 'usuario' not in session:
        return redirect('/login')

    pedido = Pedido(0)

    sucesso = pedido.finalizar_pedido(pedido_id)

    if not sucesso:
        flash('Erro: estoque insuficiente para finalizar o pedido!', 'erro')
        return redirect(request.referrer or '/')

    cliente_id = pedido.buscar_cliente_pedido(pedido_id)

    flash('Pedido finalizado e estoque atualizado!', 'certo')

    return redirect(f'/pedido_cliente/{cliente_id}')


if __name__ == '__main__':
    app.run(debug=True)