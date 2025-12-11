"""
Módulo 3: Detector de Fraudes
Analisa transações bancárias e identifica quebras de compliance
"""

import pandas as pd
from typing import List, Dict, Tuple
from llm_config import get_llm
from langchain.prompts import ChatPromptTemplate


class FraudDetector:
    def __init__(self, transactions_file: str, policy_file: str):
        """
        Inicializa o detector de fraudes
        
        Args:
            transactions_file: Caminho para CSV de transações
            policy_file: Caminho para política de compliance
        """
        self.transactions_file = transactions_file
        self.policy_file = policy_file
        self.df = None
        self.policy_text = None
        
    def load_data(self):
        """Carrega transações e política"""
        print("[*] Carregando transações...")
        self.df = pd.read_csv(self.transactions_file)
        print(f"[OK] {len(self.df)} transações carregadas")
        
        print("[*] Carregando política...")
        with open(self.policy_file, 'r', encoding='utf-8') as f:
            self.policy_text = f.read()
        print("[OK] Política carregada")
    
    def check_simple_violations(self) -> List[Dict]:
        """
        Verifica violações simples de compliance baseadas em regras
        
        Regras verificadas:
        1. Despesas > $500 sem aprovação prévia (Purchase Order)
        2. Itens proibidos (armas, mágica, etc)
        3. Smurfing (divisão de compras grandes)
        """
        violations = []
        
        print("\n[*] Verificando violações simples...")
        
        # Regra 1: Despesas > $500
        high_value = self.df[self.df['valor'] > 500]
        for _, row in high_value.iterrows():
            # Verificar se não é uma categoria que normalmente passa de $500
            if row['categoria'] not in ['Viagem', 'Hospedagem']:
                violations.append({
                    'id': row['id_transacao'],
                    'tipo': 'ALTO_VALOR_SEM_PO',
                    'funcionario': row['funcionario'],
                    'valor': row['valor'],
                    'descricao': row['descricao'],
                    'data': row['data'],
                    'severidade': 'ALTA',
                    'regra': 'Seção 1.3 - Despesas acima de $500 requerem Purchase Order'
                })
        
        # Regra 2: Itens proibidos
        forbidden_keywords = [
            'arma', 'airsoft', 'katana', 'ninja', 'mágica', 'magic',
            'algema', 'corrente', 'pombo', 'karaoke', 'discoteca',
            'vigilância', 'binóculo', 'walkie', 'spy', 'armadilha',
            'hooters', 'strip'
        ]
        
        for _, row in self.df.iterrows():
            desc_lower = row['descricao'].lower()
            for keyword in forbidden_keywords:
                if keyword in desc_lower:
                    violations.append({
                        'id': row['id_transacao'],
                        'tipo': 'ITEM_PROIBIDO',
                        'funcionario': row['funcionario'],
                        'valor': row['valor'],
                        'descricao': row['descricao'],
                        'data': row['data'],
                        'severidade': 'CRÍTICA',
                        'regra': 'Seção 3 - Item proibido detectado: ' + keyword
                    })
                    break
        
        # Regra 3: Smurfing - mesma pessoa, mesmo dia, valores suspeitos
        df_grouped = self.df.groupby(['funcionario', 'data', 'categoria']).agg({
            'valor': ['sum', 'count'],
            'id_transacao': list,
            'descricao': list
        }).reset_index()
        
        for _, group in df_grouped.iterrows():
            total = group[('valor', 'sum')]
            count = group[('valor', 'count')]
            
            # Se total > 500 mas dividido em múltiplas transações < 500
            if total > 500 and count > 1:
                transactions = group[('id_transacao', 'list')]
                if all(self.df[self.df['id_transacao'] == tid]['valor'].values[0] < 500 
                       for tid in transactions):
                    violations.append({
                        'id': ', '.join(transactions),
                        'tipo': 'SMURFING_SUSPEITO',
                        'funcionario': group['funcionario'],
                        'valor': total,
                        'descricao': f"{count} transações no mesmo dia totalizando ${total:.2f}",
                        'data': group['data'],
                        'severidade': 'ALTA',
                        'regra': 'Seção 1.3 - Possível estruturação de compra para evitar aprovação'
                    })
        
        print(f"[!] {len(violations)} violações simples detectadas")
        return violations
    
    def check_contextual_violations(self, emails_file: str) -> List[Dict]:
        """
        Verifica violações que requerem contexto de emails
        Procura por combinações suspeitas de emails + transações
        """
        print("\n[*] Verificando violações contextuais (com emails)...")
        
        violations = []
        
        # Carregar emails
        with open(emails_file, 'r', encoding='utf-8') as f:
            email_content = f.read()
        
        # Preparar transações suspeitas para análise
        suspicious_transactions = self.df[
            (self.df['valor'] > 100) | 
            (self.df['categoria'].isin(['Diversos', 'Segurança']))
        ].head(50)  # Limitar para não explodir o contexto
        
        # Criar contexto
        trans_text = []
        for _, row in suspicious_transactions.iterrows():
            trans_text.append(
                f"ID: {row['id_transacao']} | "
                f"Funcionário: {row['funcionario']} | "
                f"Data: {row['data']} | "
                f"Valor: ${row['valor']:.2f} | "
                f"Descrição: {row['descricao']}"
            )
        
        context = {
            "transacoes": "\n".join(trans_text[:30]),
            "emails": email_content[:8000]  # Limitar tamanho
        }
        
        # Prompt para análise contextual
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um auditor de compliance analisando transações e emails.

Procure por evidências de:
1. Funcionários combinando desvios de verba via email
2. Compras suspeitas mencionadas em emails
3. Conflitos de interesse (ex: comprar de parentes)
4. Uso de verba da empresa para negócios pessoais

Retorne apenas as fraudes CLARAS com evidência nos emails.
Formato JSON:
{{
    "violations": [
        {{
            "transaction_id": "TX_XXX",
            "employee": "nome",
            "fraud_type": "tipo",
            "evidence": "trecho do email que prova",
            "severity": "CRÍTICA/ALTA/MÉDIA"
        }}
    ]
}}"""),
            ("human", """TRANSAÇÕES SUSPEITAS:
{transacoes}

EMAILS CORPORATIVOS:
{emails}

Analise e identifique fraudes com evidência clara nos emails.""")
        ])
        
        llm = get_llm()
        chain = prompt | llm
        
        result = chain.invoke(context)
        
        print("[OK] Análise contextual concluída")
        
        return {
            "contextual_analysis": result.content,
            "transactions_analyzed": len(suspicious_transactions)
        }
    
    def generate_report(self, simple_violations: List[Dict], 
                       contextual_result: Dict) -> str:
        """Gera relatório consolidado de fraudes"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE AUDITORIA - DUNDER MIFFLIN SCRANTON")
        report.append("=" * 80)
        report.append("")
        
        # Violações simples
        report.append(f"VIOLAÇÕES DETECTADAS POR REGRAS: {len(simple_violations)}")
        report.append("-" * 80)
        
        # Agrupar por severidade
        critical = [v for v in simple_violations if v['severidade'] == 'CRÍTICA']
        high = [v for v in simple_violations if v['severidade'] == 'ALTA']
        
        if critical:
            report.append(f"\n[CRITICAS] ({len(critical)}):")
            for v in critical[:5]:
                report.append(f"  - {v['id']}: {v['funcionario']} - {v['descricao']}")
                report.append(f"    Valor: ${v['valor']:.2f} | Regra: {v['regra']}")
        
        if high:
            report.append(f"\n[ALTAS] ({len(high)}):")
            for v in high[:5]:
                report.append(f"  - {v['id']}: {v['funcionario']} - {v['tipo']}")
                report.append(f"    Valor: ${v['valor']:.2f} | Regra: {v['regra']}")
        
        # Violações contextuais
        report.append("\n" + "=" * 80)
        report.append("VIOLAÇÕES CONTEXTUAIS (EMAILS + TRANSAÇÕES):")
        report.append("-" * 80)
        report.append(contextual_result['contextual_analysis'])
        
        return "\n".join(report)


def demo_fraud_detection():
    """Demonstração do detector de fraudes"""
    print("\n" + "="*60)
    print("DETECTOR DE FRAUDES - AUDITORIA TOBY")
    print("="*60 + "\n")
    
    detector = FraudDetector("data/transacoes_bancarias.csv", "data/politica_compliance.txt")
    detector.load_data()
    
    # Verificar violações simples
    simple_violations = detector.check_simple_violations()
    
    # Verificar violações contextuais
    contextual_result = detector.check_contextual_violations("data/emails.txt")
    
    # Gerar relatório
    report = detector.generate_report(simple_violations, contextual_result)
    
    print("\n" + report)
    
    # Salvar relatório
    with open("relatorio_auditoria.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n[*] Relatório salvo em: relatorio_auditoria.txt")


if __name__ == "__main__":
    demo_fraud_detection()