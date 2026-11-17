# API BATTLE — FIFA | Univates 2026/B

Projeto em **Python + FastAPI + SQLite** para a atividade da disciplina de Arquiteturas de Software. Implementa os **cinco endpoints obrigatórios**, importa o dataset CSV por script, possui documentação Swagger automática e documentação manual das rotas.

## Roteiro da atividade

O grupo já está formado. A sequência restante é:

1. **Implementar a API:** este projeto contém código, banco SQLite e importação em lote. Falta executar no ambiente do grupo.
2. **Documentar:** arquivo [`DOCUMENTACAO_ROTAS.md`](DOCUMENTACAO_ROTAS.md), Swagger e ReDoc.
3. **Disponibilizar a documentação:** compartilhar o endereço da VM (`http://177.44.248.52:8000/docs` (após publicação e teste externo)) e o e-mail de contato do grupo.
4. **Testar:** comandos cURL, Postman/Insomnia e testes automatizados (`pytest`).
5. **Publicar na VM:** executar o servidor na VM e confirmar acesso externo.

> IMPORTANTE: a documentação e a publicação na VM só estarão completas quando o grupo efetivamente executar e disponibilizar a aplicação. O roteiro do professor coloca a publicação na VM após os testes, mas exige que a API esteja disponível na VM para a validação final.

**VM identificada:** `univates@177.44.248.52`, nome `VMLS52`, Ubuntu 26.04 LTS. O diretório `/home/univates/api` existe, mas estava sob `root:root`; consulte [PUBLICACAO_VM_UNIVATES.md](PUBLICACAO_VM_UNIVATES.md) para resolver permissões, copiar arquivos e publicar a API.

## Requisitos

- Python 3.10 ou superior (preferível 3.11+).
- Linux/Windows/macOS para desenvolvimento; VM com Python e porta de rede liberada para entrega.
- Não exige servidor separado de banco de dados.

## Executar (Linux / VM Ubuntu)

```bash
cd fifa_api_battle
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python import_csv.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

Atenção: **guarde a chave `API_KEY` gerada** para fazer os testes POST. Para iniciar novamente, defina a mesma chave. Como alternativa, depois de ativar o ambiente e definir a chave, use `./run.sh` (importação idempotente + execução). O banco é criado automaticamente em `data/fifa.db`.

> Em uma VM pública, `0.0.0.0` permite escuta em todas as interfaces, mas o firewall/grupo de segurança também precisa liberar a porta TCP 8000. Para produção, publique por HTTPS com proxy reverso e preserve a chave em configuração segura.

## Executar (Windows PowerShell)

```powershell
cd fifa_api_battle
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:API_KEY = "troque-por-uma-chave-forte"
python import_csv.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Consultar e testar

No navegador:

- Documentação interativa: `http://127.0.0.1:8000/docs`
- Contagem: `http://127.0.0.1:8000/fifa/count`
- Todos: `http://127.0.0.1:8000/fifa`
- Por ID: `http://127.0.0.1:8000/fifa/id/1`
- Por nacionalidade: `http://127.0.0.1:8000/fifa/nat/Brazil`

O método POST `/fifa` exige `X-API-Key` e corpo JSON. Consulte [`DOCUMENTACAO_ROTAS.md`](DOCUMENTACAO_ROTAS.md).

Em Postman ou Insomnia, crie as cinco requisições com os métodos e URLs acima; no POST, configure header `X-API-Key` e `Content-Type: application/json`, e cole o exemplo de jogador da documentação.

## Testes automatizados

```bash
pip install -r requirements-dev.txt
pytest -q
```

Os testes usam um banco temporário, conferem a importação, todas as consultas, a autenticação de POST, dados inválidos e registro duplicado.

## Estrutura

```text
fifa_api_battle/
├── main.py                  # Endpoints FastAPI
├── models.py                # Validação dos 16 campos
├── database.py              # SQLite, tabela e índices
├── import_csv.py            # Importação em lote idempotente
├── data/
│   └── fifa_player_performance_market_value.csv
├── tests/
│   └── test_api.py
├── DOCUMENTACAO_ROTAS.md    # Documentação manual
├── requirements.txt
├── requirements-dev.txt
├── run.sh
├── .env.example
└── .gitignore
```

## Desempenho

- Índice da chave primária `player_id` para buscas por ID.
- Índice na coluna `nationality` para consulta por nacionalidade.
- Consultas parametrizadas e operações em lote.
- Retorno completo no `GET /fifa` exigido pelo enunciado, sem paginação.

**Observação:** o desempenho real depende da VM, rede e volume de dados. Não há garantia de primeira colocação. Fazer medições de tempos com o mesmo equipamento/rede e comparar os endpoints.

## Segurança

A autenticação é exigida somente no POST, para permitir testes GET entre grupos. Nunca versione `.env` ou exponha a chave. `API_KEY` deve estar configurada no ambiente; sem ela, POST retorna `503`. Limitação de taxa e HTTPS devem ser implementadas no proxy reverso caso a VM fique exposta na internet.

## Dados originais

O CSV contém **2.800 jogadores** e **380 registros com `nationality = Brazil`**. Reexecutar a importação não cria duplicatas, porque `player_id` é único e o script ignora registros já existentes.
