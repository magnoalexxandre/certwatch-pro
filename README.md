# 🔐 CertMonitor - Monitoramento de Certificados SSL/TLS

<div align="center">

**Monitoramento centralizado de certificados SSL/TLS via agentes leves**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-336791.svg)](https://www.postgresql.org/)

</div>

---

## Como funciona

Agentes Python leves rodam nos servidores monitorados, escaneiam os certificados locais e enviam os metadados para o servidor central. O servidor exibe um dashboard web com o estado de todos os certificados.

```
HAProxy HOM  (/etc/haproxy/certs)
  agent.py ──────────────────────────────► Servidor Central (Docker)
                                                │
HAProxy PROD (/etc/haproxy/certs)              ├── Dashboard Web (login)
  agent.py ──────────────────────────────►     ├── PostgreSQL
                                               └── Notificações (Email / Google Chat / Telegram)
```

---

## Características

| | |
|--|--|
| **Dashboard protegido** | Login com usuário e senha |
| **Multi-servidor** | N agentes → 1 servidor central |
| **Banco de dados** | PostgreSQL (produção) |
| **Notificações** | Email SMTP · Google Chat · Telegram |
| **Formatos** | .crt · .pem · .cer · .pfx · .p12 |
| **Alertas** | Configurável em dias (ex: 30, 20, 10, 7, 3, 1) |
| **Auto-refresh** | Dashboard atualiza a cada 5 minutos |

---

## Início Rápido

### 1. Configure os segredos

```bash
cp .env.example .env
nano .env   # preencha API_TOKEN, ADMIN_PASSWORD, SECRET_KEY, POSTGRES_PASSWORD
```

### 2. Suba o servidor

```bash
docker compose up -d --build
```

Acesse **http://IP-DO-SERVIDOR:8000** e faça login com as credenciais do `.env`.

### 3. Configure o agente nos servidores HAProxy

```bash
# em cada servidor HAProxy
cd /opt && git clone <repo> certwatch-agent
cd certwatch-agent/agent
pip3 install -r requirements.txt

# edite server_url e api_token
nano agent_config.yml

# instale como serviço systemd
sudo bash install_linux.sh
```

---

## Configuração de Notificações

Edite `config/config.yml` na VM:

```yaml
notifications:
  email:
    enabled: true
    smtp_server: smtp.empresa.com.br
    smtp_port: 587
    smtp_user: alertas@empresa.com.br
    smtp_password: senha
    from: alertas@empresa.com.br
    to:
      - infra@empresa.com.br

  google_chat:
    enabled: true
    webhook_url: https://chat.googleapis.com/v1/spaces/...

  telegram:
    enabled: false
    bot_token: SEU_BOT_TOKEN
    chat_id: SEU_CHAT_ID
```

> Notificações são enviadas no máximo uma vez por hora para evitar spam.

---

## Status dos certificados

| Status | Critério |
|--------|----------|
| 🟢 **OK** | Mais de 20 dias |
| 🟡 **ATENÇÃO** | 11–20 dias |
| 🟠 **CRÍTICO** | 1–10 dias |
| 🔴 **EXPIRADO** | Vencido |

---

## Segurança

- Dashboard protegido por login (sessão com cookie assinado)
- Agentes autenticados via `X-API-Token`
- Apenas metadados são transmitidos — nenhum arquivo de certificado sai do servidor
- Segredos exclusivamente via `.env` (nunca no código)
- `.env` no `.gitignore`

---

## Troubleshooting

```bash
# Logs do servidor
docker compose logs -f certmonitor

# Verificar banco de dados
docker compose logs -f db

# Testar conectividade do agente
curl http://IP-SERVIDOR:8000/health

# Testar agente manualmente (executa uma vez)
cd agent && python3 agent.py
```

### Agente não conecta
- Verifique se `server_url` está correto em `agent_config.yml`
- Confirme que `api_token` é idêntico ao `API_TOKEN` do `.env`
- Verifique firewall: porta 8000 deve estar acessível

### Certificados não aparecem
- Verifique se o caminho em `scan_paths` existe e tem permissão de leitura
- Confirme que as extensões dos arquivos estão em `extensions`
