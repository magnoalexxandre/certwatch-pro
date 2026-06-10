#!/usr/bin/env python3
"""
Script de teste para verificar se tudo está funcionando
"""

import sys
import subprocess
import requests
import time

def check_command(cmd):
    """Verifica se um comando existe"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def test_server():
    """Testa se o servidor está respondendo"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("="*60)
    print("🔍 CertMonitor - Teste de Instalação")
    print("="*60)
    print()
    
    # Testa Python
    print("✓ Python:", sys.version.split()[0])
    
    # Testa Docker
    if check_command("docker"):
        print("✓ Docker: Instalado")
    else:
        print("✗ Docker: NÃO instalado")
        print("  Instale: https://docs.docker.com/get-docker/")
    
    # Testa Docker Compose
    if check_command("docker-compose"):
        print("✓ Docker Compose: Instalado")
    else:
        print("✗ Docker Compose: NÃO instalado")
    
    print()
    print("-"*60)
    print("Testando Servidor...")
    print("-"*60)
    
    # Testa servidor
    if test_server():
        print("✓ Servidor: ONLINE (http://localhost:8000)")
        
        # Testa API
        try:
            stats = requests.get("http://localhost:8000/api/stats").json()
            print(f"✓ API: Funcionando")
            print(f"  - Total de certificados: {stats['total']}")
            print(f"  - Servidores monitorados: {stats['hosts']}")
        except:
            print("✗ API: Erro ao acessar")
    else:
        print("✗ Servidor: OFFLINE")
        print("  Execute: docker-compose up -d")
    
    print()
    print("-"*60)
    print("Testando Agente...")
    print("-"*60)
    
    # Verifica dependências do agente
    try:
        import cryptography
        print("✓ cryptography: Instalado")
    except:
        print("✗ cryptography: NÃO instalado")
        print("  Execute: pip install -r agent/requirements.txt")
    
    try:
        import yaml
        print("✓ pyyaml: Instalado")
    except:
        print("✗ pyyaml: NÃO instalado")
    
    try:
        import requests
        print("✓ requests: Instalado")
    except:
        print("✗ requests: NÃO instalado")
    
    print()
    print("="*60)
    print("Teste Completo!")
    print("="*60)
    print()
    print("Próximos passos:")
    print("1. Se o servidor está offline: docker-compose up -d")
    print("2. Configure o agente: agent/agent_config.yml")
    print("3. Execute o agente: cd agent && python agent.py")
    print("4. Acesse: http://localhost:8000")
    print()

if __name__ == "__main__":
    main()
