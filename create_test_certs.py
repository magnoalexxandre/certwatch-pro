#!/usr/bin/env python3
"""
Script de teste para gerar certificados de exemplo
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
import os

def create_test_certificate(filename, days_valid=365):
    """Cria um certificado de teste"""
    
    # Gera chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Cria certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SP"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Sao Paulo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"test-{days_valid}days.example.com"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=days_valid)
    ).sign(private_key, hashes.SHA256())
    
    # Salva certificado
    with open(filename, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"✅ Criado: {filename} (válido por {days_valid} dias)")

if __name__ == "__main__":
    # Cria diretório de teste
    test_dir = "test_certificates"
    os.makedirs(test_dir, exist_ok=True)
    
    print("🔐 Gerando certificados de teste...\n")
    
    # Cria certificados com diferentes validades
    create_test_certificate(f"{test_dir}/cert_expired.crt", days_valid=-10)
    create_test_certificate(f"{test_dir}/cert_critical_3days.crt", days_valid=3)
    create_test_certificate(f"{test_dir}/cert_warning_15days.crt", days_valid=15)
    create_test_certificate(f"{test_dir}/cert_ok_90days.crt", days_valid=90)
    create_test_certificate(f"{test_dir}/cert_ok_365days.crt", days_valid=365)
    
    print(f"\n✅ Certificados criados em: {test_dir}/")
    print(f"\nPara testar, configure o agente para escanear: {os.path.abspath(test_dir)}")
