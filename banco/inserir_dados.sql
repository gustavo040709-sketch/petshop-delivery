INSERT INTO clientes (nome, telefone, email) VALUES
('Ana Silva', '19999999999', 'ana@email.com'),
('João Santos', '19988888888', 'joao@email.com'),
('Maria Oliveira', '19977777777', 'maria@email.com'),
('Pedro Souza', '19966666666', 'pedro@email.com'),
('Lara Costa', '19955555555', 'lara@email.com'),
('Lucas Almeida', '19944444444', 'lucas@email.com'),
('Beatriz Lima', '19933333333', 'beatriz@email.com'),
('Gabriel Rocha', '19922222222', 'gabriel@email.com'),
('Julia Martins', '19911111111', 'julia@email.com'),
('Rafael Gomes', '19900000000', 'rafael@email.com');

INSERT INTO pets (nome, especie, raca, idade, id_cliente) VALUES
('Thor', 'Cachorro', 'Golden Retriever', 3, 1),
('Mel', 'Cachorro', 'Shih Tzu', 2, 1),
('Mimi', 'Gato', 'Persa', 4, 2),
('Bob', 'Cachorro', 'Labrador', 5, 3),
('Nina', 'Gato', 'Siamês', 2, 3),
('Luna', 'Cachorro', 'Poodle', 6, 4),
('Max', 'Cachorro', 'Bulldog', 3, 5),
('Amora', 'Gato', 'Maine Coon', 1, 6),
('Toby', 'Cachorro', 'Beagle', 4, 7),
('Belinha', 'Cachorro', 'Yorkshire', 2, 7),
('Simba', 'Gato', 'Siamês', 3, 8),
('Fred', 'Cachorro', 'Pug', 5, 9),
('Kiara', 'Gato', 'Persa', 2, 9),
('Bento', 'Cachorro', 'Rottweiler', 4, 10),
('Cacau', 'Cachorro', 'Chihuahua', 1, 10);

INSERT INTO produtos (nome, categoria, preco, estoque) VALUES
('Ração para cães 10kg', 'Ração', 89.90, 20),
('Ração para gatos 10kg', 'Ração', 94.90, 15),
('Petisco sabor carne', 'Petisco', 19.90, 30),
('Petisco sabor frango', 'Petisco', 18.90, 25),
('Shampoo para cães', 'Higiene', 29.90, 12),
('Shampoo para gatos', 'Higiene', 31.90, 10),
('Coleira azul', 'Acessórios', 24.90, 18),
('Coleira vermelha', 'Acessórios', 24.90, 14),
('Brinquedo bola', 'Brinquedos', 15.90, 20),
('Brinquedo corda', 'Brinquedos', 17.90, 16),
('Cama pequena', 'Acessórios', 79.90, 8),
('Cama grande', 'Acessórios', 119.90, 6),
('Areia para gatos', 'Higiene', 22.90, 20),
('Escova para pelos', 'Higiene', 27.90, 9),
('Comedouro', 'Acessórios', 35.90, 11);

INSERT INTO servicos (nome, descricao, preco) VALUES
('Banho', 'Banho completo para o pet', 45.00),
('Tosa', 'Tosa higiênica ou completa', 55.00),
('Banho e Tosa', 'Banho completo com tosa', 85.00),
('Corte de unhas', 'Corte e cuidado das unhas', 20.00),
('Higienização', 'Higienização de ouvidos e olhos', 30.00);

INSERT INTO vendas (data_venda, id_cliente) VALUES
('2026-09-01', 1),
('2026-09-02', 2),
('2026-09-03', 3),
('2026-09-04', 1),
('2026-09-05', 4),
('2026-09-06', 5),
('2026-09-07', 6),
('2026-09-08', 7),
('2026-09-09', 8),
('2026-09-10', 9);

INSERT INTO itens_venda
(id_venda, id_produto, quantidade, preco_unitario) VALUES
(1, 1, 1, 89.90),
(1, 3, 2, 19.90),
(2, 2, 1, 94.90),
(2, 9, 1, 15.90),
(3, 5, 1, 29.90),
(3, 7, 1, 24.90),
(4, 4, 2, 18.90),
(4, 10, 1, 17.90),
(5, 11, 1, 79.90),
(6, 6, 1, 31.90),
(6, 13, 2, 22.90),
(7, 8, 1, 24.90),
(8, 12, 1, 119.90),
(9, 14, 1, 27.90),
(10, 15, 2, 35.90);

INSERT INTO agendamentos
(id_pet, id_servico, data_agendamento, horario, status) VALUES
(1, 1, '2026-09-15', '09:00', 'Agendado'),
(2, 3, '2026-09-15', '10:00', 'Agendado'),
(3, 2, '2026-09-16', '09:30', 'Agendado'),
(4, 1, '2026-09-16', '11:00', 'Concluído'),
(5, 4, '2026-09-17', '14:00', 'Agendado'),
(6, 3, '2026-09-17', '15:00', 'Agendado'),
(7, 1, '2026-09-18', '09:00', 'Cancelado'),
(8, 5, '2026-09-18', '10:30', 'Agendado'),
(9, 2, '2026-09-19', '13:00', 'Agendado'),
(10, 3, '2026-09-19', '14:00', 'Agendado');