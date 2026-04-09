# Portfólio ADMAV

Este repositório organiza, em formato de portfólio, os principais projetos e protótipos desenvolvidos no ecossistema ADMAV. A proposta aqui não é publicar tudo o que existe na pasta original, mas registrar com clareza o contexto dos trabalhos, a direção de produto e o recorte técnico que faz sentido mostrar publicamente.

Alguns projetos já estão em estágio de MVP funcional. Outros ainda estão em exploração visual, validação de arquitetura ou prototipação. Por isso, este repositório funciona como um snapshot curado do que vale apresentar no GitHub neste momento.

## Visão Geral

Os projetos reunidos aqui orbitam três frentes principais:

- IA aplicada a atendimento, operação e inteligência de contexto.
- Produtos internos com foco em automação, memória semântica e experiência assistida.
- Interfaces premium para nichos específicos, com forte preocupação de posicionamento e identidade visual.

Em termos técnicos, existe um padrão recorrente no portfólio:

- Frontend com React + Vite.
- Backends em FastAPI ou Node/Express.
- Persistência com MongoDB.
- Recursos de IA com RAG, embeddings, orquestração multiagente e integrações com modelos generativos.
- Empacotamento para deploy com Docker e, em alguns casos, organização para Railway.

## Projetos Publicados

### 1. Yafah

Plataforma de consultoria orientada por IA para empreendedoras do setor de beleza e luxo. O projeto combina branding mais refinado com recursos de inteligência prática para marketing, conteúdo, conhecimento contextual e visão financeira.

Principais características:

- Dashboard com áreas para chat, Instagram, TikTok, site, base de conhecimento e finanças.
- Backend em FastAPI com rotas para autenticação, cadastro, chat, administração, feedback, knowledge base e métricas.
- Uso de RAG e memória contextual para personalizar respostas ao histórico da usuária.
- Stack com React, FastAPI, MongoDB, LangChain, FAISS, Gemini/OpenRouter e Docker.

Status atual:

- É o projeto mais maduro do conjunto em termos de produto full stack.
- Já possui estrutura de backend, frontend, documentação de execução e organização de deploy.

### 2. O chefe

Sistema multiagente voltado para gestão de igreja, relacionamento com membros e operação institucional da ADMAV. O núcleo do projeto é uma arquitetura de agentes especializados que combinam cadastro, atendimento, RAG institucional, devocionais automáticos e contexto por unidade.

Principais características:

- Backend em FastAPI com arquitetura modular em `app/`.
- Orquestração com LangGraph e agentes como `CadastroAgent`, `WelcomeAgent`, `DevotionalAgent`, `RAGAgent`, `EngagementAgent` e `SecretaryAgent`.
- Persistência em MongoDB com coleções para membros, base de conhecimento e interações.
- Scheduler com APScheduler para fluxos automáticos, como devocionais recorrentes.
- Frontend inicial em React para cadastro de membros e integração direta com a API.

Status atual:

- Backend bem estruturado e com contexto de domínio mais sólido.
- Frontend ainda está em estágio inicial e funcional, sem o mesmo nível de acabamento do backend.

### 3. Kairos

Conceito de produto e identidade digital para uma frente criativa voltada ao contexto cristão/institucional. Neste recorte de portfólio, foi mantido apenas o protótipo visual principal, que registra a direção estética e a proposta de experiência.

Principais características:

- Protótipo estático com linguagem visual editorial e interface pensada para login, cadastro e ambientação institucional.
- Exploração de branding, tipografia e atmosfera visual com forte apelo de direção criativa.

Status atual:

- Projeto em fase de exploração.
- O scaffold full stack existente localmente ainda não está maduro o suficiente para entrar como peça principal do portfólio e, por isso, não foi priorizado nesta publicação.

## Projetos Mapeados, Mas Fora do Escopo Desta Publicação

Nem tudo o que existe na pasta original foi publicado neste repositório. Parte do material ainda é referência visual, estudo inicial ou rascunho técnico sem densidade suficiente para portfólio público.

Itens deliberadamente deixados de fora:

- `Ezer`, por conter apenas material de apoio e referência visual nesta fase.
- `site oficial`, pelo mesmo motivo: ainda está mais próximo de estudo do que de implementação apresentável.
- Arquivos soltos de experimento, mocks isolados e telas não integradas ao fluxo principal dos produtos.

## Critério de Curadoria

Para este repositório, a curadoria seguiu uma regra simples: publicar o que ajuda a entender visão, arquitetura e capacidade de execução, e não publicar o que só adiciona ruído ou risco.

Foi mantido:

- Código-fonte relevante.
- Estruturas de backend e frontend que mostram a proposta dos produtos.
- Documentação já existente e arquivos de configuração úteis para compreensão do projeto.
- Artefatos que ajudam a demonstrar direção de produto e solução técnica.

Foi omitido:

- Arquivos `.env` e credenciais.
- Chaves de API expostas em arquivos locais.
- `node_modules`, builds, caches, logs e bancos locais.
- Artefatos de machine learning e arquivos gerados em execução.
- Pastas com material apenas de referência visual.

## Estrutura Publicada

```text
.
├── README.md
├── Yafah/
├── O chefe/
└── kairos/
```

## Observações Finais

Este repositório representa uma versão curada do trabalho, pensada para apresentação pública no GitHub. Alguns projetos ainda evoluem localmente e podem conter caminhos em aberto, mas o conjunto já mostra com clareza as linhas de produto, as decisões técnicas e o tipo de solução que vem sendo construído.

Se a evolução continuar, a tendência natural é separar os projetos mais maduros em repositórios próprios. Por enquanto, este portfólio funciona como uma vitrine consolidada do ecossistema.
