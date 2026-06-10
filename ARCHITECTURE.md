# Arquitetura — CertMonitor

## Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                    USUÁRIO (Navegador)                   │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP (via HAProxy → TLS)
                          ▼
┌─────────────────────────────────────────────────────────┐
│               SERVIDOR CENTRAL (Docker na VM)           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI + Uvicorn  (porta 8000)                 │  │
│  │                                                  │  │
│  │  GET  /login         → tela de login             │  │
│  │  POST /login         → autenticação              │  │
│  │  GET  /logout        → encerrar sessão           │  │
│  │  GET  /              → dashboard (requer login)  │  │
│  │  POST /api/report    → recebe dados dos agentes  │  │
│  │  GET  /health        → health check              │  │
│  └──────────────────────┬───────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────▼───────────────────────────┐  │
│  │  PostgreSQL 16                                   │  │
│  │  tabela: certificates                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────▲───────────────────────────────┘
                          │ POST /api/report
                          │ Header: X-API-Token
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼──────────┐         ┌──────────▼─────────┐
│  Agente — HOM      │         │  Agente — PROD      │
│  HAProxy HOM       │         │  HAProxy PROD       │
│  /etc/haproxy/certs│         │ /etc/haproxy/certs  │
│  (serviço systemd) │         │ (serviço systemd)   │
└────────────────────┘         └────────────────────┘
```

---

## Fluxo de Dados

```
1. ESCANEAMENTO (Agente — a cada scan_interval segundos)
   └── percorre scan_paths recursivamente
   └── filtra por extensões configuradas (.crt, .pem, .pfx...)
   └── faz parse de cada arquivo (PEM → DER → PFX)
   └── extrai: subject, issuer, not_before, not_after, fingerprint
   └── calcula: days_remaining = not_after − agora

2. ENVIO (Agente)
   └── POST /api/report
       Header: X-API-Token: <token>
       Body:   { hostname, certificates: [...], timestamp }

3. ARMAZENAMENTO (Servidor)
   └── valida token
   └── DELETE FROM certificates WHERE hostname = ?
   └── INSERT novo lote de certificados
   └── chama notifier.check_and_notify()

4. NOTIFICAÇÕES (Servidor — máx 1x por hora)
   └── filtra expirados / críticos / atenção
   └── envia Email SMTP  (se habilitado)
   └── envia Google Chat (se habilitado)
   └── envia Telegram    (se habilitado)

5. VISUALIZAÇÃO (Usuário)
   └── GET / → verifica sessão → redireciona /login se não autenticado
   └── dashboard renderizado server-side (Jinja2)
   └── auto-refresh a cada 5 minutos
```

---

## Componentes

### server/main.py
- Aplicação FastAPI principal
- Middleware de sessão (cookie assinado com `SECRET_KEY`)
- Autenticação do dashboard: `passlib[bcrypt]` + `SessionMiddleware`
- Autenticação dos agentes: header `X-API-Token`
- Rotas: login/logout, dashboard, `/api/report`, `/health`

### server/database.py
- Pool de conexões PostgreSQL (`psycopg2.pool.SimpleConnectionPool`)
- Inicialização do schema (`init_db`)
- Funções: `upsert_report`, `get_all_certificates`, `get_stats`, `get_agent_status`

### server/notifier.py
- Carrega `config/config.yml`
- Rate-limit: notifica no máximo uma vez por hora (variável em memória)
- Canais: Email SMTP (`smtplib`), Google Chat (webhook HTTP), Telegram (bot API)

### agent/agent.py
- Scanner recursivo de diretórios
- Parser de certificados: PEM, DER, PFX/P12
- Modo `daemon` (loop) ou `once`
- Envia `POST /api/report` com token

---

## Banco de Dados

### Schema

```sql
CREATE TABLE certificates (
    id             SERIAL PRIMARY KEY,
    hostname       VARCHAR(255) NOT NULL,
    path           TEXT NOT NULL,
    subject        TEXT,
    issuer         TEXT,
    not_before     TEXT,
    not_after      TEXT,
    days_remaining INTEGER,
    serial_number  TEXT,
    fingerprint    VARCHAR(64),
    cert_type      VARCHAR(50),
    last_update    TEXT
);

CREATE INDEX idx_cert_hostname ON certificates(hostname);
CREATE INDEX idx_cert_days     ON certificates(days_remaining);
```

### Estratégia de atualização

Cada report do agente faz `DELETE` dos certificados do hostname e reinsere o lote completo. Isso garante que certificados removidos do servidor somem automaticamente.

---

## Autenticação

### Dashboard (usuário)
```
Browser              FastAPI
  │  GET /               │
  ├──────────────────────► session["authenticated"] == True?
  │                       │  NÃO → redirect /login
  │  GET /login           │
  │◄──────────────────────┤
  │  POST /login          │
  │  {username, password} │
  ├──────────────────────► bcrypt.verify(password, hash)
  │                       │  OK → session["authenticated"] = True
  │  redirect /           │
  ◄──────────────────────┤
```

### Agentes (API)
```
Agent                FastAPI
  │  POST /api/report     │
  │  X-API-Token: <token> │
  ├──────────────────────► token == API_TOKEN?
  │                       │  NÃO → 401
  │  200 OK               │
  ◄──────────────────────┤
```

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `API_TOKEN` | Sim | Token compartilhado com os agentes |
| `ADMIN_USER` | Não | Usuário do dashboard (padrão: `admin`) |
| `ADMIN_PASSWORD` | Sim | Senha do dashboard |
| `SECRET_KEY` | Sim | Chave para assinar cookies de sessão |
| `DATABASE_URL` | Sim | URL de conexão PostgreSQL (montada pelo Compose) |
| `POSTGRES_USER` | Sim | Usuário do banco |
| `POSTGRES_PASSWORD` | Sim | Senha do banco |
| `POSTGRES_DB` | Sim | Nome do banco |
| `ALERT_DAYS` | Não | Dias para alertas, separados por vírgula |

---

## Docker Compose

```
certmonitor (FastAPI)  ←── depende de → db (PostgreSQL)
     ↑
  porta 8000
     ↑
  HAProxy (TLS termination — infra existente)
```

Os dados do PostgreSQL persistem no volume `postgres_data`. Não há volume para o servidor além do `config/` (notificações).

---

## Decisões de Design

| Decisão | Motivo |
|---------|--------|
| PostgreSQL em vez de JSON | ACID, sem race condition entre 2 agentes simultâneos |
| Sessão por cookie (não JWT) | Dashboard é web browser, cookie é mais simples e seguro |
| smtplib (stdlib) para email | Sem dependência extra; suficiente para SMTP com STARTTLS |
| Rate-limit de notificação em memória | Evita spam sem precisar de tabela extra no banco |
| Agente em Python puro | Instalável com `pip` em qualquer servidor Linux/Windows |
| TLS via HAProxy externo | Reutiliza infra existente; sem duplicação de certs no Docker |
