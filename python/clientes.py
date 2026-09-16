from banco import conectar


def cadastrar_cliente():
    cliente = {
        "nome": input("Nome do cliente: "),
        "telefone": input("Telefone: "),
        "email": input("E-mail: ")
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO clientes (nome, telefone, email)
        VALUES (?, ?, ?)
    """, (
        cliente["nome"],
        cliente["telefone"],
        cliente["email"]
    ))

    banco.commit()
    banco.close()

    print("Cliente cadastrado com sucesso!")


def listar_clientes():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    banco.close()

    lista = []

    for cliente in clientes:
        dados = {
            "id": cliente[0],
            "nome": cliente[1],
            "telefone": cliente[2],
            "email": cliente[3]
        }

        lista.append(dados)

    print("\n--- CLIENTES ---")

    for cliente in lista:
        print(
            f'ID: {cliente["id"]} | '
            f'Nome: {cliente["nome"]} | '
            f'Telefone: {cliente["telefone"]} | '
            f'E-mail: {cliente["email"]}'
        )