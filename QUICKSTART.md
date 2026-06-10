# Guia de Início Rápido — CertMonitor

## Pré-requisitos

- VM Linux com Docker e Docker Compose instalados
- Acesso SSH aos servidores HAProxy (HOM e PROD)
- Python 3.8+ nos servidores HAProxy

---

## Passo 1: Configurar o servidor central

### 1.1 Crie o arquivo `.env`

```bash
cp .env.example .env
```

Edite o `.env` e preencha todos os campos:

```env
API_TOKEN=gere-com-openssl-rand-hex-32
ADMIN_USER=admin
ADMIN_PASSWORD=senha-segura
SECRET_KEY=gere-com-openssl-rand-hex-32
POSTGRES_USER=certmonitor
POSTGRES_PASSWORD=senha-segura-do-banco
POSTGRES_DB=certmonitor
ALERT_DAYS=30,20,10,7,3,1
```

> Para gerar tokens seguros: `openssl rand -hex 32`

### 1.2 Suba o stack

```bash
docker compose up -d --build
```

### 1.3 Verifique

```bash
docker compose ps           # certmonitor e db devem estar "healthy"
curl http://localhost:8000/health
```

Acesse **http://IP-DA-VM:8000** — você verá a tela de login.

---

## Passo 2: Configurar notificações (opcional)

Edite `config/config.yml`:

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
    webhook_url: https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=...
```

Após editar, reinicie o servidor para carregar:

```bash
docker compose restart certmonitor
```

---

## Passo 3: Instalar o agente nos servidores HAProxy

Execute os passos a seguir **em cada servidor HAProxy** (HOM e PROD):

### 3.1 Copie a pasta `agent/`

```bash
scp -r agent/ usuario@haproxy-hom:/opt/certwatch-agent/
```

### 3.2 Configure

```bash
ssh usuario@haproxy-hom
cd /opt/certwatch-agent

# edite server_url e api_token
nano agent_config.yml
```

```yaml
server_url: http://IP-DA-VM:8000
api_token: mesmo-token-do-env
scan_paths:
  - /etc/haproxy/certs
mode: daemon
scan_interval: 3600
```

### 3.3 Instale as dependências

```bash
pip3 install -r requirements.txt
```

### 3.4 Teste manualmente

```bash
python3 agent.py
# deve imprimir os certificados encontrados e "Relatório enviado com sucesso"
```

### 3.5 Instale como serviço systemd

```bash
sudo bash install_linux.sh
sudo systemctl status certwatch-agent
```

Repita o passo 3 no HAProxy PROD.

---

## Passo 4: Verificar o dashboard

Acesse **http://IP-DA-VM:8000** e faça login.

Você verá:
- Cards com totais por status (Expirado / Crítico / Atenção / OK)
- Status dos agentes com hora do último report
- Tabela completa com todos os certificados
- Filtro por hostname (HOM / PROD)

---

## Interpretação dos Status

| Status | Dias restantes |
|--------|---------------|
| 🟢 **OK** | > 20 dias |
| 🟡 **ATENÇÃO** | 11–20 dias |
| 🟠 **CRÍTICO** | 1–10 dias |
| 🔴 **EXPIRADO** | Vencido |

---

## Comandos úteis

```bash
# Logs em tempo real
docker compose logs -f certmonitor

# Reiniciar apenas o servidor (ex: após editar config.yml)
docker compose restart certmonitor

# Parar tudo
docker compose down

# Parar e remover dados do banco (cuidado!)
docker compose down -v
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Agente: `Connection refused` | Verifique `server_url` e se a porta 8000 está acessível |
| Agente: `401 Invalid API token` | Confirme que `api_token` no agente == `API_TOKEN` no `.env` |
| Dashboard: senha inválida | Verifique `ADMIN_USER` e `ADMIN_PASSWORD` no `.env` |
| Certificados não aparecem | Verifique `scan_paths` e permissões de leitura no HAProxy |
| Banco não sobe | `docker compose logs db` — verifique `POSTGRES_PASSWORD` |
