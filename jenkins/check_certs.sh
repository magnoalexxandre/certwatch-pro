#!/bin/bash
# Verifica certificados em CERT_PATH e imprime os que estão vencendo.
# Saída: HOSTNAME|ARQUIVO|CN|DIAS_RESTANTES
#
# Uso: bash check_certs.sh [cert_path] [warn_days]

CERT_PATH="${1:-/etc/haproxy/certs}"
WARN_DAYS="${2:-30}"
HOSTNAME=$(hostname -f)

for cert in "$CERT_PATH"/*.pem "$CERT_PATH"/*.crt "$CERT_PATH"/*.cer; do
    [ -f "$cert" ] || continue

    expiry=$(openssl x509 -enddate -noout -in "$cert" 2>/dev/null | cut -d= -f2)
    [ -z "$expiry" ] && continue

    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null)
    now_epoch=$(date +%s)
    days=$(( (expiry_epoch - now_epoch) / 86400 ))

    if [ "$days" -lt "$WARN_DAYS" ]; then
        cn=$(openssl x509 -subject -noout -in "$cert" 2>/dev/null \
            | sed 's/.*CN\s*=\s*//' | sed 's/[,\/].*//')
        filename=$(basename "$cert")
        echo "${HOSTNAME}|${filename}|${cn}|${days}"
    fi
done
