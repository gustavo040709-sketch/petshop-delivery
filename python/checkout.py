
from flask import Flask, request, jsonify, send_from_directory
from banco import conectar, criar_tabelas
from pathlib import Path
from datetime import datetime
import uuid

BASE_DIR = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    static_folder=str(BASE_DIR),
    static_url_path=""
)


def preparar_banco():
    criar_tabelas()


@app.route("/")
def inicio():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/checkout", methods=["POST"])
def finalizar_compra():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "Dados inválidos."}), 400

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip().lower()
    telefone = dados.get("telefone", "").strip()
    pagamento = dados.get("pagamento")
    carrinho = dados.get("carrinho", [])

    formas_validas = ["pix", "cartao", "dinheiro"]

    if not nome or not email or not telefone:
        return jsonify({
            "erro": "Preencha todos os dados do cliente."
        }), 400

    if pagamento not in formas_validas:
        return jsonify({
            "erro": "Forma de pagamento inválida."
        }), 400

    if not isinstance(carrinho, list) or not carrinho:
        return jsonify({
            "erro": "Seu carrinho está vazio."
        }), 400

    banco = conectar()
    cursor = banco.cursor()

    try:
        # Localiza o cliente pelo e-mail.
        cursor.execute(
            "SELECT id FROM clientes WHERE email = ?",
            (email,)
        )

        cliente = cursor.fetchone()

        if cliente:
            cliente_id = cliente[0]

            cursor.execute("""
                UPDATE clientes
                SET nome = ?, telefone = ?
                WHERE id = ?
            """, (nome, telefone, cliente_id))

        else:
            cursor.execute("""
                INSERT INTO clientes (nome, telefone, email)
                VALUES (?, ?, ?) RETURNING id
            """, (nome, telefone, email))

            cliente_id = cursor.fetchone()[0]

        pedido_codigo = str(uuid.uuid4())[:8].upper()
        valor_total = 0
        itens = []

        # Confere os produtos e o estoque.
        for item in carrinho:
            produto_id = int(item.get("id", 0))
            quantidade = int(item.get("quantidade", 0))

            if produto_id <= 0 or quantidade <= 0:
                raise ValueError("Produto ou quantidade inválida.")

            cursor.execute("""
                SELECT nome, preco, estoque
                FROM produtos
                WHERE id = ?
            """, (produto_id,))

            produto = cursor.fetchone()

            if not produto:
                raise ValueError(
                    f"Produto de ID {produto_id} não encontrado."
                )

            nome_produto, preco, estoque = produto

            if quantidade > estoque:
                raise ValueError(
                    f"Estoque insuficiente para {nome_produto}."
                )

            subtotal = float(preco) * quantidade
            valor_total += subtotal

            itens.append({
                "id": produto_id,
                "nome": nome_produto,
                "quantidade": quantidade,
                "subtotal": subtotal
            })

        # Registra a venda e atualiza o estoque.
        for item in itens:
            cursor.execute("""
                INSERT INTO vendas (
                    data,
                    quantidade,
                    valor_total,
                    cliente_id,
                    produto_id,
                    pedido_codigo,
                    forma_pagamento,
                    status_pagamento
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                item["quantidade"],
                item["subtotal"],
                cliente_id,
                item["id"],
                pedido_codigo,
                pagamento,
                "pendente"
            ))

            cursor.execute("""
                UPDATE produtos
                SET estoque = estoque - ?
                WHERE id = ?
            """, (item["quantidade"], item["id"]))

        banco.commit()

        return jsonify({
            "mensagem": "Pedido realizado com sucesso!",
            "pedido": pedido_codigo,
            "cliente": nome,
            "total": round(valor_total, 2),
            "pagamento": pagamento,
            "status": "pendente",
            "itens": itens
        }), 201

    except ValueError as erro:
        banco.rollback()
        return jsonify({"erro": str(erro)}), 400

    except Exception:
        banco.rollback()
        return jsonify({
            "erro": "Não foi possível finalizar o pedido."
        }), 500

    finally:
        banco.close()


if __name__ == "__main__":
    preparar_banco()
    app.run(debug=True)
