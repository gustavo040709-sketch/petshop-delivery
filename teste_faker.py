from faker import Faker

# Inicializa o gerador (em português do Brasil)
fake = Faker('pt_BR')

# Gera dados de teste
print("Nome:", fake.name())
print("Endereço:", fake.address())
print("E-mail:", fake.email())