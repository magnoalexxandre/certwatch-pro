#!/bin/bash
set -e

SERVICE_NAME="certwatch-agent"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_BIN="$VENV_PATH/bin/python3"
CONFIG_FILE="$SCRIPT_DIR/agent_config.yml"

echo "========================================"
echo " CertWatch Agent — Instalador"
echo "========================================"
echo

if [ "$EUID" -ne 0 ]; then
    echo "ERRO: Execute com sudo."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERRO: python3 não encontrado."
    echo "  Debian/Ubuntu: apt install python3 python3-venv"
    echo "  RHEL/CentOS:   yum install python3"
    exit 1
fi

# --- Configura agent_config.yml ---

if [ ! -f "$CONFIG_FILE" ]; then
    cp "$SCRIPT_DIR/agent_config.yml.example" "$CONFIG_FILE"
    echo "agent_config.yml criado a partir do exemplo."
fi

if grep -q "mesmo-valor-do-API_TOKEN-no-env" "$CONFIG_FILE" 2>/dev/null; then
    echo "Configuração do agente:"
    echo
    read -p "  API_TOKEN (mesmo do servidor): " INPUT_TOKEN
    read -p "  Hostname para o dashboard [$(hostname)]: " INPUT_HOST

    sed -i "s|troque-por-token-seguro|${INPUT_TOKEN}|g" "$CONFIG_FILE"

    if [ -n "$INPUT_HOST" ]; then
        sed -i "s|hostname: \"\"|hostname: \"${INPUT_HOST}\"|g" "$CONFIG_FILE"
    fi
    echo
fi

# --- Ambiente virtual ---

if [ -d "$VENV_PATH" ] && [ ! -f "$VENV_PATH/bin/pip" ]; then
    echo "Venv incompleto encontrado. Removendo..."
    rm -rf "$VENV_PATH"
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "Criando ambiente virtual Python..."
    python3 -m venv "$VENV_PATH" 2>/dev/null || {
        echo "python3-venv não encontrado. Instalando..."
        PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        apt-get install -y "python${PYVER}-venv" 2>/dev/null || \
        yum install -y python3 2>/dev/null || true
        python3 -m venv "$VENV_PATH" || {
            echo "ERRO: Falha ao criar venv. Instale manualmente: apt install python${PYVER}-venv"
            exit 1
        }
    }
fi

chmod +x "$SCRIPT_DIR/agent.py"

echo "Instalando dependências..."
"$VENV_PATH/bin/pip" install --upgrade pip -q
"$VENV_PATH/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q
echo "Dependências instaladas."
echo

# --- Serviço systemd ---

cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=CertWatch Agent — Certificate Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${PYTHON_BIN} ${SCRIPT_DIR}/agent.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "========================================"
echo " Agente instalado e iniciado!"
echo "========================================"
echo
echo "  Hostname:   $(grep 'hostname:' "$CONFIG_FILE" | head -1)"
echo "  Server URL: $(grep 'server_url:' "$CONFIG_FILE" | head -1)"
echo "  Scan path:  $(grep -A1 'scan_paths:' "$CONFIG_FILE" | tail -1)"
echo
echo "  Comandos:"
echo "    Status:  systemctl status $SERVICE_NAME"
echo "    Logs:    journalctl -u $SERVICE_NAME -f"
echo "    Parar:   systemctl stop $SERVICE_NAME"
echo
systemctl status "$SERVICE_NAME" --no-pager -l
