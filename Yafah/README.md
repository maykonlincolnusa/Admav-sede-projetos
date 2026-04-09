<div align="center">
  <h1 style="font-family: serif; font-style: italic; font-size: 3.5rem;">Yafah AI</h1>
  <p style="letter-spacing: 0.5rem; text-transform: uppercase; font-size: 0.9rem; color: #D4AF37;">יָפָה ✦ Sophisticated Business Intelligence</p>
  <p><strong>A elite em consultoria estratégica orientada por IA para o ecossistema de luxo e beleza.</strong></p>
  <br />
  <p>
    <img src="https://img.shields.io/badge/React-18-black?style=for-the-badge&logo=react" alt="React" />
    <img src="https://img.shields.io/badge/FastAPI-0.110-black?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/MongoDB-Atlas-black?style=for-the-badge&logo=mongodb" alt="MongoDB" />
    <img src="https://img.shields.io/badge/Railway-Production-black?style=for-the-badge&logo=railway" alt="Railway" />
  </p>
</div>

<br />

## ✦ A Essência do Projeto

**Yafah** transcende a definição de software; é uma extensão digital da visão empreendedora. Unindo uma estética **Neutral Luxury** (Matte Black, Brushed Gold e Nude) com as mais avançadas técnicas de **RAG (Retrieval-Augmented Generation)**, a plataforma atua como uma sócia estratégica dedicada a empreendedoras que valorizam a excelência.

Através de uma memória semântica baseada em vetores, a Yafah aprende com cada interação, refinando seus conselhos sobre branding, marketing e gestão para criar um roadmap personalizado de crescimento e propósito.

---

## ⚡ Suíte Editorial de Inteligência

- **Cérebro de Curadoria (RAG System):** Memória de longo prazo indexada via FAISS e LangChain. Recorda métricas, tom de voz e estratégias passadas para cada cliente.
- **Instagram Exclusive Suite:** Criação de narrativas visuais e legendas de alto impacto emocional e conversão.
- **TikTok Viral Scripts:** Roteiros estruturados para retenção e autoridade, lapidados pelo modelo Google Gemini 1.5/2.0.
- **Website Copywriting:** Engenharia de textos persuasivos para domínios digitais com foco em SEO de luxo.
- **Painel Curator (Admin):** Gestão exclusiva de credenciais e solicitações de acesso via sistema de curadoria interna.

---

## 🏗️ Arquitetura Técnica Premium

A Yafah utiliza um stack de ponta para garantir estabilidade e escalabilidade:

### Infraestrutura
* **Backend:** FastAPI (Python) Assíncrono com injeção de dependências e Middlewares de segurança.
* **Database:** MongoDB Atlas (NoSQL) para persistência de dados brutos.
* **Vector Store:** FAISS-cpu para busca semântica em tempo real (Embedding models do Google).
* **Frontend:** React (Vite) com arquitetura modular, Design Tokens personalizados e Glassmorphism refinado.

---

## 🚀 Deployment: Organização para Produção

A plataforma está otimizada para implantação profissional via **Railway** ou **Docker**.

### 1. Via Railway (Recomendado)
A Yafah possui Dockerfiles otimizados para detecção automática:
1. Conecte seu repositório ao [Railway](https://railway.app/).
2. Crie dois serviços compartilhando o mesmo repo:
   - **Service A (Backend):** Aponte para a pasta `/backend`. Adicione as variáveis `MONGODB_URI` e `GOOGLE_API_KEY`.
   - **Service B (Frontend):** Aponte para a pasta `/frontend`. Adicione a variável `VITE_API_URL` apontando para o seu backend.
3. O Railway detectará os `Dockerfile`s automaticamente e iniciará o deploy.

### 2. Via Docker Compose (Local & Staging)
Para orquestrar todo o ecossistema localmente:
```bash
docker-compose up --build
```
Isso iniciará o Backend na porta `8000` e o Frontend com Nginx na porta `80`.

---

## ⚙️ Configuração Manual

### Credenciais Essenciais (`.env` no /backend)
```env
MONGODB_URI="sua_uri_do_mongodb_atlas"
GOOGLE_API_KEY="sua_chave_do_google_ai_studio"
ADMIN_SECRET="yafah_admin_2024"
```

### Inicialização Rápida
1. **Backend:** `pip install -r requirements.txt` -> `uvicorn main:app`
2. **Frontend:** `npm install` -> `npm run dev`

---

<div align="center">
  <p><em>"Quem sabe se não foi para um momento como este que você chegou?" — Ester 4:14</em></p>
  <p><strong>Yafah AI ✦ O Futuro da Inteligência na Beleza</strong></p>
</div>
---

<p align="center">Feito com 🩷 para simplificar e escalar negócios de Empreendedoras Brasileiras.</p>
