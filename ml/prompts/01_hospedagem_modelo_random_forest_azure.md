# Prompt: Hospedar Modelo Random Forest no Azure com Baixo Custo

Você é um engenheiro de ML Ops e backend. Preciso hospedar em nuvem, da forma mais barata possível no Azure, um modelo simples de machine learning gerado no notebook `trabalho2/9_tuning_ga_rf.ipynb`.

O objetivo é expor o modelo via API HTTP/REST para que uma aplicação com LLM livre, como Llama ou outro modelo open source, consiga consultar essa API durante um trabalho acadêmico.

## Contexto do Projeto

- Repositório local: `/workspace`
- Modelo treinado: `trabalho2/artifacts/random_forest.joblib`
- Notebook de origem: `trabalho2/9_tuning_ga_rf.ipynb`
- Tipo do modelo: `RandomForestClassifier`
- Target: `TARGET_CANCER_MAMA_PROVAVEL`
- Número de features: 24
- Formato de entrada: features já codificadas
- Uso: acadêmico, não clínico

Já existem artefatos de Azure ML em:

- `trabalho2/deploy/azureml/score.py`
- `trabalho2/deploy/azureml/sample-request.json`
- `trabalho2/deploy/azureml/conda.yml`
- `trabalho2/deploy/azureml/README_AZURE_ML.md`
- `trabalho2/deploy/azureml/deployment.yml`
- `trabalho2/deploy/azureml/endpoint.yml`

Mas Azure ML Managed Online Endpoint ficou caro demais para este trabalho. Não usar Azure ML para a hospedagem final.

## Estratégia Desejada

Criar uma alternativa barata usando Azure Container Apps em modo consumo, com escala mínima `0`, para pagar pouco ou quase nada quando a API não estiver em uso.

Se houver uma opção ainda mais barata e simples dentro do Azure, como Azure Functions Consumption Plan, pode sugerir, mas priorize Azure Container Apps porque:

- Permite empacotar `scikit-learn`, `pandas` e `joblib` em container sem brigar com limitações de runtime.
- Expõe HTTP publicamente de forma simples.
- Permite escalar para zero.
- É suficiente para uma API acadêmica de baixa demanda.

## Tarefa

Criar na pasta `trabalho3/ml` uma implementação completa e documentada para servir o modelo via API.

Não alterar o notebook original nem retreinar o modelo.

## Arquitetura Esperada

Criar uma API Python simples com FastAPI:

- `GET /health`
  - Retorna status da API e confirmação de que o modelo foi carregado.

- `GET /metadata`
  - Retorna nome do modelo, versão, classe positiva, quantidade de features e lista de features esperadas.

- `POST /predict`
  - Recebe uma instância ou lista de instâncias no mesmo formato aceito pelo `score.py` atual.
  - Retorna predição, probabilidade estimada da classe positiva para o registro enviado, métricas globais do modelo, nome do modelo e versão.
  - A probabilidade estimada por registro não deve ser descrita como acurácia, precisão global do modelo ou probabilidade diagnóstica real.

Formato de request compatível com `trabalho2/deploy/azureml/sample-request.json`:

```json
{
  "features": {
    "CO_TEMPO_MAMO_ANTERIOR_NUM": 0,
    "CO_IDADE_PACIENTE_NUM": 50,
    "SG_SEXO_F": 1,
    "SG_SEXO_I": 0,
    "SG_SEXO_M": 0,
    "CO_RACA_COR_01": 0,
    "CO_RACA_COR_02": 0,
    "CO_RACA_COR_03": 0,
    "CO_RACA_COR_04": 0,
    "CO_RACA_COR_05": 0,
    "TP_RESP_APRES_RISC_ELEV_CANCER_01": 1,
    "TP_RESP_APRES_RISC_ELEV_CANCER_02": 0,
    "TP_RESP_APRES_RISC_ELEV_CANCER_03": 0,
    "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_01": 1,
    "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_02": 0,
    "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_03": 0,
    "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_01": 1,
    "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_02": 0,
    "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_03": 0,
    "CO_IND_CLINICA_01": 1,
    "CO_IND_CLINICA_02": 0,
    "TP_MAMOGRAFIA_RASTREAMENT_01": 1,
    "TP_MAMOGRAFIA_RASTREAMENT_02": 0,
    "TP_MAMOGRAFIA_RASTREAMENT_03": 0
  }
}
```

Resposta esperada:

```json
{
  "model_name": "RandomForestClassifier",
  "model_version": "0.1.0",
  "target_column": "TARGET_CANCER_MAMA_PROVAVEL",
  "positive_class": 1,
  "probability_meaning": "Probabilidade estimada pelo classificador para a classe positiva do alvo TARGET_CANCER_MAMA_PROVAVEL. Nao representa acuracia, precisao do modelo ou probabilidade clinica diagnostica.",
  "model_metrics": {
    "accuracy": 0.760875,
    "recall": 0.424779,
    "f1": 0.13085,
    "precision": 0.077336,
    "roc_auc": 0.628885,
    "balanced_accuracy": 0.600263
  },
  "predictions": [
    {
      "prediction": 0,
      "positive_class_probability": 0.1234,
      "predicted_class_probability": 0.8766,
      "probability": 0.1234,
      "positive_class": 1,
      "model_name": "RandomForestClassifier",
      "model_version": "0.1.0"
    }
  ]
}
```

## Requisitos Técnicos

Criar ou ajustar os seguintes arquivos em `trabalho3/ml`:

- `app/main.py`
  - API FastAPI.
  - Carregamento do modelo `random_forest.joblib`.
  - Validação de schema das 24 features.
  - Respostas de erro claras para feature ausente ou inesperada.

- `app/model_service.py`
  - Lógica isolada para carregar o bundle do modelo e executar inferência.
  - Reaproveitar a lógica existente de `trabalho2/deploy/azureml/score.py` quando fizer sentido.

- `requirements.txt`
  - Dependências mínimas:
    - `fastapi`
    - `uvicorn[standard]`
    - `joblib`
    - `pandas`
    - `scikit-learn`
    - `numpy`

- `Dockerfile`
  - Imagem Python slim.
  - Copiar o código da API e o arquivo `random_forest.joblib`.
  - Expor porta `8000`.
  - Rodar `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

- `.dockerignore`
  - Evitar copiar notebooks, bases grandes, build Flutter, caches e arquivos desnecessários.

- `sample-request.json`
  - Copiar/adaptar o exemplo de `trabalho2/deploy/azureml/sample-request.json`.

- `README.md`
  - Explicar como rodar localmente.
  - Explicar como testar com `curl`.
  - Explicar como fazer deploy barato no Azure Container Apps.
  - Explicar como consultar a API a partir de um LLM.
  - Incluir aviso de uso acadêmico e não diagnóstico.

## Deploy no Azure

Documentar comandos usando Azure CLI para:

1. Login:

```bash
az login
```

2. Definir variáveis:

```bash
RESOURCE_GROUP=rg-siscan-ml-academico
LOCATION=brazilsouth
ACR_NAME=<nome-unico-do-container-registry>
APP_NAME=siscan-rf-api
ENV_NAME=siscan-rf-env
IMAGE_NAME=siscan-rf-api
```

3. Criar resource group:

```bash
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"
```

4. Criar Azure Container Registry básico:

```bash
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true
```

5. Buildar e enviar a imagem:

```bash
az acr build \
  --registry "$ACR_NAME" \
  --image "$IMAGE_NAME:latest" \
  .
```

6. Criar ambiente do Container Apps:

```bash
az containerapp env create \
  --name "$ENV_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION"
```

7. Criar Container App com escala mínima zero:

```bash
az containerapp create \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ENV_NAME" \
  --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest" \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 1 \
  --cpu 0.25 \
  --memory 0.5Gi \
  --registry-server "$ACR_NAME.azurecr.io"
```

8. Obter URL pública:

```bash
az containerapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

9. Testar:

```bash
API_URL=https://<fqdn-retornado>

curl "$API_URL/health"

curl -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  --data @sample-request.json
```

## Segurança e Custo

Para este trabalho acadêmico, manter simples, mas documentar:

- Usar `--min-replicas 0` para reduzir custo quando sem uso.
- Usar `--max-replicas 1` para evitar crescimento inesperado de custo.
- Usar `--cpu 0.25` e `--memory 0.5Gi` inicialmente.
- Remover os recursos após a apresentação se não forem mais necessários.
- O Azure Container Registry Basic tem custo fixo; se o trabalho acabar, excluir também o registry.
- Se precisar reduzir ainda mais custo, avaliar publicar imagem em outro registry gratuito e manter apenas o Container App, se permitido pela disciplina e pelas políticas do ambiente.

Comando para remover tudo:

```bash
az group delete \
  --name "$RESOURCE_GROUP" \
  --yes \
  --no-wait
```

## Critérios de Aceite

- A API roda localmente com Docker.
- `GET /health` retorna sucesso.
- `POST /predict` aceita o payload de exemplo.
- A API retorna JSON compatível com integração por LLM.
- O README contém os comandos de deploy no Azure Container Apps.
- O deploy usa escala mínima zero e limite máximo de uma réplica.
- O projeto deixa claro que o modelo é para uso acadêmico e não deve ser usado para diagnóstico clínico.
