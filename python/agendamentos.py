from banco import conectar


def cadastrar_agendamento():
    agendamento = {
        "data": input("Data do agendamento: "),
        "horario": input("Horário: "),
        "pet_id": int(input("ID do pet: ")),
        "servico_id": int(input("ID do serviço: ")),
        "funcionario_id": int(input("ID do funcionário: "))
    }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO agendamentos
        (data, horario, pet_id, servico_id, funcionario_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        agendamento["data"],
        agendamento["horario"],
        agendamento["pet_id"],
        agendamento["servico_id"],
        agendamento["funcionario_id"]
    ))

    banco.commit()
    banco.close()

    print("Agendamento realizado com sucesso!")


def listar_agendamentos():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        SELECT
            agendamentos.id,
            agendamentos.data,
            agendamentos.horario,
            pets.nome,
            servicos.nome,
            funcionarios.nome
        FROM agendamentos
        JOIN pets ON agendamentos.pet_id = pets.id
        JOIN servicos ON agendamentos.servico_id = servicos.id
        JOIN funcionarios ON agendamentos.funcionario_id = funcionarios.id
    """)

    agendamentos = cursor.fetchall()

    banco.close()

    lista = []

    for agendamento in agendamentos:
        dados = {
            "id": agendamento[0],
            "data": agendamento[1],
            "horario": agendamento[2],
            "pet": agendamento[3],
            "servico": agendamento[4],
            "funcionario": agendamento[5]
        }

        lista.append(dados)

    print("\n--- AGENDAMENTOS ---")

    for agendamento in lista:
        print(
            f'ID: {agendamento["id"]} | '
            f'Data: {agendamento["data"]} | '
            f'Horário: {agendamento["horario"]} | '
            f'Pet: {agendamento["pet"]} | '
            f'Serviço: {agendamento["servico"]} | '
            f'Funcionário: {agendamento["funcionario"]}'
        )