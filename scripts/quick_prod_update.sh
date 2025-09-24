#!/usr/bin/env bash
# One-shot script: rota claves (añade nuevas versiones), asegura permisos y redeploy.
# USO:
#   ./scripts/quick_prod_update.sh "NUEVA_OPENAI_KEY" "NUEVA_JUDGE0_KEY"
# Requiere: gcloud autenticado y proyecto correcto.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Uso: $0 <NUEVA_OPENAI_KEY> <NUEVA_JUDGE0_KEY>" >&2
  exit 1
fi

NEW_OPENAI="$1"
NEW_JUDGE0="$2"

PROJECT_ID="fr-prod-470013"
REGION="us-central1"
SERVICE="fluent-reflect-api"
RUNTIME_SA_ID="fluent-reflect-runtime"
RUNTIME_SA_EMAIL="$RUNTIME_SA_ID@$PROJECT_ID.iam.gserviceaccount.com"
USER_EMAIL="$(gcloud config get-value account)"

step() { echo -e "\n[+] $1"; }

step "Creando service account si no existe"
gcloud iam service-accounts describe "$RUNTIME_SA_EMAIL" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud iam service-accounts create "$RUNTIME_SA_ID" --project "$PROJECT_ID" --display-name="Fluent Reflect Runtime"

step "Dando permiso actAs a $USER_EMAIL (iam.serviceAccountUser)"
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA_EMAIL" \
  --project "$PROJECT_ID" \
  --member "user:$USER_EMAIL" \
  --role roles/iam.serviceAccountUser >/dev/null 2>&1 || true

step "Asegurando que los secretos existen"
for S in OPENAI_API_KEY JUDGE0_API_KEY; do
  gcloud secrets describe "$S" --project "$PROJECT_ID" >/dev/null 2>&1 || \
    gcloud secrets create "$S" --project "$PROJECT_ID" --replication-policy=automatic
done

step "Añadiendo nuevas versiones (rotación)"
printf "%s" "$NEW_OPENAI" | gcloud secrets versions add OPENAI_API_KEY --project "$PROJECT_ID" --data-file=-
printf "%s" "$NEW_JUDGE0" | gcloud secrets versions add JUDGE0_API_KEY --project "$PROJECT_ID" --data-file=-

step "Concediendo secretAccessor al runtime SA"
for S in OPENAI_API_KEY JUDGE0_API_KEY; do
  gcloud secrets add-iam-policy-binding "$S" \
    --project "$PROJECT_ID" \
    --member "serviceAccount:$RUNTIME_SA_EMAIL" \
    --role roles/secretmanager.secretAccessor >/dev/null 2>&1 || true
done

step "Actualizando servicio Cloud Run (inyecta secretos + SA)"
gcloud run services update "$SERVICE" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --service-account "$RUNTIME_SA_EMAIL" \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest,JUDGE0_API_KEY=JUDGE0_API_KEY:latest"

URL=$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')

step "Health check autenticado"
TOKEN=$(gcloud auth print-identity-token)
HTTP=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "$URL/health")
echo "Health /health => $HTTP"

if [[ "$HTTP" != "200" ]]; then
  echo "[!] Health no devolvió 200. Revisa logs: gcloud logs tail --project $PROJECT_ID --region $REGION --service $SERVICE" >&2
  exit 2
fi

step "Listo. URL servicio: $URL"
