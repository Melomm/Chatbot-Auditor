#!/usr/bin/env python3
"""
Script de setup rápido para o Sistema de Auditoria Dunder Mifflin
"""

import os
import sys


def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("[!] Python 3.8+ é necessário!")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_files():
    """Verifica se os arquivos necessários existem"""
    required_files = [
        "data/politica_compliance.txt",
        "data/transacoes_bancarias.csv", 
        "data/emails.txt"
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[!] {file} não encontrado!")
            missing.append(file)
    
    return len(missing) == 0, missing


def check_env():
    """Verifica configuração do .env"""
    if not os.path.exists(".env"):
        print("[!] Arquivo .env não encontrado!")
        print("\nCrie um arquivo .env com pelo menos uma das chaves:")
        print("GROQ_API_KEY=gsk-sua-chave-aqui")
        print("OPENAI_API_KEY=sk-sua-chave-aqui")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        
        has_groq = "gsk-" in content or "GROQ_API_KEY" in content
        has_openai = "sk-" in content or "OPENAI_API_KEY" in content
        
        if not has_groq and not has_openai:
            print("[!] .env existe mas não tem nenhuma API key válida")
            print("Adicione pelo menos uma:")
            print("  GROQ_API_KEY=gsk-sua-chave-aqui (RECOMENDADO - grátis)")
            print("  OPENAI_API_KEY=sk-sua-chave-aqui")
            return False
        
        if has_groq:
            print("[OK] .env configurado (Groq detectado)")
        elif has_openai:
            print("[OK] .env configurado (OpenAI detectado)")
            print("[!] Considere usar Groq (grátis): https://console.groq.com/")
    
    return True


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("\nVerificando dependências principais...")
    
    required = {
        'langchain': 'langchain',
        'openai': 'openai',
        'pandas': 'pandas',
        'faiss': 'faiss-cpu',
        'dotenv': 'python-dotenv'
    }
    
    optional = {
        'langchain_groq': 'langchain-groq (RECOMENDADO para usar Groq)'
    }
    
    missing = []
    
    # Verificar obrigatórias
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [!] {package} não encontrado")
            missing.append(package)
    
    # Verificar opcionais
    for module, description in optional.items():
        try:
            __import__(module)
            print(f"  [OK] {description}")
        except ImportError:
            print(f"  [!] {description} não encontrado (opcional)")
    
    if missing:
        print(f"\n[!] Faltam dependências obrigatórias: {', '.join(missing)}")
        print("\nExecute: pip install -r requirements.txt")
        return False
    
    print("\n[OK] Todas as dependências obrigatórias instaladas")
    return True


def check_llm_config():
    """Verifica se llm_config.py existe"""
    if os.path.exists("llm_config.py"):
        print("[OK] llm_config.py encontrado")
        return True
    else:
        print("[!] llm_config.py não encontrado!")
        print("Este arquivo é necessário para configurar o LLM")
        return False


def main():
    """Executa todas as verificações"""
    print("\n" + "="*60)
    print("SETUP - SISTEMA DE AUDITORIA DUNDER MIFFLIN")
    print("="*60 + "\n")
    
    checks = [
        ("Versão do Python", check_python_version),
        ("Arquivos de dados", check_files),
        ("Arquivo .env", check_env),
        ("Configuração LLM", check_llm_config),
        ("Dependências", check_dependencies)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[*] Verificando: {name}")
        print("-" * 60)
        result = check_func()
        if isinstance(result, tuple):
            result = result[0]
        results.append(result)
    
    print("\n" + "="*60)
    if all(results):
        print("[OK] SETUP COMPLETO! Sistema pronto para uso.")
        print("\nExecute: python main.py")
    else:
        print("[!] SETUP INCOMPLETO. Corrija os problemas acima.")
        
        if not results[1]:  # Arquivos faltando
            _, missing = check_files()
            print("\n[*] Arquivos faltando:")
            for f in missing:
                print(f"   - {f}")
        
        if not results[2]:  # .env faltando
            print("\n[*] Crie um arquivo .env com:")
            print("   GROQ_API_KEY=gsk-sua-chave-aqui")
            print("   (Obtenha em: https://console.groq.com/)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()