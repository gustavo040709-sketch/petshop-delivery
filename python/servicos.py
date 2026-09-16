from banco import conectar


def cadastrar_servico():
    servico = {
        "nome": input("Nome do serviço: "),
        "preco": float(input("Preço: R$ "))
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO servicos (nome, preco)
        VALUES (?, ?)
    """, (
        servico["nome"],
        servico["preco"]
    ))

    banco.commit()
    banco.close()

    print("Serviço cadastrado com sucesso!")


def listar_servicos():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("SELECT * FROM servicos")
    servicos = cursor.fetchall()

    banco.close()

    lista = []

    for servico in servicos:
        dados = {
            "id": servico[0],
            "nome": servico[1],
            "preco": servico[2]
        }

        lista.append(dados)

    print("\n--- SERVIÇOS ---")

    for servico in lista:
        print(
            f'ID: {servico["id"]} | '
            f'Serviço: {servico["nome"]} | '
            f'Preço: R$ {servico["preco"]:.2f}'
        )