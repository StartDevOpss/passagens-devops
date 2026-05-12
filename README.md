# ✈️ FlightHunter Dashboard & K8s Bot

Sistema automatizado de monitoramento de passagens aéreas que utiliza **Kubernetes** para orquestração e **Discord** para alertas inteligentes.

## 🚀 Destaques Técnicos

- **Orquestração com Kubernetes:** Utilização de `Deployments`, `ConfigMaps` e `Secrets` para uma aplicação resiliente e segura.
- **Persistência de Dados:** Configuração de `PersistentVolumeClaim (PVC)` para armazenamento de cache de ofertas (`JSON`), garantindo que os dados persistam mesmo após restarts do container.
- **Roteamento Inteligente:** Lógica em Python (`router.py`) que filtra ofertas por preço, data e destino, direcionando-as para diferentes Webhooks do Discord.
- **Dashboard em Tempo Real:** Frontend estático em **Tailwind CSS** hospedado via **GitHub Pages**, que consome os dados gerados pelo bot no cluster.

## 🛠️ Tecnologias
- **Backend:** Python 3.10 (Requests, Logging, JSON)
- **Infra:** Docker, Kubernetes (Minikube), Kubectl
- **API:** SerpApi (Google Flights)
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Fetch API)

## 🔧 Como o projeto foi construído (Step-by-Step)

1. **Desenvolvimento do Bot:** Criação do motor de busca em Python integrado à SerpApi.
2. **Containerização:** Escrita do `Dockerfile` otimizado para rodar o bot de forma isolada.
3. **Manifestos K8s:** Criação da infraestrutura como código (IaC) para subir o bot no Minikube.
4. **Volume Persistente:** Implementação do PVC para que o bot e o dashboard compartilhassem o arquivo `ofertas.json`.
5. **CI/CD estático:** Configuração do GitHub Pages para servir o dashboard automaticamente a partir da pasta `/docs`.

---
*Projeto desenvolvido para fins de portfólio em Engenharia de Plataforma / DevOps.*