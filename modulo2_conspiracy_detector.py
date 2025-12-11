"""
Módulo 2: Detector de Conspiração
Vasculha emails procurando evidências de Michael conspirando contra Toby
"""

import re
from typing import List, Dict
from llm_config import get_llm
from langchain.prompts import ChatPromptTemplate


class ConspiracyDetector:
    def __init__(self, emails_file: str):
        """
        Inicializa o detector de conspiração
        
        Args:
            emails_file: Caminho para o arquivo de emails
        """
        self.emails_file = emails_file
        self.emails = []
        
    def parse_emails(self) -> List[Dict]:
        """Parse do arquivo de emails em estrutura de dados"""
        print("[*] Parseando emails...")
        
        with open(self.emails_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir por separadores
        email_blocks = content.split('-------------------------------------------------------------------------------')
        
        emails = []
        for block in email_blocks:
            block = block.strip()
            if not block or block.startswith('DUMP DE SERVIDOR'):
                continue
                
            # Extrair campos
            de_match = re.search(r'De: (.+?) <(.+?)>', block)
            para_match = re.search(r'Para: (.+?) <(.+?)>', block)
            data_match = re.search(r'Data: (.+)', block)
            assunto_match = re.search(r'Assunto: (.+)', block)
            
            # Extrair mensagem (tudo após "Mensagem:")
            msg_match = re.search(r'Mensagem:\s*\n(.+)', block, re.DOTALL)
            
            if de_match and msg_match:
                email = {
                    'de_nome': de_match.group(1).strip(),
                    'de_email': de_match.group(2).strip(),
                    'para_nome': para_match.group(1).strip() if para_match else '',
                    'para_email': para_match.group(2).strip() if para_match else '',
                    'data': data_match.group(1).strip() if data_match else '',
                    'assunto': assunto_match.group(1).strip() if assunto_match else '',
                    'mensagem': msg_match.group(1).strip()
                }
                emails.append(email)
        
        self.emails = emails
        print(f"[OK] {len(emails)} emails parseados")
        return emails
    
    def find_michael_emails_about_toby(self) -> List[Dict]:
        """Encontra emails de/sobre Michael e Toby"""
        relevant_emails = []
        
        keywords = [
            'toby', 'hr', 'recursos humanos', 'flenderson',
            'conspiração', 'conspirar', 'contra', 'odeia', 'odeio'
        ]
        
        for email in self.emails:
            # Emails de Michael
            is_from_michael = 'michael.scott' in email['de_email'].lower()
            
            # Emails para/sobre Toby
            mentions_toby = any(
                keyword in email['assunto'].lower() or 
                keyword in email['mensagem'].lower() or
                keyword in email['para_email'].lower()
                for keyword in keywords
            )
            
            if is_from_michael and mentions_toby:
                relevant_emails.append(email)
        
        return relevant_emails
    
    def analyze_conspiracy(self) -> Dict:
        """Usa LLM para analisar se há conspiração"""
        print("\n[*] Analisando conspiração contra Toby...")
        
        relevant_emails = self.find_michael_emails_about_toby()
        
        if not relevant_emails:
            print("[!] Nenhum email relevante encontrado")
            return {
                "conspiracy_found": False,
                "evidence": [],
                "analysis": "Nenhum email de Michael mencionando Toby foi encontrado."
            }
        
        print(f"[*] Encontrados {len(relevant_emails)} emails relevantes")
        
        # Preparar contexto para a LLM
        email_texts = []
        for i, email in enumerate(relevant_emails, 1):
            email_text = f"""
EMAIL #{i}
De: {email['de_nome']}
Para: {email['para_nome']}
Data: {email['data']}
Assunto: {email['assunto']}
Mensagem: {email['mensagem']}
"""
            email_texts.append(email_text)
        
        context = "\n---\n".join(email_texts)
        
        # Prompt para análise
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um detetive analisando emails corporativos.
Sua tarefa é identificar se há evidências de Michael Scott conspirando contra Toby Flenderson.

Procure por:
- Comentários negativos sobre Toby
- Planos para prejudicar ou sabotar Toby
- Tentativas de evitar ou excluir Toby
- Atitudes hostis ou desrespeitosas

Responda em formato JSON:
{{
    "conspiracy_found": true/false,
    "confidence": "baixa/média/alta",
    "evidence": ["evidência 1", "evidência 2", ...],
    "summary": "resumo da análise"
}}"""),
            ("human", "Analise os seguintes emails:\n\n{emails}")
        ])
        
        llm = get_llm()
        chain = prompt | llm
        
        result = chain.invoke({"emails": context})
        
        return {
            "raw_result": result.content,
            "relevant_emails": relevant_emails
        }


def demo_conspiracy():
    """Demonstração do detector de conspiração"""
    print("\n" + "="*60)
    print("DETECTOR DE CONSPIRAÇÃO - OPERAÇÃO ANTI-TOBY")
    print("="*60 + "\n")
    
    detector = ConspiracyDetector("data/emails.txt")
    detector.parse_emails()
    
    result = detector.analyze_conspiracy()
    
    print("\n[*] RESULTADO DA ANÁLISE:")
    print("="*60)
    print(result['raw_result'])
    
    if result['relevant_emails']:
        print(f"\n\n[*] EMAILS RELEVANTES ENCONTRADOS: {len(result['relevant_emails'])}")
        print("="*60)
        for i, email in enumerate(result['relevant_emails'][:3], 1):
            print(f"\n{i}. {email['assunto']}")
            print(f"   De: {email['de_nome']} ({email['data']})")
            print(f"   Trecho: {email['mensagem'][:200]}...")


if __name__ == "__main__":
    demo_conspiracy()