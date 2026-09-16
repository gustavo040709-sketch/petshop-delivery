from banco import conectar


def cadastrar_funcionario():
    funcionario = {
        "nome": input("Nome do funcionário: "),
        "cargo": input("Cargo: "),
        "telefone": input("Telefone: ")
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO funcionarios
        (nome, cargo, telefone)
        VALUES (?, ?, ?)
    """, (
        funcionario["nome"],
        funcionario["cargo"],
        funcionario["telefone"]
    ))

    banco.commit()
    banco.close()

    print("Funcionário cadastrado com sucesso!")


def listar_funcionarios():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("SELECT * FROM funcionarios")
    funcionarios = cursor.fetchall()

    banco.close()

    lista = []

    for funcionario in funcionarios:
        dados = {
            "id": funcionario[0],
            "nome": funcionario[1],
            "cargo": funcionario[2],
            "telefone": funcionario[3]
        }

        lista.append(dados)

    print("\n--- FUNCIONÁRIOS ---")

    for funcionario in lista:
        print(
            f'ID: {funcionario["id"]} | '
            f'Nome: {funcionario["nome"]} | '
            f'Cargo: {funcionario["cargo"]} | '
            f'Telefone: {funcionario["telefone"]}'
        )