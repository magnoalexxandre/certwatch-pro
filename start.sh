#!/bin/bash
set -e

echo "========================================"
echo " CertMonitor — Servidor Central"
echo "========================================"
echo

# --- Pré-requisitos ---

if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker não encontrado."
    echo "Instale com: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "ERRO: 'docker compose' (plugin) não encontrado."
    echo "Atualize o Docker para uma versão recente."
    exit 1
fi

# --- Arquivo .env ---

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Arquivo .env criado. Preencha os campos antes de continuar:"
    echo
    echo "  API_TOKEN         — token compartilhado com os agentes"
    echo "  ADMIN_PASSWORD    — senha do dashboard web"
    echo "  SECRET_KEY        — chave para cookies de sessão"
    echo "  POSTGRES_PASSWORD — senha do banco de dados"
    echo
    echo "  Use: openssl rand -hex 32    para gerar valores seguros"
    echo
    read -p "Pressione ENTER após editar o .env (Ctrl+C para cancelar)..."
    echo
fi

source .env
for var in API_TOKEN ADMIN_PASSWORD SECRET_KEY POSTGRES_PASSWORD; do
    val="${!var}"
    if [ -z "$val" ] || [[ "$val" == *"troque"* ]] || [[ "$val" == *"change"* ]]; then
        echo "ERRO: '$var' no .env não foi configurado."
        exit 1
    fi
done

# --- Sobe o stack ---

echo "Subindo servidor CertMonitor + PostgreSQL..."
docker compose up -d --build
echo

echo "Aguardando banco de dados..."
sleep 8

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    echo "Servidor OK."
else
    echo "Servidor ainda iniciando. Verifique com: docker compose logs -f certmonitor"
fi

echo
echo "========================================"
echo " Servidor pronto!"
echo "========================================"
echo
echo "  Dashboard:  https://certs-sat.sef.sc.gov.br"
echo "  (direto)    http://$(hostname -I | awk '{print $1}'):8000"
echo "  Usuário:    ${ADMIN_USER:-admin}"
echo
echo "  Próximo passo: instale o agente nos servidores HAProxy."
echo "  Copie a pasta agent/ para cada HAProxy e execute:"
echo
echo "    sudo bash install_linux.sh"
echo
