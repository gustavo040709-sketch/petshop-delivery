# Pet Shop

Loja e sistema de gerenciamento de pet shop em Python, Flask e PostgreSQL.
O banco Neon configurado em `DATABASE_URL` é usado localmente e pelo Vercel,
mantendo os dois ambientes conectados aos mesmos dados.

## Banco de dados Neon

No painel do Neon, copie a connection string PostgreSQL. Para o Vercel, prefira
a URL com pooler. Não coloque a senha no código nem a envie para o Git.

### Executar localmente

No PowerShell, crie o arquivo local de configuração e edite-o para preencher
`DATABASE_URL` com a connection string copiada do Neon:

```powershell
Copy-Item .env.example .env
```

Instale as dependências e inicie o Flask:

```powershell
py -m pip install -r requirements.txt
py app.py
```

Abra `http://127.0.0.1:5000`. O `.env` é ignorado pelo Git; mantenha nele a URL
do banco e as credenciais do Mercado Pago usadas localmente.

Na inicialização, o app cria as tabelas necessárias. Se o banco já tiver sido
criado pelo script PostgreSQL antigo deste projeto, a inicialização renomeia as
colunas conhecidas para os nomes esperados pela aplicação e preserva os dados.

### Publicar no Vercel

1. Importe este repositório no Vercel.
2. Em **Settings > Environment Variables**, adicione `DATABASE_URL` com a mesma
   connection string PostgreSQL do Neon (de preferência a URL com pooler e
   `sslmode=require`) para os ambientes usados (Production, Preview e/ou
   Development).
3. Adicione também as variáveis do Mercado Pago se for habilitar pagamentos.
4. Faça um novo deploy depois de salvar as variáveis.

O arquivo `api/index.py` encaminha as requisições ao Flask e `vercel.json`
configura o roteamento. O Vercel não usa o arquivo `.env` local. A conexão e
criação/atualização das tabelas acontecem no primeiro acesso à API que consulta
o banco, não durante o carregamento da função; assim, uma falha no Neon não
impede a página inicial de abrir. Sem `DATABASE_URL` configurada, a API retorna
um erro de configuração e não usa um banco local temporário. Consulte **Runtime
Logs** no Vercel para detalhes de falhas de conexão.

## Estrutura

A pasta `banco` contém os scripts SQL e a pasta `python` contém os módulos
Python do sistema.

## Interface web

O front-end está na raiz do projeto. Materialize CSS 1.0.0 é carregado por CDN
antes dos estilos próprios, que permanecem responsáveis pelo tema da loja. O
botão de finalizar pedido abre uma página de checkout separada. O formulário
de cartão é fornecido pelo Card Payment
Brick do Mercado Pago; os dados sensíveis do cartão não são enviados nem
armazenados pelo site. Configure primeiro as credenciais de teste do Mercado
Pago e só use credenciais de produção em um ambiente HTTPS.

Para atualizar o status dos pagamentos online, configure no painel do Mercado
Pago o webhook `https://seu-dominio/api/mercado-pago/webhook` para eventos de
pagamento e use a assinatura secreta em `MP_WEBHOOK_SECRET`. O pagamento em
dinheiro na entrega não depende do gateway.

## Integrantes

- Pedro Henrique Ferraz da Silva
- Gustavo Santos da Silva
- Lara Costa Bollis
