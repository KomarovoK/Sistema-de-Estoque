import sqlite3

conexao = sqlite3.connect('database.db', check_same_thread=False)
cursor = conexao.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL, 
    telefone TEXT NOT NULL)''')  

class Cliente:

    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone
        
    def cadastrar_cliente(self):
        cursor.execute(
        'SELECT * FROM clientes WHERE telefone = ?',
        (self.telefone,)
        )

        cliente = cursor.fetchone()

        if cliente:
            return False

        
        cursor.execute(
        '''
        INSERT INTO clientes (
            nome,
            telefone
        )
        VALUES (?, ?)
        ''',
        (self.nome, self.telefone)
        )
            
        conexao.commit()
        return True
    
    def deletar_cliente(self, id_cliente):
        cursor.execute('DELETE FROM clientes WHERE id = ?', (id_cliente,))
        conexao.commit()

    def editar_cliente(self, id_cliente):

        cursor.execute(
            '''
            SELECT * FROM clientes
            WHERE telefone = ? AND id != ?
            ''',
            (self.telefone, id_cliente)
            )

        cliente = cursor.fetchone()

        if cliente:
            return False

        cursor.execute(
            '''
            UPDATE clientes
            SET nome = ?, telefone = ?
            WHERE id = ?
            ''',
            (self.nome, self.telefone, id_cliente)
        )

        conexao.commit()
        return True

    def listar_clientes(self):
        cursor.execute('SELECT * FROM clientes')
        return cursor.fetchall()
    
    def buscar_cliente(self, id_cliente):
        
        cursor.execute(
        'SELECT * FROM clientes WHERE id = ?',
        (id_cliente,)
        )
        return cursor.fetchone()