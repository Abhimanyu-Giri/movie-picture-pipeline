# Evidence still required before resubmission

No AWS runtime evidence was generated during this repair. Do not submit this document as deployment proof.

Preserve your existing `Action Proof/` screenshots from GitHub; they were not included in the uploaded ZIP. Add these files after the repaired deployment actually succeeds:

| Suggested filename/location | What it must show |
| --- | --- |
| `Action Proof/backend-cd.png` | Backend CD name, successful lint/test/build/deploy jobs and run/commit identity |
| `Action Proof/frontend-cd.png` | Frontend CD name, successful lint/test/build/deploy jobs and run/commit identity |
| `Action Proof/backend-verification.png` | Green `Verify Kubernetes deployment` and `Verify Backend ECR image` steps with their output |
| `Action Proof/frontend-verification.png` | Green `Verify Kubernetes deployment` and `Verify Frontend ECR image` steps with their output |
| `Runtime/backend-browser.png` | Backend ELB `/movies` in the browser address bar and returned movie JSON |
| `Runtime/frontend-browser.png` | Frontend ELB in the address bar with the actual movie list rendered |
| `Runtime/frontend-network.png` | Browser Network tab: `/movies` request to backend ELB, HTTP 200 and response |
| `Runtime/kubernetes.png` | Ready pods, deployments, both LoadBalancer addresses and image tags |
| `Runtime/all/` | Output of `bash scripts/collect-runtime-evidence.sh all` |

Download the runtime artifacts from both successful CD runs as supporting evidence. The scripts save actual HTTP responses, timestamps and Kubernetes manifests; browser interaction still needs screenshots. Avoid screenshots of AWS credentials, tokens or GitHub Secrets values.

The browser address bars must contain the actual `http://...amazonaws.com` LoadBalancer addresses. Do not submit `localhost`, a Udacity workspace preview URL, or any `YOUR_...` placeholder.
