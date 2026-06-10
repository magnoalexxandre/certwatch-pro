def CHAT_URL = 'https://chat.googleapis.com/v1/spaces/AAAAfWUP3JQ/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=A352dYCjJ8CFo6V0v4O8V6V4LiwJ11Wj0iofkzI1mpo'
def EMAIL_TO = 'monitoramento-sat@sef.sc.gov.br'

pipeline {
    agent none

    triggers {
        cron('H 8 * * *')
    }

    parameters {
        string(name: 'CERT_PATH', defaultValue: '/etc/haproxy/certs', description: 'Caminho dos certificados')
        string(name: 'WARN_DAYS', defaultValue: '30',                  description: 'Alertar quando faltar X dias')
    }

    stages {

        stage('Verificar Certificados') {
            agent { label 'built-in' }
            steps {
                script {
                    def servers = [
                        'lnsat-lb-int-h1.sef.sc.gov.br',
                        'lnsat-lb-int-h2.sef.sc.gov.br',
                        'lnsat-lb-int-p1.sef.sc.gov.br',
                        'lnsat-lb-int-p2.sef.sc.gov.br',
                        'lnsat-lb-ext-h1.sef.sc.gov.br',
                        'lnsat-lb-ext-h2.sef.sc.gov.br',
                        'lnsat-lb-ext-p1.sef.sc.gov.br',
                        'lnsat-lb-ext-p2.sef.sc.gov.br'
                    ]

                    def checkScript = """
                        CERT_PATH='${params.CERT_PATH}'
                        WARN_DAYS='${params.WARN_DAYS}'
                        HOSTNAME=\$(hostname -f)
                        for cert in "\$CERT_PATH"/*.pem "\$CERT_PATH"/*.crt "\$CERT_PATH"/*.cer; do
                            [ -f "\$cert" ] || continue
                            expiry=\$(openssl x509 -enddate -noout -in "\$cert" 2>/dev/null | cut -d= -f2)
                            [ -z "\$expiry" ] && continue
                            expiry_epoch=\$(date -d "\$expiry" +%s 2>/dev/null)
                            now_epoch=\$(date +%s)
                            days=\$(( (expiry_epoch - now_epoch) / 86400 ))
                            if [ "\$days" -lt "\$WARN_DAYS" ]; then
                                cn=\$(openssl x509 -subject -noout -in "\$cert" 2>/dev/null | sed 's/.*CN\\s*=\\s*//' | sed 's/[,\\/].*//')
                                echo "\${HOSTNAME}|\$(basename \$cert)|\${cn}|\${days}"
                            fi
                        done
                    """

                    def resultados = [:]
                    def jobs = [:]

                    servers.each { server ->
                        jobs[server] = {
                            node(server) {
                                def out = sh(script: checkScript, returnStdout: true).trim()
                                if (out) resultados[server] = out
                            }
                        }
                    }

                    parallel jobs

                    def alertas = []
                    resultados.each { _, output ->
                        output.split('\n').each { linha ->
                            if (linha.trim()) {
                                def p = linha.trim().split('\\|')
                                alertas << [hostname: p[0], file: p[1], cn: p[2], days: p[3].toInteger()]
                            }
                        }
                    }

                    alertas.sort { it.days }

                    if (alertas) {
                        notificarCertificados(alertas, CHAT_URL, EMAIL_TO, env.BUILD_URL)
                        echo "Notificação enviada — ${alertas.size()} alerta(s)"
                    } else {
                        echo "Todos os certificados OK."
                    }
                }
            }
        }
    }

    post {
        failure {
            node('built-in') {
                httpRequest(
                    url:         CHAT_URL,
                    httpMode:    'POST',
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson([
                        text: "❌ *CertWatch* — Falha na verificação de certificados\nBuild: ${env.BUILD_URL}"
                    ])
                )
            }
        }
    }
}

// =============================================================
def notificarCertificados(List alertas, String chatUrl, String emailTo, String buildUrl) {
    def expired  = alertas.findAll { it.days < 0 }
    def critical = alertas.findAll { it.days >= 0 && it.days <= 10 }
    def warning  = alertas.findAll { it.days > 10 }

    // --- Google Chat ---
    def chatMsg = '🔐 *CertWatch — Alerta de Certificados*\n\n'

    if (expired) {
        chatMsg += "🔴 *EXPIRADOS (${expired.size()}):*\n"
        expired.each { chatMsg += "  • `${it.hostname}` — ${it.cn}\n    Expirado há ${Math.abs(it.days)} dias\n" }
        chatMsg += '\n'
    }
    if (critical) {
        chatMsg += "🟠 *CRÍTICOS (${critical.size()}):*\n"
        critical.each { chatMsg += "  • `${it.hostname}` — ${it.cn}\n    Expira em ${it.days} dias\n" }
        chatMsg += '\n'
    }
    if (warning) {
        chatMsg += "🟡 *ATENÇÃO (${warning.size()}):*\n"
        warning.each { chatMsg += "  • `${it.hostname}` — ${it.cn}\n    Expira em ${it.days} dias\n" }
        chatMsg += '\n'
    }
    chatMsg += "📊 Total: ${alertas.size()} certificado(s) com alertas\n${buildUrl}"

    httpRequest(
        url:         chatUrl,
        httpMode:    'POST',
        contentType: 'APPLICATION_JSON',
        requestBody: groovy.json.JsonOutput.toJson([text: chatMsg])
    )

    // --- Email ---
    def linhasHtml = alertas.collect { a ->
        def cor   = a.days < 0 ? '#e74c3c' : (a.days <= 10 ? '#e67e22' : '#f39c12')
        def label = a.days < 0 ? 'EXPIRADO' : (a.days <= 10 ? 'CRÍTICO' : 'ATENÇÃO')
        def info  = a.days < 0 ? "Expirado há ${Math.abs(a.days)} dias" : "Expira em ${a.days} dias"
        """<tr>
            <td style='padding:8px;border-bottom:1px solid #eee;'>
                <span style='background:${cor};color:white;padding:3px 10px;border-radius:4px;font-size:12px;'>${label}</span>
            </td>
            <td style='padding:8px;border-bottom:1px solid #eee;font-weight:bold;'>${a.hostname}</td>
            <td style='padding:8px;border-bottom:1px solid #eee;'>${a.cn}</td>
            <td style='padding:8px;border-bottom:1px solid #eee;color:${cor};font-weight:bold;'>${info}</td>
        </tr>"""
    }.join('\n')

    def emailBody = """
        <html><body style='font-family:Arial,sans-serif;'>
        <div style='background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;border-radius:8px 8px 0 0;'>
            <h2 style='color:white;margin:0;'>🔐 CertWatch — Alerta de Certificados</h2>
        </div>
        <div style='padding:20px;border:1px solid #ddd;border-top:none;border-radius:0 0 8px 8px;'>
            <table style='width:100%;border-collapse:collapse;'>
                <thead>
                    <tr style='background:#f8f9fa;'>
                        <th style='padding:10px;text-align:left;border-bottom:2px solid #ddd;'>Status</th>
                        <th style='padding:10px;text-align:left;border-bottom:2px solid #ddd;'>Servidor</th>
                        <th style='padding:10px;text-align:left;border-bottom:2px solid #ddd;'>Certificado</th>
                        <th style='padding:10px;text-align:left;border-bottom:2px solid #ddd;'>Situação</th>
                    </tr>
                </thead>
                <tbody>${linhasHtml}</tbody>
            </table>
            <p style='margin-top:16px;color:#666;font-size:13px;'>
                Total: ${alertas.size()} certificado(s) com alertas<br>
                <a href='${buildUrl}'>Ver build no Jenkins</a>
            </p>
        </div>
        </body></html>
    """

    mail(
        to:       emailTo,
        subject:  "CertWatch — ${expired ? 'EXPIRADOS' : 'Certificados próximos do vencimento'} (${alertas.size()})",
        body:     emailBody,
        charset:  'UTF-8',
        mimeType: 'text/html'
    )
}

