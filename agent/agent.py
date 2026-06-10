#!/usr/bin/env python3
import os
import sys
import time
import socket
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import yaml
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

class CertificateScanner:
    def __init__(self, config_path="agent_config.yml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.server_url = self.config['server_url'].rstrip('/')
        self.api_token = self.config['api_token']
        self.hostname = self.config.get('hostname') or socket.gethostname()
        self.scan_paths = self.config['scan_paths']
        self.extensions = tuple(self.config['extensions'])
        self.scan_interval = self.config['scan_interval']
        self.mode = self.config.get('mode', 'daemon')
        self.ssl_verify = self.config.get('ssl_verify', True)
    
    def find_certificates(self) -> List[Path]:
        """Encontra todos os certificados nos diretórios configurados"""
        cert_files = []
        
        for scan_path in self.scan_paths:
            path = Path(scan_path)
            if not path.exists():
                print(f"⚠️  Caminho não existe: {scan_path}")
                continue
            
            print(f"🔍 Escaneando: {scan_path}")
            
            try:
                for file_path in path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in self.extensions:
                        cert_files.append(file_path)
            except PermissionError as e:
                print(f"⚠️  Sem permissão: {e}")
        
        return cert_files
    
    def parse_certificate(self, file_path: Path) -> Dict:
        """Extrai informações do certificado"""
        try:
            # Tenta ler como PEM
            with open(file_path, 'rb') as f:
                cert_data = f.read()
            
            # Tenta diferentes formatos
            cert = None
            cert_type = "Unknown"
            
            # PEM
            try:
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                cert_type = "PEM"
            except:
                pass
            
            # DER
            if not cert:
                try:
                    cert = x509.load_der_x509_certificate(cert_data, default_backend())
                    cert_type = "DER"
                except:
                    pass
            
            # PFX/P12 (requer senha, pula por enquanto)
            if not cert and file_path.suffix.lower() in ['.pfx', '.p12']:
                cert_type = "PFX/P12 (requer senha)"
                return None
            
            if not cert:
                return None
            
            # Extrai informações
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            serial = cert.serial_number
            
            # Calcula fingerprint
            fingerprint = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
            
            # Calcula dias restantes
            days_remaining = (not_after - datetime.now()).days
            
            return {
                "hostname": self.hostname,
                "path": str(file_path),
                "subject": subject,
                "issuer": issuer,
                "not_before": not_before.isoformat(),
                "not_after": not_after.isoformat(),
                "days_remaining": days_remaining,
                "serial_number": str(serial),
                "fingerprint": fingerprint[:16],
                "cert_type": cert_type
            }
        
        except Exception as e:
            print(f"❌ Erro ao processar {file_path}: {e}")
            return None
    
    def scan_certificates(self) -> List[Dict]:
        """Escaneia todos os certificados"""
        print(f"\n{'='*60}")
        print(f"🚀 Iniciando escaneamento - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  Hostname: {self.hostname}")
        print(f"{'='*60}\n")
        
        cert_files = self.find_certificates()
        print(f"\n📄 Encontrados {len(cert_files)} arquivos de certificado\n")
        
        certificates = []
        for cert_file in cert_files:
            cert_info = self.parse_certificate(cert_file)
            if cert_info:
                certificates.append(cert_info)
                status = "✅" if cert_info['days_remaining'] > 30 else "⚠️" if cert_info['days_remaining'] > 7 else "🔴"
                print(f"{status} {cert_file.name}: {cert_info['days_remaining']} dias")
        
        print(f"\n✅ Processados {len(certificates)} certificados válidos\n")
        return certificates
    
    def send_report(self, certificates: List[Dict]):
        """Envia relatório para o servidor central"""
        if not certificates:
            print("⚠️  Nenhum certificado para enviar")
            return
        
        report = {
            "hostname": self.hostname,
            "certificates": certificates,
            "timestamp": datetime.now().isoformat()
        }
        
        headers = {
            "X-API-Token": self.api_token,
            "Content-Type": "application/json"
        }
        
        try:
            print(f"📤 Enviando relatório para {self.server_url}/api/report")
            response = requests.post(
                f"{self.server_url}/api/report",
                json=report,
                headers=headers,
                timeout=30,
                verify=self.ssl_verify
            )
            
            if response.status_code == 200:
                print(f"✅ Relatório enviado com sucesso!")
                print(f"   {len(certificates)} certificados reportados")
            else:
                print(f"❌ Erro ao enviar: {response.status_code} - {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro: Não foi possível conectar ao servidor {self.server_url}")
            print(f"   Verifique se o servidor está rodando e acessível")
        except Exception as e:
            print(f"❌ Erro ao enviar relatório: {e}")
    
    def run(self):
        """Executa o agente"""
        print("\n" + "="*60)
        print("🔐 CertMonitor Agent")
        print("="*60)
        print(f"Servidor: {self.server_url}")
        print(f"Hostname: {self.hostname}")
        print(f"Modo: {self.mode}")
        print(f"Intervalo: {self.scan_interval}s")
        print("="*60 + "\n")
        
        if self.mode == "once":
            certificates = self.scan_certificates()
            self.send_report(certificates)
        else:
            print("🔄 Modo daemon ativado. Pressione Ctrl+C para parar.\n")
            while True:
                try:
                    certificates = self.scan_certificates()
                    self.send_report(certificates)
                    print(f"\n⏰ Próximo scan em {self.scan_interval} segundos...")
                    print(f"{'='*60}\n")
                    time.sleep(self.scan_interval)
                except KeyboardInterrupt:
                    print("\n\n👋 Agente finalizado pelo usuário")
                    sys.exit(0)
                except Exception as e:
                    print(f"\n❌ Erro: {e}")
                    print(f"⏰ Tentando novamente em {self.scan_interval} segundos...")
                    time.sleep(self.scan_interval)

if __name__ == "__main__":
    try:
        scanner = CertificateScanner()
        scanner.run()
    except FileNotFoundError:
        print("❌ Erro: Arquivo agent_config.yml não encontrado!")
        print("   Crie o arquivo de configuração antes de executar o agente.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Agente finalizado")
        sys.exit(0)
