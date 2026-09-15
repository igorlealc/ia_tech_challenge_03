# SISCAN Random Forest API

API FastAPI para servir o modelo `RandomForestClassifier` gerado em `trabalho2/9_tuning_ga_rf.ipynb`.

Esta API foi pensada para uso academico e para integracao com um LLM livre, como Llama, que pode chamar o endpoint `/predict` via HTTP. O modelo nao deve ser usado como diagnostico clinico.

## Estrutura

- `app/main.py`: endpoints HTTP.
- `app/model_service.py`: carregamento do modelo, validacao de schema e inferencia.
- `model/random_forest.joblib`: bundle do modelo treinado.
- `sample-request.json`: payload de exemplo com as 24 features codificadas.
- `Dockerfile`: imagem para execucao local ou Azure Container Apps.

## Rodar Localmente

Com ambiente Python:

```bash
cd trabalho3/ml
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Com Docker:

```bash
cd trabalho3/ml
docker build -t siscan-rf-api .
docker run --rm -p 8000:8000 siscan-rf-api
```

## Testar

```bash
curl http://localhost:8000/health

curl http://localhost:8000/metadata

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  --data @sample-request.json
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

O campo `positive_class_probability` é calculado com `predict_proba` para o registro enviado. Ele não deve ser confundido com as métricas globais do modelo, como `accuracy`, `precision`, `recall` ou `f1`, que aparecem em `model_metrics`.

## Deploy Barato no Azure

Use Azure Container Apps em modo consumo com escala minima zero. Esta opcao evita o custo alto de Azure ML Managed Online Endpoint para um trabalho academico de baixa demanda.

Pre-requisitos:

- Azure CLI instalada.
- Login com `az login`.
- Extensao `containerapp` instalada, se a CLI solicitar.
- Docker nao e obrigatorio quando usar `az acr build`, pois o build ocorre no Azure Container Registry.

Defina as variaveis:

```bash
RESOURCE_GROUP=rg-siscan-ml-academico
LOCATION=brazilsouth
ACR_NAME=<nome-unico-do-container-registry>
APP_NAME=siscan-rf-api
ENV_NAME=siscan-rf-env
IMAGE_NAME=siscan-rf-api
```

Crie o resource group:

```bash
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"
```

Crie o Azure Container Registry Basic:

```bash
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true
```

Build e push da imagem:

```bash
cd trabalho3/ml

az acr build \
  --registry "$ACR_NAME" \
  --image "$IMAGE_NAME:latest" \
  .
```

Crie o ambiente do Container Apps:

```bash
az containerapp env create \
  --name "$ENV_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION"
```

Obtenha as credenciais do registry:

```bash
ACR_USERNAME=$(az acr credential show \
  --name "$ACR_NAME" \
  --query username \
  --output tsv)

ACR_PASSWORD=$(az acr credential show \
  --name "$ACR_NAME" \
  --query "passwords[0].value" \
  --output tsv)
```

Crie o Container App com custo controlado:

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
  --registry-server "$ACR_NAME.azurecr.io" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD"
```

Obtenha a URL publica:

```bash
API_FQDN=$(az containerapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

API_URL="https://$API_FQDN"
echo "$API_URL"
```

Teste a API publicada:

```bash
curl "$API_URL/health"

curl -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  --data @sample-request.json
```

## Integracao com LLM

O LLM deve chamar a API somente quando precisar obter a predicao do modelo estruturado. A chamada HTTP deve enviar JSON para `/predict` com as 24 features ja codificadas.

Exemplo de instrucao para o agente LLM:

```text
Quando precisar estimar a classe TARGET_CANCER_MAMA_PROVAVEL, chame a API POST /predict.
Envie as features no formato JSON esperado e use a resposta apenas como apoio academico.
Nao apresente o resultado como diagnostico clinico.
```

## Controle de Custo

- `--min-replicas 0` reduz custo quando sem chamadas.
- `--max-replicas 1` evita crescimento inesperado.
- `--cpu 0.25` e `--memory 0.5Gi` sao suficientes para iniciar uma API pequena.
- O Azure Container Registry Basic tem custo fixo enquanto existir.
- Exclua os recursos depois da apresentacao se nao forem mais necessarios.

Remover tudo:

```bash
az group delete \
  --name "$RESOURCE_GROUP" \
  --yes \
  --no-wait
```
