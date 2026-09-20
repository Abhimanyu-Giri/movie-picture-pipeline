# Run the Udacity CD project in your personal AWS account

Use this guide after pushing this repository version to GitHub.

## What changed for your personal account

The deployment now uses GitHub Actions OIDC. GitHub receives temporary AWS credentials only for workflow runs on the `main` branch. You only need to save these GitHub repository secrets:

- `AWS_ROLE_ARN`
- `AWS_REGION`
- `EKS_CLUSTER_NAME`
- `ECR_REPOSITORY_BACKEND`
- `ECR_REPOSITORY_FRONTEND`

You do not need `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or `AWS_SESSION_TOKEN`.

## Cost control

This project creates paid AWS resources. Keep it running only long enough to collect the proof. The Terraform is set to one `t3.small` EKS node and one EKS cluster, and the Kubernetes services create public AWS load balancers during deployment. An AWS Budget can email you, but it does not automatically stop resources.

## Step 1: Push this fixed repo to GitHub

From your local project folder:

```bash
git status
git add .
git commit -m "Fix CD deployment for personal AWS"
git push origin main
```

If Git says there is nothing to commit, confirm that GitHub already has these files:

- `.github/workflows/backend-cd.yaml`
- `.github/workflows/frontend-cd.yaml`
- `setup/terraform/main.tf`
- `setup/terraform/outputs.tf`
- `setup/terraform/variables.tf`

## Step 2: Create AWS infrastructure

Open AWS CloudShell in `us-east-1` from your personal AWS account, then run:

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

Replace `YOUR_EMAIL@example.com` with your email address. If you do not want the budget email alert, run `terraform apply` without the `-var` option.

## Step 3: Put Terraform outputs into GitHub secrets

Run this in CloudShell:

```bash
terraform output -json github_actions_secrets
```

Create the five repository secrets in GitHub from that JSON output.

## Step 4: Run deployments

In GitHub Actions:

1. Run **Backend Continuous Deployment**.
2. Wait for it to pass.
3. Run **Frontend Continuous Deployment**.
4. Download the runtime evidence artifacts from both runs.

The frontend workflow verifies the live backend LoadBalancer and builds React with that backend URL.

At the end of each CD run, expand these reviewer-requested steps and confirm they are green:

- `Verify Kubernetes deployment`
- `Verify Backend ECR image` or `Verify Frontend ECR image`

## Step 5: Update proof for resubmission

For the next Udacity submission, include:

- screenshots of both green CD workflow runs
- the downloaded `backend-aws-runtime-...` artifact contents
- the downloaded `frontend-aws-runtime-...` artifact contents
- the real frontend and backend LoadBalancer URLs from the evidence files

Print the same live URLs from CloudShell with:

```bash
aws eks update-kubeconfig --name movie-picture-pipeline --region us-east-1
BACKEND_HOST=$(kubectl get service backend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
FRONTEND_HOST=$(kubectl get service frontend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "Backend:  http://${BACKEND_HOST}/movies"
echo "Frontend: http://${FRONTEND_HOST}"
```

Open both URLs in a browser and take separate screenshots. The browser address bar must show the full AWS LoadBalancer URL. The frontend screenshot must show the movie list, and the backend screenshot must show the movie JSON.

Remove any `YOUR_...` placeholders from the proof folder before resubmitting.

## Step 6: Destroy AWS resources

When you have the proof, clean up immediately.

```bash
aws eks update-kubeconfig --name movie-picture-pipeline --region us-east-1
kubectl delete service frontend backend --ignore-not-found
kubectl delete deployment frontend backend --ignore-not-found
cd ~/movie-picture-pipeline/setup/terraform
terraform destroy -var='billing_email=YOUR_EMAIL@example.com'
```

Use the same `billing_email` setting you used during apply. If you omitted it during apply, omit it during destroy.
