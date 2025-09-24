#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup_secrets.sh <PROJECT_ID> <OPENAI_KEY> <JUDGE0_KEY>
# Creates (or reuses) secrets and adds new versions with provided values.
# Grants accessor role to the current Cloud Run runtime service account.

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <PROJECT_ID> <OPENAI_KEY> <JUDGE0_KEY>" >&2
  exit 1
fi

PROJECT_ID="$1"
OPENAI_VALUE="$2"
JUDGE0_VALUE="$3"

RUNTIME_SA="581268440769-compute@developer.gserviceaccount.com"  # existing default compute SA

create_secret_if_absent() {
  local name="$1"
  if ! gcloud secrets describe "$name" --project "$PROJECT_ID" >/dev/null 2>&1; then
    echo "[+] Creating secret $name"
    gcloud secrets create "$name" --project "$PROJECT_ID" --replication-policy=automatic
  else
    echo "[=] Secret $name already exists"
  fi
}

add_version() {
  local name="$1"
  local value="$2"
  if [[ -z "$value" ]]; then
    echo "[!] Skipping $name because provided value is empty" >&2
    return 1
  fi
  # Use printf -n to avoid trailing newline
  printf "%s" "$value" | gcloud secrets versions add "$name" --project "$PROJECT_ID" --data-file=-
}

grant_accessor() {
  local name="$1"
  echo "[+] Granting accessor on $name to $RUNTIME_SA"
  gcloud secrets add-iam-policy-binding "$name" \
    --project "$PROJECT_ID" \
    --member "serviceAccount:$RUNTIME_SA" \
    --role roles/secretmanager.secretAccessor >/dev/null
}

main() {
  echo "== Secret setup start =="
  create_secret_if_absent OPENAI_API_KEY
  create_secret_if_absent JUDGE0_API_KEY

  echo "[+] Adding new versions"
  add_version OPENAI_API_KEY "$OPENAI_VALUE"
  add_version JUDGE0_API_KEY "$JUDGE0_VALUE"

  grant_accessor OPENAI_API_KEY
  grant_accessor JUDGE0_API_KEY

  echo "[+] Done. Now update Cloud Run service (if not already) with:"
  cat <<EOF
  gcloud run services update fluent-reflect-api \
    --project $PROJECT_ID \
    --region us-central1 \
    --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-secrets JUDGE0_API_KEY=JUDGE0_API_KEY:latest
EOF
  echo "== Secret setup complete =="
}

main "$@"
