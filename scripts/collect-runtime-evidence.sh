#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:-all}"
namespace="${K8S_NAMESPACE:-default}"
case "$mode" in
  backend|frontend|all) ;;
  *) echo 'Usage: bash scripts/collect-runtime-evidence.sh [backend|frontend|all]' >&2; exit 1 ;;
esac
out="PROOF/Runtime/$mode"
mkdir -p "$out"
# Remove old success summaries before verifying the current deployment.
rm -f "$out/checks.json" "$out/ENDPOINTS.md" "$out/run-metadata.txt"
backend_url=$(bash scripts/load-balancer-url.sh backend)
kubectl -n "$namespace" rollout status deployment/backend --timeout=300s
args=(--backend "$backend_url" --output "$out")
if [[ "$mode" != backend ]]; then
  kubectl -n "$namespace" rollout status deployment/frontend --timeout=300s
  frontend_url=$(bash scripts/load-balancer-url.sh frontend)
  if [[ -n "${EXPECTED_BACKEND_URL:-}" && "$backend_url" != "$EXPECTED_BACKEND_URL" ]]; then
    echo 'Backend address changed after the frontend build. Rerun Frontend CD.' >&2
    exit 1
  fi
  args+=(--frontend "$frontend_url")
fi
if [[ -n "${EXPECTED_IMAGE:-}" && "$mode" != all ]]; then
  actual_image=$(kubectl -n "$namespace" get deployment "$mode" -o "jsonpath={.spec.template.spec.containers[?(@.name=='$mode')].image}")
  if [[ "$actual_image" != "$EXPECTED_IMAGE" ]]; then
    echo "Deployment image does not match the commit image: $actual_image" >&2
    exit 1
  fi
fi
kubectl -n "$namespace" get deployments,pods,services -o wide > "$out/kubernetes.txt"
kubectl -n "$namespace" get deployments backend -o json > "$out/backend-deployment.json"
if [[ "$mode" != backend ]]; then
  kubectl -n "$namespace" get deployments frontend -o json > "$out/frontend-deployment.json"
fi
python3 scripts/verify-runtime.py "${args[@]}"
{
  printf 'Captured at UTC: %s\n' "$(date -u +%FT%TZ)"
  printf 'Repository commit: %s\n' "${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || printf 'unavailable: not a git checkout')}"
  if [[ -n "${GITHUB_RUN_ID:-}" ]]; then
    printf 'Actions run: %s/%s/actions/runs/%s\n' "$GITHUB_SERVER_URL" "$GITHUB_REPOSITORY" "$GITHUB_RUN_ID"
  fi
} > "$out/run-metadata.txt"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  cat "$out/ENDPOINTS.md" >> "$GITHUB_STEP_SUMMARY"
fi
if [[ "$mode" == all ]]; then
  python3 - <<'PY'
from pathlib import Path
readme = Path('README.md')
text = readme.read_text()
start, end = '<!-- AWS_RUNTIME_START -->', '<!-- AWS_RUNTIME_END -->'
if start not in text or end not in text:
    raise SystemExit('README runtime markers are missing; copy PROOF/Runtime/all/ENDPOINTS.md into README manually.')
before, rest = text.split(start, 1)
_, after = rest.split(end, 1)
evidence = Path('PROOF/Runtime/all/ENDPOINTS.md').read_text()
readme.write_text(before + start + '\n' + evidence + end + after)
PY
  echo 'Updated README.md with the measured AWS URLs. Add browser screenshots before committing.'
fi
