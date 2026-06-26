#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

PYTHON_BIN="${PYTHON_BIN:-python}"
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

"$PYTHON_BIN" -m pytest --junitxml=reports/pytest-junit.xml

if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --source . --redact --report-format json --report-path reports/gitleaks.json || true
else
  echo "gitleaks nao encontrado; instale para executar Secret Detection localmente."
fi

if command -v pip-audit >/dev/null 2>&1; then
  pip-audit -r requirements.txt --format json --output reports/pip-audit.json || true
else
  echo "pip-audit nao encontrado; instale com: $PYTHON_BIN -m pip install pip-audit"
fi

if command -v bandit >/dev/null 2>&1; then
  bandit -r app -f json -o reports/bandit.json || true
else
  echo "bandit nao encontrado; instale com: $PYTHON_BIN -m pip install bandit"
fi

if command -v semgrep >/dev/null 2>&1; then
  semgrep scan --config p/python --config p/owasp-top-ten --json --output reports/semgrep.json || true
else
  echo "semgrep nao encontrado; instale com: $PYTHON_BIN -m pip install semgrep"
fi

echo "Relatorios locais salvos em reports/."
