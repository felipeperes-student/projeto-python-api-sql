# Oficina Fácil

Sistema web acadêmico para gerenciamento de uma oficina mecânica, desenvolvido com Python, Flask, SQLite, SQL nativo, Jinja2, HTML e CSS.

## Funcionalidades
- Painel com indicadores de clientes, veículos, ordens em aberto e faturamento concluído.
- Cadastro, listagem, edição e exclusão de clientes.
- Cadastro, listagem e exclusão de veículos.
- Cadastro, listagem e exclusão de serviços.
- Criação e acompanhamento de ordens de serviço.
- Alteração de status e visualização dos serviços de cada ordem.
- Relacionamento entre clientes, veículos, ordens e serviços.

## Requisitos
- Python 3.10 ou superior
- pip

## Como executar

No terminal, dentro da pasta do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
flask --app app init-db
flask --app app run --debug
```

Acesse: http://127.0.0.1:5000

Para recriar o banco do zero, encerre o servidor, apague `oficina.db` e execute novamente `flask --app app init-db`.

## Estrutura

```text
oficina_facil/
├── app.py
├── db_sql.py
├── schema.sql
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── sobre.html
    ├── contato.html
    ├── clientes.html
    ├── form_cliente.html
    ├── veiculos.html
    ├── form_veiculo.html
    ├── servicos.html
    ├── form_servico.html
    ├── ordens.html
    ├── form_ordem.html
    ├── detalhe_ordem.html
    └── 404.html
```

## Modelo de dados

- `clientes` 1:N `veiculos`
- `veiculos` 1:N `ordens_servico`
- `ordens_servico` N:N `servicos`, resolvido pela tabela associativa `os_servicos`

As chaves estrangeiras usam `ON DELETE RESTRICT` para impedir a exclusão de registros que possuem dependências importantes. A tabela associativa usa `ON DELETE CASCADE`, pois seus itens não fazem sentido sem a ordem de serviço correspondente.

## Consultas SQL utilizadas

O arquivo `db_sql.py` concentra o acesso ao banco e utiliza comandos SQL nativos parametrizados (`?`), incluindo `INSERT`, `SELECT`, `UPDATE` e `DELETE`. As listagens de veículos e ordens utilizam `INNER JOIN` porque precisam exibir os dados relacionados obrigatórios.

## Observação acadêmica

Os dados de contato exibidos são fictícios. O projeto é uma base funcional para fins didáticos e pode ser ampliado com autenticação, validações adicionais e relatórios.
