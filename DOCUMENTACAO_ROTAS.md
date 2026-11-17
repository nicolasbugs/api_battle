# Documentação das rotas — API BATTLE FIFA

**Disciplina:** Arquiteturas de Software — Univates — 2026/B  
**Versão:** 1.0.0  
**Endereço base (local):** `http://127.0.0.1:8000`  
**Base prevista na VM Univates:** `http://177.44.248.52:8000` (ainda não confirmada como acessível externamente).  
**Máquina:** `VMLS52` — Ubuntu 26.04 LTS — usuário SSH `univates` — caminho planejado `/home/univates/api`.  
**Implantação:** pendente; o SSH funciona, mas a pasta `api` foi identificada como `root:root` (ver `PUBLICACAO_VM_UNIVATES.md`).

## Documentação interativa

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

Depois de publicada e testada externamente na VM, as URLs previstas são:

- Swagger: `http://177.44.248.52:8000/docs`
- OpenAPI: `http://177.44.248.52:8000/openapi.json`
- ReDoc: `http://177.44.248.52:8000/redoc`

**Para usar Postman/Insomnia na VM**, substitua `http://127.0.0.1:8000` por `http://177.44.248.52:8000` em cada exemplo; esses endereços dependem de rede/porta liberadas.

A API retorna JSON em UTF-8. As quatro rotas GET são públicas, facilitando a validação por outro grupo. O POST é protegido por cabeçalho `X-API-Key` com a chave configurada no servidor.

## Estrutura do jogador

Os 16 campos abaixo devem estar presentes no POST, com os nomes exatos do dataset:

| Campo | Tipo | Observação |
|---|---|---|
| `player_id` | inteiro | ID único positivo; chave primária |
| `player_name` | texto | Nome do jogador |
| `age` | inteiro | Idade entre 0 e 120 |
| `nationality` | texto | Nacionalidade; exemplo: `Brazil` |
| `club` | texto | Clube |
| `position` | texto | Posição |
| `overall_rating` | inteiro | 0 a 100 |
| `potential_rating` | inteiro | 0 a 100 |
| `matches_played` | inteiro | 0 ou maior |
| `goals` | inteiro | 0 ou maior |
| `assists` | inteiro | 0 ou maior |
| `minutes_played` | inteiro | 0 ou maior |
| `market_value_million_eur` | decimal | Valor em milhões de euros; >= 0 |
| `contract_years_left` | inteiro | >= 0 |
| `injury_prone` | texto | `Yes` ou `No` |
| `transfer_risk_level` | texto | `Low`, `Medium` ou `High` |

## 1. POST `/fifa` — inserir jogador

- **Objetivo:** cadastra um novo jogador.
- **Autenticação:** obrigatória. Header: `X-API-Key: SUA_CHAVE`.
- **Content-Type:** `application/json`.
- **Sucesso:** HTTP `201 Created`, com o registro criado.
- **Erros:** `401` (chave ausente/incorreta), `409` (player_id duplicado), `422` (dados inválidos), `503` (chave não configurada no servidor).

**Exemplo de corpo JSON:**

```json
{
  "player_id": 50000,
  "player_name": "Jogador Exemplo",
  "age": 24,
  "nationality": "Brazil",
  "club": "Clube Exemplo",
  "position": "ST",
  "overall_rating": 80,
  "potential_rating": 88,
  "matches_played": 25,
  "goals": 10,
  "assists": 5,
  "minutes_played": 1800,
  "market_value_million_eur": 12.5,
  "contract_years_left": 3,
  "injury_prone": "No",
  "transfer_risk_level": "Low"
}
```

**Exemplo cURL:**

```bash
curl -X POST http://127.0.0.1:8000/fifa \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: SUA_CHAVE' \
  -d '{"player_id":50000,"player_name":"Jogador Exemplo","age":24,"nationality":"Brazil","club":"Clube Exemplo","position":"ST","overall_rating":80,"potential_rating":88,"matches_played":25,"goals":10,"assists":5,"minutes_played":1800,"market_value_million_eur":12.5,"contract_years_left":3,"injury_prone":"No","transfer_risk_level":"Low"}'
```

## 2. GET `/fifa/count` — contar jogadores

- **Objetivo:** retorna o número total de registros existentes no banco.
- **Autenticação:** não exige.
- **Sucesso:** HTTP `200 OK`.

**Exemplo:** `GET http://127.0.0.1:8000/fifa/count`

```json
{ "total": 2800 }
```

O total ilustrado corresponde ao CSV original importado sem novos cadastros.

## 3. GET `/fifa` — listar todos

- **Objetivo:** retorna todos os registros da tabela, ordenados por `player_id`.
- **Autenticação:** não exige.
- **Sucesso:** HTTP `200 OK` e array JSON contendo todos os registros.

**Exemplo:** `GET http://127.0.0.1:8000/fifa`

**Resposta abreviada (apenas alguns campos foram exibidos aqui; a API retorna os 16):**

```json
[
  { "player_id": 1, "player_name": "Player_1", "nationality": "Germany", "...": "demais campos" },
  { "player_id": 2, "player_name": "Player_2", "nationality": "England", "...": "demais campos" }
]
```

Esta rota intencionalmente **não tem paginação**, pois o roteiro exige a consulta de todos os jogadores. O tamanho da resposta cresce com o banco.

## 4. GET `/fifa/id/{id}` — buscar por ID

- **Objetivo:** retorna um único registro pela coluna `player_id`.
- **Parâmetro de caminho:** `id` (inteiro positivo).
- **Autenticação:** não exige.
- **Sucesso:** HTTP `200 OK`, objeto com os 16 campos.
- **Erro:** HTTP `404 Not Found` se o jogador não existir; `422` se ID inválido.

**Exemplo:** `GET http://127.0.0.1:8000/fifa/id/1`

**Resposta abreviada:**

```json
{ "player_id": 1, "player_name": "Player_1", "nationality": "Germany", "...": "demais campos" }
```

## 5. GET `/fifa/nat/{exp}` — filtrar por nacionalidade

- **Objetivo:** retorna jogadores cuja coluna `nationality` é exatamente igual ao valor informado.
- **Parâmetro de caminho:** `exp` (texto, exemplo `Brazil`; a comparação é exata).
- **Autenticação:** não exige.
- **Sucesso:** HTTP `200 OK` e array JSON; se não houver correspondências, retorna `[]`.

**Exemplo:** `GET http://127.0.0.1:8000/fifa/nat/Brazil`

**Resposta abreviada:**

```json
[
  { "nationality": "Brazil", "...": "demais campos" }
]
```

Com os dados CSV originais, a rota retorna **380 jogadores**. Consulte o endpoint para obter os registros completos.

## Padrão dos erros

A maioria dos erros retorna JSON com uma propriedade `detail`:

```json
{ "detail": "Jogador não encontrado" }
```

Em erros de validação (`422`), `detail` contém uma lista de campos e motivos.

## Boas práticas de segurança e desempenho

- SQL com parâmetros (`?`) protege contra injeção de SQL.
- API Key protegendo POST; não compartilhar a chave com o grupo adversário durante os testes GET.
- Pydantic valida tipo e faixa dos campos, recusando campos desconhecidos.
- A chave é lida de variável de ambiente; não deve ser enviada ao repositório.
- `player_id` é chave primária e usa índice; `nationality` possui índice dedicado.
- No SQLite, consultas e contagens são feitas diretamente no banco, sem carregar toda a tabela desnecessariamente (exceto `GET /fifa`, que precisa de todos).
- Para produção na internet, usar HTTPS e limitar o acesso de rede; uma API Key enviada por HTTP pode ser interceptada.
- Limitação de taxa no proxy reverso é recomendada em ambiente exposto à internet; não está configurada neste projeto básico.

## Checklist de validação de outro grupo

1. Abrir `/docs` e conferir as cinco rotas.
2. Executar `GET /fifa/count` e confirmar que há jogadores importados.
3. Executar `GET /fifa` e verificar o array de registros.
4. Executar `GET /fifa/id/1` e depois um ID inexistente.
5. Executar `GET /fifa/nat/Brazil` e conferir a nacionalidade.
6. Solicitar uma chave de testes ao responsável pelo grupo e validar `POST /fifa`, caso o professor exija a validação da escrita.
7. Medir o tempo das consultas sob condições equivalentes.
