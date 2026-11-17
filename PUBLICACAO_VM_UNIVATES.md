# Publicação na VM da Univates — API BATTLE FIFA

**Atualização:** 16/11/2026  
**Disciplina:** Arquiteturas de Software — Prof. Fabrício — 2026/B

## 1. Dados confirmados e previstos

| Item | Valor | Situação |
|---|---|---|
| Máquina | `VMLS52` | Confirmado pelo terminal SSH |
| Sistema operacional | Ubuntu 26.04 LTS, kernel 7.0.0-27-generic | Confirmado pelo login SSH |
| IP da VM | `177.44.248.52` | Confirmado pelo login SSH |
| Usuário SSH | `univates` | Confirmado |
| Pasta de destino | `/home/univates/api` | Existe, mas pertence a `root:root` |
| Permissões da pasta | `drwxr-xr-x root root` | Confirmadas com `ls -ld` |
| Porta da API | `8000/tcp` | Planejada; acesso externo não confirmado |
| URL da documentação | `http://177.44.248.52:8000/docs` | Prevista, depende da API no ar e porta liberada |
| Banco | SQLite (`data/fifa.db`) | Configurado no código; criação na VM não confirmada |
| Status de implantação | Pendente | Não foi demonstrada execução na VM |

**Segurança:** evite compartilhar a senha SSH e o valor de `API_KEY`. Não coloque uma chave real na documentação pública. A autenticação por API Key está no POST, mas HTTP sem TLS não protege o segredo em trânsito; para acesso público, prefira HTTPS via proxy reverso.

## 2. Corrigir o erro de envio por SCP

A pasta `/home/univates/api` foi criada com propriedade `root:root` e permissões `755`, então o usuário `univates` não pode gravar nela. O erro observado foi `Permission denied`.

**Opção A — se a pasta é exclusiva do grupo e houver autorização/sudo:**

```bash
# Na VM, conectado como univates
sudo chown -R univates:univates /home/univates/api
ls -ld /home/univates/api
```

**Opção B — sem sudo ou sem permissão para alterar a pasta:**

```bash
# Na VM
mkdir -p /home/univates/fifa_api
```

Na opção B, substitua `api` por `fifa_api` nos comandos seguintes. Não altere permissões de pastas compartilhadas sem autorização.

## 3. Enviar os arquivos do computador local à VM

No **computador local** (`nicolas.bugs@lab5-20-lin`), não dentro do SSH:

```bash
# Confirme a pasta de origem
ls -la "$HOME/Área de trabalho/fifa_api_battle_fastapi/"

# Após corrigir as permissões da pasta /home/univates/api
scp -r "$HOME/Área de trabalho/fifa_api_battle_fastapi/." univates@177.44.248.52:/home/univates/api/
```

Se estiver usando **este ZIP atualizado**, descompacte-o no computador local; o diretório interno chama-se `fifa_api_battle_vm_univates`. Aponte o `scp` para esse diretório em vez de `fifa_api_battle_fastapi`.

**Verificação no servidor:**

```bash
ssh univates@177.44.248.52
cd /home/univates/api
ls -la
```

Confirme que existem `main.py`, `database.py`, `models.py`, `import_csv.py`, `requirements.txt` e o diretório `data/`.

## 4. Instalar e executar na VM

```bash
ssh univates@177.44.248.52
cd /home/univates/api
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Gera chave aleatória para a sessão de execução atual; guarde-a com segurança.
export API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Importação em lote e contagem inicial
python import_csv.py

# Executar a API em primeiro plano
uvicorn main:app --host 0.0.0.0 --port 8000
```

Se `python3 -m venv` falhar por falta do pacote do sistema, solicite ao administrador instalar `python3-venv` (ou instale com `sudo apt install python3-venv`, caso haja autorização). **Não execute Uvicorn com sudo**.

Para verificar em outro terminal **na VM**:

```bash
curl -i http://127.0.0.1:8000/fifa/count
curl -i http://127.0.0.1:8000/fifa/id/1
curl -i http://127.0.0.1:8000/fifa/nat/Brazil
```

Após importar apenas o dataset original e antes de novos POSTs, espera-se `{"total":2800}` e 380 jogadores com nacionalidade `Brazil`. Esses números mudarão com novos cadastros.

## 5. Endereços para a validação entre grupos

**Base prevista:** `http://177.44.248.52:8000`

| Método | Rota | URL prevista | Autenticação |
|---|---|---|---|
| POST | `/fifa` | `http://177.44.248.52:8000/fifa` | `X-API-Key` obrigatório |
| GET | `/fifa/count` | `http://177.44.248.52:8000/fifa/count` | Não |
| GET | `/fifa` | `http://177.44.248.52:8000/fifa` | Não |
| GET | `/fifa/id/{id}` | `http://177.44.248.52:8000/fifa/id/1` | Não |
| GET | `/fifa/nat/{exp}` | `http://177.44.248.52:8000/fifa/nat/Brazil` | Não |

- Swagger (interativo): `http://177.44.248.52:8000/docs`
- OpenAPI JSON: `http://177.44.248.52:8000/openapi.json`
- ReDoc: `http://177.44.248.52:8000/redoc`

**Importante:** os links são os endereços esperados, ainda **não verificados externamente**.

## 6. Problemas comuns

| Sintoma | Possível causa e ação |
|---|---|
| `scp: remote setstat ... Permission denied` | Pasta remota pertence a root; corrigir a propriedade da pasta autorizada ou usar `~/fifa_api`. |
| `scp: stat remote: No such file or directory` | Confirmar que o diretório remoto existe e a conta consegue acessá-lo. |
| `ModuleNotFoundError: fastapi` | Ativar `.venv` e executar `python -m pip install -r requirements.txt`. |
| `Address already in use` | A porta 8000 já está ocupada; verificar com `ss -ltnp \| grep :8000`. |
| `Connection refused` de fora | Aplicação não iniciou, caiu ou está ouvindo na interface incorreta. |
| Tempo esgotado de fora | Firewall/regras de rede podem bloquear a porta 8000. Solicite liberação autorizada. |
| `503` no POST | `API_KEY` não está definida no processo do servidor. |
| `401` no POST | Chave não foi enviada ou está incorreta. |

## 7. Checklist de entrega e roteiro

1. **Implementar:** código dos cinco endpoints e importação em lote preparados.
2. **Documentar:** `DOCUMENTACAO_ROTAS.md`, este guia e documentação automática FastAPI.
3. **Disponibilizar documentação:** compartilhar `/docs` **somente após confirmar acesso externo** e informar e-mail de contato do grupo.
4. **Testar:** cadastrar as cinco requisições no Postman/Insomnia, verificar códigos/respostas e testar com o outro grupo.
5. **Publicar na VM:** manter o serviço no ar durante validações e confirmar disponibilidade pela rede externa. Apesar dessa ser a última etapa numerada pelo professor, a API precisa estar acessível na VM no momento exigido pelo cronograma.

**Cronograma do enunciado:** 19h30 início; 20h15 disponibilizar documentação; 20h45 API disponível para GET; 21h15 entrega; 21h16 validações.

Não há confirmação, nas evidências fornecidas, de chave configurada, importação concluída na VM, publicação externa, ou testes feitos por outro grupo.
