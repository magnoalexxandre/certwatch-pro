# Índice de Documentação - CertMonitor

Guia completo de toda a documentação disponível no projeto.

---

## inciando

### 1. [START_HERE.md](START_HERE.md) ⭐
**Comece por aqui!**
- Início rápido em 5 minutos
- Comandos essenciais
- Preview da interface
- Primeiros passos

### 2. [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
**Resumo executivo**
- O que é o CertMonitor
- Principais características
- Benefícios
- Casos de uso

### 3. [README.md](README.md)
**Documentação principal**
- Visão geral completa
- Características
- Instalação detalhada
- Configuração

---

##  Guias de Uso

### 4. [QUICKSTART.md](QUICKSTART.md)
**Guia de início rápido**
- Instalação passo a passo
- Servidor Central (Docker)
- Agente Cliente (Windows/Linux)
- Configuração básica

### 5. [EXAMPLES.md](EXAMPLES.md)
**Exemplos práticos**
- 10 cenários reais de uso
- Configurações específicas
- Integração com CI/CD
- Dicas avançadas

### 6. [FAQ.md](FAQ.md)
**Perguntas frequentes**
- Dúvidas comuns
- Troubleshooting
- Configurações
- Segurança

---

##  Documentação Técnica

### 7. [ARCHITECTURE.md](ARCHITECTURE.md)
**Arquitetura do sistema**
- Diagramas de arquitetura
- Fluxo de dados
- Componentes detalhados
- Escalabilidade
- Performance

### 8. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
**Estrutura do projeto**
- Organização de arquivos
- Descrição de cada componente
- Fluxo de trabalho
- Customização

---

##  Informações do Projeto

### 9. [CHANGELOG.md](CHANGELOG.md)
**Histórico de versões**
- Versão atual (1.0.0)
- Funcionalidades implementadas
- Roadmap futuro
- Planejamento de releases

### 10. [LICENSE](LICENSE)
**Licença MIT**
- Termos de uso
- Direitos e permissões
- Uso comercial permitido

---

## 🛠️ Scripts e Ferramentas

### Scripts de Inicialização

#### [start.sh](start.sh) / [start.bat](start.bat)
**Início rápido**
- Inicia servidor Docker
- Cria certificados de teste
- Configuração automática

#### [demo.py](demo.py)
**Demonstração completa**
- Executa todos os passos automaticamente
- Verifica requisitos
- Testa instalação
- Mostra resultados

#### [test_installation.py](test_installation.py)
**Teste de instalação**
- Verifica dependências
- Testa servidor
- Testa agente
- Diagnóstico completo

#### [create_test_certs.py](create_test_certs.py)
**Gerador de certificados de teste**
- Cria certificados com diferentes validades
- Útil para desenvolvimento
- Testes automatizados

---

## 📂 Estrutura de Diretórios

### [server/](server/)
**Servidor Central**
- `main.py` - Aplicação FastAPI
- `Dockerfile` - Container Docker
- `requirements.txt` - Dependências
- `templates/index.html` - Interface web

### [agent/](agent/)
**Agente Cliente**
- `agent.py` - Scanner de certificados
- `agent_config.yml` - Configuração
- `requirements.txt` - Dependências
- `install_windows.bat` - Instalador Windows
- `install_linux.sh` - Instalador Linux

### [config/](config/)
**Configurações**
- `config.yml` - Config do servidor (alertas, notificações)

### [data/](data/)
**Dados (gerado em runtime)**
- `certificates.json` - Banco de dados de certificados

---

## 🎯 Guia de Leitura por Perfil

### 👨‍💼 Gerente/Decisor
1. [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - Entenda o valor
2. [README.md](README.md) - Visão geral
3. [EXAMPLES.md](EXAMPLES.md) - Casos de uso

### 👨‍💻 Desenvolvedor
1. [START_HERE.md](START_HERE.md) - Comece rápido
2. [QUICKSTART.md](QUICKSTART.md) - Setup detalhado
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Como funciona
4. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Estrutura do código

### 🔧 DevOps/SRE
1. [QUICKSTART.md](QUICKSTART.md) - Instalação
2. [EXAMPLES.md](EXAMPLES.md) - Cenários de produção
3. [FAQ.md](FAQ.md) - Troubleshooting
4. [ARCHITECTURE.md](ARCHITECTURE.md) - Escalabilidade

### 🔒 Segurança
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura de segurança
2. [FAQ.md](FAQ.md) - Questões de segurança
3. [LICENSE](LICENSE) - Termos legais

### 🆕 Iniciante
1. [START_HERE.md](START_HERE.md) - Comece aqui!
2. [QUICKSTART.md](QUICKSTART.md) - Passo a passo
3. [FAQ.md](FAQ.md) - Dúvidas comuns
4. [EXAMPLES.md](EXAMPLES.md) - Aprenda com exemplos

---

## 🔍 Busca Rápida

### Instalação
- Início rápido: [START_HERE.md](START_HERE.md)
- Guia completo: [QUICKSTART.md](QUICKSTART.md)
- Docker: [docker-compose.yml](docker-compose.yml)

### Configuração
- Servidor: [config/config.yml](config/config.yml)
- Agente: [agent/agent_config.yml](agent/agent_config.yml)
- Docker: [docker-compose.yml](docker-compose.yml)

### Uso
- Exemplos: [EXAMPLES.md](EXAMPLES.md)
- FAQ: [FAQ.md](FAQ.md)
- Scripts: [start.sh](start.sh), [start.bat](start.bat)

### Desenvolvimento
- Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md)
- Estrutura: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- Código: [server/](server/), [agent/](agent/)

### Troubleshooting
- FAQ: [FAQ.md](FAQ.md)
- Teste: [test_installation.py](test_installation.py)
- Logs: Ver FAQ.md

---

## 📊 Estatísticas da Documentação

- **Total de arquivos:** 18
- **Documentação:** 10 arquivos .md
- **Scripts:** 4 arquivos Python
- **Configuração:** 4 arquivos
- **Código fonte:** 2 diretórios principais

---

## 🎓 Trilha de Aprendizado Recomendada

### Nível 1: Básico (30 minutos)
1. ✅ [START_HERE.md](START_HERE.md) - 5 min
2. ✅ Execute [start.sh](start.sh) ou [start.bat](start.bat) - 5 min
3. ✅ Explore a interface web - 10 min
4. ✅ [QUICKSTART.md](QUICKSTART.md) - 10 min

### Nível 2: Intermediário (1 hora)
1. ✅ [EXAMPLES.md](EXAMPLES.md) - 20 min
2. ✅ Configure agente em servidor real - 20 min
3. ✅ [FAQ.md](FAQ.md) - 20 min

### Nível 3: Avançado (2 horas)
1. ✅ [ARCHITECTURE.md](ARCHITECTURE.md) - 30 min
2. ✅ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 20 min
3. ✅ Explore o código fonte - 40 min
4. ✅ Customize e estenda - 30 min

---

## 🔗 Links Úteis

### Documentação Online
- GitHub: (adicione seu link)
- Wiki: (adicione seu link)
- Issues: (adicione seu link)

### Recursos Externos
- Docker: https://docs.docker.com/
- Python: https://www.python.org/
- FastAPI: https://fastapi.tiangolo.com/
- Cryptography: https://cryptography.io/

---

## 💡 Dicas de Navegação

### Buscar por Palavra-Chave
Use o comando `grep` (Linux/Mac) ou `findstr` (Windows):

```bash
# Linux/Mac
grep -r "palavra-chave" *.md

# Windows
findstr /s "palavra-chave" *.md
```

### Visualizar no GitHub
Todos os arquivos .md são renderizados automaticamente no GitHub com formatação.

### Gerar PDF
Use ferramentas como `pandoc` para converter .md em PDF:

```bash
pandoc README.md -o README.pdf
```

---

## 📞 Precisa de Ajuda?

1. **Consulte o FAQ:** [FAQ.md](FAQ.md)
2. **Veja exemplos:** [EXAMPLES.md](EXAMPLES.md)
3. **Teste instalação:** Execute [test_installation.py](test_installation.py)
4. **Abra uma issue:** GitHub Issues

---

## 🤝 Contribuindo

Quer melhorar a documentação?

1. Fork o projeto
2. Edite os arquivos .md
3. Envie um Pull Request

Toda contribuição é bem-vinda! 🎉

---

**Última atualização:** 2024-01-15  
**Versão da documentação:** 1.0.0
