#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "=== Mi Mercado Global — Startup ==="
echo ""

# ── 1. Contenedores ──────────────────────────────────────────────────────────
echo "[1/5] Levantando Docker..."
docker compose -f "$ROOT/docker-compose.localstack.yml" up -d

# ── 2. Esperar a que LocalStack esté listo ───────────────────────────────────
echo "[2/5] Esperando LocalStack..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"dynamodb": "available"'; do
  sleep 2
done
echo "      LocalStack listo."

# ── 3. CDK deploy ────────────────────────────────────────────────────────────
echo "[3/5] Desplegando infraestructura (CDK)..."
cd "$ROOT/cdk"
cdklocal deploy --require-approval never --outputs-file /dev/null 2>&1 | tail -5

# ── 4. Insertar datos ─────────────────────────────────────────────────────────
echo "[4/5] Insertando datos..."
cd "$ROOT/mi-mercado-global-back"
DYNAMODB_ENDPOINT=http://localhost:4566 python insertar_datos.py
DYNAMODB_ENDPOINT=http://localhost:4566 python insertar_mas_datos.py
DYNAMODB_ENDPOINT=http://localhost:4566 python insertar_productos.py

# ── 5. GSI_2 (por si CDK no lo creó) ────────────────────────────────────────
echo "[5/5] Verificando GSI_2..."
GSI=$(aws dynamodb describe-table \
  --table-name MiMercadoGlobal \
  --endpoint-url http://localhost:4566 \
  --query "Table.GlobalSecondaryIndexes[?IndexName=='GSI_2'].IndexName" \
  --output text 2>/dev/null)

if [ -z "$GSI" ]; then
  echo "      GSI_2 no encontrado, creando..."
  aws dynamodb update-table \
    --table-name MiMercadoGlobal \
    --endpoint-url http://localhost:4566 \
    --attribute-definitions \
      AttributeName=Categoria,AttributeType=S \
      AttributeName=Nombre,AttributeType=S \
    --global-secondary-index-updates '[{
      "Create": {
        "IndexName": "GSI_2",
        "KeySchema": [
          {"AttributeName":"Categoria","KeyType":"HASH"},
          {"AttributeName":"Nombre","KeyType":"RANGE"}
        ],
        "Projection": {"ProjectionType":"ALL"},
        "ProvisionedThroughput": {"ReadCapacityUnits":5,"WriteCapacityUnits":5}
      }
    }]' > /dev/null
  echo "      GSI_2 creado."
else
  echo "      GSI_2 OK."
fi

# ── Listo ─────────────────────────────────────────────────────────────────────
echo ""
echo "=== Todo listo ==="
echo ""
echo "  Frontend:  cd mi-mercado-global-front && npm run dev"
echo "  API:       http://localhost:4566 (via proxy Vite en localhost:5173)"
echo ""
