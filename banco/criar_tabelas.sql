CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS pets (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especie VARCHAR(50),
    raca VARCHAR(100),
    idade INTEGER,
    cliente_id INTEGER
);

CREATE TABLE IF NOT EXISTS funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(100),
    telefone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    data TEXT,
    horario TEXT,
    pet_id INTEGER,
    servico_id INTEGER,
    funcionario_id INTEGER
);

CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    preco NUMERIC(10, 2),
    estoque INTEGER,
    imagem TEXT
);

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
);

CREATE TABLE IF NOT EXISTS enderecos_pedidos (
    pedido_codigo TEXT PRIMARY KEY,
    cep TEXT NOT NULL,
    rua TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL
);
