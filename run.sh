#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -z "${API_KEY:-}" ]]; then
  echo "ERRO: defina API_KEY antes de iniciar. Ex.: export API_KEY=uma-chave-forte" >&2
  exit 1
fi
python import_csv.py
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
