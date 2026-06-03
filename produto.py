import sqlite3
from flask import request, flash

conexao = sqlite3.connect('database.db', check_same_thread=False)
cursor = conexao.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, preco REAL NOT NULL, quantidade INTEGER NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT NOT NULL UNIQUE, senha TEXT NOT NULL)''')

class Produto:
    def __init__(self, nome, preco, quantidade):
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade

    def cadastrar_produtos(self):

        cursor.execute(
        'SELECT * FROM produtos WHERE nome = ?',
        (self.nome,)
    )

        produto = cursor.fetchone()

        if produto:
            print('Produto já cadastrado!')

        else:
            cursor.execute(
            '''
            INSERT INTO produtos (
                nome,
                preco,
                quantidade
            )
            VALUES (?, ?, ?)
            ''',
            (self.nome, self.preco, self.quantidade)
        )
            
            conexao.commit()
                
     
    def listar_produtos(self):
        cursor.execute('SELECT * FROM produtos')

        produtos = cursor.fetchall()

        return produtos

    def deletar_produto(self, id_produto):  
        cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
        conexao.commit()



    def editar_produto(self, id_produto):

        cursor.execute(
        '''
        UPDATE produtos
        SET nome = ?, preco = ?, quantidade = ?
        WHERE id = ?
        ''',
        (self.nome, self.preco, self.quantidade, id_produto)
    )
        conexao.commit()
        
      
    def buscar_produto(self):
        nome = input('Digite o nome do produto: ')

        cursor.execute('SELECT * FROM produtos WHERE nome = ?', (nome,))

        produto = cursor.fetchone()

        if produto:
            print(produto)
        else:
            print('Produto não encontrado!') 



def validar_produto():

    nome = request.form['nome'].strip()

    if not nome:
        flash('O campo nome é obrigatório.', 'erro')
        return None

    try:
        preco = float(request.form['preco'])

        if preco <= 0:
            flash('O campo preço deve ser positivo.', 'erro')
            return None

    except (KeyError, ValueError):
        flash('Preço inválido.', 'erro')
        return None

    try:
        quantidade = int(request.form['quantidade'])

        if quantidade < 0:
            flash('Quantidade inválida.', 'erro')
            return None

    except (KeyError, ValueError):
        flash('Quantidade inválida.', 'erro')
        return None

    return nome, preco, quantidade