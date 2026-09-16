from banco import criar_tabelas

from clientes import cadastrar_cliente, listar_clientes
from pets import cadastrar_pet, listar_pets
from funcionarios import cadastrar_funcionario, listar_funcionarios
from servicos import cadastrar_servico, listar_servicos
from agendamentos import cadastrar_agendamento, listar_agendamentos
from produto import cadastrar_produto, listar_produtos
from vendas import realizar_venda, listar_vendas


def menu():
    while True:
        print("\n==============================")
        print("       PETSHOP SISTEMA")
        print("==============================")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("3 - Cadastrar pet")
        print("4 - Listar pets")
        print("5 - Cadastrar funcionário")
        print("6 - Listar funcionários")
        print("7 - Cadastrar serviço")
        print("8 - Listar serviços")
        print("9 - Cadastrar agendamento")
        print("10 - Listar agendamentos")
        print("11 - Cadastrar produto")
        print("12 - Listar produtos")
        print("13 - Realizar venda")
        print("14 - Listar vendas")
        print("0 - Sair")
        print("==============================")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_cliente()

        elif opcao == "2":
            listar_clientes()

        elif opcao == "3":
            cadastrar_pet()

        elif opcao == "4":
            listar_pets()

        elif opcao == "5":
            cadastrar_funcionario()

        elif opcao == "6":
            listar_funcionarios()

        elif opcao == "7":
            cadastrar_servico()

        elif opcao == "8":
            listar_servicos()

        elif opcao == "9":
            cadastrar_agendamento()

        elif opcao == "10":
            listar_agendamentos()

        elif opcao == "11":
            cadastrar_produto()

        elif opcao == "12":
            listar_produtos()

        elif opcao == "13":
            realizar_venda()

        elif opcao == "14":
            listar_vendas()

        elif opcao == "0":
            print("Sistema encerrado!")
            break

        else:
            print("Opção inválida!")


criar_tabelas()
menu()