# Guide de Déploiement — HiveBox

## Prérequis

| Outil | Version minimale | Usage |
|---|---|---|
| [Docker](https://www.docker.com/) | 24+ | Build & exécution des images |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | 1.28+ | Gestion du cluster |
| [KIND](https://kind.sigs.k8s.io/) | 0.20+ | Cluster Kubernetes local |
| [Helm](https://helm.sh/) | 3.12+ | Packaging applicatif |
| [uv](https://astral.sh/uv/) | 0.4+ | Gestion des dépendances Python |
| [Terraform](https://www.terraform.io/) | 1.5+ | Infrastructure Cloud (optionnel) |

---

## 1. Déploiement local (développement)

### 1.1 Installation des dépendances Python

```bash
git clone https://github.com/Yannislrg/hivebox.git
cd hivebox

uv sync --dev
```

### 1.2 Configuration de l'environnement

Créez un fichier `.env` à la racine :

```env
BASE_URL=https://api.opensensemap.org
BOX_ID=5c21ff8f919bf8001adf2488,5ade1acf223bd80019a1011c
VALKEY_HOST=localhost
VALKEY_PORT=6379
VALKEY_TTL=300
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=hivebox-data
```

### 1.3 Lancer l'application

```bash
uv run uvicorn src.app.main:app --reload
```

L'API est disponible sur `http://localhost:8000`.

### 1.4 Vérification rapide

```bash
curl http://localhost:8000/version
curl http://localhost:8000/temperature
curl http://localhost:8000/readyz
curl http://localhost:8000/metrics
```

---

## 2. Déploiement Kubernetes local (KIND)

Cette section couvre le déploiement complet de la stack sur un cluster KIND :
**HiveBox + Valkey + MinIO + Grafana Alloy**.

### 2.1 Création du cluster KIND

```bash
kind create cluster --config k8s/kind-config.yaml
```

Le fichier `kind-config.yaml` expose les ports 80 et 443 sur l'hôte pour l'Ingress.

### 2.2 Installation de l'Ingress Controller (NGINX)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 2.3 Déploiement de l'infrastructure (Valkey & MinIO)

```bash
kubectl apply -k infra/overlays/development

# Attendre que les pods soient prêts
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=redis \
  -n valkey --timeout=120s

kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=minio \
  -n minio --timeout=120s
```

### 2.4 Build et chargement de l'image dans KIND

```bash
docker build -t hivebox:local .
kind load docker-image hivebox:local
```

> Si vous utilisez l'image GHCR (CI/CD), passez directement à l'étape suivante.

### 2.5 Déploiement de HiveBox

**Option A — via les manifestes Kubernetes bruts :**

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

kubectl wait --for=condition=available deployment/hivebox-deployment --timeout=120s
```

**Option B — via Helm :**

```bash
helm install hivebox ./charts/hivebox \
  --set image.repository=hivebox \
  --set image.tag=local \
  --set image.pullPolicy=Never
```

Pour mettre à jour :

```bash
helm upgrade hivebox ./charts/hivebox \
  --set image.tag=<nouvelle-version>
```

### 2.6 Accès à l'application

**Via port-forward (le plus simple) :**

```bash
kubectl port-forward service/hivebox-service 8000:80
# Accès : http://localhost:8000
```

**Via Ingress (hivebox.local) :**

Ajoutez cette ligne à `/etc/hosts` :
```
127.0.0.1 hivebox.local
```

L'application est ensuite accessible sur `https://hivebox.local` (TLS activé, redirection HTTP→HTTPS forcée).

---

## 3. Observabilité — Grafana Alloy

Grafana Alloy collecte les métriques Prometheus et les logs Kubernetes puis les envoie vers Grafana Cloud.

### 3.1 Créer le secret des credentials Grafana Cloud

```bash
kubectl create secret generic grafana-cloud-credentials \
  --from-literal=prometheus-url="<PROMETHEUS_REMOTE_WRITE_URL>" \
  --from-literal=prometheus-user="<PROMETHEUS_USER_ID>" \
  --from-literal=loki-url="<LOKI_URL>" \
  --from-literal=loki-user="<LOKI_USER_ID>" \
  --from-literal=api-key="<GRAFANA_CLOUD_API_KEY>"
```

Ces valeurs se trouvent dans votre stack Grafana Cloud sous **Details > Send metrics / Send logs**.

### 3.2 Déployer Grafana Alloy

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana-alloy grafana/alloy \
  -f k8s/grafana-alloy/values.yaml \
  --namespace monitoring --create-namespace
```

### 3.3 Importer le dashboard Grafana

Une fois le dashboard HiveBox finalisé (fichier `.json`) :

1. Dans Grafana Cloud, aller dans **Dashboards > Import**
2. Uploader le fichier JSON ou coller son contenu
3. Sélectionner la datasource Prometheus correspondante

> Le dashboard expose les métriques clés : `hivebox_healthy_boxes_total`, `hivebox_cache_miss_total`, ainsi que les métriques standard FastAPI (latence, taux d'erreur, requêtes/s).

---

## 4. Infrastructure Cloud (Terraform + GKE)

Pour un déploiement en production sur Google Kubernetes Engine.

### 4.1 Prérequis

- Compte GCP avec un projet actif
- `gcloud` CLI configuré : `gcloud auth application-default login`

### 4.2 Configuration

Créez `terraform/terraform.tfvars` :

```hcl
project_id   = "votre-projet-gcp"
region       = "europe-west1"
cluster_name = "hivebox-cluster"
```

### 4.3 Déploiement

```bash
cd terraform

terraform init
terraform plan
terraform apply
```

Terraform crée :
- Un réseau VPC dédié (`hivebox-vpc`)
- Un sous-réseau (`10.0.1.0/24`)
- Un cluster GKE avec un node pool (`e2-small`, preemptible)

### 4.4 Récupérer les credentials du cluster

```bash
gcloud container clusters get-credentials hivebox-cluster \
  --zone europe-west1-a \
  --project votre-projet-gcp
```

Répétez ensuite les étapes 2.3 à 2.5 pour déployer l'application sur GKE.

### 4.5 Destruction de l'infrastructure

```bash
terraform destroy
```

---

## 5. Tests

### Tests unitaires et d'intégration

```bash
uv run pytest
```

### Tests E2E (nécessite l'application déployée)

```bash
venom run tests/e2e/hivebox.yml --var base_url=http://localhost:8000
```

### Linting

```bash
uv run flake8 src/
```

---

## 6. CI/CD — GitHub Actions

Les workflows déclenchés automatiquement à chaque push/PR sont :

| Workflow | Déclencheur | Action |
|---|---|---|
| `lint.yml` | push, PR | Flake8 + Hadolint |
| `tests.yml` | push, PR | pytest (unit + intégration) |
| `build.yml` | push `main`, tags | Build & push image GHCR |
| `main.yml` | push `main` | Pipeline principal |
| `integration-tests.yml` | push, PR | Tests d'intégration complets |
| `e2e-tests.yml` | push `main` | Tests E2E Venom sur KIND |
| `terrascan.yml` | push, PR | Scan sécurité infra |
| `scorecard.yml` | hebdomadaire | OpenSSF Scorecard |

L'image Docker publiée est disponible sur GHCR :
```
ghcr.io/yannislrg/hivebox:<tag>
```

---

## 7. Résolution des problèmes courants

**Les pods HiveBox restent en `Pending`**
```bash
kubectl describe pod -l app=HiveBox
# Vérifier les events et les ressources disponibles sur le nœud
```

**L'endpoint `/readyz` retourne 503**

Le readiness probe échoue si Valkey est inaccessible. Vérifier :
```bash
kubectl get pods -n valkey
kubectl logs -n valkey -l app.kubernetes.io/name=redis
```

**Impossible d'accéder à `hivebox.local`**

Vérifier que l'entrée `/etc/hosts` est correcte et que l'Ingress controller est bien démarré :
```bash
kubectl get pods -n ingress-nginx
```

**Grafana Alloy ne pousse pas les métriques**

Vérifier que le secret `grafana-cloud-credentials` existe et que les URLs sont correctes :
```bash
kubectl get secret grafana-cloud-credentials -o yaml
kubectl logs -n monitoring -l app.kubernetes.io/name=alloy
```
