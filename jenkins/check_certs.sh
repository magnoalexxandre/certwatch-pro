#!/bin/bash
# Verifica certificados em CERT_PATH e exibe o status de cada um.
#
# Uso: bash check_certs.sh [cert_path] [warn_days]

CERT_PATH="${1:-/etc/haproxy/certs}"
WARN_DAYS="${2:-30}"
HOSTNAME=$(hostname -f)
TIMESTAMP=$(date '+%b %d %H:%M:%S')

total=0
alertas=0

for cert in "$CERT_PATH"/*.pem "$CERT_PATH"/*.crt "$CERT_PATH"/*.cer; do
    [ -f "$cert" ] || continue

    expiry=$(openssl x509 -enddate -noout -in "$cert" 2>/dev/null | cut -d= -f2)
    [ -z "$expiry" ] && continue

    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null)
    now_epoch=$(date +%s)
    days=$(( (expiry_epoch - now_epoch) / 86400 ))
    filename=$(basename "$cert")
    cn=$(openssl x509 -subject -noout -in "$cert" 2>/dev/null \
        | sed 's/.*CN\s*=\s*//' | sed 's/[,\/].*//')

    total=$(( total + 1 ))

    if [ "$days" -lt 0 ]; then
        echo "$TIMESTAMP $HOSTNAME ❌ ${filename}: EXPIRADO há $(( days * -1 )) dias (CN: ${cn})"
        alertas=$(( alertas + 1 ))
        echo "${HOSTNAME}|${filename}|${cn}|${days}"
    elif [ "$days" -lt "$WARN_DAYS" ]; then
        echo "$TIMESTAMP $HOSTNAME ⚠️  ${filename}: ${days} dias restantes (CN: ${cn})"
        alertas=$(( alertas + 1 ))
        echo "${HOSTNAME}|${filename}|${cn}|${days}"
    else
        echo "$TIMESTAMP $HOSTNAME ✅ ${filename}: ${days} dias (CN: ${cn})"
    fi
done

echo "$TIMESTAMP $HOSTNAME 📋 Processados ${total} certificados — ${alertas} alerta(s)"
