# Personal AWS setup for Movie Picture Pipeline

These Terraform files create the AWS resources needed for the Udacity CD evidence:

- one EKS cluster in standard support
- one small managed node group
- two ECR repositories named `frontend` and `backend`
- a GitHub Actions OIDC role restricted to `Abhimanyu-Giri/movie-picture-pipeline` on the `main` branch
- an optional AWS Budget email alert

The GitHub Actions workflows use temporary AWS credentials through OIDC. Do not create long-lived AWS access keys for this project.

## 1. Run Terraform from AWS CloudShell

Sign in to your AWS account with an administrator identity and open **AWS CloudShell** in `us-east-1`. Then run:

```bash
git clone https://github.com/Abhimanyu-Giri/movie-picture-pipeline.git
cd movie-picture-pipeline/setup/terraform
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform
terraform init -upgrade
terraform fmt -check
terraform validate
terraform plan -var='billing_email=YOUR_EMAIL@example.com'
terraform apply -var='billing_email=YOUR_EMAIL@example.com'
```

If you do not want the budget email alert, omit the `billing_email` variable.

## 2. Add GitHub Actions secrets

After `terraform apply` finishes, print the values GitHub needs:

```bash
terraform output -json github_actions_secrets
```

In GitHub, go to **Settings > Secrets and variables > Actions > New repository secret** and create these secrets from the output:

| Secret | Meaning |
| --- | --- |
| `AWS_ROLE_ARN` | Role that GitHub Actions assumes through OIDC |
| `AWS_REGION` | AWS region, normally `us-east-1` |
| `EKS_CLUSTER_NAME` | EKS cluster name |
| `ECR_REPOSITORY_BACKEND` | Backend ECR repository name |
| `ECR_REPOSITORY_FRONTEND` | Frontend ECR repository name |

## 3. Run the CD workflows

Run **Backend Continuous Deployment** first. When it passes, run **Frontend Continuous Deployment**. The frontend workflow reads the real backend LoadBalancer URL before it builds the Docker image, so the React app points at the AWS backend URL instead of localhost.

Each successful CD run uploads runtime evidence under the Actions run artifacts:

- `backend-aws-runtime-...`
- `frontend-aws-runtime-...`

Use those artifacts and screenshots for the Udacity proof folder.

## 4. Clean up to stop AWS charges

Before destroying the cluster, delete the Kubernetes LoadBalancer services so AWS removes the public load balancers:

```bash
aws eks update-kubeconfig --name movie-picture-pipeline --region us-east-1
kubectl delete service frontend backend --ignore-not-found
kubectl delete deployment frontend backend --ignore-not-found
```

Then destroy the Terraform resources:

```bash
cd ~/movie-picture-pipeline/setup/terraform
terraform destroy -var='billing_email=YOUR_EMAIL@example.com'
```

If you omitted `billing_email` during apply, omit it during destroy too.
