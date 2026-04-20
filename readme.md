

file arborescence

hivebox/
│
├── 📄 Dockerfile
├── 📄 requirements.txt
├── 📄 README.md
├── 📄 .gitignore
│
├── 📁 src/
│   └── 📁 app/
│       ├── main.py               # Point d'entrée Flask/FastAPI
│       ├── config.py             # Config via env vars (senseBox IDs, etc.)
│       ├── 📁 routes/
│       │   ├── version.py        # GET /version
│       │   ├── temperature.py    # GET /temperature
│       │   ├── metrics.py        # GET /metrics (Prometheus)
│       │   ├── readyz.py         # GET /readyz
│       │   └── store.py          # GET /store
│       └── 📁 services/
│           ├── opensensemap.py   # Client API openSenseMap
│           ├── cache.py          # Intégration Valkey/Redis
│           └── storage.py        # Intégration MinIO (S3)
│
├── 📁 tests/
│   ├── 📁 unit/
│   │   ├── test_version.py
│   │   └── test_temperature.py
│   ├── 📁 integration/
│   │   └── test_api.py
│   └── 📁 e2e/
│       └── suite.yaml            # Venom test suite
│
├── 📁 k8s/
│   ├── kind-config.yaml          # Cluster KIND + Ingress-Nginx
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
│
├── 📁 helm/
│   └── 📁 hivebox/               # Helm chart de l'app (Phase 5)
│       ├── Chart.yaml
│       ├── values.yaml
│       └── 📁 templates/
│
├── 📁 kustomize/                 # Infra (Valkey, MinIO)
│   ├── 📁 base/
│   │   ├── valkey.yaml
│   │   └── minio.yaml
│   └── 📁 overlays/
│       ├── 📁 dev/
│       └── 📁 prod/
│
├── 📁 infra/                     # Terraform (Phase 5)
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── 📁 docs/
│   ├── architecture.md
│   ├── api.md
│   └── runbook.md
│
└── 📁 .github/
    └── 📁 workflows/
        ├── ci.yaml               # Lint, build, test, SonarQube, Terrascan
        ├── cd.yaml               # Push image GHCR, release
        └── scorecard.yaml        # OpenSSF Scorecard