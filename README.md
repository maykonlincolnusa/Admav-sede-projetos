<div align="center">

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=42&duration=1&pause=1000&color=FFFFFF&center=true&vCenter=true&repeat=false&width=500&height=80&lines=ADMAV">
  <img src="https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=42&duration=1&pause=1000&color=0a0a0a&center=true&vCenter=true&repeat=false&width=500&height=80&lines=ADMAV" alt="ADMAV" />
</picture>

<br/>

<p align="center">
  <sub>ASSEMBLEIA DE DEUS · ADMAV SEDE</sub>
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Ecossistema%20Digital-Portfólio%20Institucional-0a0a0a?style=flat-square&labelColor=0a0a0a&color=0a0a0a" />
  &nbsp;
  <img src="https://img.shields.io/badge/Versão-2025-0a0a0a?style=flat-square&labelColor=0a0a0a&color=3b3b3b" />
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
</p>

</div>

<br/>
<br/>

---

<br/>

## Apresentação

Este repositório reúne, em formato de portfólio institucional, os projetos e protótipos desenvolvidos no ecossistema digital da ADMAV. Não se trata de um repositório de código aberto genérico — é um registro organizado de um conjunto coerente de produtos, construídos com arquitetura de software profissional e aplicados diretamente à operação e à identidade de uma rede de igrejas.

Cada projeto aqui documentado tem um propósito claro dentro do ecossistema: alguns já operam como MVPs funcionais, outros estão em fase de validação arquitetural ou exploração de produto. Em todos os casos, a curadoria segue o mesmo princípio: **publicar o que demonstra visão, decisão técnica e capacidade de execução.**

<br/>

---

<br/>

## Arquitetura do Ecossistema

O portfólio é estruturado em torno de três eixos estratégicos:

<br/>

| Eixo | Descrição |
|:---|:---|
| **Inteligência Operacional** | IA aplicada a atendimento, gestão de membros e automação de processos institucionais |
| **Produtos Internos** | Sistemas com memória semântica, orquestração multiagente e experiência assistida |
| **Identidade Digital** | Interfaces com posicionamento visual sólido e linguagem de marca consistente |

<br/>

**Padrão técnico recorrente:**

```
Frontend    →   React + Vite + TailwindCSS
Backend     →   FastAPI · Node/Express
Persistência →  MongoDB
IA          →   RAG · Embeddings · LangChain · LangGraph · Orquestração Multiagente
Infra       →   Docker · Railway
```

<br/>

---

<br/>

## Portfólio de Projetos

<br/>

### `01` &nbsp; Yafah

**Plataforma de consultoria orientada por IA para o setor de beleza e luxo**

Yafah é o projeto de maior maturidade no portfólio. Voltado para empreendedoras do setor de beleza, entrega inteligência prática para tomada de decisão em marketing, conteúdo, gestão financeira e conhecimento de contexto — com branding refinado e experiência centrada na usuária.

<br/>

| Componente | Detalhes |
|:---|:---|
| **Interface** | Dashboard modular com chat, Instagram, TikTok, site, knowledge base e finanças |
| **Backend** | FastAPI com rotas para autenticação, cadastro, chat, administração, feedback e métricas |
| **Inteligência** | RAG com memória contextual para personalização baseada no histórico da usuária |
| **Infraestrutura** | Deploy documentado com Docker e Railway |

<br/>

<p>
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=flat-square&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/FAISS-FF6F00?style=flat-square&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Status-MVP%20Funcional-2ea44f?style=flat-square" />
</p>

<br/>

---

<br/>

### `02` &nbsp; O Chefe

**Sistema multiagente para gestão institucional e relacionamento com membros da ADMAV**

O Chefe é a camada de inteligência operacional da ADMAV. Sua arquitetura de agentes especializados cobre o ciclo completo de engajamento de membros — do cadastro ao acompanhamento pastoral — com automação de fluxos, memória institucional via RAG e suporte a múltiplas unidades da rede.

<br/>

| Componente | Detalhes |
|:---|:---|
| **Arquitetura** | FastAPI modular em `app/` com separação clara de domínios |
| **Agentes** | `CadastroAgent` · `WelcomeAgent` · `DevotionalAgent` · `RAGAgent` · `EngagementAgent` · `SecretaryAgent` |
| **Persistência** | MongoDB com coleções para membros, base de conhecimento e histórico de interações |
| **Automação** | APScheduler para devocionais recorrentes e fluxos programados |
| **Interface** | Frontend React para cadastro de membros com integração direta à API |

<br/>

<p>
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=flat-square&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento%20Ativo-0075ca?style=flat-square" />
</p>

<br/>

---

<br/>

### `03` &nbsp; Site Oficial ADMAV

**Presença digital institucional da Assembleia de Deus do Ministério Água Viva**

O site oficial é a interface pública da rede — o primeiro ponto de contato digital para visitantes, novos membros e parceiros institucionais. Mais do que uma página informativa, é uma experiência de identidade: transmite propósito, organização e acolhimento desde o primeiro acesso, alinhada ao posicionamento da ADMAV como rede com presença estruturada e profissional.

<br/>

| Componente | Detalhes |
|:---|:---|
| **Identidade** | Visual coeso alinhado ao branding institucional da ADMAV |
| **Conteúdo** | Apresentação da rede, programação, liderança e localização das unidades |
| **Integração** | Arquitetura planejada para conexão com O Chefe e Kairos |
| **Qualidade** | Foco em performance, acessibilidade e SEO desde a base |
| **Escalabilidade** | Estrutura preparada para CMS e gestão de conteúdo dinâmico |

<br/>

<p>
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-e3b341?style=flat-square" />
</p>

<br/>

---

<br/>

### `04` &nbsp; Kairos

**Identidade digital e conceito de produto para comunicação institucional cristã**

Kairos é a frente criativa do ecossistema — um projeto orientado por identidade visual, atmosfera e posicionamento editorial. O recorte publicado aqui preserva o protótipo principal: o artefato que registra com precisão a direção estética e a proposta de experiência que guia o produto.

<br/>

| Componente | Detalhes |
|:---|:---|
| **Protótipo** | Interface estática com linguagem visual editorial |
| **Escopo** | Fluxos de login, cadastro e ambientação institucional |
| **Direção** | Exploração intensa de branding, tipografia e atmosfera visual |

<br/>

<p>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" />
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Status-Exploração%20Visual-8b949e?style=flat-square" />
</p>

<br/>

---

<br/>

## Critério de Curadoria

<br/>

> *"Publicar o que demonstra visão, decisão técnica e capacidade de execução. Omitir o que apenas adiciona ruído."*

<br/>

**O que foi publicado:**

- Código-fonte relevante de backend e frontend
- Estruturas de projeto que evidenciam a proposta de cada produto
- Documentação existente e arquivos de configuração pertinentes
- Artefatos que demonstram direção de produto e solução técnica aplicada

**O que foi omitido:**

- Arquivos `.env`, credenciais e chaves de API
- `node_modules`, builds, caches, logs e bancos de dados locais
- Artefatos de machine learning e arquivos gerados em execução
- Material de referência visual sem contexto de implementação
- Projetos em estágio de rascunho sem densidade suficiente para apresentação pública

<br/>

---

<br/>

## Estrutura do Repositório

```
admav-portfolio/
│
├── README.md
│
├── Yafah/                         # Consultoria com IA · Setor de beleza e luxo
│   ├── backend/                   # FastAPI · Rotas · Agentes · RAG
│   └── frontend/                  # React · Dashboard modular
│
├── O chefe/                       # Gestão institucional · Multiagente
│   ├── app/                       # FastAPI · LangGraph · Agentes especializados
│   └── frontend/                  # React · Interface de cadastro
│
├── site-oficial/                  # Presença digital · ADMAV
│   ├── src/                       # React · Vite · TailwindCSS
│   └── public/                    # Assets institucionais
│
└── kairos/                        # Identidade e conceito · Comunicação cristã
    └── prototype/                 # Protótipo visual estático
```

<br/>

---

<br/>

## Projetos Fora do Escopo Desta Publicação

Os itens abaixo existem no ecossistema local, mas foram deliberadamente excluídos desta publicação por não atingirem o nível de maturidade exigido para apresentação pública:

- **Ezer** — contém exclusivamente material de apoio e referência visual nesta fase
- Experimentos isolados, mocks desconectados e telas sem integração ao fluxo principal dos produtos

<br/>

---

<br/>

<div align="center">

<br/>

**ADMAV · Ecossistema Digital Institucional**

<sub>Este repositório é uma versão curada do trabalho em andamento.<br/>Projetos maduros serão progressivamente migrados para repositórios independentes.</sub>

<br/>

---

<sub>Construído com intencionalidade · © 2025 ADMAV</sub>

<br/>

</div>
