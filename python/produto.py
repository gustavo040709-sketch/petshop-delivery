from banco import conectar


def cadastrar_produto():
    produto = {
        "nome": input("Nome do produto: "),
        "categoria": input("Categoria: "),
        "preco": float(input("Preço: R$ ")),
        "estoque": int(input("Quantidade em estoque: "))
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO produtos
        (nome, categoria, preco, estoque)
        VALUES (?, ?, ?, ?)
    """, (
        produto["nome"],
        produto["categoria"],
        produto["preco"],
        produto["estoque"]
    ))

    banco.commit()
    banco.close()

    print("Produto cadastrado com sucesso!")


def listar_produtos():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    banco.close()

    lista = []

    for produto in produtos:
        dados = {
            "id": produto[0],
            "nome": produto[1],
            "categoria": produto[2],
            "preco": produto[3],
            "estoque": produto[4]
        }

        lista.append(dados)

    print("\n--- PRODUTOS ---")

    for produto in lista:
        print(
            f'ID: {produto["id"]} | '
            f'Produto: {produto["nome"]} | '
            f'Categoria: {produto["categoria"]} | '
            f'Preço: R$ {produto["preco"]:.2f} | '
            f'Estoque: {produto["estoque"]}'
        )