# Start here: finish the Movie Picture Pipeline resubmission

This package fixes the two remaining CD review gaps:

- Backend CD runs lint, tests, image build, deploy, rollout verification, and runtime evidence collection.
- Frontend CD verifies the live backend AWS LoadBalancer before the image build and passes that real URL as `REACT_APP_MOVIE_API_URL`.
- Both CD workflows end with the exact Kubernetes and ECR verification steps requested in the latest review.

Because the Udacity AWS account is unavailable, use your personal AWS account only long enough to collect proof, then destroy the resources.

## 1. Push this version to GitHub

From your local checkout of `Abhimanyu-Giri/movie-picture-pipeline`:

```bash
git status
git add .
git commit -m "Fix CD deployment for personal AWS"
git push origin main
```

## 2. Create the AWS infrastructure

Open AWS CloudShell in `us-east-1` from your personal AWS account and run:

```bash
git clone https://github.com/Abhimanyu-Giri/movie-picture-pipeline.git
cd movie-picture-pipeline/setup/terraform
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform
terraform init -upgrade
terraform fmt -check
terraform validate
terraform apply -var='billing_email=YOUR_EMAIL@example.com'
```

Replace `YOUR_EMAIL@example.com` with your email. If you do not want AWS Budget email alerts, run `terraform apply` without the `-var` option.

The Terraform creates an EKS cluster, one small managed node, frontend/backend ECR repositories, and a GitHub Actions OIDC role restricted to this repository on `main`.

## 3. Add GitHub repository secrets

After Terraform finishes, run:

```bash
terraform output -json github_actions_secrets
```

In GitHub, open **Settings > Secrets and variables > Actions** and create these repository secrets:

| Secret | Value source |
| --- | --- |
| `AWS_ROLE_ARN` | Terraform output `AWS_ROLE_ARN` |
| `AWS_REGION` | Terraform output `AWS_REGION` |
| `EKS_CLUSTER_NAME` | Terraform output `EKS_CLUSTER_NAME` |
| `ECR_REPOSITORY_BACKEND` | Terraform output `ECR_REPOSITORY_BACKEND` |
| `ECR_REPOSITORY_FRONTEND` | Terraform output `ECR_REPOSITORY_FRONTEND` |

Do not create `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or `AWS_SESSION_TOKEN` for this project. The workflows use GitHub OIDC and temporary AWS credentials.

## 4. Run the CD workflows

Run **Backend Continuous Deployment** first. Wait for it to pass. Then run **Frontend Continuous Deployment**.

The frontend workflow discovers the actual backend AWS LoadBalancer, checks `/movies`, and builds the React image with that backend URL. This is the reviewer's main failed item from the previous submission.

## 5. Collect proof for Udacity

From the successful GitHub Actions runs, download these artifacts:

- `backend-aws-runtime-...`
- `frontend-aws-runtime-...`

Open each successful CD run and confirm its final two steps are green:

- `Verify Kubernetes deployment`
- `Verify Backend ECR image` or `Verify Frontend ECR image`

Get the live addresses in CloudShell:

```bash
aws eks update-kubeconfig --name movie-picture-pipeline --region us-east-1
BACKEND_HOST=$(kubectl get service backend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
FRONTEND_HOST=$(kubectl get service frontend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "Backend:  http://${BACKEND_HOST}/movies"
echo "Frontend: http://${FRONTEND_HOST}"
```

Open both printed URLs in a browser. Take one screenshot of the backend JSON and one screenshot of the rendered frontend movie list. Keep the complete `http://...amazonaws.com` address visible in the browser address bar. Also take screenshots of both green CD runs, including the final verification steps. Replace every old `YOUR_...` placeholder with the real addresses from this deployment.

## 6. Destroy AWS resources after proof

After saving proof, clean up immediately:

```bash
aws eks update-kubeconfig --name movie-picture-pipeline --region us-east-1
kubectl delete service frontend backend --ignore-not-found
kubectl delete deployment frontend backend --ignore-not-found
cd ~/movie-picture-pipeline/setup/terraform
terraform destroy -var='billing_email=YOUR_EMAIL@example.com'
```

Use the same `billing_email` setting used for apply. If you omitted it during apply, omit it during destroy.

See `PERSONAL_AWS_GUIDE.md` for the same steps with more context.
