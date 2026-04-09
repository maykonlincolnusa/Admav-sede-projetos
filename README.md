<div align="center">

<br/>

```
 █████╗ ██████╗ ███╗   ███╗ █████╗ ██╗   ██╗
██╔══██╗██╔══██╗████╗ ████║██╔══██╗██║   ██║
███████║██║  ██║██╔████╔██║███████║██║   ██║
██╔══██║██║  ██║██║╚██╔╝██║██╔══██║╚██╗ ██╔╝
██║  ██║██████╔╝██║ ╚═╝ ██║██║  ██║ ╚████╔╝ 
╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝  ╚═══╝  
```

**Portfólio de Produtos · Visão Geral do Ecossistema**

<br/>

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento%20Ativo-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=4ade80)](.)
[![Stack](https://img.shields.io/badge/Stack-React%20·%20FastAPI%20·%20MongoDB-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=60a5fa)](.)
[![IA](https://img.shields.io/badge/IA-RAG%20·%20LangGraph%20·%20Multiagente-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=a78bfa)](.)
[![Deploy](https://img.shields.io/badge/Deploy-Docker%20·%20Railway-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=f472b6)](.)

<br/>

</div>

---

<br/>

## Sobre Este Repositório

Este repositório organiza, em formato de portfólio, os principais projetos e protótipos desenvolvidos no ecossistema ADMAV. O objetivo não é publicar tudo — é registrar com clareza o contexto de cada trabalho, a direção de produto e o recorte técnico que faz sentido apresentar publicamente.

Alguns projetos já estão em estágio de MVP funcional. Outros ainda estão em exploração visual, validação de arquitetura ou prototipação. Este repositório funciona como um **snapshot curado** do que vale apresentar no GitHub neste momento.

<br/>

---

<br/>

## O Que é Construído Aqui

Os projetos reunidos aqui orbitam três frentes principais:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ◆  IA aplicada a atendimento, operação e inteligência        │
│      de contexto.                                               │
│                                                                 │
│   ◆  Produtos internos com foco em automação, memória           │
│      semântica e experiência assistida.                          │
│                                                                 │
│   ◆  Interfaces premium para nichos específicos, com forte      │
│      preocupação de posicionamento e identidade visual.          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

**Padrão técnico recorrente no portfólio:**

| Camada | Tecnologias |
|---|---|
| **Frontend** | React + Vite |
| **Backend** | FastAPI · Node/Express |
| **Persistência** | MongoDB |
| **IA / Inteligência** | RAG · Embeddings · LangChain · LangGraph · Orquestração multiagente |
| **Infraestrutura** | Docker · Railway |

<br/>

---

<br/>

## Projetos Publicados

<br/>

### 01 — Yafah

> *Plataforma de consultoria orientada por IA para empreendedoras do setor de beleza e luxo.*

Yafah combina branding refinado com recursos de inteligência prática para marketing, conteúdo, conhecimento contextual e visão financeira. É o produto mais maduro do ecossistema em termos de execução full stack.

**Principais características:**
- Dashboard com áreas para chat, Instagram, TikTok, site, base de conhecimento e finanças
- Backend em FastAPI com rotas para autenticação, cadastro, chat, administração, feedback, knowledge base e métricas
- RAG e memória contextual para personalizar respostas com base no histórico de cada usuária
- Estrutura completa de deploy com documentação e organização de configuração

**Stack:** `React` `FastAPI` `MongoDB` `LangChain` `FAISS` `Gemini / OpenRouter` `Docker`

**Status:** `MVP` — Backend, frontend, documentação de execução e organização de deploy no lugar.

<br/>

---

<br/>

### 02 — O Chefe

> *Sistema multiagente para gestão de igreja, relacionamento com membros e operação institucional da ADMAV.*

No núcleo deste projeto está uma arquitetura de agentes especializados que combina cadastro, atendimento, RAG institucional, devocionais automáticos e contexto por unidade — construído para servir uma rede religiosa distribuída com múltiplas filiais.

**Principais características:**
- Backend em FastAPI com arquitetura modular em `app/`
- Orquestração com LangGraph e agentes: `CadastroAgent`, `WelcomeAgent`, `DevotionalAgent`, `RAGAgent`, `EngagementAgent`, `SecretaryAgent`
- Coleções MongoDB para membros, base de conhecimento e interações
- APScheduler para fluxos automáticos como devocionais recorrentes
- Frontend inicial em React para cadastro de membros com integração direta à API

**Stack:** `React` `FastAPI` `LangGraph` `MongoDB` `APScheduler` `Docker`

**Status:** `Ativo` — Backend bem estruturado com sólido contexto de domínio. Frontend funcional, ainda em evolução.

<br/>

---

<br/>

### 03 — Site Oficial ADMAV

> *Presença digital institucional da Assembleia de Deus do Ministério Água Viva.*

O site oficial da ADMAV é a vitrine pública da rede de igrejas — o primeiro ponto de contato digital para visitantes, novos membros e parceiros institucionais. A proposta vai além de uma página informativa: é uma experiência de identidade que transmite propósito, organização e acolhimento desde o primeiro acesso.

**Principais características:**
- Identidade visual coesa alinhada ao branding institucional da ADMAV
- Seções para apresentação da rede, programação, liderança e localização das unidades
- Integração planejada com os sistemas internos do ecossistema (O Chefe, Kairos)
- Arquitetura leve com foco em performance, acessibilidade e SEO
- Estrutura preparada para evolução progressiva com CMS e conteúdo dinâmico

**Stack:** `React` `Vite` `TailwindCSS`

**Status:** `Em Desenvolvimento` — Direção de produto definida, implementação em andamento com foco em presença pública e integração ao ecossistema.

<br/>

---

<br/>

### 04 — Kairos

> *Conceito de produto e identidade digital para uma frente criativa voltada ao contexto cristão e institucional.*

Neste recorte de portfólio, foi mantido apenas o protótipo visual principal — aquele que registra a direção estética e a proposta de experiência. Nenhuma interface se reduz apenas à sua camada funcional; Kairos existe aqui como registro dessa convicção.

**Principais características:**
- Protótipo estático com linguagem visual editorial
- Interface pensada para login, cadastro e ambientação institucional
- Exploração de branding, tipografia e atmosfera visual com forte apelo de direção criativa

**Status:** `Exploração` — O scaffold full stack existe localmente, mas ainda não está maduro o suficiente para apresentação pública.

<br/>

---

<br/>

## Mapeados, Mas Fora do Escopo Desta Publicação

Nem tudo o que existe na pasta original foi publicado. Parte do material ainda é referência visual, estudo inicial ou rascunho técnico sem densidade suficiente para portfólio público.

**Deliberadamente omitidos:**

- **Ezer** — contém apenas material de apoio e referência visual nesta fase
- Arquivos soltos de experimento, mocks isolados e telas não integradas ao fluxo principal dos produtos

<br/>

---

<br/>

## Critério de Curadoria

A regra foi simples: **publicar o que ajuda a entender visão, arquitetura e capacidade de execução. Não publicar o que apenas adiciona ruído ou risco.**

**Mantido:**
- Código-fonte relevante
- Estruturas de backend e frontend que mostram a proposta dos produtos
- Documentação já existente e arquivos de configuração úteis para compreensão dos projetos
- Artefatos que demonstram direção de produto e solução técnica

**Omitido:**
- Arquivos `.env` e credenciais
- Chaves de API expostas em arquivos locais
- `node_modules`, builds, caches, logs e bancos locais
- Artefatos de machine learning e arquivos gerados em execução
- Pastas com material apenas de referência visual

<br/>

---

<br/>

## Estrutura do Repositório

```text
.
├── README.md
│
├── Yafah/                    ←  Plataforma de consultoria com IA para o setor de beleza
│   ├── backend/
│   └── frontend/
│
├── O chefe/                  ←  Sistema multiagente de gestão de igreja
│   ├── app/
│   └── frontend/
│
├── site-oficial/             ←  Presença digital institucional da ADMAV
│   ├── src/
│   └── public/
│
└── kairos/                   ←  Conceito visual e identidade institucional
    └── prototype/
```

<br/>

---

<br/>

## Considerações Finais

<div align="center">

*Este repositório é uma versão curada do trabalho — pensada para apresentação pública no GitHub.*

*Alguns projetos continuam evoluindo localmente e podem conter caminhos em aberto,*
*mas o conjunto já mostra com clareza as linhas de produto, as decisões técnicas*
*e o tipo de solução que vem sendo construído.*

<br/>

À medida que a maturidade cresce, o próximo passo natural é separar os projetos mais avançados em repositórios próprios. Por enquanto, este portfólio funciona como uma vitrine consolidada do ecossistema.

<br/>

---

**Ecossistema ADMAV** · Construído com intencionalidade.

</div>
