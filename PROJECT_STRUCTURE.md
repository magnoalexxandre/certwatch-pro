# Estrutura do Projeto — CertMonitor

```
certwatch-pro/
│
├── .env.example                 # Template de variáveis de ambiente
├── .env                         # Segredos (não versionado)
├── .gitignore
├── docker-compose.yml           # Stack: certmonitor + PostgreSQL
│
├── README.md
├── QUICKSTART.md
├── ARCHITECTURE.md
├── PROJECT_STRUCTURE.md
├── CHANGELOG.md
│
├── server/                      # SERVIDOR CENTRAL
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # FastAPI: rotas, auth, dashboard
│   ├── database.py              # Pool PostgreSQL + queries
│   ├── notifier.py              # Email · Google Chat · Telegram
│   └── templates/
│       ├── login.html           # Tela de login
│       └── index.html           # Dashboard principal
│
├── agent/                       # AGENTE CLIENTE
│   ├── agent.py                 # Scanner + reporter
│   ├── agent_config.yml         # Configuração (server_url, scan_paths...)
│   ├── requirements.txt
│   ├── install_linux.sh         # Instala como serviço systemd
│   └── install_windows.bat      # Instala como serviço Windows
│
└── config/                      # CONFIGURAÇÕES DO SERVIDOR
    └── config.yml               # Alertas e notificações (email, chat...)
```

---

## Arquivos principais

### `docker-compose.yml`
Define dois serviços:
- `certmonitor` — o servidor FastAPI (porta 8000)
- `db` — PostgreSQL 16 com volume persistente

Ambos consomem o `.env` para segredos.

### `server/main.py`
- Middleware de sessão (`SessionMiddleware`)
- Rotas de auth: `GET/POST /login`, `GET /logout`
- Dashboard: `GET /` (requer login)
- API dos agentes: `POST /api/report` (requer `X-API-Token`)
- `GET /health`

### `server/database.py`
- `init_db()` — cria pool e executa migrations
- `upsert_report()` — substitui certificados do hostname
- `get_all_certificates()` — todos os registros
- `get_stats()` — contagens por status
- `get_agent_status()` — último report por hostname

### `server/notifier.py`
- `check_and_notify()` — ponto de entrada chamado após cada report
- Rate-limit de 1 hora (variável em memória)
- Suporte a Email (smtplib), Google Chat (webhook), Telegram (bot API)

### `agent/agent_config.yml`
```yaml
server_url: http://IP-DO-SERVIDOR:8000
api_token: mesmo-token-do-env
scan_paths:
  - /etc/haproxy/certs
scan_interval: 3600   # segundos
mode: daemon
```

### `config/config.yml`
```yaml
alert_days: [30, 20, 10, 7, 3, 1]
notifications:
  email:      { enabled: false, ... }
  google_chat:{ enabled: false, webhook_url: ... }
  telegram:   { enabled: false, ... }
```

---

## Fluxo de segredos

```
.env
 ├── API_TOKEN        → docker-compose → certmonitor env → main.py
 ├── ADMIN_PASSWORD   → docker-compose → certmonitor env → main.py (hash bcrypt)
 ├── SECRET_KEY       → docker-compose → certmonitor env → SessionMiddleware
 ├── POSTGRES_*       → docker-compose → db env + DATABASE_URL → database.py
 └── (nunca commitado — está no .gitignore)
```

---

## API Endpoints

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `GET` | `/login` | — | Tela de login |
| `POST` | `/login` | — | Autenticação |
| `GET` | `/logout` | Sessão | Encerra sessão |
| `GET` | `/` | Sessão | Dashboard |
| `POST` | `/api/report` | X-API-Token | Recebe dados do agente |
| `GET` | `/health` | — | Health check |
