# 📡 NetMapper
### Monitoramento de Velocidade de Rede por Ambientes

> Projeto universitário — Python (FastAPI) + VueJS 3 + PostgreSQL + Docker

---

## 🧭 Proposta do Projeto

O **NetMapper** é uma aplicação web que permite medir a velocidade da conexão com a internet (download, upload, ping e jitter) diretamente pelo navegador, sem depender de APIs externas pagas.

As medições são categorizadas por **ambientes** (ex: Sala de Reunião, Escritório, Cozinha) e mantêm um **histórico completo** visualizado em gráficos interativos. O sistema suporta múltiplos usuários com autenticação segura via JWT.

Todo o projeto sobe com **um único comando Docker**, isolando banco, backend e frontend em containers independentes.

---

## 🗂️ Estrutura do Repositório

```
NetMapper/
├── docker-compose.yml       ← orquestra os 3 containers
├── .env                     ← variáveis de ambiente (não commitar)
├── .gitignore
│
├── backend/                 ← API Python + FastAPI
│   ├── Dockerfile
│   └── ...
│
└── frontend/                ← Interface VueJS 3
    ├── Dockerfile
    └── ...
```

---

## 🐳 Subindo o Projeto com Docker

### Pré-requisitos
- [Docker](https://www.docker.com/) instalado
- Docker Compose (já incluso no Docker Desktop)

### Comandos

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd NetMapper

# Criar o arquivo .env na raiz (ver seção abaixo)

# Primeira vez — build e subida de todos os containers
docker compose up --build

# Próximas vezes
docker compose up

# Rodar em background
docker compose up -d

# Derrubar os containers
docker compose down

# Derrubar e apagar os dados do banco
docker compose down -v
```

### Serviços disponíveis após subir
| Serviço | URL |
|---|---|
| Frontend (VueJS) | http://localhost:5173 |
| Backend (FastAPI) | http://localhost:8000 |
| Documentação API | http://localhost:8000/docs |
| Banco (PostgreSQL) | localhost:5432 |

---

## ⚙️ Variáveis de Ambiente — `.env`

Crie este arquivo na **raiz do projeto** antes de subir os containers:

```env
# Banco de dados
POSTGRES_DB=netmapper
POSTGRES_USER=netmapper_user
POSTGRES_PASSWORD=netmapper_pass
DATABASE_URL=postgresql://netmapper_user:netmapper_pass@db:5432/netmapper

# JWT
SECRET_KEY=troque_isso_por_uma_chave_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ O host do banco é `db`, não `localhost` — é o nome do serviço definido no Docker Compose.

---

## 📁 `.gitignore`

```
# Python
venv/
__pycache__/
*.pyc
.env

# Node
node_modules/
dist/

# Banco local
*.db
```

---
---

## 🟦 FRENTE 1 — Banco de Dados

**Responsável:** Responsavel 1

### Objetivo
Definir e versionar toda a estrutura de dados do projeto. O banco roda em um container PostgreSQL gerenciado pelo backend via SQLAlchemy + Alembic.

### Tecnologias
| Tecnologia | Função |
|---|---|
| **PostgreSQL 16** | Banco relacional — roda via Docker, sem instalação local |
| **SQLAlchemy** | ORM — mapeia as tabelas como classes Python |
| **Alembic** | Migrations — versiona as mudanças no esquema do banco |
| **psycopg2-binary** | Driver de conexão Python ↔ PostgreSQL |

### Container — `docker-compose.yml`

O PostgreSQL **não precisa de Dockerfile próprio**. Sua configuração fica no Compose:

```yaml
db:
  image: postgres:16-alpine
  container_name: netmapper_db
  restart: always
  env_file: .env
  environment:
    POSTGRES_DB: ${POSTGRES_DB}
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
    interval: 10s
    timeout: 5s
    retries: 5
```

> O `healthcheck` garante que o backend só sobe **depois** que o banco estiver pronto para aceitar conexões.

### Modelo de Dados

```
┌──────────────────────────────┐
│           users              │
├──────────────────────────────┤
│ id            SERIAL PK      │
│ name          VARCHAR        │
│ email         VARCHAR UNIQUE │
│ password_hash VARCHAR        │
│ created_at    TIMESTAMP      │
└──────────────┬───────────────┘
               │ 1
               │ N
┌──────────────▼───────────────┐
│           rooms              │
├──────────────────────────────┤
│ id            SERIAL PK      │
│ user_id       FK → users.id  │
│ name          VARCHAR        │  ex: "Sala de Reunião", "Cozinha"
│ created_at    TIMESTAMP      │
└──────────────┬───────────────┘
               │ 1
               │ N
┌──────────────▼───────────────┐
│        measurements          │
├──────────────────────────────┤
│ id            SERIAL PK      │
│ user_id       FK → users.id  │
│ room_id       FK → rooms.id  │
│ download_mbps FLOAT          │
│ upload_mbps   FLOAT          │
│ ping_ms       FLOAT          │
│ jitter_ms     FLOAT          │
│ measured_at   TIMESTAMP      │
└──────────────────────────────┘
```

### Checklist
- [ ] Configurar serviço `db` no `docker-compose.yml`
- [ ] Criar o arquivo `.env` com as variáveis do banco
- [ ] Criar `backend/database.py` com engine e sessão SQLAlchemy
- [ ] Criar models: `User`, `Room`, `Measurement`
- [ ] Iniciar Alembic: `alembic init alembic`
- [ ] Gerar e rodar a primeira migration: `alembic upgrade head`
- [ ] Validar a conexão e a criação das tabelas no PostgreSQL

---
---

## 🟩 FRENTE 2 — Backend

**Responsável:** Responsavel 2

### Objetivo
Construir toda a API REST que serve o frontend: autenticação com JWT, CRUD de cômodos, histórico de medições e os endpoints que o **LibreSpeed JS** usa para realizar o teste de velocidade no browser do usuário.

### Tecnologias
| Tecnologia | Função |
|---|---|
| **FastAPI** | Framework principal da API |
| **Uvicorn** | Servidor ASGI que executa o FastAPI |
| **Pydantic** | Validação e serialização dos dados (schemas) |
| **SQLAlchemy** | ORM para comunicação com o PostgreSQL |
| **Alembic** | Migrations do banco |
| **python-jose** | Geração e validação de tokens JWT |
| **bcrypt** | Hash seguro de senhas |
| **psycopg2-binary** | Driver de conexão com o PostgreSQL |
| **python-multipart** | Suporte a recebimento de dados binários (teste de upload) |
| **python-dotenv** | Leitura do arquivo `.env` |

### `backend/requirements.txt`
```
fastapi
uvicorn
sqlalchemy
alembic
pydantic
python-jose[cryptography]
bcrypt
psycopg2-binary
python-multipart
python-dotenv
```

### `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Trecho no `docker-compose.yml`
```yaml
backend:
  build: ./backend
  container_name: netmapper_backend
  restart: always
  env_file: .env
  ports:
    - "8000:8000"
  volumes:
    - ./backend:/app
  depends_on:
    db:
      condition: service_healthy
```

### Estrutura de Pastas
```
backend/
├── Dockerfile
├── requirements.txt
├── main.py                  ← inicializa o FastAPI, CORS e routers
├── database.py              ← engine, sessão e Base do SQLAlchemy
│
├── models/                  ← tabelas mapeadas (SQLAlchemy)
│   ├── user.py
│   ├── room.py
│   └── measurement.py
│
├── schemas/                 ← contratos de entrada e saída (Pydantic)
│   ├── auth.py
│   ├── room.py
│   └── measurement.py
│
├── routers/                 ← rotas separadas por domínio
│   ├── auth.py              ← /auth/register  /auth/login
│   ├── rooms.py             ← /rooms (CRUD)
│   ├── measurements.py      ← /measurements
│   └── speedtest.py         ← /backend/garbage  /backend/empty  /backend/getIp
│
├── services/
│   └── auth_service.py      ← lógica de JWT e bcrypt
│
└── assets/
    └── garbage.bin          ← arquivo ~10MB para teste de download
```

### Endpoints da API

#### 🔐 Autenticação
| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/auth/register` | Cadastra novo usuário | ✗ |
| POST | `/auth/login` | Login — retorna token JWT | ✗ |

#### 🏠 Cômodos
| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/rooms` | Lista cômodos do usuário | ✔ JWT |
| POST | `/rooms` | Cria novo cômodo | ✔ JWT |
| DELETE | `/rooms/{id}` | Remove um cômodo | ✔ JWT |

#### 📊 Medições
| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/measurements` | Salva resultado de um teste | ✔ JWT |
| GET | `/measurements` | Lista histórico completo | ✔ JWT |
| GET | `/measurements?room_id=1` | Filtra por cômodo | ✔ JWT |

#### ⚡ LibreSpeed — Teste de Velocidade
| Método | Rota | Descrição |
|---|---|---|
| GET | `/backend/garbage` | Serve arquivo ~10MB para medir download |
| POST | `/backend/empty` | Endpoint vazio para medir upload |
| GET | `/backend/getIp` | Retorna o IP do cliente |

### Fluxo de Autenticação JWT
```
1. POST /auth/login  →  { email, senha }
2. Backend valida senha com bcrypt
3. Backend gera token JWT assinado com SECRET_KEY
4. Frontend recebe e armazena o token
5. Toda requisição protegida envia:
       Authorization: Bearer <token>
6. FastAPI valida o token antes de processar a rota
```

### Checklist
- [ ] Criar `backend/Dockerfile`
- [ ] Criar `requirements.txt` com todas as dependências
- [ ] Criar `main.py` com FastAPI, CORS e routers registrados
- [ ] Criar `database.py` lendo `DATABASE_URL` do `.env`
- [ ] Implementar `auth_service.py` (bcrypt + JWT)
- [ ] Criar routers: `auth`, `rooms`, `measurements`, `speedtest`
- [ ] Gerar `assets/garbage.bin` (~10MB) com dados aleatórios
- [ ] Testar todos os endpoints via Swagger: `http://localhost:8000/docs`

---
---

## 🟨 FRENTE 3 — Frontend

**Responsável:** Responsavel 3

### Objetivo
Construir a interface web completa: login, gerenciamento de cômodos, execução do teste de velocidade com LibreSpeed JS rodando no browser do usuário e dashboard com gráficos de análise histórica.

### Tecnologias
| Tecnologia | Função |
|---|---|
| **VueJS 3** | Framework frontend principal |
| **Vite** | Bundler e servidor de desenvolvimento |
| **Vue Router 4** | Navegação entre páginas (SPA) com guards de rota |
| **Pinia** | Gerenciamento de estado global (auth e medições) |
| **Axios** | Requisições HTTP com interceptor automático de JWT |
| **Chart.js + vue-chartjs** | Gráficos: linha, barra e mapa de calor |
| **LibreSpeed JS** | Realiza o teste de velocidade no browser do usuário |

### `frontend/Dockerfile`
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
```

> O `--host` é obrigatório para o Vite aceitar conexões de fora do container.

### Trecho no `docker-compose.yml`
```yaml
frontend:
  build: ./frontend
  container_name: netmapper_frontend
  restart: always
  ports:
    - "5173:5173"
  volumes:
    - ./frontend:/app
    - /app/node_modules
  depends_on:
    - backend
```

> O volume `/app/node_modules` evita que o bind mount sobrescreva os módulos instalados dentro do container.

### Instalação das Dependências
```bash
npm create vite@latest frontend -- --template vue
cd frontend
npm install axios pinia vue-router chart.js vue-chartjs
```

> Baixar o `librespeed.js` em `https://github.com/librespeed/speedtest`
> e colocar em `frontend/public/librespeed/`

### Estrutura de Pastas
```
frontend/
├── Dockerfile
├── package.json
├── vite.config.js
│
├── public/
│   └── librespeed/
│       └── librespeed.js        ← biblioteca do teste de velocidade
│
└── src/
    ├── main.js                  ← inicializa Vue, Router e Pinia
    ├── App.vue
    │
    ├── router/
    │   └── index.js             ← rotas com guards (redireciona se não logado)
    │
    ├── stores/
    │   ├── auth.js              ← armazena token JWT e dados do usuário
    │   └── measurements.js      ← histórico de medições
    │
    ├── services/
    │   └── api.js               ← Axios com interceptor de JWT
    │
    ├── views/
    │   ├── Login.vue            ← tela de login
    │   ├── Register.vue         ← tela de cadastro
    │   ├── SpeedTest.vue        ← execução do teste de velocidade
    │   ├── Dashboard.vue        ← gráficos e histórico
    │   └── Rooms.vue            ← gerenciar cômodos
    │
    └── components/
        ├── SpeedGauge.vue       ← velocímetro animado em tempo real
        ├── LineChart.vue        ← evolução da velocidade no tempo
        ├── BarChart.vue         ← comparativo entre cômodos
        └── HeatMap.vue          ← horário × velocidade (mapa de calor)
```

### Telas e Funcionalidades

#### Login / Register
- Formulário com email e senha
- Após login, JWT salvo no Pinia e redirecionamento ao Dashboard

#### SpeedTest.vue — Tela de Medição
```
1. Dropdown para selecionar o cômodo
2. Botão "Iniciar Teste"
3. LibreSpeed JS faz requisições para /backend/* do FastAPI
4. SpeedGauge.vue anima em tempo real: download → upload → ping
5. Ao finalizar → POST /measurements com os resultados
6. Exibe resultado final: download, upload, ping e jitter
```

#### Dashboard.vue — Gráficos
| Componente | Tipo | O que mostra |
|---|---|---|
| `LineChart.vue` | Linha | Download e upload ao longo do tempo |
| `BarChart.vue` | Barra | Média de velocidade por cômodo |
| `HeatMap.vue` | Mapa de calor | Horários com melhor e pior sinal |
| `SpeedGauge.vue` | Gauge | Velocidade em tempo real durante o teste |

### Fluxo Completo
```
Usuário faz login
      ↓
JWT salvo no Pinia
      ↓
Seleciona cômodo → clica "Iniciar Teste"
      ↓
LibreSpeed JS faz requisições para /backend/*
      ↓
Gauge anima em tempo real na tela
      ↓
Teste finaliza → POST /measurements (JWT no header)
      ↓
Dashboard atualiza os gráficos automaticamente
```

### Checklist
- [ ] Criar `frontend/Dockerfile`
- [ ] Criar projeto com Vite e instalar dependências npm
- [ ] Baixar e adicionar `librespeed.js` em `public/librespeed/`
- [ ] Configurar `services/api.js` com Axios + interceptor de JWT
- [ ] Configurar Vue Router com guards para rotas protegidas
- [ ] Criar stores de autenticação e medições com Pinia
- [ ] Criar telas: Login, Register, Rooms
- [ ] Integrar LibreSpeed JS na `SpeedTest.vue`
- [ ] Criar `SpeedGauge.vue` com animação em tempo real
- [ ] Criar Dashboard com os 4 gráficos via Chart.js
- [ ] Conectar todos os dados à API real

---
---

## 🐳 `docker-compose.yml` Completo

```yaml
services:

  db:
    image: postgres:16-alpine
    container_name: netmapper_db
    restart: always
    env_file: .env
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: netmapper_backend
    restart: always
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    container_name: netmapper_frontend
    restart: always
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## 👥 Integrantes

| Nome | Frente |
|----|---|
| R1 | 🟦 Banco de Dados |
| R2 | 🟩 Backend |
| R3 | 🟨 Frontend |

---

> **Disciplina:** Desenvolvimento de Projeto 1
> **Instituição:** UTFPR - PG
> **Período:** 1/2026
