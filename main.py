"""
Sistema Principal de Auditoria - Dunder Mifflin
Integra os 3 módulos de análise
"""

import os
from dotenv import load_dotenv
from modulo1_rag_compliance import ComplianceChatbot
from modulo2_conspiracy_detector import ConspiracyDetector
from modulo3_fraud_detector import FraudDetector


def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main_menu():
    """Menu principal do sistema"""
    load_dotenv()
    
    # Verificar se pelo menos uma API key está configurada
    has_groq = os.getenv("GROQ_API_KEY")
    has_openai = os.getenv("OPENAI_API_KEY")
    
    if not has_groq and not has_openai:
        print("[!] ERRO: Nenhuma API key encontrada!")
        print("\nPor favor, configure pelo menos uma no arquivo .env:")
        print("  GROQ_API_KEY=gsk-sua-chave-aqui (RECOMENDADO - grátis)")
        print("  OPENAI_API_KEY=sk-sua-chave-aqui")
        print("\nObtenha uma chave Groq em: https://console.groq.com/")
        return
    
    # Informar qual será usada
    if has_groq:
        print("[*] Sistema configurado para usar Groq (grátis e rápido)")
    else:
        print("[*] Sistema configurado para usar OpenAI")
    
    print_header("SISTEMA DE AUDITORIA DUNDER MIFFLIN")
    print("Bem-vindo ao sistema de compliance e auditoria")
    print("Desenvolvido para Toby Flenderson - Recursos Humanos\n")
    
    while True:
        print("\n" + "-" * 80)
        print("MENU PRINCIPAL:")
        print("-" * 80)
        print("1. [RAG] Chatbot de Compliance")
        print("2. [CONSPIRACY] Detector de Conspiração (Michael vs Toby)")
        print("3. [FRAUD] Detector de Fraudes (Análise de Transações)")
        print("4. [FULL] Auditoria Completa (Todos os módulos)")
        print("0. [EXIT] Sair")
        print("-" * 80)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            run_compliance_chatbot()
        elif choice == "2":
            run_conspiracy_detector()
        elif choice == "3":
            run_fraud_detector()
        elif choice == "4":
            run_full_audit()
        elif choice == "0":
            print("\n[*] Tchau :)")
            break
        else:
            print("\n[!] Opção inválida!")

def run_compliance_chatbot():
    """Executa o módulo 1: Chatbot RAG"""
    print_header("MÓDULO 1: CHATBOT DE COMPLIANCE")
    
    chatbot = ComplianceChatbot("data/politica_compliance.txt")
    
    # Verificar se já existe índice
    if os.path.exists("./faiss_index"):
        try:
            chatbot.load_existing_index()
        except Exception as e:
            print(f"[!] Erro ao carregar índice: {e}")
            print("[*] Criando novo índice...")
            chatbot.load_and_index()
    else:
        chatbot.load_and_index()
    
    chatbot.setup_qa_chain()
    
    print("\n[OK] Chatbot pronto! Faça perguntas sobre a política de compliance.")
    print("Digite 'voltar' para retornar ao menu principal.\n")
    
    while True:
        question = input("[?] Sua pergunta: ").strip()
        
        if question.lower() in ['voltar', 'menu', 'sair']:
            break
            
        if not question:
            continue
            
        try:
            result = chatbot.ask(question)
            print(f"\n[A] Resposta:\n{result['result']}\n")
        except Exception as e:
            print(f"\n[!] Erro: {e}\n")


def run_conspiracy_detector():
    """Executa o módulo 2: Detector de Conspiração"""
    print_header("MÓDULO 2: DETECTOR DE CONSPIRAÇÃO")
    
    detector = ConspiracyDetector("data/emails.txt")
    detector.parse_emails()
    
    result = detector.analyze_conspiracy()
    
    print("\n[*] RESULTADO DA ANÁLISE:")
    print("=" * 80)
    print(result['raw_result'])
    
    if result['relevant_emails']:
        print(f"\n\n[*] EMAILS RELEVANTES: {len(result['relevant_emails'])}")
        print("=" * 80)
        
        show_all = input("\nMostrar todos os emails? (s/n): ").strip().lower()
        limit = None if show_all == 's' else 5
        
        for i, email in enumerate(result['relevant_emails'][:limit], 1):
            print(f"\n{i}. {email['assunto']}")
            print(f"   De: {email['de_nome']}")
            print(f"   Para: {email['para_nome']}")
            print(f"   Data: {email['data']}")
            print(f"   Mensagem: {email['mensagem'][:300]}...")
    
    input("\n\nPressione ENTER para voltar ao menu...")


def run_fraud_detector():
    """Executa o módulo 3: Detector de Fraudes"""
    print_header("MÓDULO 3: DETECTOR DE FRAUDES")
    
    detector = FraudDetector("data/transacoes_bancarias.csv", "data/politica_compliance.txt")
    detector.load_data()
    
    print("\n[*] Analisando transações...")
    simple_violations = detector.check_simple_violations()
    
    print("\n[*] Analisando contexto de emails...")
    contextual_result = detector.check_contextual_violations("data/emails.txt")
    
    report = detector.generate_report(simple_violations, contextual_result)
    
    print("\n" + report)
    
    # Salvar relatório
    filename = "relatorio_auditoria.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n[*] Relatório salvo em: {filename}")
    
    # Opção de ver detalhes
    if simple_violations:
        show_details = input("\nMostrar detalhes de todas as violações? (s/n): ").strip().lower()
        
        if show_details == 's':
            print("\n" + "=" * 80)
            print("DETALHES DAS VIOLAÇÕES:")
            print("=" * 80)
            
            for i, v in enumerate(simple_violations, 1):
                print(f"\n{i}. [{v['severidade']}] {v['tipo']}")
                print(f"   ID: {v['id']}")
                print(f"   Funcionário: {v['funcionario']}")
                print(f"   Data: {v['data']}")
                print(f"   Valor: ${v['valor']:.2f}")
                print(f"   Descrição: {v['descricao']}")
                print(f"   Regra Violada: {v['regra']}")
    
    input("\n\nPressione ENTER para voltar ao menu...")


def run_full_audit():
    """Executa auditoria completa (todos os módulos)"""
    print_header("AUDITORIA COMPLETA - TODOS OS MÓDULOS")
    
    print("[*] Iniciando auditoria completa...")
    print("Isso pode levar alguns minutos...\n")
    
    # Módulo 2: Conspiração
    print("\n[*] [1/2] Analisando conspiração...")
    detector_conspiracy = ConspiracyDetector("data/emails.txt")
    detector_conspiracy.parse_emails()
    conspiracy_result = detector_conspiracy.analyze_conspiracy()
    
    # Módulo 3: Fraudes
    print("\n[*] [2/2] Analisando fraudes...")
    detector_fraud = FraudDetector("data/transacoes_bancarias.csv", "data/politica_compliance.txt")
    detector_fraud.load_data()
    simple_violations = detector_fraud.check_simple_violations()
    contextual_result = detector_fraud.check_contextual_violations("data/emails.txt")
    
    # Gerar relatório consolidado
    print("\n[*] Gerando relatório consolidado...")
    
    full_report = []
    full_report.append("=" * 80)
    full_report.append("RELATÓRIO DE AUDITORIA COMPLETA - DUNDER MIFFLIN SCRANTON")
    full_report.append("Sistema desenvolvido para Toby Flenderson - RH")
    full_report.append("=" * 80)
    full_report.append("")
    
    # Seção 1: Conspiração
    full_report.append("## SEÇÃO 1: ANÁLISE DE CONSPIRAÇÃO")
    full_report.append("-" * 80)
    full_report.append(conspiracy_result['raw_result'])
    full_report.append("")
    
    # Seção 2: Fraudes
    full_report.append("\n## SEÇÃO 2: ANÁLISE DE FRAUDES")
    full_report.append("-" * 80)
    fraud_report = detector_fraud.generate_report(simple_violations, contextual_result)
    full_report.append(fraud_report)
    
    # Estatísticas
    full_report.append("\n\n## ESTATÍSTICAS GERAIS")
    full_report.append("-" * 80)
    full_report.append(f"Total de transações analisadas: {len(detector_fraud.df)}")
    full_report.append(f"Total de emails analisados: {len(detector_conspiracy.emails)}")
    full_report.append(f"Violações de compliance detectadas: {len(simple_violations)}")
    full_report.append(f"Emails suspeitos (Michael vs Toby): {len(conspiracy_result.get('relevant_emails', []))}")
    
    full_report_text = "\n".join(full_report)
    
    # Mostrar na tela
    print("\n" + full_report_text)
    
    # Salvar
    filename = "relatorio_completo.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_report_text)
    
    print(f"\n\n[*] Relatório completo salvo em: {filename}")
    
    input("\n\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    main_menu()