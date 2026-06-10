pipeline {
    agent none

    triggers {
        cron('H 8 * * *')   // todo dia às 8h
    }

    parameters {
        string(name: 'CERT_PATH',  defaultValue: '/etc/haproxy/certs', description: 'Caminho dos certificados nos HAProxy')
        string(name: 'WARN_DAYS',  defaultValue: '30',                  description: 'Alertar quando faltar X dias')
    }

    environment {
        GOOGLE_CHAT_WEBHOOK = credentials('google-chat-webhook')
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

                    def resultados = [:]
                    def jobs = [:]

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

                    servers.each { server ->
                        jobs[server] = {
                            node(server) {
                                def out = sh(script: checkScript, returnStdout: true).trim()
                                if (out) {
                                    resultados[server] = out
                                }
                            }
                        }
                    }

                    parallel jobs

                    // Consolida resultados
                    def linhas = []
                    resultados.each { _, output ->
                        output.split('\n').each { l -> if (l.trim()) linhas << l.trim() }
                    }

                    env.TOTAL_ALERTS = linhas.size().toString()

                    if (linhas) {
                        def expired  = linhas.findAll { it.split('\\|')[3].toInteger() < 0 }
                        def critical = linhas.findAll { def d = it.split('\\|')[3].toInteger(); d >= 0 && d <= 10 }
                        def warning  = linhas.findAll { def d = it.split('\\|')[3].toInteger(); d > 10 }

                        def msg = '🔐 *CertWatch — Alerta de Certificados*\n\n'

                        if (expired) {
                            msg += "🔴 *EXPIRADOS (${expired.size()}):*\n"
                            expired.each {
                                def p = it.split('\\|')
                                msg += "  • `${p[0]}` — ${p[2]}\n    Expirado há ${Math.abs(p[3].toInteger())} dias\n"
                            }
                            msg += '\n'
                        }
                        if (critical) {
                            msg += "🟠 *CRÍTICOS (${critical.size()}):*\n"
                            critical.each {
                                def p = it.split('\\|')
                                msg += "  • `${p[0]}` — ${p[2]}\n    Expira em ${p[3]} dias\n"
                            }
                            msg += '\n'
                        }
                        if (warning) {
                            msg += "🟡 *ATENÇÃO (${warning.size()}):*\n"
                            warning.each {
                                def p = it.split('\\|')
                                msg += "  • `${p[0]}` — ${p[2]}\n    Expira em ${p[3]} dias\n"
                            }
                        }

                        msg += "\n📊 Total: ${linhas.size()} certificado(s) com alertas"

                        env.CHAT_MESSAGE = msg
                    }
                }
            }
        }

        stage('Notificar Google Chat') {
            agent { label 'built-in' }
            when {
                expression { env.TOTAL_ALERTS?.toInteger() > 0 }
            }
            steps {
                script {
                    def payload = groovy.json.JsonOutput.toJson([text: env.CHAT_MESSAGE])
                    writeFile file: 'payload.json', text: payload
                    sh "curl -s -X POST '${env.GOOGLE_CHAT_WEBHOOK}' -H 'Content-Type: application/json' -d @payload.json"
                    echo "Notificação enviada — ${env.TOTAL_ALERTS} alerta(s)"
                }
            }
        }

    }

    post {
        success { echo "Verificação concluída — alertas: ${env.TOTAL_ALERTS ?: '0'}" }
        failure { echo "Erro durante a verificação de certificados" }
    }
}
