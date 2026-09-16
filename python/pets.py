from banco import conectar


def cadastrar_pet():
    pet = {
        "nome": input("Nome do pet: "),
        "especie": input("Espécie: "),
        "raca": input("Raça: "),
        "idade": int(input("Idade: ")),
        "cliente_id": int(input("ID do dono: "))
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO pets
        (nome, especie, raca, idade, cliente_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        pet["nome"],
        pet["especie"],
        pet["raca"],
        pet["idade"],
        pet["cliente_id"]
    ))

    banco.commit()
    banco.close()

    print("Pet cadastrado com sucesso!")


def listar_pets():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        SELECT pets.id, pets.nome, pets.especie,
               pets.raca, pets.idade, clientes.nome
        FROM pets
        JOIN clientes ON pets.cliente_id = clientes.id
    """)

    pets = cursor.fetchall()

    banco.close()

    lista = []

    for pet in pets:
        dados = {
            "id": pet[0],
            "nome": pet[1],
            "especie": pet[2],
            "raca": pet[3],
            "idade": pet[4],
            "dono": pet[5]
        }

        lista.append(dados)

    print("\n--- PETS ---")

    for pet in lista:
        print(
            f'ID: {pet["id"]} | '
            f'Nome: {pet["nome"]} | '
            f'Espécie: {pet["especie"]} | '
            f'Raça: {pet["raca"]} | '
            f'Idade: {pet["idade"]} | '
            f'Dono: {pet["dono"]}'
        )



