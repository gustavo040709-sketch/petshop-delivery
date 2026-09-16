CREATE TABLE clientes (
    id_cliente SERIAL, PRIMARY KEY,
    nome VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(70),
);

CREATE TABLE pets (
    id_pet SERIAL, PRIMARY KEY,
    nome VARCHAR(100),
    especie VARCHAR(50),
    raca VARCHAR(100),
    idade INTEGER,
    id_cliente INTEGER,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
)

CREATE TABLE produtos (
    id_produto SERIAL, PRIMARY KEY,
    nome VARCHAR(100),
    categoria VARCHAR(50),
    estoque INTEGER
    preco DECIMAL(10, 2)
)

CREATE TABLE vendas (
    id_venda SERIAL, PRIMARY KEY,
    id_cliente INTEGER,
    data_venda DATE,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE itens_venda (
    id_item SERIAL, PRIMARY KEY,
    id_venda INTEGER,
    id_produto INTEGER,
    quantidade INTEGER,
    preco_unitario DECIMAL(10, 2),
    FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
);

CREATE TABLE servicos (
    id_servico SERIAL, PRIMARY KEY,
    nome VARCHAR(100),
    descricao VARCHAR(200),
    preco DECIMAL(10, 2)
);

CREATE TABLE agendamentos (
    id_agendamento SERIAL, PRIMARY KEY,
    id_cliente INTEGER,
    id_pet INTEGER,
    id_servico INTEGER,
    data_agendamento DATE,
    horario TIME,
    FOREIGN KEY (id_pet) REFERENCES pets(id_pet),
    FOREIGN KEY (id_servico) REFERENCES servicos(id_servico)
);