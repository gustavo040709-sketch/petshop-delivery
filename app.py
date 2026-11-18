import json
import hashlib
import hmac
import os
import re
import sys
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request, send_from_directory

PYTHON_DIR = Path(__file__).resolve().parent / "python"
sys.path.insert(0, str(PYTHON_DIR))

from banco import conectar, criar_tabelas

BASE_DIR = Path(__file__).resolve().parent
MERCADO_PAGO_API = "https://api.mercadopago.com/v1/payments"
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


class MercadoPagoError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def preparar_banco():
    criar_tabelas()


def validar_carrinho(carrinho):
    if not isinstance(carrinho, list) or not carrinho:
        raise ValueError("Sua sacola está vazia.")

    quantities = {}
    for item in carrinho:
        if not isinstance(item, dict):
            raise ValueError("Um produto da sacola é inválido.")
        product_id = item.get("id")
        quantity = item.get("quantidade")
        if (
            isinstance(product_id, bool)
            or not isinstance(product_id, int)
            or isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or product_id <= 0
            or quantity <= 0
            or quantity > 99
        ):
            raise ValueError("Produto ou quantidade inválida.")
        quantities[product_id] = quantities.get(product_id, 0) + quantity
    return quantities


def cpf_valido(value):
    digits = re.sub(r"\D", "", value)
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    for position in (9, 10):
        checksum = sum(
            int(digit) * weight
            for digit, weight in zip(digits[:position], range(position + 1, 1, -1))
        )
        remainder = (checksum * 10) % 11
        expected = 0 if remainder == 10 else remainder
        if expected != int(digits[position]):
            return False
    return True


def carregar_produtos(cursor, quantities, check_stock=True, lock_stock=False):
    items = []
    total = Decimal("0.00")
    for product_id, quantity in quantities.items():
        query = "SELECT nome, preco, estoque FROM produtos WHERE id = ?"
        if lock_stock:
            query += " FOR UPDATE"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        if not product:
            raise ValueError(f"Produto de ID {product_id} não encontrado.")
        name, price, stock = product
        if check_stock and quantity > stock:
            raise ValueError(f"Estoque insuficiente para {name}.")
        subtotal = Decimal(str(price)) * quantity
        total += subtotal
        items.append({
            "id": product_id,
            "nome": name,
            "quantidade": quantity,
            "preco": float(price),
            "subtotal": float(subtotal),
        })
    return items, total.quantize(Decimal("0.01"))


def enviar_pagamento_mercado_pago(payment_data, idempotency_key):
    access_token = os.environ.get("MP_ACCESS_TOKEN")
    if not access_token:
        raise MercadoPagoError(
            "O pagamento online ainda não está configurado. Fale com a loja.",
            503,
        )

    body = json.dumps(payment_data).encode("utf-8")
    provider_request = Request(
        MERCADO_PAGO_API,
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": idempotency_key,
        },
        method="POST",
    )
    try:
        with urlopen(provider_request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        app.logger.warning("Mercado Pago respondeu com HTTP %s.", error.code)
        try:
            provider_error = json.loads(response_body)
        except json.JSONDecodeError:
            provider_error = {}
        causes = provider_error.get("cause")
        cause = provider_error.get("message")
        if not cause and isinstance(causes, list) and causes and isinstance(causes[0], dict):
            cause = causes[0].get("description")
        message = "O Mercado Pago não conseguiu processar o pagamento."
        if cause:
            message = f"Pagamento não processado: {cause}"
        raise MercadoPagoError(message, 402) from error
    except (URLError, TimeoutError) as error:
        app.logger.warning("Falha de comunicação com o Mercado Pago: %s", error)
        raise MercadoPagoError(
            "Não foi possível conectar ao Mercado Pago. Tente novamente.",
            502,
        ) from error
    except json.JSONDecodeError as error:
        app.logger.exception("O Mercado Pago retornou uma resposta inválida.")
        raise MercadoPagoError(
            "O Mercado Pago retornou uma resposta inválida. Tente novamente.",
            502,
        ) from error


def buscar_pagamento_mercado_pago(payment_id):
    access_token = os.environ.get("MP_ACCESS_TOKEN")
    if not access_token:
        raise MercadoPagoError("O pagamento online não está configurado.", 503)
    provider_request = Request(
        f"{MERCADO_PAGO_API}/{payment_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urlopen(provider_request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        app.logger.warning("Não foi possível consultar a notificação do Mercado Pago.")
        raise MercadoPagoError("Não foi possível confirmar o pagamento.", 502) from error


@app.route("/")
def inicio():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/checkout")
@app.route("/checkout.html")
def checkout():
    return send_from_directory(BASE_DIR, "checkout.html")



@app.get("/api/produtos")
def listar_produtos():
    banco = conectar()

    try:
        cursor = banco.cursor()

        cursor.execute("""
            SELECT id, nome, categoria, preco, estoque, imagem
            FROM produtos
            WHERE estoque > 0 
            ORDER BY id
        """)

        products = [
            {
                "id": product_id,
                "nome": name,
                "categoria": category or "",
                "preco": float(price),
                "estoque": stock,
                "imagem": imagem or ""
            }
            for product_id, name, category, price, stock, imagem
            in cursor.fetchall()
        ]

        return jsonify({"produtos": products})

    except Exception:
        app.logger.exception("Falha ao carregar os produtos da loja.")
        return jsonify({
            "erro": "Não foi possível carregar os produtos agora."
        }), 500

    finally:
        banco.close()



@app.get("/api/checkout/config")
def checkout_config():
    return jsonify({"public_key": os.environ.get("MP_PUBLIC_KEY", "")})


@app.post("/api/checkout/quote")
def checkout_quote():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"erro": "Dados inválidos."}), 400
    try:
        quantities = validar_carrinho(data.get("carrinho"))
        banco = conectar()
        try:
            items, total = carregar_produtos(banco.cursor(), quantities)
        finally:
            banco.close()
        return jsonify({"itens": items, "total": float(total)})
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


@app.post("/api/checkout")
def finalizar_compra():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"erro": "Dados inválidos."}), 400

    name = data.get("nome")
    email = data.get("email")
    phone = data.get("telefone")
    payment_method = data.get("pagamento")
    address = data.get("endereco")
    if not all(isinstance(value, str) and value.strip() for value in (name, email, phone)):
        return jsonify({"erro": "Preencha nome, e-mail e telefone."}), 400
    name, email, phone = name.strip(), email.strip().lower(), phone.strip()
    if len(name) > 100 or len(email) > 120 or len(phone) > 20 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"erro": "Confira seus dados de contato."}), 400
    if payment_method not in ("pix", "cartao", "dinheiro"):
        return jsonify({"erro": "Forma de pagamento inválida."}), 400
    if not isinstance(address, dict):
        return jsonify({"erro": "Informe o endereço de entrega."}), 400
    address_fields = ("cep", "rua", "numero", "complemento", "bairro", "cidade", "estado")
    if any(not isinstance(address.get(field, ""), str) for field in address_fields):
        return jsonify({"erro": "O endereço de entrega é inválido."}), 400
    normalized_address = {field: address.get(field, "").strip() for field in address_fields}
    if any(not normalized_address[field] for field in ("cep", "rua", "numero", "bairro", "cidade", "estado")):
        return jsonify({"erro": "Preencha os campos obrigatórios do endereço."}), 400
    if any(len(value) > limit for value, limit in (
        (normalized_address["cep"], 9),
        (normalized_address["rua"], 120),
        (normalized_address["numero"], 12),
        (normalized_address["complemento"], 80),
        (normalized_address["bairro"], 80),
        (normalized_address["cidade"], 80),
        (normalized_address["estado"], 2),
    )):
        return jsonify({"erro": "Confira os dados do endereço."}), 400

    try:
        quantities = validar_carrinho(data.get("carrinho"))
        key_value = data.get("idempotency_key")
        idempotency_key = str(uuid.UUID(key_value)) if isinstance(key_value, str) else str(uuid.uuid4())
    except (ValueError, AttributeError) as error:
        return jsonify({"erro": str(error) or "Chave de pedido inválida."}), 400

    card_data = data.get("cartao")
    if payment_method == "cartao":
        if not isinstance(card_data, dict):
            return jsonify({"erro": "Preencha os dados do cartão no formulário Mercado Pago."}), 400
        token = card_data.get("token")
        payment_method_id = card_data.get("payment_method_id")
        installments = card_data.get("installments")
        if (
            not isinstance(token, str)
            or not token
            or len(token) > 2048
            or not isinstance(payment_method_id, str)
            or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", payment_method_id)
            or isinstance(installments, bool)
            or not isinstance(installments, int)
            or installments < 1
            or installments > 12
        ):
            return jsonify({"erro": "Os dados tokenizados do cartão são inválidos. Tente novamente."}), 400

    banco = conectar()
    try:
        banco.execute("BEGIN")
        cursor = banco.cursor()
        items, total = carregar_produtos(cursor, quantities, lock_stock=True)
        order_code = str(uuid.uuid4())[:8].upper()
                
        payment = None

        if payment_method == "cartao":
            name_parts = name.split(maxsplit=1)
            payer = {"email": email, "first_name": name_parts[0]}

            if len(name_parts) > 1:
                payer["last_name"] = name_parts[1]

            payer_data = card_data.get("payer")

            if isinstance(payer_data, dict):
                identification = payer_data.get("identification")

                if isinstance(identification, dict):
                    if identification.get("type") and identification.get("number"):
                        payer["identification"] = {
                            "type": identification["type"],
                            "number": identification["number"],
                        }

            provider_payload = {
                "transaction_amount": float(total),
                "token": token,
                "description": f"Pedido {order_code} - Pata & Companhia",
                "installments": installments,
                "payment_method_id": payment_method_id,
                "payer": payer,
                "external_reference": order_code,
            }

            issuer_id = card_data.get("issuer_id")

            if issuer_id is not None:
                provider_payload["issuer_id"] = str(issuer_id)

            payment = enviar_pagamento_mercado_pago(
                provider_payload, idempotency_key
            )

            if payment.get("status") not in ("approved", "pending", "in_process"):
                raise MercadoPagoError(
                    "O pagamento não foi aprovado. Confira os dados ou tente outra forma de pagamento.",
                    402,
                )

            payment_status = payment["status"]

        elif payment_method == "pix":
            payment_status = "aguardando confirmação manual"

        else:
            payment_status = "aguardando pagamento na entrega"

        cursor.execute("SELECT id FROM clientes WHERE email = ?", (email,))
        customer = cursor.fetchone()
        if customer:
            customer_id = customer[0]
            cursor.execute(
                "UPDATE clientes SET nome = ?, telefone = ? WHERE id = ?",
                (name, phone, customer_id),
            )
        else:
            cursor.execute(
                "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?) RETURNING id",
                (name, phone, email),
            )
            customer_id = cursor.fetchone()[0]

        payment_id = str(payment["id"]) if payment else None
        payment_reference = "dinheiro" if payment_method == "dinheiro" else payment_method
        for item in items:
            cursor.execute("""
                INSERT INTO vendas (
                    data, quantidade, valor_total, cliente_id, produto_id,
                    pedido_codigo, forma_pagamento, status_pagamento, mercado_pago_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                item["quantidade"],
                item["subtotal"],
                customer_id,
                item["id"],
                order_code,
                payment_reference,
                payment_status,
                payment_id,
            ))
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["id"]),
            )

        cursor.execute("""
            INSERT INTO enderecos_pedidos (
                pedido_codigo, cep, rua, numero, complemento, bairro, cidade, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_code,
            normalized_address["cep"],
            normalized_address["rua"],
            normalized_address["numero"],
            normalized_address["complemento"],
            normalized_address["bairro"],
            normalized_address["cidade"],
            normalized_address["estado"],
        ))
        banco.commit()

        response = {
            "pedido": order_code,
            "cliente": name,
            "total": float(total),
            "pagamento": payment_method,
            "status": payment_status,
            "status_pagamento": payment_status,
        }
        if payment_method == "pix":
            response["pix"] = {
                "manual": True,
                "qr_code_url": "/imagens/pix.png",
            }
        return jsonify(response), 201
    except ValueError as error:
        banco.rollback()
        return jsonify({"erro": str(error)}), 400
    except MercadoPagoError as error:
        banco.rollback()
        return jsonify({"erro": str(error)}), error.status_code
    except Exception:
        banco.rollback()
        app.logger.exception("Falha ao finalizar a compra.")
        return jsonify({"erro": "Não foi possível finalizar a compra."}), 500
    finally:
        banco.close()

@app.post("/api/mercado-pago/webhook")
def mercado_pago_webhook():
    secret = os.environ.get("MP_WEBHOOK_SECRET")
    if not secret:
        return jsonify({"erro": "Webhook do Mercado Pago não configurado."}), 503

    signature_parts = {}
    for part in request.headers.get("x-signature", "").split(","):
        key, separator, value = part.strip().partition("=")
        if separator:
            signature_parts[key] = value
    data_id = request.args.get("data.id", "")
    request_id = request.headers.get("x-request-id", "")
    timestamp = signature_parts.get("ts", "")
    signature = signature_parts.get("v1", "")
    if not all((data_id, request_id, timestamp, signature)):
        return jsonify({"erro": "Assinatura do webhook inválida."}), 401

    manifest = f"id:{data_id.lower()};request-id:{request_id};ts:{timestamp};"
    expected_signature = hmac.new(
        secret.encode("utf-8"), manifest.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        return jsonify({"erro": "Assinatura do webhook inválida."}), 401

    notification = request.get_json(silent=True) or {}
    notification_type = request.args.get("topic") or request.args.get("type") or notification.get("type")
    if notification_type != "payment" or not data_id.isdigit():
        return jsonify({"recebido": True}), 200

    try:
        payment = buscar_pagamento_mercado_pago(data_id)
        if str(payment.get("id")) != data_id:
            return jsonify({"erro": "Pagamento não confere com a notificação."}), 400
        status = payment.get("status")
        allowed_statuses = {
            "approved", "pending", "in_process", "rejected",
            "cancelled", "refunded", "charged_back",
        }
        if status not in allowed_statuses:
            return jsonify({"erro": "Status de pagamento desconhecido."}), 400

        banco = conectar()
        try:
            cursor = banco.cursor()
            cursor.execute("""
                SELECT produto_id, quantidade FROM vendas
                WHERE mercado_pago_id = ?
                  AND status_pagamento IN ('pending', 'in_process')
            """, (data_id,))
            reserved_items = cursor.fetchall()
            cursor.execute("""
                UPDATE vendas SET status_pagamento = ?
                WHERE mercado_pago_id = ?
            """, (status, data_id))
            if status in ("rejected", "cancelled"):
                for product_id, quantity in reserved_items:
                    cursor.execute(
                        "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
                        (quantity, product_id),
                    )
            banco.commit()
        finally:
            banco.close()
        return jsonify({"recebido": True}), 200
    except MercadoPagoError as error:
        return jsonify({"erro": str(error)}), error.status_code
    except Exception:
        app.logger.exception("Falha ao processar webhook do Mercado Pago.")
        return jsonify({"erro": "Não foi possível processar a notificação."}), 500


preparar_banco()


if __name__ == "__main__":
    app.run(debug=False)
