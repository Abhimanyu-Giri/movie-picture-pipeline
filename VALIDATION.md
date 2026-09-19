# Validation of this CD repair

These results are local code checks, not AWS deployment evidence. No GitHub push, Actions run, ECR upload, EKS deployment, resource creation or resource deletion was performed in this session.

| Check actually performed | Result |
| --- | --- |
| Frontend dependency installation with `npm ci` | Passed |
| Frontend `npm run lint` | Passed |
| Frontend tests, noninteractive | 2 suites, 3 tests passed |
| Frontend production build with an explicit synthetic API URL | Compiled successfully |
| Inspect compiled JavaScript for that build argument | Found the supplied URL |
| Backend flake8, version 6.0.0 from the lock | Passed |
| Backend pytest, version 7.2.1 from the lock | 3 tests passed |
| Import backend as the existing uWSGI module and request `/movies` with Flask's test client | Passed; HTTP 200 |
| All four workflows with actionlint 1.7.7 | Passed |
| All workflow shell steps and new shell helpers with `bash -n` | Passed |
| Both manifest sets with Kustomize 5.4.2 | Rendered successfully |
| SHA image substitutions, service selectors, target/container/probe ports | Passed |
| Runtime-verifier offline tests | 7 passed; covers wrong URL, missing movies, wrong bundle and CORS failures |
| Scan deliverable text for AWS access-key ID patterns | No matches after removal |

The frontend checks used the available Node 24.19.0 runtime. The backend checks used Python 3.12.14 with the relevant application/test/lint packages at their committed lock versions. GitHub Actions and the existing Dockerfiles retain the project's Node 18 / Python 3.10 environments. These exact runner/container environments still need an actual Actions run. Existing packages emitted deprecation warnings; the application dependencies were not broadly upgraded as part of this CD repair.

Docker was unavailable locally, so neither Docker image was built or started here. uWSGI itself was not compiled/run; the entry-point import and Flask response were checked. AWS permissions, cluster capacity, load balancer provisioning and actual browser rendering remain unverified. Terraform was not applied or upgraded.

The synthetic URL used for the frontend build is test input only. That generated bundle is excluded from the deliverable. No fabricated AWS URLs, runtime responses or screenshots are included as proof.

## Reproduce the useful checks

From `starter/frontend` with the project's Node version installed:

```bash
npm ci
npm run lint
CI=true npm test -- --watchAll=false --runInBand
```

From `starter/backend` with Python 3.10 and Pipenv installed:

```bash
pipenv sync --dev
pipenv run lint
pipenv run test
```

From the repository root:

```bash
python3 -m unittest discover -s tests -v
bash -n scripts/load-balancer-url.sh
bash -n scripts/collect-runtime-evidence.sh
```

After AWS access returns, follow `START_HERE.md` to run both CD workflows and collect real runtime proof.
