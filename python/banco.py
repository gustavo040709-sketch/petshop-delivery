import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class DatabaseConfigurationError(RuntimeError):
    pass


class CursorPostgres:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, parameters=None):
        self._cursor.execute(query.replace("?", "%s"), parameters)
        return self

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class ConexaoPostgres:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return CursorPostgres(self._connection.cursor())

    def execute(self, query, parameters=None):
        return CursorPostgres(self._connection.cursor()).execute(query, parameters)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def conectar():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise DatabaseConfigurationError(
            "Configure DATABASE_URL com a URL de conexão PostgreSQL do Neon."
        )
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise DatabaseConfigurationError(
            "DATABASE_URL precisa ser uma URL PostgreSQL."
        )

    return ConexaoPostgres(
        psycopg.connect(database_url, connect_timeout=10)
    )


def _tabela_existe(banco, tabela):
    cursor = banco.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = current_schema() AND table_name = ?
        )
        """,
        (tabela,),
    )
    return cursor.fetchone()[0]


def _coluna_existe(banco, tabela, coluna):
    cursor = banco.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = ?
              AND column_name = ?
        )
        """,
        (tabela, coluna),
    )
    return cursor.fetchone()[0]


def _renomear_coluna_legada(banco, tabela, antiga, nova):
    if (
        _tabela_existe(banco, tabela)
        and _coluna_existe(banco, tabela, antiga)
        and not _coluna_existe(banco, tabela, nova)
    ):
        banco.execute(f"ALTER TABLE {tabela} RENAME COLUMN {antiga} TO {nova}")


def _adicionar_coluna(banco, tabela, coluna, tipo):
    if not _coluna_existe(banco, tabela, coluna):
        banco.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")


def criar_tabelas():
    banco = conectar()
    try:
        for tabela, antiga, nova in (
            ("clientes", "id_cliente", "id"),
            ("pets", "id_pet", "id"),
            ("pets", "id_cliente", "cliente_id"),
            ("funcionarios", "id_funcionario", "id"),
            ("servicos", "id_servico", "id"),
            ("produtos", "id_produto", "id"),
            ("vendas", "id_venda", "id"),
            ("vendas", "id_cliente", "cliente_id"),
            ("vendas", "data_venda", "data"),
            ("agendamentos", "id_agendamento", "id"),
            ("agendamentos", "id_cliente", "cliente_id"),
            ("agendamentos", "id_pet", "pet_id"),
            ("agendamentos", "id_servico", "servico_id"),
            ("agendamentos", "id_funcionario", "funcionario_id"),
            ("agendamentos", "data_agendamento", "data"),
        ):
            _renomear_coluna_legada(banco, tabela, antiga, nova)

        for statement in (
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                telefone VARCHAR(20),
                email VARCHAR(120)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pets (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                especie VARCHAR(50),
                raca VARCHAR(100),
                idade INTEGER,
                cliente_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS funcionarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cargo VARCHAR(100),
                telefone VARCHAR(20)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS servicos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                preco NUMERIC(10, 2)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS agendamentos (
                id SERIAL PRIMARY KEY,
                data TEXT,
                horario TEXT,
                pet_id INTEGER,
                servico_id INTEGER,
                funcionario_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                categoria VARCHAR(50),
                preco NUMERIC(10, 2),
                estoque INTEGER,
                imagem TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                data TEXT,
                quantidade INTEGER,
                valor_total NUMERIC(10, 2),
                cliente_id INTEGER,
                produto_id INTEGER,
                pedido_codigo TEXT,
                forma_pagamento TEXT,
                status_pagamento TEXT,
                mercado_pago_id TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS enderecos_pedidos (
                pedido_codigo TEXT PRIMARY KEY,
                cep TEXT NOT NULL,
                rua TEXT NOT NULL,
                numero TEXT NOT NULL,
                complemento TEXT,
                bairro TEXT NOT NULL,
                cidade TEXT NOT NULL,
                estado TEXT NOT NULL
            )
            """,
        ):
            banco.execute(statement)

        _adicionar_coluna(banco, "produtos", "imagem", "TEXT")
        _adicionar_coluna(
            banco, "agendamentos", "funcionario_id", "INTEGER"
        )

        for coluna, tipo in (
            ("quantidade", "INTEGER"),
            ("valor_total", "NUMERIC(10, 2)"),
            ("produto_id", "INTEGER"),
            ("pedido_codigo", "TEXT"),
            ("forma_pagamento", "TEXT"),
            ("status_pagamento", "TEXT"),
            ("mercado_pago_id", "TEXT"),
        ):
            _adicionar_coluna(banco, "vendas", coluna, tipo)

        banco.execute(
            "ALTER TABLE vendas ALTER COLUMN data TYPE TEXT USING data::text"
        )
        banco.execute(
            "ALTER TABLE clientes ALTER COLUMN email TYPE VARCHAR(120)"
        )
        banco.commit()
    except Exception:
        banco.rollback()
        raise
    finally:
        banco.close()
