from banco import conectar


def realizar_venda():
    venda = {
        "data": input("Data da venda: "),
        "quantidade": int(input("Quantidade: ")),
        "cliente_id": int(input("ID do cliente: ")),
        "produto_id": int(input("ID do produto: "))
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute(
        "SELECT nome, preco, estoque FROM produtos WHERE id = ?",
        (venda["produto_id"],)
    )

    produto = cursor.fetchone()

    if produto is None:
        print("Produto não encontrado!")
        banco.close()
        return

    nome_produto = produto[0]
    preco = produto[1]
    estoque = produto[2]

    if venda["quantidade"] > estoque:
        print("Estoque insuficiente!")
        banco.close()
        return

    valor_total = preco * venda["quantidade"]

    cursor.execute("""
        INSERT INTO vendas
        (data, quantidade, valor_total, cliente_id, produto_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        venda["data"],
        venda["quantidade"],
        valor_total,
        venda["cliente_id"],
        venda["produto_id"]
    ))

    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque - ?
        WHERE id = ?
    """, (
        venda["quantidade"],
        venda["produto_id"]
    ))

    banco.commit()
    banco.close()

    print("\nVenda realizada com sucesso!")
    print(f"Produto: {nome_produto}")
    print(f"Valor total: R$ {valor_total:.2f}")


def listar_vendas():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        SELECT
            vendas.id,
            vendas.data,
            clientes.nome,
            produtos.nome,
            vendas.quantidade,
            vendas.valor_total
        FROM vendas
        JOIN clientes ON vendas.cliente_id = clientes.id
        JOIN produtos ON vendas.produto_id = produtos.id
    """)

    vendas = cursor.fetchall()

    banco.close()

    lista = []

    for venda in vendas:
        dados = {
            "id": venda[0],
            "data": venda[1],
            "cliente": venda[2],
            "produto": venda[3],
            "quantidade": venda[4],
            "valor_total": venda[5]
        }

        lista.append(dados)

    print("\n--- VENDAS ---")

    for venda in lista:
        print(
            f'ID: {venda["id"]} | '
            f'Data: {venda["data"]} | '
            f'Cliente: {venda["cliente"]} | '
            f'Produto: {venda["produto"]} | '
            f'Quantidade: {venda["quantidade"]} | '
            f'Total: R$ {venda["valor_total"]:.2f}'
        )