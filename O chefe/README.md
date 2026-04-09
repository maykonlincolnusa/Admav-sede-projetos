# ADMAV AI CHURCH SYSTEM

Sistema multiagente para gestão de igreja com cadastro de membros, comunicação automatizada, memória institucional via RAG, devocionais automáticos e suporte a múltiplas unidades.

## Visão Geral

O projeto foi estruturado para atender o cenário ADMAV com:

- cadastro centralizado de membros
- mensagens automáticas de boas-vindas
- respostas orientadas por contexto da igreja via RAG
- geração de devocionais 3x por semana
- fluxo conversacional roteado por múltiplos agentes
- operação multi-unidades

## Stack

- Backend: Python + FastAPI
- Banco: MongoDB
- IA: LangChain + LangGraph
- Embeddings: Google, OpenAI ou HuggingFace
- Scheduler: APScheduler
- Frontend: React + Vite

## Unidades Atendidas

- ADMAV Sede
- ADMAV Freguesia
- ADMAV Colônia
- MAV Recreio
- ADMAV Campo Grande
- ADMAV Praça Seca

## Arquitetura

```text
Frontend React
    |
    v
FastAPI API
    |
    +-- /members
    +-- /chat
    +-- /rag/train
    +-- /devotional/send
    |
    v
LangGraph Orchestrator
    |
    +-- CadastroAgent
    +-- WelcomeAgent
    +-- DevotionalAgent
    +-- RAGAgent
    +-- EngagementAgent
    +-- SecretaryAgent
    |
    v
MongoDB
    |
    +-- members
    +-- knowledge_base
    +-- interactions
```

## Agentes

### `OrchestratorAgent`

- detecta intenção
- carrega contexto do membro no MongoDB
- consulta o RAG quando necessário
- encaminha o fluxo para o agente correto

### `CadastroAgent`

- orienta o processo de cadastro
- responde dúvidas sobre os dados obrigatórios

### `WelcomeAgent`

- gera mensagem de boas-vindas pastoral e acolhedora
- é acionado automaticamente após novo cadastro

### `DevotionalAgent`

- gera devocionais curtos com versículo, reflexão e aplicação
- é usado no envio manual e no agendamento automático

### `RAGAgent`

- consulta a base vetorial armazenada no MongoDB
- monta contexto semântico
- responde usando a memória da igreja

### `EngagementAgent`

- usa histórico recente de interações
- sugere ações de acompanhamento e retenção

### `SecretaryAgent`

- responde perguntas operacionais e administrativas
- usa contexto institucional oficial

## Estrutura do Projeto

```text
app/
  agents/
    base.py
    cadastro.py
    devotional.py
    engagement.py
    orchestrator.py
    rag_agent.py
    secretary.py
    welcome.py
  api/
    deps.py
    routes/
      chat.py
      devotional.py
      members.py
      rag.py
  core/
    logging.py
  db/
    mongo.py
    repositories.py
  rag/
    embeddings.py
    service.py
  services/
    communication_service.py
    container.py
    devotional_service.py
    interaction_service.py
    llm_service.py
    member_service.py
    orchestrator_service.py
  config.py
  constants.py
  main.py
  schemas.py
  scheduler.py

frontend/
  index.html
  package.json
  vite.config.js
  src/
    App.jsx
    main.jsx
    styles.css
```

## Collections MongoDB

### `members`

```json
{
  "_id": "ObjectId",
  "name": "string",
  "phone": "string",
  "email": "string|null",
  "birth_date": "date|null",
  "marital_status": "string|null",
  "address": "string|null",
  "unit": "string",
  "created_at": "datetime",
  "tags": [],
  "interactions": []
}
```

### `knowledge_base`

```json
{
  "_id": "ObjectId",
  "type": "string",
  "content": "string",
  "embedding": [],
  "unit": "string|null",
  "created_at": "datetime"
}
```

### `interactions`

```json
{
  "_id": "ObjectId",
  "member_id": "string|null",
  "message": "string",
  "response": "string",
  "timestamp": "datetime"
}
```

## Fluxos Principais

### Cadastro de membro

1. Cliente envia `POST /members`
2. FastAPI valida nome, telefone e unidade
3. Dados são gravados em `members`
4. `WelcomeAgent` gera a mensagem automática
5. A interação é registrada em `interactions`

### Chat com roteamento multiagente

1. Cliente envia `POST /chat`
2. O sistema verifica se a unidade foi informada
3. Se não houver unidade, retorna um menu com as 6 igrejas
4. Após identificar a unidade, `OrchestratorAgent` classifica a intenção
5. O estado do fluxo é roteado no LangGraph
6. O agente especializado gera a resposta
7. A interação é persistida no MongoDB

### RAG

1. Cliente envia documentos via `POST /rag/train`
2. O sistema gera embeddings
3. Vetores são salvos em `knowledge_base`
4. No chat, o sistema busca documentos semanticamente relevantes
5. O contexto recuperado alimenta a resposta final

### Devocional automático

1. APScheduler executa o job em `mon,wed,fri`
2. `DevotionalAgent` cria o conteúdo
3. O sistema envia para os membros da unidade
4. O disparo é registrado nas interações

## Requisitos

- Python 3.11+
- Node.js 20+
- MongoDB 7+ ou Docker

## Configuração

Copie o arquivo de ambiente:

```bash
copy .env.example .env
```

Principais variáveis:

- `LLM_PROVIDER`
- `GOOGLE_API_KEY`
- `GOOGLE_CHAT_MODEL`
- `GOOGLE_EMBEDDING_MODEL`
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `OPENAI_API_KEY`
- `OPENAI_CHAT_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `EMBEDDING_PROVIDER`
- `HUGGINGFACE_EMBEDDING_MODEL`
- `SCHEDULER_DEVOTIONAL_DAYS`
- `SCHEDULER_DEVOTIONAL_HOUR`

## Execução Local

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- App React: `http://localhost:5173`

## Docker

```bash
copy .env.example .env
docker compose up --build
```

Serviços:

- API FastAPI em `http://localhost:8000`
- MongoDB em `mongodb://localhost:27017`

## Endpoints

### `POST /members`

Cria um membro.

Payload:

```json
{
  "name": "Maria Silva",
  "phone": "+5521999999999",
  "email": "maria@email.com",
  "birth_date": "1992-05-12",
  "marital_status": "Casada",
  "address": "Rua Exemplo, 100",
  "unit": "ADMAV Sede"
}
```

### `GET /members`

Lista os membros cadastrados.

### `POST /chat`

Envia uma mensagem para o fluxo multiagente.

Se a unidade não for enviada e não puder ser inferida, a API retorna um menu inicial com as igrejas disponíveis.

Payload:

```json
{
  "message": "Quais são os horários dos cultos da ADMAV Sede?",
  "member_id": null,
  "unit": "ADMAV Sede"
}
```

Também aceita seleção por número quando o usuário responde ao menu:

```json
{
  "message": "1",
  "member_id": null,
  "unit": null
}
```

### `POST /rag/train`

Treina a base de conhecimento.

Payload:

```json
{
  "documents": [
    {
      "type": "schedule",
      "content": "A ADMAV Sede realiza culto aos domingos às 18h.",
      "unit": "ADMAV Sede"
    }
  ]
}
```

### `POST /devotional/send`

Dispara devocional manualmente.

Payload:

```json
{
  "unit": "ADMAV Sede"
}
```

## Frontend

O frontend inclui um formulário React com:

- nome
- telefone
- email
- data de nascimento
- estado civil
- endereço
- unidade

O envio é feito diretamente para `POST /members`.

## Scheduler

O agendamento usa APScheduler com trigger configurável por ambiente.

Padrão:

- segunda-feira
- quarta-feira
- sexta-feira
- 07:00

## Observações de Operação

- O sistema agora pode funcionar com Google Gemini ou OpenAI.
- O provedor de chat e agentes e definido em `LLM_PROVIDER`.
- Para usar Google, configure `GOOGLE_API_KEY` e opcionalmente `GOOGLE_CHAT_MODEL`.
- Para usar embeddings do Google, configure `EMBEDDING_PROVIDER=google`.
- Para trocar depois para OpenAI, altere `LLM_PROVIDER=openai` e configure `OPENAI_API_KEY`.
- O sistema ainda funciona com `HuggingFaceEmbeddings` sem chave OpenAI.
- O envio de mensagens está preparado via serviço interno de comunicação, com logging estruturado.
- O RAG usa busca semântica por similaridade cosseno sobre embeddings armazenados no MongoDB.

## Onde Esta a Integracao Google

- Chat e agentes: [app/services/llm_service.py](c:/Users/gomes/OneDrive/Área%20de%20Trabalho/O%20chefe/app/services/llm_service.py)
- Embeddings Google: [app/rag/embeddings.py](c:/Users/gomes/OneDrive/Área%20de%20Trabalho/O%20chefe/app/rag/embeddings.py)
- Variaveis de ambiente: [app/config.py](c:/Users/gomes/OneDrive/Área%20de%20Trabalho/O%20chefe/app/config.py)
- Exemplo de configuracao: [.env.example](c:/Users/gomes/OneDrive/Área%20de%20Trabalho/O%20chefe/.env.example)

## Validação Executada

```bash
python -m compileall app
```
