# Changelog

## [2.0.0] - 2026-06-09

### Produção — Breaking Changes

Esta versão adapta o projeto para uso em produção com foco em segurança, persistência robusta e notificações múltiplas.

#### Adicionado
- **PostgreSQL** substituiu o arquivo `certificates.json` — sem mais race conditions entre agentes simultâneos
- **Autenticação no dashboard** — login com usuário/senha, sessão por cookie assinado (bcrypt + itsdangerous)
- **Notificações por Email SMTP** — HTML formatado, com tabela de certificados críticos
- **Notificações por Google Chat** — via webhook, mensagem em Markdown
- **Rate-limit de notificações** — máximo uma vez por hora para evitar spam
- **Arquivo `.env`** — todos os segredos via variáveis de ambiente (nenhum hardcoded)
- **Status dos agentes no dashboard** — mostra hostname, quantidade de certs e hora do último report
- **`server/database.py`** — módulo dedicado para pool de conexões e queries
- **`server/templates/login.html`** — tela de login com design consistente com o dashboard
- **`.env.example`** — template documentado para configuração

#### Modificado
- `docker-compose.yml` — adicionado serviço PostgreSQL com healthcheck; tudo via `env_file`
- `server/main.py` — reescrito para usar PostgreSQL, SessionMiddleware e auth
- `server/notifier.py` — adicionado email SMTP e Google Chat; rate-limit implementado
- `server/requirements.txt` — adicionado `psycopg2-binary`, `passlib[bcrypt]`, `itsdangerous`
- `agent/agent_config.yml` — simplificado para uso em HAProxy (`scan_paths: /etc/haproxy/certs`)
- `config/config.yml` — adicionada seção `google_chat`
- `.gitignore` — adicionado `.env`

#### Removido
- Persistência em `data/certificates.json` (substituída por PostgreSQL)
- Variáveis de ambiente diretas no `docker-compose.yml` (movidas para `.env`)

---

## [1.0.0] - 2024-01-15

### Lançamento Inicial

- Servidor central FastAPI + Uvicorn
- Dashboard web responsivo (Jinja2)
- Agente Python multi-plataforma (Windows/Linux)
- Suporte a PEM, DER, PFX/P12
- Autenticação via API token (`X-API-Token`)
- Notificações Telegram
- Docker Compose
- Instaladores de serviço (systemd / Windows Service)
