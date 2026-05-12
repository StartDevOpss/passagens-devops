# ✈️ FlightHunter — Passagens DevOps

![CI/CD](https://github.com/StartDevOpss/passagens-devops/actions/workflows/ci-cd.yml/badge.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5?logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)

> Bot automatizado de monitoramento de passagens aéreas com alertas no Discord, rodando em Kubernetes com pipeline CI/CD completo via GitHub Actions.

**Projeto de portfólio** focado em práticas DevOps reais: containerização, orquestração, CI/CD, segurança e observabilidade.

---

## 🏗️ Arquitetura

```
GitHub Actions (CI/CD)
    │
    ├── Lint (flake8 + bandit)
    ├── Build & Push → ghcr.io (GHCR)
    ├── Security Scan (Trivy)
    └── Deploy → Kubernetes (Minikube)
                    │
                    ├── Namespace: passagens
                    ├── Deployment: passagens-bot
                    │     └── Container Python (non-root)
                    ├── ConfigMap (configs não-sensíveis)
                    ├── Secret (webhook + api key via CI)
                    └── PVC (persistência do ofertas.json)
                              │
                              └── Discord Webhooks 🔔
```

---

## 🚀 Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| API de Voos | SerpApi (Google Flights) |
| Alertas | Discord Webhooks |
| Container | Docker (multi-stage, non-root) |
| Orquestração | Kubernetes (Minikube) |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |
| Segurança | Trivy (scan de imagem) + Bandit (SAST) |
| Frontend | HTML + Tailwind CSS → GitHub Pages |

---

## 🔧 Como rodar localmente

### Pré-requisitos
- Docker
- Minikube
- kubectl

### 1. Clone e configure o ambiente

```bash
git clone https://github.com/StartDevOpss/passagens-devops
cd passagens-devops

# Configure suas variáveis de ambiente
cp .env.example .env
# Edite o .env com seus valores reais
```

### 2. Rodar com Docker

```bash
docker build -t passagens-bot .
docker run --env-file .env passagens-bot
```

### 3. Rodar no Minikube

```bash
# Inicia o cluster
minikube start

# Cria o namespace e configs
kubectl apply -f k8s/namespace-and-config.yaml

# Cria o secret com seus valores reais
kubectl create secret generic passagens-secret \
  --from-literal=DISCORD_WEBHOOK_URL="sua_url" \
  --from-literal=SERPAPI_KEY="sua_chave" \
  -n passagens

# Faz o deploy
kubectl apply -f k8s/deployment.yaml

# Verifica os pods
kubectl get pods -n passagens
```

---

## 🔐 Segurança

- Secrets gerenciados via **Kubernetes Secrets** + **GitHub Secrets** (nunca no código)
- Container roda como **usuário não-root** (UID 1000)
- **Trivy** escaneia a imagem a cada push para detectar CVEs
- **Bandit** analisa o código Python em busca de vulnerabilidades
- `.gitignore` configurado para bloquear `.env` e arquivos de secret K8s

---

## 📦 Pipeline CI/CD

O pipeline roda automaticamente a cada `push` na `main`:

1. **Lint** — flake8 + bandit no código Python
2. **Build & Push** — imagem Docker enviada para o GHCR com tag `sha-` e `latest`
3. **Security Scan** — Trivy varre a imagem; resultado vai para o GitHub Security
4. **Deploy** — `kubectl set image` + `rollout status` garantem zero-downtime

### Secrets necessários no GitHub

| Secret | Descrição |
|---|---|
| `DISCORD_WEBHOOK_URL` | URL do webhook do Discord |
| `SERPAPI_KEY` | Chave da SerpApi |
| `KUBECONFIG_BASE64` | kubeconfig em base64 para acesso ao cluster |

---

## 📊 Dashboard

Acesse o dashboard em tempo real via GitHub Pages:
**[https://startdevopss.github.io/passagens-devops](https://startdevopss.github.io/passagens-devops)**

---

*Projeto desenvolvido para portfólio em Engenharia de Plataforma / DevOps.*
