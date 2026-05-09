# CLAUDE.md — NetMapper

> Guia de contexto para o Claude Code trabalhar neste repositório.

---

## O que é este projeto

**NetMapper** é uma aplicação web para medir e historiar a velocidade da conexão (download, upload, ping, jitter) por ambiente físico (cômodo). Roda inteiramente em Docker com três containers independentes: banco PostgreSQL, API FastAPI e frontend VueJS 3.

Stack principal: Python 3.12 · FastAPI · SQLAlchemy · Alembic · PostgreSQL 16 · VueJS 3 · Vite · Pinia · Chart.js · LibreSpeed JS.

---

## Estrutura do Repositório

```
NetMapper/
├── docker-compose.yml       # orquestra os 3 containers
├── .env                     # variáveis de ambiente — NÃO commitar
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh        # roda alembic upgrade head antes de subir o uvicorn
│   ├── requirements.txt
│   ├── alembic.ini          # configuração do Alembic
│   ├── alembic/
│   │   ├── env.py           # lê DATABASE_URL do ambiente e detecta modelos
│   │   ├── script.py.mako   # template de novas migrations
│   │   └── versions/        # migrations versionadas
│   │       └── 0001_create_initial_tables.py
│   ├── main.py              # inicialização do FastAPI
│   ├── database.py          # engine + sessão SQLAlchemy
│   ├── models/              # User, Room, Measurement (SQLAlchemy)
│   ├── schemas/             # contratos Pydantic (auth, room, measurement)
│   ├── routers/             # auth, rooms, measurements, speedtest
│   ├── services/
│   │   └── auth_service.py  # bcrypt + JWT
│   └── assets/
│       └── garbage.bin      # ~10 MB para teste de download (não versionado)
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── public/
    │   └── librespeed/
    │       └── librespeed.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/index.js
        ├── stores/           # auth.js, measurements.js (Pinia)
        ├── services/api.js   # Axios + interceptor JWT
        ├── views/            # Login, Register, SpeedTest, Dashboard, Rooms
        └── components/       # SpeedGauge, LineChart, BarChart, HeatMap
```

---

## Subir o Projeto

```bash
# Primeira vez
docker compose up --build

# Próximas vezes
docker compose up

# Background
docker compose up -d

# Derrubar
docker compose down

# Derrubar e apagar dados do banco
docker compose down -v
```

| Serviço     | URL                        |
|-------------|----------------------------|
| Frontend    | http://localhost:5173      |
| Backend     | http://localhost:8000      |
| Swagger UI  | http://localhost:8000/docs |
| PostgreSQL  | localhost:5432             |

---

## Variáveis de Ambiente (`.env`)

Crie na **raiz do projeto** antes de subir:

```env
POSTGRES_DB=netmapper
POSTGRES_USER=netmapper_user
POSTGRES_PASSWORD=netmapper_pass
DATABASE_URL=postgresql://netmapper_user:netmapper_pass@db:5432/netmapper

SECRET_KEY=troque_isso_por_uma_chave_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> O host do banco é `db` (nome do serviço no Compose), não `localhost`.

---

## Modelo de Dados

```
users (id, name, email, password_hash, created_at)
  └── rooms (id, user_id FK, name, created_at)
        └── measurements (id, user_id FK, room_id FK,
                          download_mbps, upload_mbps,
                          ping_ms, jitter_ms, measured_at)
```

---

## API — Endpoints

### Autenticação (sem JWT)
| Método | Rota             | Descrição               |
|--------|------------------|-------------------------|
| POST   | `/auth/register` | Cadastra novo usuário   |
| POST   | `/auth/login`    | Login, retorna token JWT|

### Cômodos (JWT obrigatório)
| Método | Rota           | Descrição              |
|--------|----------------|------------------------|
| GET    | `/rooms`       | Lista cômodos do usuário |
| POST   | `/rooms`       | Cria novo cômodo       |
| DELETE | `/rooms/{id}`  | Remove um cômodo       |

### Medições (JWT obrigatório)
| Método | Rota                        | Descrição              |
|--------|-----------------------------|------------------------|
| POST   | `/measurements`             | Salva resultado        |
| GET    | `/measurements`             | Histórico completo     |
| GET    | `/measurements?room_id=1`   | Filtrado por cômodo    |

### LibreSpeed — Teste de velocidade
| Método | Rota                  | Descrição                        |
|--------|-----------------------|----------------------------------|
| GET    | `/backend/garbage`    | Arquivo ~10 MB para medir download |
| POST   | `/backend/empty`      | Endpoint vazio para medir upload |
| GET    | `/backend/getIp`      | Retorna IP do cliente            |

---

## Autenticação JWT — Fluxo

```
POST /auth/login → { email, senha }
  → backend valida senha com bcrypt
  → gera token JWT assinado com SECRET_KEY
  → frontend salva token no Pinia
  → toda rota protegida envia: Authorization: Bearer <token>
  → FastAPI valida antes de processar
```

---

## Fluxo do Teste de Velocidade

```
Usuário seleciona cômodo → clica "Iniciar Teste"
  → LibreSpeed JS faz requisições para /backend/*
  → SpeedGauge.vue anima em tempo real (download → upload → ping)
  → ao finalizar: POST /measurements com JWT no header
  → Dashboard atualiza gráficos automaticamente
```

---

## Frontend — Telas e Componentes

| Arquivo              | Função                                           |
|----------------------|--------------------------------------------------|
| `Login.vue`          | Formulário de login, salva JWT no Pinia          |
| `Register.vue`       | Cadastro de novo usuário                         |
| `Rooms.vue`          | CRUD de cômodos                                  |
| `SpeedTest.vue`      | Seleção de cômodo + execução do teste            |
| `Dashboard.vue`      | Gráficos de histórico                            |
| `SpeedGauge.vue`     | Velocímetro animado em tempo real                |
| `LineChart.vue`      | Download/upload ao longo do tempo                |
| `BarChart.vue`       | Média por cômodo (comparativo)                   |
| `HeatMap.vue`        | Horário × velocidade (mapa de calor)             |

---

## Migrations — Alembic

### Como funciona
O `entrypoint.sh` do container backend executa `alembic upgrade head` antes de iniciar o uvicorn. Isso garante que o banco esteja sempre na versão mais recente sem intervenção manual.

### Criar uma nova migration
```bash
# Dentro do container backend
docker compose exec backend alembic revision --autogenerate -m "descricao_da_mudanca"

# Ou localmente (com DATABASE_URL apontando para o banco)
cd backend
alembic revision --autogenerate -m "descricao_da_mudanca"
```

### Aplicar migrations manualmente
```bash
docker compose exec backend alembic upgrade head
```

### Reverter uma migration
```bash
docker compose exec backend alembic downgrade -1
```

### Ver histórico de versões
```bash
docker compose exec backend alembic history --verbose
docker compose exec backend alembic current
```

### Regras
- **Nunca altere o banco diretamente** — sempre via migration.
- Os arquivos em `alembic/versions/` são commitados no git e representam o histórico do schema.
- O `garbage.bin` não é versionado (gerado com `dd if=/dev/urandom of=assets/garbage.bin bs=1M count=10`).

---

## Convenções e Decisões de Projeto

- **Sem APIs externas pagas** — o teste de velocidade usa LibreSpeed JS apontando para os próprios endpoints do backend.
- **Migrations via Alembic** — nunca altere o banco diretamente; crie uma migration.
- **Senhas nunca em texto puro** — sempre hashear com `bcrypt` antes de persistir.
- **CORS configurado no `main.py`** — ajuste a lista de origens permitidas conforme o ambiente.
- **`garbage.bin`** deve ter ~10 MB de dados aleatórios; gere com `dd if=/dev/urandom of=assets/garbage.bin bs=1M count=10`.
- **Guards de rota no Vue Router** — rotas protegidas redirecionam para `/login` se não houver token.
- **Axios interceptor** em `services/api.js` injeta o JWT em todas as requisições autenticadas automaticamente.
- **Volume `/app/node_modules`** no Compose evita que o bind mount do host sobrescreva os módulos instalados dentro do container frontend.
- **`--host` no Vite** é obrigatório para o servidor aceitar conexões de fora do container.
- **`healthcheck` no container `db`** garante que o backend só inicia após o PostgreSQL estar pronto.
- **`entrypoint.sh`** garante que `alembic upgrade head` rode antes do uvicorn — nunca pule esse passo.

---

## Dependências Principais

### Backend (`requirements.txt`)
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

### Frontend (`npm`)
```
vue@3 · vite · vue-router@4 · pinia · axios · chart.js · vue-chartjs
```
> LibreSpeed JS: baixar em https://github.com/librespeed/speedtest e colocar em `frontend/public/librespeed/librespeed.js`.

---

## Divisão de Responsabilidades

| Frente | Escopo |
|--------|--------|
| 🟦 Banco de Dados (R1) | `docker-compose.yml` (serviço db), `database.py`, models SQLAlchemy, migrations Alembic |
| 🟩 Backend (R2) | FastAPI, todos os routers, `auth_service.py`, `garbage.bin`, Swagger |
| 🟨 Frontend (R3) | VueJS 3, Vite, Pinia, Axios, LibreSpeed JS, Chart.js, todas as views e components |

---

## Contexto Acadêmico

- **Disciplina:** Desenvolvimento de Projeto 1  
- **Instituição:** UTFPR — Câmpus Ponta Grossa  
- **Período:** 1/2026