#!/bin/bash
# Verifica certificados em CERT_PATH.
# stdout: HOSTNAME|ARQUIVO|CN|DIAS  (apenas alertas — parseado pelo Jenkinsfile)
# stderr: linhas de log legíveis     (exibidas no console Jenkins)
#
# Uso: check_certs.sh [cert_path] [warn_days]

CERT_PATH="${1:-/etc/haproxy/certs}"
WARN_DAYS="${2:-30}"
HOSTNAME=$(hostname -f)
total=0

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
        echo "❌ ${filename}: EXPIRADO há $(( days * -1 )) dias" >&2
        echo "${HOSTNAME}|${filename}|${cn}|${days}"
    elif [ "$days" -lt "$WARN_DAYS" ]; then
        echo "⚠️  ${filename}: ${days} dias restantes" >&2
        echo "${HOSTNAME}|${filename}|${cn}|${days}"
    else
        echo "✅ ${filename}: ${days} dias" >&2
    fi
done

echo "📋 ${HOSTNAME} — ${total} certificado(s) verificado(s)" >&2
