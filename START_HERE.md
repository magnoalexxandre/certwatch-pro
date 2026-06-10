# CertMonitor — Por onde começar

## Escolha sua arquitetura

### Opção A — Servidor dedicado (recomendado)

```
VM dedicada         HAProxy HOM          HAProxy PROD
(Docker)            /etc/haproxy/certs   /etc/haproxy/certs
CertMonitor   ◄──── agente         ◄──── agente
PostgreSQL
```

Servidor e agentes ficam separados. Mais limpo, sem dependência entre os HAProxy.

### Opção B — Servidor no HAProxy HOM

```
HAProxy HOM                          HAProxy PROD
Docker (CertMonitor + PostgreSQL)    /etc/haproxy/certs
/etc/haproxy/certs                   agente ──────────────►
agente (local) ──────────────────►
```

Economiza uma VM. O HOM acumula duas funções.

---

## Opção A — VM dedicada

### Passo 1 — Na VM do servidor

```bash
git clone <repo> /opt/certwatch
cd /opt/certwatch
chmod +x start.sh
./start.sh
```

O script cria o `.env`, sobe o Docker stack e mostra o endereço do dashboard.

### Passo 2 — Em cada HAProxy (HOM e PROD)

```bash
# Copie só a pasta agent/ para o HAProxy
scp -r /opt/certwatch/agent/ usuario@haproxy-hom:/opt/certwatch-agent/
scp -r /opt/certwatch/agent/ usuario@haproxy-prod:/opt/certwatch-agent/

# Em cada HAProxy execute:
cd /opt/certwatch-agent
sudo bash install_linux.sh
# O script vai pedir: API_TOKEN e hostname (ex: haproxy-hom)
```

---

## Opção B — Servidor no HAProxy HOM

### Passo 1 — No HAProxy HOM

```bash
git clone <repo> /opt/certwatch
cd /opt/certwatch
chmod +x start.sh
./start.sh   # sobe Docker stack

# Instala o agente local também
cd agent
sudo bash install_linux.sh
```

### Passo 2 — No HAProxy PROD (só o agente)

```bash
scp -r /opt/certwatch/agent/ usuario@haproxy-prod:/opt/certwatch-agent/
ssh usuario@haproxy-prod
cd /opt/certwatch-agent
sudo bash install_linux.sh
```

---

## Após o setup

Acesse **https://certs-sat.sef.sc.gov.br** e faça login.

Você verá os dois agentes (`haproxy-hom` e `haproxy-prod`) com todos os certificados de `/etc/haproxy/certs` de cada um.

---

## Comandos do dia a dia

```bash
# No servidor (VM ou HAProxy HOM)
cd /opt/certwatch
docker compose logs -f certmonitor      # logs do servidor
docker compose restart certmonitor      # recarregar config.yml

# Em cada HAProxy
systemctl status certwatch-agent        # status do agente
journalctl -u certwatch-agent -f        # logs do agente
```
