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

### Product Portfolio · Ecosystem Overview

<br/>

[![Status](https://img.shields.io/badge/Status-Active%20Development-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=4ade80)](.)
[![Stack](https://img.shields.io/badge/Stack-React%20·%20FastAPI%20·%20MongoDB-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=60a5fa)](.)
[![AI](https://img.shields.io/badge/AI-RAG%20·%20LangGraph%20·%20Multiagent-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=a78bfa)](.)
[![Deploy](https://img.shields.io/badge/Deploy-Docker%20·%20Railway-0a0a0a?style=for-the-badge&labelColor=0a0a0a&color=f472b6)](.)

</div>

<br/>

---

<br/>

## Overview

This repository organizes, in portfolio format, the main projects and prototypes developed within the ADMAV ecosystem. The goal is not to publish everything — it is to register with clarity the context of each work, the product direction, and the technical scope that makes sense to show publicly.

Some projects are already at a functional MVP stage. Others are still in visual exploration, architecture validation, or prototyping. This repository works as a **curated snapshot** of what is worth presenting on GitHub right now.

<br/>

---

<br/>

## What Gets Built Here

The projects here orbit three main fronts:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ◆  AI applied to service, operations, and context        │
│      intelligence.                                          │
│                                                             │
│   ◆  Internal products focused on automation, semantic      │
│      memory, and assisted experience.                        │
│                                                             │
│   ◆  Premium interfaces for specific niches, with strong    │
│      visual identity and positioning.                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

<br/>

**Recurring technical pattern across the portfolio:**

| Layer | Technologies |
|---|---|
| **Frontend** | React + Vite |
| **Backend** | FastAPI · Node/Express |
| **Persistence** | MongoDB |
| **AI / Intelligence** | RAG · Embeddings · LangChain · LangGraph · Multiagent orchestration |
| **Infrastructure** | Docker · Railway |

<br/>

---

<br/>

## Published Projects

<br/>

### 01 — Yafah

> *AI-powered consulting platform for women entrepreneurs in the beauty and luxury sector.*

Yafah combines refined branding with practical intelligence for marketing, content, contextual knowledge, and financial visibility. It is the most mature product in this ecosystem in terms of full-stack execution.

**Core features:**
- Dashboard with dedicated areas for chat, Instagram, TikTok, website, knowledge base, and finances
- FastAPI backend with routes for auth, registration, chat, admin, feedback, knowledge base, and metrics
- RAG and contextual memory to personalize responses based on each user's history
- Full deployment structure with documentation and configuration

**Stack:** `React` `FastAPI` `MongoDB` `LangChain` `FAISS` `Gemini / OpenRouter` `Docker`

**Status:** `MVP` — Backend, frontend, execution documentation, and deploy organization in place.

<br/>

---

<br/>

### 02 — O Chefe

> *Multi-agent system for church management, member relations, and institutional operations at ADMAV.*

At the core of this project is a specialized agent architecture that combines registration, attendance, institutional RAG, automatic devotionals, and per-unit context — all built to serve a distributed, multi-branch religious network.

**Core features:**
- FastAPI backend with modular architecture under `app/`
- LangGraph orchestration with agents: `CadastroAgent`, `WelcomeAgent`, `DevotionalAgent`, `RAGAgent`, `EngagementAgent`, `SecretaryAgent`
- MongoDB collections for members, knowledge base, and interactions
- APScheduler for automated flows such as recurring devotionals
- Initial React frontend for member registration integrated directly with the API

**Stack:** `React` `FastAPI` `LangGraph` `MongoDB` `APScheduler` `Docker`

**Status:** `Active` — Backend well-structured with solid domain context. Frontend functional, still evolving.

<br/>

---

<br/>

### 03 — Kairos

> *Visual concept and digital identity for a creative front aimed at the Christian and institutional context.*

In this portfolio scope, only the main visual prototype was retained — the one that registers the aesthetic direction and the experience proposal. No interface can be reduced to its functional layer alone; Kairos exists here as a record of that conviction.

**Core features:**
- Static prototype with editorial visual language
- Interface designed for login, registration, and institutional onboarding
- Exploration of branding, typography, and visual atmosphere with strong creative direction

**Status:** `Exploration` — The full-stack scaffold exists locally but is not yet ready for public presentation.

<br/>

---

<br/>

## Out of Scope — Mapped but Not Published

Not everything in the original folder was published here. Some material is still visual reference, initial study, or technical draft without enough density for public portfolio.

**Deliberately left out:**

- **Ezer** — contains only reference and visual support material at this stage
- **Official site** — still closer to a study than a presentable implementation
- Loose experiment files, isolated mocks, and screens not integrated into any main product flow

<br/>

---

<br/>

## Curation Criteria

The rule was simple: **publish what helps someone understand vision, architecture, and execution capacity. Do not publish what adds noise or risk.**

**Kept:**
- Relevant source code
- Backend and frontend structures that demonstrate the product proposition
- Existing documentation and configuration files useful for understanding the project
- Artifacts that demonstrate product direction and technical solutions

**Omitted:**
- `.env` files and credentials
- API keys exposed in local files
- `node_modules`, builds, caches, logs, and local databases
- Machine learning artifacts and execution-generated files
- Folders with visual reference material only

<br/>

---

<br/>

## Repository Structure

```text
.
├── README.md
│
├── Yafah/                  ← AI consulting platform for the beauty sector
│   ├── backend/
│   └── frontend/
│
├── O chefe/                ← Multi-agent church management system
│   ├── app/
│   └── frontend/
│
└── kairos/                 ← Visual concept and institutional identity
    └── prototype/
```

<br/>

---

<br/>

## Final Notes

<div align="center">

*This repository is a curated version of the work — designed for public presentation on GitHub.*

*Some projects continue to evolve locally and may contain open paths,*
*but the set already shows with clarity the product lines, technical decisions,*
*and the type of solution being built.*

<br/>

As maturity grows, the natural next step is splitting the most advanced projects into their own repositories. For now, this portfolio works as a consolidated window into the ecosystem.

<br/>

---

**ADMAV Ecosystem** · Built with intentionality.

</div>
