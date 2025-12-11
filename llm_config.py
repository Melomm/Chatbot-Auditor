"""
Configuração centralizada de LLM
Usa Groq por padrão (grátis e rápido), fallback para OpenAI
"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Retorna LLM configurado"""
    
    # Tentar Groq primeiro (grátis e rápido)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from langchain_groq import ChatGroq
            print("[*] Usando Groq (Llama 3.3 70B)")
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0,
                max_tokens=8000
            )
        except ImportError:
            print("[!] langchain-groq não instalado")
            print("[!] Execute: pip install langchain-groq")
        except Exception as e:
            print(f"[!] Erro ao conectar Groq: {e}")
    
    # Fallback para OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from langchain_openai import ChatOpenAI
        print("[*] Usando OpenAI (GPT-4o-mini)")
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )
    
    raise ValueError(
        "Nenhuma API key configurada!\n"
        "Configure GROQ_API_KEY ou OPENAI_API_KEY no arquivo .env"
    )