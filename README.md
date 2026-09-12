# Projeto de Pos-Graduacao FIAP IA para Devs - Trabalho 3

Este diretorio contem a terceira etapa do trabalho desenvolvido para a Pos-Graduacao da FIAP em IA para Devs. A entrega evolui o projeto das fases anteriores para uma aplicacao local integrada, combinando modelo preditivo supervisionado, assistente com LLM local, fine-tuning com MLX e frontend Flutter Web.

O objetivo e disponibilizar um fluxo academico no qual um profissional informa um caso clinico em linguagem natural, o assistente interpreta a mensagem, aciona o modelo preditivo quando aplicavel, consulta a API de inferencia e devolve uma resposta em portugues do Brasil com explicacao do resultado.

Por se tratar de um contexto de saude, o sistema tem finalidade exclusivamente academica. Ele nao produz diagnostico medico, nao recomenda conduta clinica definitiva e nao substitui avaliacao profissional.

## Contexto Geral

O projeto parte dos artefatos gerados no `trabalho2`, principalmente o modelo `RandomForestClassifier` treinado com dados publicos do DATASUS/SISCAN sobre exames de mamografia.

Na Fase 3, esse modelo e exposto por uma API local e passa a ser consumido por um assistente de IA. O usuario final interage por uma aplicacao Flutter Web, sem precisar informar JSON tecnico. A propria camada de IA extrai os dados clinicos, monta a estrutura necessaria para o modelo preditivo e interpreta o retorno.

## Arquitetura

Fluxo principal:

```text
Flutter Web -> Assistant API -> LLM local com fine-tuning -> Extracao de dados -> ML API -> Interpretacao -> Flutter Web
```

Componentes:

- `fe/`: aplicacao Flutter Web de chat academico;
- `assistant/`: API FastAPI com fluxo LangGraph, LLM local, extracao de dados e interpretacao;
- `ml/`: API FastAPI que serve o modelo `RandomForestClassifier`;
- `fine-tuning/`: scripts e dados para preparar dataset e treinar adapter LoRA com MLX;
- `docker-compose.yml`: sobe frontend e API de ML em containers;
- `start_local.sh`: sobe Docker Compose, inicia o assistant local e abre o frontend;
- `fine_tuning.sh`: executa o fine-tuning local;
- `run_all.sh`: executa fine-tuning e depois inicia a aplicacao.

## Estrutura

```text
trabalho3/
  assistant/
    app/
    run_local.py
  fe/
    lib/
    web/
    Dockerfile
    nginx.conf
  fine-tuning/
    data/
    1_preparar_dataset.py
    2_treinar_modelo.py
  ml/
    app/
    model/
    Dockerfile
  docker-compose.yml
  fine_tuning.sh
  requirements.txt
  run_all.sh
  start_local.sh
```

## Pre-requisitos

Para executar localmente no Mac:

- macOS com Apple Silicon recomendado para MLX;
- Python 3;
- Docker Desktop com Docker Compose;
- Flutter, apenas se for executar o frontend fora do Docker;
- acesso local ao modelo `mlx-community/Llama-3.2-3B-Instruct-4bit` ou snapshot ja baixado;
- dependencias Python instaladas automaticamente pelos scripts em `trabalho3/.venv`.

## Como Executar a Aplicacao

Execute a partir da raiz do `trabalho3`:

```bash
./start_local.sh
```

Esse script:

1. executa `docker compose up --build -d`;
2. sobe a API de ML em `http://localhost:8000`;
3. sobe o frontend em `http://localhost:8080`;
4. cria ou reutiliza `trabalho3/.venv`;
5. inicia o assistant local em `http://localhost:8010`;
6. abre o navegador na aplicacao Flutter Web.

Endpoints principais:

- frontend: `http://localhost:8080`;
- assistant: `http://localhost:8010/health`;
- modelo preditivo: `http://localhost:8000/health`;
- metadados do modelo: `http://localhost:8000/metadata`.

Para encerrar, pressione `Ctrl+C` no terminal em que o script esta rodando. O script tambem executa `docker compose down`.

## Fine-tuning

Para executar apenas o fine-tuning:

```bash
./fine_tuning.sh
```

O script:

1. cria `trabalho3/.venv` se necessario;
2. instala as dependencias de `requirements.txt`;
3. prepara os arquivos JSONL a partir de `fine-tuning/data/ori_pqal.json`;
4. executa o treinamento com `mlx_lm.lora`;
5. salva o adapter em `fine-tuning/adapters/llama3_2_3b_pubmedqa`.

Para executar o fine-tuning e, em seguida, iniciar a aplicacao:

```bash
./run_all.sh
```

## Docker

O Docker Compose da raiz sobe dois servicos:

- `ml`: API FastAPI com o modelo Random Forest;
- `fe`: frontend Flutter Web servido por Nginx.

Comando manual:

```bash
docker compose up --build -d
```

Para parar:

```bash
docker compose down
```

O assistant nao roda no Docker neste fluxo porque utiliza MLX local e o adapter de fine-tuning no ambiente do Mac.

## Modelo Preditivo

A API em `ml/` carrega o arquivo:

```text
ml/model/random_forest.joblib
```

O modelo recebe 24 features codificadas, valida o schema e retorna a classe prevista com probabilidade associada. A chamada direta pode ser testada com:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metadata
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" --data @ml/sample-request.json
```

No uso normal da aplicacao, o medico nao precisa fornecer JSON. O assistant interpreta o texto clinico e monta a estrutura de entrada do modelo.

## Assistant

O assistant e uma API FastAPI que organiza o fluxo de IA:

1. recebe a mensagem do chat;
2. decide se o modelo preditivo deve ser consultado;
3. extrai dados clinicos em formato estruturado;
4. converte esses dados para as features esperadas pelo Random Forest;
5. chama a API de ML;
6. interpreta o resultado em linguagem natural;
7. retorna resposta em portugues do Brasil com aviso academico.

As principais variaveis de ambiente sao configuradas em `start_local.sh`, incluindo:

- `LLM_PROVIDER=mlx`;
- `ML_API_URL=http://localhost:8000`;
- `MLX_MODEL=mlx-community/Llama-3.2-3B-Instruct-4bit`;
- `MLX_ADAPTER_PATH=adapters/llama3_2_3b_pubmedqa`;
- `EXTRACT_FEATURES_WITH_LLM=true`;
- `TRANSLATE_TO_PTBR=true`.

Arquivos Python principais:

- `assistant/run_local.py`: inicializa a API do assistant localmente na porta `8010`;
- `assistant/app/main.py`: define a aplicacao FastAPI, configura CORS, expoe `/health` e recebe mensagens em `POST /chat/messages`;
- `assistant/app/config.py`: centraliza as configuracoes de ambiente, como URL da API de ML, provedor LLM, modelo MLX, adapter, timeouts e traducao;
- `assistant/app/graph.py`: implementa o fluxo principal com LangGraph, decidindo quando consultar o modelo preditivo, chamando a LLM, extraindo dados, acionando a API de ML e montando a resposta final;
- `assistant/app/tools.py`: contem a ferramenta de chamada ao modelo preditivo, a conversao de dados clinicos para features tecnicas e extratores auxiliares;
- `assistant/app/schemas.py`: define os contratos Pydantic de entrada e saida do endpoint de chat;
- `assistant/app/safety.py`: mantem o aviso academico usado nas respostas do assistente;
- `assistant/app/audit.py`: registra a trilha de auditoria local com mensagem, decisao de uso do modelo, features, resultado do ML, fontes e erros.

## Frontend

O frontend em Flutter Web oferece uma tela de chat para interacao com o assistente.

Caracteristicas:

- rota unica `/`;
- consumo do endpoint `POST /chat/messages`;
- respostas copiaveis;
- timeout ampliado para chamadas longas;
- URL da API configurada por `API_BASE_URL`;
- build Docker com Nginx.

Para rodar somente o frontend em Docker:

```bash
cd fe
docker build -t medical-ai-chat-fe .
docker run -p 8080:80 medical-ai-chat-fe
```

## Dados e Artefatos

Principais artefatos:

- `ml/model/random_forest.joblib`: modelo supervisionado treinado no `trabalho2`;
- `fine-tuning/data/ori_pqal.json`: base usada para preparar o dataset de fine-tuning;
- `fine-tuning/data/*.jsonl`: arquivos gerados para treino e validacao;
- `fine-tuning/adapters/`: adapters LoRA gerados pelo MLX;
- `logs/`: logs locais de execucao;
- `assistant/logs/audit.jsonl`: trilha de auditoria das chamadas do assistant.

Arquivos gerados como `.venv`, `adapters/`, `outputs/`, logs e JSONL de treino ficam fora do versionamento pelo `.gitignore`.

## Observacoes

- O modelo preditivo e um apoio estatistico academico, nao um diagnostico.
- A resposta final deve sempre estar em portugues do Brasil.
- O medico informa o caso em texto livre; o JSON tecnico e montado internamente.
- A chamada ao modelo preditivo deve aparecer interpretada na resposta quando for aplicavel.
- O frontend e a API de ML rodam em Docker; o assistant roda localmente para acessar MLX no Mac.
- O uso de Ollama foi deixado como alternativa futura, mas o fluxo principal local usa MLX.
