-- CONSULTAS

-- Todos os clientes
SELECT * FROM clientes;


-- Nome e telefone dos clientes
SELECT nome, telefone
FROM clientes;


-- Pets do cliente 1
SELECT *
FROM pets
WHERE id_cliente = 1;


-- Somente cachorros
SELECT nome, raca, idade
FROM pets
WHERE especie = 'Cachorro';


-- Produtos com estoque baixo
SELECT nome, estoque
FROM produtos
WHERE estoque < 10;


-- Produtos acima de R$ 50
SELECT nome, preco
FROM produtos
WHERE preco > 50;


-- Vendas e seus clientes
SELECT clientes.nome, vendas.id_venda, vendas.data_venda
FROM clientes
JOIN vendas
ON clientes.id_cliente = vendas.id_cliente;


-- Pets e seus donos
SELECT pets.nome AS pet, clientes.nome AS dono
FROM pets
JOIN clientes
ON pets.id_cliente = clientes.id_cliente;


-- Agendamentos completos
SELECT
    pets.nome AS pet,
    servicos.nome AS servico,
    agendamentos.data_agendamento,
    agendamentos.horario,
    agendamentos.status
FROM agendamentos
JOIN pets
ON agendamentos.id_pet = pets.id_pet
JOIN servicos
ON agendamentos.id_servico = servicos.id_servico;


-- Agendamentos ativos
SELECT
    pets.nome AS pet,
    servicos.nome AS servico,
    agendamentos.data_agendamento,
    agendamentos.horario
FROM agendamentos
JOIN pets
ON agendamentos.id_pet = pets.id_pet
JOIN servicos
ON agendamentos.id_servico = servicos.id_servico
WHERE agendamentos.status = 'Agendado';


-- Total de cada item vendido
SELECT
    id_venda,
    id_produto,
    quantidade,
    preco_unitario,
    quantidade * preco_unitario AS total
FROM itens_venda;


-- Atualizar estoque
UPDATE produtos
SET estoque = 25
WHERE id_produto = 1;


-- Atualizar telefone
UPDATE clientes
SET telefone = '19912345678'
WHERE id_cliente = 1;


-- Excluir um agendamento
DELETE FROM agendamentos
WHERE id_agendamento = 7; 