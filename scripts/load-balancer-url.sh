#!/usr/bin/env bash
# Print only the discovered URL to stdout; diagnostics go to stderr.
set -euo pipefail
service="${1:?Usage: bash scripts/load-balancer-url.sh backend|frontend}"
namespace="${K8S_NAMESPACE:-default}"
case "$service" in
  backend|frontend) ;;
  *) echo 'Expected service backend or frontend.' >&2; exit 1 ;;
esac

service_type=$(kubectl -n "$namespace" get service "$service" -o jsonpath='{.spec.type}')
if [[ "$service_type" != LoadBalancer ]]; then
  echo "Service $service must exist and have type LoadBalancer. Deploy backend first on a new cluster." >&2
  exit 1
fi
for attempt in {1..60}; do
  hostname=$(kubectl -n "$namespace" get service "$service" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
  if [[ "$hostname" =~ ^[a-zA-Z0-9.-]+\.elb\.(amazonaws\.com|[a-z0-9-]+\.amazonaws\.com)$ ]]; then
    printf 'http://%s\n' "$hostname"
    exit 0
  fi
  if [[ -n "$hostname" ]]; then
    echo "Service $service did not return a supported AWS ELB hostname: $hostname" >&2
    exit 1
  fi
  echo "Waiting for the $service AWS LoadBalancer address ($attempt/60)..." >&2
  sleep 5
done
echo "Timed out waiting for $service. Inspect kubectl describe service $service." >&2
exit 1
