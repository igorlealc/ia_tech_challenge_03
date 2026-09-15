# Projeto de Pós-Graduação FIAP IA para Devs - Trabalho 3

Este diretório contém a terceira etapa do trabalho desenvolvido para a Pós-Graduação da FIAP em IA para Devs. A entrega evolui o projeto das fases anteriores para uma aplicação local integrada, combinando modelo preditivo supervisionado, assistente com LLM local, fine-tuning com MLX e frontend Flutter Web.

O objetivo é disponibilizar um fluxo acadêmico no qual um profissional informa um caso clínico em linguagem natural, o assistente interpreta a mensagem, aciona o modelo preditivo quando aplicável, consulta a API de inferência e devolve uma resposta em português do Brasil com explicação do resultado.

Por se tratar de um contexto de saúde, o sistema tem finalidade exclusivamente acadêmica. Ele não produz diagnóstico médico, não recomenda conduta clínica definitiva e não substitui avaliação profissional.

## Contexto Geral

O projeto parte dos artefatos gerados no `trabalho2`, principalmente o modelo `RandomForestClassifier` treinado com dados públicos do DATASUS/SISCAN sobre exames de mamografia.

Na Fase 3, esse modelo é exposto por uma API local e passa a ser consumido por um assistente de IA. O usuário final interage por uma aplicação Flutter Web, sem precisar informar JSON técnico. A própria camada de IA extrai os dados clínicos, monta a estrutura necessária para o modelo preditivo e interpreta o retorno.

## Arquitetura

Fluxo principal:

```text
Flutter Web -> Assistant API -> LLM local com fine-tuning -> Extração de dados -> ML API -> Interpretação -> Flutter Web
```

Componentes:

- `fe/`: aplicação Flutter Web de chat acadêmico;
- `assistant/`: API FastAPI com fluxo LangGraph, LLM local, extração de dados e interpretação;
- `ml/`: API FastAPI que serve o modelo `RandomForestClassifier`;
- `fine-tuning/`: scripts e dados para preparar dataset e treinar adapter LoRA com MLX;
- `docker-compose.yml`: sobe frontend e API de ML em containers;
- `start_local.sh`: sobe Docker Compose, inicia o assistant local e abre o frontend;
- `fine_tuning.sh`: executa o fine-tuning local;
- `run_all.sh`: executa o fine-tuning e depois inicia a aplicação.

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

## Pré-requisitos

Para executar localmente no Mac:

- macOS com Apple Silicon recomendado para MLX;
- Python 3;
- Docker Desktop com Docker Compose;
- Flutter, apenas se for executar o frontend fora do Docker;
- acesso local ao modelo `mlx-community/Llama-3.2-3B-Instruct-4bit` ou snapshot já baixado;
- dependências Python instaladas automaticamente pelos scripts em `trabalho3/.venv`.

## Primeira Execução

Na primeira execução, recomenda-se rodar o fluxo completo a partir da raiz do `trabalho3`:

```bash
./run_all.sh
```

Esse comando executa o fine-tuning e, após a conclusão do treinamento, inicializa a aplicação local.

O processo realiza as seguintes etapas:

1. cria o ambiente virtual Python em `trabalho3/.venv`, caso ele ainda não exista;
2. instala as dependências de `requirements.txt`;
3. prepara os arquivos de treino e validação em `fine-tuning/data/`;
4. executa o treinamento do adapter LoRA com MLX;
5. salva o adapter em `fine-tuning/adapters/llama3_2_3b_pubmedqa`;
6. realiza o build das imagens Docker do frontend e da API de ML;
7. sobe a API de ML em `http://localhost:8000`;
8. sobe o frontend em `http://localhost:8080`;
9. inicia o assistant local em `http://localhost:8010`;
10. abre o navegador na aplicação Flutter Web.

Caso o adapter já tenha sido treinado anteriormente, é possível iniciar apenas a aplicação com `./start_local.sh`.

## Como Executar a Aplicação

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
6. abre o navegador na aplicação Flutter Web.

Endpoints principais:

- frontend: `http://localhost:8080`;
- assistant: `http://localhost:8010/health`;
- modelo preditivo: `http://localhost:8000/health`;
- metadados do modelo: `http://localhost:8000/metadata`.

Para encerrar, pressione `Ctrl+C` no terminal em que o script está rodando. O script também executa `docker compose down`.

## Fine-tuning

Para executar apenas o fine-tuning:

```bash
./fine_tuning.sh
```

O script:

1. cria `trabalho3/.venv`, se necessário;
2. instala as dependências de `requirements.txt`;
3. prepara os arquivos JSONL a partir de `fine-tuning/data/ori_pqal.json`;
4. executa o treinamento com `mlx_lm.lora`;
5. salva o adapter em `fine-tuning/adapters/llama3_2_3b_pubmedqa`.

Para executar o fine-tuning e, em seguida, iniciar a aplicação:

```bash
./run_all.sh
```

## Docker

O Docker Compose da raiz sobe dois serviços:

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

O assistant não roda no Docker neste fluxo porque utiliza MLX local e o adapter de fine-tuning no ambiente do Mac.

## Modelo Preditivo

A API em `ml/` carrega o arquivo:

```text
ml/model/random_forest.joblib
```

O modelo recebe 24 features codificadas, valida o schema e retorna a classe prevista com a probabilidade estimada da classe positiva para o registro enviado. Essa probabilidade é a saída de `predict_proba` do classificador; ela não representa acurácia, precisão global do modelo ou probabilidade diagnóstica real. As métricas globais do modelo são retornadas separadamente em `model_metrics`. A chamada direta pode ser testada com:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metadata
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" --data @ml/sample-request.json
```

No uso normal da aplicação, o médico não precisa fornecer JSON. O assistant interpreta o texto clínico e monta a estrutura de entrada do modelo.

## Assistant

O assistant é uma API FastAPI que organiza o fluxo de IA:

1. recebe a mensagem do chat;
2. decide se o modelo preditivo deve ser consultado;
3. extrai dados clínicos em formato estruturado;
4. converte esses dados para as features esperadas pelo Random Forest;
5. chama a API de ML;
6. interpreta o resultado em linguagem natural;
7. retorna resposta em português do Brasil com aviso acadêmico.

As principais variáveis de ambiente são configuradas em `start_local.sh`, incluindo:

- `LLM_PROVIDER=mlx`;
- `ML_API_URL=http://localhost:8000`;
- `MLX_MODEL=mlx-community/Llama-3.2-3B-Instruct-4bit`;
- `MLX_ADAPTER_PATH=adapters/llama3_2_3b_pubmedqa`;
- `EXTRACT_FEATURES_WITH_LLM=true`;
- `TRANSLATE_TO_PTBR=true`.

Arquivos Python principais:

- `assistant/run_local.py`: inicializa a API do assistant localmente na porta `8010`;
- `assistant/app/main.py`: define a aplicação FastAPI, configura CORS, expõe `/health` e recebe mensagens em `POST /chat/messages`;
- `assistant/app/config.py`: centraliza as configurações de ambiente, como URL da API de ML, provedor LLM, modelo MLX, adapter, timeouts e tradução;
- `assistant/app/graph.py`: implementa o fluxo principal com LangGraph, decidindo quando consultar o modelo preditivo, chamando a LLM, extraindo dados, acionando a API de ML e montando a resposta final;
- `assistant/app/tools.py`: contém a ferramenta de chamada ao modelo preditivo, a conversão de dados clínicos para features técnicas e extratores auxiliares;
- `assistant/app/schemas.py`: define os contratos Pydantic de entrada e saída do endpoint de chat;
- `assistant/app/safety.py`: mantém o aviso acadêmico usado nas respostas do assistente;
- `assistant/app/audit.py`: registra a trilha de auditoria local com mensagem, decisão de uso do modelo, features, resultado do ML, fontes e erros.

## Frontend

O frontend em Flutter Web oferece uma tela de chat para interação com o assistente.

Características:

- rota única `/`;
- consumo do endpoint `POST /chat/messages`;
- respostas copiáveis;
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
- `fine-tuning/data/*.jsonl`: arquivos gerados para treino e validação;
- `fine-tuning/adapters/`: adapters LoRA gerados pelo MLX;
- `logs/`: logs locais de execução;
- `assistant/logs/audit.jsonl`: trilha de auditoria das chamadas do assistant.

Arquivos gerados como `.venv`, `adapters/`, `outputs/`, logs e JSONL de treino ficam fora do versionamento pelo `.gitignore`.

## Observações

- O modelo preditivo é um apoio estatístico acadêmico, não um diagnóstico.
- A resposta final deve sempre estar em português do Brasil.
- O médico informa o caso em texto livre; o JSON técnico é montado internamente.
- A chamada ao modelo preditivo deve aparecer interpretada na resposta quando for aplicável.
- O frontend e a API de ML rodam em Docker; o assistant roda localmente para acessar MLX no Mac.
- O uso de Ollama foi deixado como alternativa futura, mas o fluxo principal local usa MLX.
