import sqlite3
from datetime import datetime

conexao = sqlite3.connect('database.db', check_same_thread=False)
cursor = conexao.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    data_pedido TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'aberto'         
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL
)
''')

conexao.commit()


class Pedido:
    def __init__(self, cliente_id):
        self.cliente_id = cliente_id

    def criar_pedido(self):
        data_pedido = datetime.now().strftime('%d/%m/%Y %H:%M')

        cursor.execute(
            '''
            INSERT INTO pedidos (cliente_id, data_pedido)
            VALUES (?, ?)
            ''',
            (self.cliente_id, data_pedido)
        )

        conexao.commit()
        return cursor.lastrowid

    def adicionar_item_pedido(self, pedido_id, produto_id, quantidade):
        cursor.execute(
            '''
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade)
            VALUES (?, ?, ?)
            ''',
            (pedido_id, produto_id, quantidade)
        )
        conexao.commit()

    def listar_itens(self, pedido_id):
        cursor.execute(
            '''
            SELECT itens_pedido.id,
                   produtos.nome,
                   produtos.preco,
                   itens_pedido.quantidade
            FROM itens_pedido
            INNER JOIN produtos
            ON itens_pedido.produto_id = produtos.id
            WHERE itens_pedido.pedido_id = ?
            ''',
            (pedido_id,)
        )
        return cursor.fetchall()

    def buscar_pedido_cliente(self, cliente_id):
        cursor.execute(
            '''
            SELECT id, status
            FROM pedidos
            WHERE cliente_id = ?
            ''',
            (cliente_id,)
        )
        return cursor.fetchone()

    def verificar_estoque(self, produto_id):
        cursor.execute(
            '''
            SELECT quantidade
            FROM produtos
            WHERE id = ?
            ''',
            (produto_id,)
        )
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0

    def listar_produtos_disponiveis(self):
        cursor.execute('''
            SELECT *
            FROM produtos
            WHERE quantidade > 0
        ''')
        return cursor.fetchall()

    def buscar_cliente_pedido(self, pedido_id):
        cursor.execute(
            '''
            SELECT cliente_id
            FROM pedidos
            WHERE id = ?
            ''',
            (pedido_id,)
        )
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

    def excluir_item_pedido(self, item_id):
        cursor.execute(
            '''
            SELECT produto_id, quantidade
            FROM itens_pedido
            WHERE id = ?
            ''',
            (item_id,)
        )

        item = cursor.fetchone()

        if not item:
            return False

        produto_id, quantidade = item

        cursor.execute(
            '''
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?
            ''',
            (quantidade, produto_id)
        )

        cursor.execute(
            '''
            DELETE FROM itens_pedido
            WHERE id = ?
            ''',
            (item_id,)
        )

        conexao.commit()
        return True

    def buscar_item(self, item_id):
        cursor.execute(
            '''
            SELECT 
                itens_pedido.id,
                produtos.nome,
                produtos.preco,
                itens_pedido.quantidade,
                itens_pedido.pedido_id
            FROM itens_pedido
            INNER JOIN produtos
                ON itens_pedido.produto_id = produtos.id
            WHERE itens_pedido.id = ?
            ''',
            (item_id,)
     )

        return cursor.fetchone()

    def editar_item(self, item_id, nova_quantidade):
        cursor.execute(
            '''
            SELECT produto_id, quantidade
            FROM itens_pedido
            WHERE id = ?
            ''',
            (item_id,)
        )

        item = cursor.fetchone()

        if not item:
            return False

        produto_id, quantidade_antiga = item

        diferenca = nova_quantidade - quantidade_antiga

        if diferenca > 0:
            cursor.execute(
                '''
                SELECT quantidade
                FROM produtos
                WHERE id = ?
                ''',
                (produto_id,)
            )

            estoque_atual = cursor.fetchone()[0]

            if estoque_atual < diferenca:
                return False

            cursor.execute(
                '''
                UPDATE produtos
                SET quantidade = quantidade - ?
                WHERE id = ?
                ''',
                (diferenca, produto_id)
            )

        elif diferenca < 0:
            cursor.execute(
                '''
                UPDATE produtos
                SET quantidade = quantidade + ?
                WHERE id = ?
                ''',
                (-diferenca, produto_id)
            )

        cursor.execute(
            '''
            UPDATE itens_pedido
            SET quantidade = ?
            WHERE id = ?
            ''',
            (nova_quantidade, item_id)
        )

        conexao.commit()
        return True
    

    def finalizar_pedido(self, pedido_id):

        cursor.execute(
            '''
            SELECT produto_id, quantidade
            FROM itens_pedido
            WHERE pedido_id = ?
            ''',
            (pedido_id,)
        )

        itens = cursor.fetchall()

        for produto_id, quantidade in itens:

            cursor.execute(
                '''
                SELECT quantidade
                FROM produtos
                WHERE id = ?
                ''',
                (produto_id,)
            )

            estoque = cursor.fetchone()[0]

            if estoque < quantidade:
                return False

        for produto_id, quantidade in itens:

            cursor.execute(
                '''
                UPDATE produtos
                SET quantidade = quantidade - ?
                WHERE id = ?
                ''',
                (quantidade, produto_id)
            )

        cursor.execute(
            '''
            UPDATE pedidos
            SET status = 'finalizado'
            WHERE id = ?
            ''',
            (pedido_id,)
        )

        conexao.commit()
        return True