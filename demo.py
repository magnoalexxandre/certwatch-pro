#!/usr/bin/env python3
"""
Script de demonstração completa do CertMonitor
Executa todos os passos automaticamente para demonstração
"""

import os
import sys
import time
import subprocess
import requests

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step, text):
    print(f"\n[{step}] {text}")
    print("-" * 60)

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def wait_for_server(url, timeout=30):
    """Aguarda servidor ficar disponível"""
    print(f"Aguardando servidor em {url}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print("✅ Servidor está online!")
                return True
        except:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    print("\n❌ Timeout aguardando servidor")
    return False

def main():
    print_header("🔐 CertMonitor - Demonstração Completa")
    
    # Passo 1: Verificar requisitos
    print_step("1/6", "Verificando requisitos...")
    
    # Verifica Python
    print(f"✓ Python: {sys.version.split()[0]}")
    
    # Verifica Docker
    success, _, _ = run_command("docker --version")
    if success:
        print("✓ Docker: Instalado")
    else:
        print("✗ Docker: NÃO instalado")
        print("\nPor favor, instale o Docker primeiro:")
        print("https://docs.docker.com/get-docker/")
        return
    
    # Passo 2: Criar certificados de teste
    print_step("2/6", "Criando certificados de teste...")
    success, stdout, stderr = run_command("python create_test_certs.py")
    if success:
        print("✅ Certificados de teste criados!")
    else:
        print(f"❌ Erro: {stderr}")
        return
    
    # Passo 3: Iniciar servidor
    print_step("3/6", "Iniciando servidor Docker...")
    success, stdout, stderr = run_command("docker-compose up -d")
    if success:
        print("✅ Servidor iniciado!")
    else:
        print(f"❌ Erro: {stderr}")
        return
    
    # Aguarda servidor
    if not wait_for_server("http://localhost:8000/health"):
        return
    
    # Passo 4: Instalar dependências do agente
    print_step("4/6", "Instalando dependências do agente...")
    success, stdout, stderr = run_command("pip install -r requirements.txt", cwd="agent")
    if success:
        print("✅ Dependências instaladas!")
    else:
        print(f"⚠️  Aviso: {stderr}")
    
    # Passo 5: Executar agente (uma vez)
    print_step("5/6", "Executando agente (modo teste)...")
    
    # Modifica config para modo once
    config_path = "agent/agent_config.yml"
    with open(config_path, 'r') as f:
        config = f.read()
    
    config_backup = config
    config = config.replace("mode: daemon", "mode: once")
    
    with open(config_path, 'w') as f:
        f.write(config)
    
    # Executa agente
    success, stdout, stderr = run_command("python agent.py", cwd="agent")
    
    # Restaura config
    with open(config_path, 'w') as f:
        f.write(config_backup)
    
    if success:
        print("✅ Agente executado com sucesso!")
        print("\nSaída do agente:")
        print(stdout)
    else:
        print(f"❌ Erro: {stderr}")
    
    # Passo 6: Verificar resultados
    print_step("6/6", "Verificando resultados...")
    
    try:
        # Busca estatísticas
        response = requests.get("http://localhost:8000/api/stats")
        stats = response.json()
        
        print("\n📊 Estatísticas:")
        print(f"   Total de certificados: {stats['total']}")
        print(f"   Expirados: {stats['expired']}")
        print(f"   Críticos (≤7 dias): {stats['critical']}")
        print(f"   Atenção (≤30 dias): {stats['warning']}")
        print(f"   OK: {stats['ok']}")
        print(f"   Servidores: {stats['hosts']}")
        
        # Busca certificados
        response = requests.get("http://localhost:8000/api/certificates")
        certs = response.json()
        
        print(f"\n📋 Certificados encontrados: {len(certs)}")
        for cert in certs[:3]:  # Mostra apenas os 3 primeiros
            status = "🔴" if cert['days_remaining'] < 0 else "🟠" if cert['days_remaining'] <= 7 else "🟡" if cert['days_remaining'] <= 30 else "🟢"
            print(f"   {status} {cert['subject']}: {cert['days_remaining']} dias")
        
        if len(certs) > 3:
            print(f"   ... e mais {len(certs) - 3} certificados")
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
    
    # Finalização
    print_header("✅ Demonstração Completa!")
    
    print("\n🎉 Tudo funcionando perfeitamente!\n")
    print("Próximos passos:")
    print("1. Acesse a interface: http://localhost:8000")
    print("2. Explore o dashboard e os certificados")
    print("3. Configure o agente para seus servidores")
    print("4. Leia a documentação em README.md")
    print("\nPara parar o servidor:")
    print("   docker-compose down")
    print("\nPara executar o agente continuamente:")
    print("   cd agent && python agent.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
