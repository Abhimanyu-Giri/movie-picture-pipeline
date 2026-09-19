# Finish the Movie Picture Pipeline CD resubmission

Repository: https://github.com/Abhimanyu-Giri/movie-picture-pipeline

## Current status

The reviewer passed both CI specifications. Frontend CD and Backend CD still need a successful AWS deployment and runtime evidence. This package repairs the source supplied in your ZIP. It has not been pushed to GitHub or deployed to AWS. It is not yet a complete resubmission.

The uploaded ZIP differs from the submission described in the feedback: it has no `PROOF/Action Proof/` directory, no repository link in the original README, and an incomplete Backend CD file. Preserve your newer GitHub README and existing screenshots when applying these changes.

## 1. Resolve the exhausted AWS credits

Ask Udacity Support or your Accenture training coordinator for a lab-credit extension/reactivation, or written approval for another way to demonstrate CD. A credit increase is a request, not guaranteed. The reviewer specifically asked for AWS runtime evidence; local Docker, a Udacity workspace URL, or green CI alone does not demonstrate that requirement.

Support form: https://support.udacity.com/hc/en-us/requests/new

Suggested ticket text:

> Subject: AWS lab credits exhausted — Movie Picture Pipeline CD resubmission
>
> I am completing the DevOps for ATCI Movie Picture Pipeline project. My latest review passed both CI specifications and requested changes to Frontend CD and Backend CD, including deployment to AWS and screenshots of the actual LoadBalancer URLs. My Udacity AWS lab credits are exhausted, so I cannot complete the remaining runtime verification. Could you extend/reactivate my lab budget, or confirm an approved alternative for demonstrating these two CD specifications? I can attach the reviewer feedback and a screenshot of the credit-limit message. Repository: https://github.com/Abhimanyu-Giri/movie-picture-pipeline

The original backend workflow also contained a literal AWS access-key ID. It has been removed. If that key is still active, deactivate it and create replacement credentials through your lab's authorized process; update GitHub Secrets. Removing source text does not deactivate a key or remove it from earlier Git history. Do not include credentials in screenshots or support tickets.

You can apply and test the code while waiting. Do not create personal paid AWS resources just to get past the credit limit without first deciding to accept those costs and confirming the course accepts that account.

## 2. Apply the corrected files

Copy the following files into your existing repository, keeping existing screenshots and unrelated work. Use your current GitHub checkout so your latest project history is preserved. On macOS, press Command+Shift+Period in Finder to see `.github`.

| File | Change |
| --- | --- |
| `.github/workflows/backend-cd.yaml` | Separate lint/test gates, SHA image build/push, completed Kustomize deployment, rollout and endpoint checks |
| `.github/workflows/frontend-cd.yaml` | Discover backend AWS URL before Docker build; lint/test gates; SHA deployment and runtime checks |
| `.github/workflows/backend-ci.yaml` | Install the committed development dependencies, including flake8 |
| `starter/backend/__init__.py` | Support imports under both pytest and the existing uWSGI entry point |
| `starter/backend/k8s/kustomization.yaml` | Remove the hardcoded old AWS account/image override |
| `starter/backend/k8s/deployment.yaml` | HTTP readiness/liveness probes |
| `starter/frontend/k8s/deployment.yaml` | HTTP readiness/liveness probes |
| `starter/frontend/Dockerfile` | Fail an image build when its API build argument is missing |
| `starter/backend/.dockerignore`, `starter/frontend/.dockerignore` | Exclude local dependencies, build output and local environment files |
| `tests/` | Offline checks of the runtime verifier; these are not AWS proof |
| `scripts/` | Discover ELB URLs, check deployed API/UI bundles, collect actual evidence |
| `START_HERE.md`, `PROOF/README.md`, `VALIDATION.md` | Recovery, evidence and validation notes |
| Top section of `README.md` | Repository link, honest runtime status and markers for automatically inserting actual URLs |

Do not copy `node_modules`, a locally generated `build` folder, Terraform state, or credentials. The included ZIP excludes local validation dependencies and output.

Both CD workflows have the required exact names and filenames. They run on matching application changes pushed/merged to `main`, workflow/helper changes, and manual dispatch on `main`. Lint and tests run in parallel; a failure blocks build and deploy. A dispatch on another branch is intentionally skipped.

The workflows expect an existing authorized EKS cluster and ECR repositories. They do not create or destroy infrastructure.

## 3. Confirm AWS infrastructure after lab access returns

In the Udacity workspace, first export your current lab credentials using its Cloud Gateway instructions. Then run:

```bash
aws sts get-caller-identity
aws eks list-clusters --region us-east-1
aws eks describe-cluster --name cluster --region us-east-1 --query 'cluster.{status:status,version:version}'
aws eks update-kubeconfig --name cluster --region us-east-1
kubectl get nodes
aws ecr describe-repositories --region us-east-1 --query 'repositories[].repositoryName'
```

The uploaded setup uses region `us-east-1`, cluster `cluster`, node group `udacity`, and ECR repositories `backend` and `frontend`. Use different values if the restored lab actually provides them. Nodes must be Ready. A cluster with no working nodes cannot run the application.

If the lab was deleted, use the course's current infrastructure setup after credits return. Preserve any existing Terraform state and inspect `terraform plan`; do not blindly recreate resources that already exist. The uploaded starter uses Terraform 1.3.9, an older AWS provider and Kubernetes 1.31. Check the course's current supported setup/version before recreating it. These infrastructure files were not upgraded or applied in this repair.

If the GitHub IAM user has not been granted Kubernetes access, run the supplied `setup/init.sh` from the authenticated lab workspace, as described in the original project instructions. This legacy helper uses `aws-auth`; a replacement cluster may instead require EKS access entries. Use the course/admin's prescribed authorization. Do not solve a Forbidden error by granting unrelated accounts access.

## 4. Set GitHub Actions secrets

Open the repository → Settings → Secrets and variables → Actions → Repository secrets.

| Secret | Value |
| --- | --- |
| `AWS_ACCESS_KEY_ID` | Active key for the authorized deployment identity |
| `AWS_SECRET_ACCESS_KEY` | Matching secret key |
| `AWS_SESSION_TOKEN` | Required for temporary credentials; leave absent for long-lived IAM-user credentials |
| `AWS_REGION` | `us-east-1` for the uploaded setup |
| `EKS_CLUSTER_NAME` | `cluster` for the uploaded setup |
| `ECR_REPOSITORY_BACKEND` | `backend` (repository name, not full URL) |
| `ECR_REPOSITORY_FRONTEND` | `frontend` (repository name, not full URL) |

The identity must be able to push images to those ECR repositories and deploy to the Kubernetes `default` namespace. All parts of temporary credentials must come from the same session, and expired sessions must be refreshed.

No manually entered frontend API URL is needed: Frontend CD reads `service/backend` from Kubernetes and checks its real `/movies` endpoint before building. Kubernetes Service names such as `http://backend` are not usable by an external user's browser. `localhost` would refer to that user's computer. Create React App embeds `REACT_APP_MOVIE_API_URL` during the image build, so changing only a pod environment variable later cannot repair the compiled bundle.

## 5. Run Backend CD, then Frontend CD

Merge the reviewed file changes into `main` once the secrets and cluster are ready. The matching push will trigger CD. On a new cluster both workflows may start together; if frontend reaches its build before backend exists, finish Backend CD and manually run Frontend CD afterward.

1. GitHub → Actions → **Backend Continuous Deployment** → Run workflow → branch `main`.
2. Wait for lint, test, build and deploy to succeed. Open its run summary and the backend `/movies` URL. Expect JSON with movie titles.
3. GitHub → Actions → **Frontend Continuous Deployment** → Run workflow → branch `main`.
4. Confirm the build summary displays the actual backend ELB URL. Wait for all four jobs to succeed.
5. Open the frontend URL from its run summary. This starter exposes HTTP on port 80. Use `http://` for this project unless you deliberately add TLS to both services.
6. Confirm the movie titles are visible and clicking a movie shows its details. In browser Developer Tools → Network, check that `/movies` is requested from the backend ELB and returns 200.

The deploy job checks the expected image, completed rollout, API response and, for frontend, CORS plus the backend URL embedded in the served JavaScript. These checks complement the browser screenshots; they do not replace observing the rendered application.

If the backend LoadBalancer is deleted/recreated, run Frontend CD again to embed its new URL.

## 6. Collect the actual resubmission evidence

In an authenticated repository checkout with Bash, Python 3, AWS CLI and kubectl:

```bash
aws eks update-kubeconfig --name cluster --region us-east-1
bash scripts/collect-runtime-evidence.sh all
```

This reads the live cluster and public endpoints, saves responses and image information under `PROOF/Runtime/all/`, and inserts the actual verified URLs between the runtime markers in `README.md`. It stops on failed checks rather than creating a success report. Do not paste guessed or example hostnames into the README.

Also download the `backend-aws-runtime-...` and `frontend-aws-runtime-...` artifacts from the successful Actions runs. Keep the successful Actions run links, source commit, deployment image tags and screenshots together. Neither artifact is present in this repair package because AWS was not run here.

Add the screenshots listed in `PROOF/README.md`. Preserve your previous CI proof. Commit the actual generated evidence and URLs after reviewing them; they contain public deployment information, not AWS secrets.

Before resubmitting, check:

- Both CD workflows show lint, test, build and deploy passing for the repaired code.
- Backend `/movies` and the frontend UI work at AWS LoadBalancer URLs.
- The frontend displays actual movie data fetched from that backend.
- The README contains the repository link and real observed URLs, not a pending status.
- The evidence folder includes Actions proof, browser address bars, Network proof and Kubernetes rollout/image information.

## Common failures

| Failure | What to check |
| --- | --- |
| `ExpiredToken` / invalid security token | Refresh all temporary credentials together, including `AWS_SESSION_TOKEN` |
| Cluster/repository not found | Lab may have been reset; verify region, account and actual resource names |
| `Unauthorized` / `Forbidden` from kubectl | The Actions identity needs the cluster's prescribed Kubernetes access |
| `ImagePullBackOff` | ECR image exists, image tag is correct, node IAM role can pull it |
| LoadBalancer address stays empty | `kubectl describe service backend` or `frontend`; inspect events, subnet/controller setup and lab quotas |
| Frontend build cannot find backend service | Complete Backend CD first; rerun Frontend CD |
| Frontend page appears but no movies | Check Network request URL, backend availability, CORS; rerun frontend after an ELB change |
| Bundle check fails | The deployed frontend was not built for the currently discovered backend URL |

## Credit management after capturing evidence

Ask your reviewer/trainer whether endpoints must remain live during review. If screenshots suffice, capture everything before following the course cleanup steps. If live access is required, agree on a short review window. Stopping work or closing the workspace does not itself delete deployed AWS resources.

For cleanup, delete this project's Kubernetes LoadBalancer services before destroying its cluster so their AWS load balancers can be removed. Use the correct project Terraform state and review the destroy plan. This repair does not run any deletion commands for you.

## Official references

- [Udacity AWS budget and cleanup guidance](https://support.udacity.com/hc/en-us/articles/4409515588749-AWS-Cloud-Resource-Best-Practices)
- [Create React App build-time environment variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [GitHub workflow syntax and job dependencies](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Kustomize image transformations](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [EKS Kubernetes version lifecycle](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
