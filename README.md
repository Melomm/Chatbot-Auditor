# Sistema de Auditoria Dunder Mifflin

Sistema de auditoria inteligente desenvolvido para detectar violações de compliance, fraudes financeiras e conspiração corporativa usando LLMs e RAG (Retrieval-Augmented Generation).


https://github.com/user-attachments/assets/911a6863-9c0f-4b90-8167-434de828971f


## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Executar](#como-executar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades Detalhadas](#funcionalidades-detalhadas)

---

## Visão Geral

O sistema é composto por três módulos independentes que podem ser executados separadamente ou de forma integrada:

1. **Módulo 1 - Chatbot RAG de Compliance**: Sistema de perguntas e respostas sobre políticas corporativas usando busca vetorial
2. **Módulo 2 - Detector de Conspiração**: Análise de emails corporativos usando LLM para identificar padrões de comportamento hostil
3. **Módulo 3 - Detector de Fraudes**: Análise de transações bancárias com regras determinísticas e análise contextual via LLM

---

## Arquitetura do Sistema

### Visão Geral da Arquitetura
```
┌────────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE AUDITORIA                            │
│                      (main.py - Orquestrador)                      │
└────────────────────────────────────────────────────────────────────┘
                              |
         ┌────────────────────┼────────────────────┐
         |                    |                    |
         v                    v                    v
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   MÓDULO 1      │  │   MÓDULO 2      │  │   MÓDULO 3      │
│   RAG Engine    │  │   Email         │  │   Fraud         │
│   (Q&A)         │  │   Analyzer      │  │   Detector      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Módulo 1: RAG de Compliance (modulo1_rag_compliance.py)

**Objetivo**: Responder perguntas sobre políticas de compliance usando busca semântica

**Componentes**:
```
[Documento de Política]
         |
         v
[RecursiveCharacterTextSplitter]
  - chunk_size: 1000
  - chunk_overlap: 200
         |
         v
[OpenAI Embeddings (text-embedding-ada-002)]
         |
         v
[FAISS Vector Store] <--- Persistência em disco
         |
         v
[Similarity Search (k=4)]
         |
         v
[LLM + Prompt Template]
  - Groq (Llama 3.3 70B) ou
  - OpenAI (GPT-4o-mini)
         |
         v
[Resposta Contextualizada]
```

**Fluxo de Execução**:

1. **Indexação (primeira execução)**:
   - Carrega `politica_compliance.txt`
   - Divide em chunks de 1000 caracteres com overlap de 200
   - Gera embeddings usando OpenAI
   - Armazena no FAISS (salvo em `./faiss_index/`)

2. **Query (tempo de execução)**:
   - Recebe pergunta do usuário
   - Converte pergunta em embedding
   - Busca top-4 chunks mais similares no FAISS
   - Envia chunks + pergunta para LLM
   - Retorna resposta com citações

**Ferramentas**:
- LangChain: Orquestração de chains
- FAISS: Banco vetorial (Facebook AI Similarity Search)
- OpenAI Embeddings: Geração de embeddings
- Groq/OpenAI: Geração de respostas

---

### Módulo 2: Detector de Conspiração (modulo2_conspiracy_detector.py)

**Objetivo**: Analisar emails corporativos para identificar padrões de hostilidade

**Componentes**:
```
[Arquivo de Emails (emails.txt)]
         |
         v
[Regex Parser]
  - Extrai: De, Para, Data, Assunto, Mensagem
         |
         v
[Filtro de Relevância]
  - Remetente = Michael Scott
  - Menciona: Toby, HR, etc.
         |
         v
[Agregação de Contexto]
  - Formata emails relevantes
         |
         v
[LLM Analyzer]
  - Prompt: "Você é um detetive..."
  - Análise de sentimento
  - Identificação de evidências
         |
         v
[Relatório JSON]
  {
    "conspiracy_found": true/false,
    "confidence": "baixa/média/alta",
    "evidence": [...],
    "summary": "..."
  }
```

**Fluxo de Execução**:

1. **Parse de Emails**:
   - Lê arquivo completo
   - Divide por separadores
   - Usa regex para extrair campos estruturados
   - Armazena em lista de dicionários

2. **Filtragem**:
   - Identifica emails de Michael Scott
   - Verifica menção a keywords relacionadas a Toby
   - Retorna subset de emails relevantes

3. **Análise LLM**:
   - Concatena emails relevantes
   - Envia para LLM com prompt especializado
   - Recebe análise estruturada em JSON

**Ferramentas**:
- Regex: Parsing de emails
- LangChain: Prompt templates
- Groq/OpenAI: Análise de sentimento e contexto

---

### Módulo 3: Detector de Fraudes (modulo3_fraud_detector.py)

**Objetivo**: Identificar violações de compliance em transações bancárias

**Componentes**:
```
[Transações CSV]     [Política TXT]     [Emails TXT]
       |                    |                 |
       v                    v                 v
[Pandas DataFrame]   [String Buffer]   [String Buffer]
       |                    |                 |
       └────────────────────┴─────────────────┘
                          |
       ┌──────────────────┴──────────────────┐
       |                                     |
       v                                     v
[Rule Engine]                        [LLM Contextual]
  - Valor > $500                       - Cruza emails
  - Itens proibidos                    - Identifica combos
  - Smurfing detection                 - Conflitos interesse
       |                                     |
       v                                     v
[Violações Simples]                  [Violações Contextuais]
       |                                     |
       └──────────────────┬──────────────────┘
                          v
                  [Relatório Consolidado]
                  - Críticas / Altas / Médias
                  - Evidências
                  - Estatísticas
```

**Fluxo de Execução**:

1. **Carregamento de Dados**:
   - CSV de transações -> Pandas DataFrame
   - Política de compliance -> String
   - Emails -> String

2. **Análise de Violações Simples** (Rule-Based):
   
   **Regra 1 - Alto Valor**:
```python
   if transacao.valor > 500 and categoria not in ['Viagem', 'Hospedagem']:
       violacao = "Requer Purchase Order"
```
   
   **Regra 2 - Itens Proibidos**:
```python
   keywords_proibidas = ['arma', 'mágica', 'vigilância', 'walkie', ...]
   if keyword in descricao.lower():
       violacao = "Item proibido"
```
   
   **Regra 3 - Smurfing**:
```python
   group = transacoes.groupby(['funcionario', 'data', 'categoria'])
   if group.valor.sum() > 500 and group.valor.count() > 1:
       violacao = "Estruturação suspeita"
```

3. **Análise Contextual** (LLM-Based):
   - Seleciona transações suspeitas (valor > 100 ou categorias sensíveis)
   - Extrai trechos relevantes de emails
   - Envia contexto combinado para LLM
   - LLM identifica fraudes que requerem contexto:
     - Funcionários combinando desvios
     - Compras de parentes (conflito interesse)
     - Negócios pessoais com verba corporativa

4. **Geração de Relatório**:
   - Consolida violações simples e contextuais
   - Categoriza por severidade (CRÍTICA, ALTA, MÉDIA)
   - Salva em arquivo texto

**Ferramentas**:
- Pandas: Análise de dados tabulares
- Regex: Detecção de padrões em descrições
- LangChain: Prompt engineering para análise contextual
- Groq/OpenAI: Análise de fraudes complexas

---

### Configuração de LLM (llm_config.py)

**Objetivo**: Centralizar configuração de modelos LLM com fallback automático

**Estratégia**:
```python
def get_llm():
    # 1. Tenta Groq (grátis, rápido)
    if GROQ_API_KEY exists:
        return ChatGroq(model="llama-3.3-70b-versatile")
    
    # 2. Fallback para OpenAI
    if OPENAI_API_KEY exists:
        return ChatOpenAI(model="gpt-4o-mini")
    
    # 3. Erro se nenhuma key
    raise ValueError("Configure API key")
```

**Vantagens**:
- Permite trocar LLM sem modificar módulos
- Suporta múltiplos provedores
- Fallback automático

---

## Tecnologias Utilizadas

### Core Framework
- **LangChain**: Orquestração de LLMs, chains e prompts
- **Python 3.8+**: Linguagem base

### LLMs e Embeddings
- **Groq (Llama 3.3 70B)**: LLM principal (grátis, 500+ tokens/s)
- **OpenAI GPT-4o-mini**: LLM alternativo
- **OpenAI text-embedding-ada-002**: Geração de embeddings

### Armazenamento Vetorial
- **FAISS**: Banco vetorial em memória com persistência

### Processamento de Dados
- **Pandas**: Análise de transações CSV
- **Regex**: Parsing de emails e detecção de padrões

### Infraestrutura
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **tiktoken**: Contagem de tokens

---

## Requisitos

### Dependências Python
Todas listadas em `requirements.txt`:
```
langchain>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5
langchain-groq>=0.1.0
faiss-cpu>=1.7.4
pandas>=2.0.0
python-dotenv>=1.0.0
openai>=1.0.0
tiktoken>=0.5.0
```

### API Keys Necessárias

**Opção 1 (Recomendada)**: Groq
- Gratuito
- Rápido (500+ tokens/segundo)
- Sem necessidade de cartão de crédito
- Obter em: https://console.groq.com/

**Opção 2**: OpenAI
- Requer cartão de crédito
- Custo aproximado: $0.10 por auditoria completa
- Obter em: https://platform.openai.com/

---

## Instalação

### Passo 1: Clonar/Baixar Projeto
```bash
# Se usando Git
git clone <url-do-repositorio>
cd dunder-mifflin-audit

# Ou baixe e extraia o ZIP
```

### Passo 2: Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Preparar Dados

Coloque os arquivos de dados na pasta `data/`:
```
projeto/
├── data/
│   ├── politica_compliance.txt
│   ├── transacoes_bancarias.csv
│   └── emails.txt
├── main.py
├── modulo1_rag_compliance.py
├── modulo2_conspiracy_detector.py
├── modulo3_fraud_detector.py
├── llm_config.py
├── setup.py
└── requirements.txt
```

---

## Configuração

### Configurar API Key

#### Opção A: Groq (Recomendado)

1. Acesse: https://console.groq.com/
2. Crie uma conta (gratuito)
3. Vá em "API Keys"
4. Clique em "Create API Key"
5. Copie a chave (começa com `gsk-`)

#### Opção B: OpenAI

1. Acesse: https://platform.openai.com/
2. Faça login
3. Vá em "API Keys"
4. Crie nova chave
5. Copie a chave (começa com `sk-`)

### Criar Arquivo .env

Crie um arquivo chamado `.env` na raiz do projeto:
```bash
# Opção 1: Groq (recomendado - grátis)
GROQ_API_KEY=gsk-sua-chave-aqui

# Opção 2: OpenAI (alternativa)
OPENAI_API_KEY=sk-sua-chave-aqui

# Você pode configurar ambas (Groq terá prioridade)
```

**IMPORTANTE**: O arquivo `.env` já está no `.gitignore` e não será commitado

### Verificar Instalação

Execute o script de verificação:
```bash
python setup.py
```

Saída esperada:
```
============================================================
SETUP - SISTEMA DE AUDITORIA DUNDER MIFFLIN
============================================================

[*] Verificando: Versão do Python
------------------------------------------------------------
[OK] Python 3.8

[*] Verificando: Arquivos de dados
------------------------------------------------------------
[OK] data/politica_compliance.txt
[OK] data/transacoes_bancarias.csv
[OK] data/emails.txt

[*] Verificando: Arquivo .env
------------------------------------------------------------
[OK] .env configurado (Groq detectado)

[*] Verificando: Configuração LLM
------------------------------------------------------------
[OK] llm_config.py encontrado

[*] Verificando: Dependências
------------------------------------------------------------
[OK] Todas as dependências obrigatórias instaladas

============================================================
[OK] SETUP COMPLETO! Sistema pronto para uso.
============================================================
```

---

## Como Executar

### Execução do Sistema Completo (Recomendado)
```bash
python main.py
```

#### Menu Interativo
```
--------------------------------------------------------------------------------
MENU PRINCIPAL:
--------------------------------------------------------------------------------
1. [RAG] Chatbot de Compliance
2. [CONSPIRACY] Detector de Conspiração (Michael vs Toby)
3. [FRAUD] Detector de Fraudes (Análise de Transações)
4. [FULL] Auditoria Completa (Todos os módulos)
0. [EXIT] Sair
--------------------------------------------------------------------------------
```

**Opção 1**: Chatbot interativo de perguntas e respostas
**Opção 2**: Análise de conspiração em emails
**Opção 3**: Detecção de fraudes em transações
**Opção 4**: Executa módulos 2 e 3 sequencialmente

### Execução de Módulos Individuais

#### Módulo 1: RAG de Compliance
```bash
python modulo1_rag_compliance.py
```

Funcionalidades:
- Cria/carrega índice vetorial automaticamente
- Executa 3 perguntas de teste
- Entra em modo interativo
- Digite 'sair' para encerrar

#### Módulo 2: Detector de Conspiração
```bash
python modulo2_conspiracy_detector.py
```

Funcionalidades:
- Parse automático de todos os emails
- Filtragem de emails relevantes
- Análise via LLM
- Exibe resultado JSON

#### Módulo 3: Detector de Fraudes
```bash
python modulo3_fraud_detector.py
```

Funcionalidades:
- Carrega transações e política
- Aplica regras de compliance
- Análise contextual com emails
- Gera relatório em `relatorio_auditoria.txt`

---

## Estrutura do Projeto
```
dunder-mifflin-audit/
│
├── data/                                # Dados de entrada
│   ├── politica_compliance.txt          # Política corporativa
│   ├── transacoes_bancarias.csv         # Transações bancárias
│   └── emails.txt                       # Dump de emails
│
├── faiss_index/                         # Índice vetorial (gerado)
│   ├── index.faiss                      # Vetores FAISS
│   └── index.pkl                        # Metadados
│
├── venv/                                # Ambiente virtual Python
│
├── main.py                              # Orquestrador principal
├── modulo1_rag_compliance.py            # Chatbot RAG
├── modulo2_conspiracy_detector.py       # Detector de conspiração
├── modulo3_fraud_detector.py            # Detector de fraudes
├── llm_config.py                        # Configuração centralizada LLM
├── setup.py                             # Script de verificação
│
├── requirements.txt                     # Dependências Python
├── .env                                 # Variáveis de ambiente (criar)
├── .env.example                         # Template de configuração
├── .gitignore                           # Arquivos ignorados pelo Git
│
├── README.md                            # Este arquivo
│
└── relatorio_auditoria.txt              # Relatório gerado (output)
```

### Arquivos Gerados Durante Execução

- `faiss_index/`: Índice vetorial do FAISS (persistente)
- `relatorio_auditoria.txt`: Relatório de fraudes (Módulo 3)
- `relatorio_completo.txt`: Relatório consolidado (Opção 4)

---

## Funcionalidades Detalhadas

### 1. Chatbot RAG de Compliance

**Entrada**: Perguntas em linguagem natural
**Saída**: Respostas contextualizadas com citações

**Exemplos de Uso**:
```
[?] Pergunta: Qual é o limite para despesas menores?
[A] Resposta: Despesas menores (Categoria C) são aquelas até US$ 50,00.
O funcionário possui autonomia para realizar o gasto, mas deve solicitar
reembolso à Contabilidade em até 30 dias com recibo fiscal original.
(Seção 1.1)
```
```
[?] Pergunta: Posso comprar equipamentos de mágica?
[A] Resposta: Não. A Seção 3.1 proíbe explicitamente kits de mágica,
algemas de escape, correntes, fumaça em pó, pombos treinados e
baralhos marcados.
```

**Características**:
- Busca semântica (não keyword-based)
- Respostas sempre contextualizadas
- Citação de seções da política
- Índice persistente (rápido após primeira execução)

---

### 2. Detector de Conspiração

**Entrada**: Arquivo de emails corporativos
**Saída**: Relatório JSON com análise de hostilidade

**Saída Exemplo**:
```json
{
    "conspiracy_found": true,
    "confidence": "alta",
    "evidence": [
        "Email de 15/04 onde Michael exclui Toby de evento",
        "Email de 22/04 com comentários depreciativos sobre RH",
        "Email de 03/05 ignorando solicitações de Toby"
    ],
    "summary": "Análise identificou padrão sistemático de hostilidade..."
}
```

**Métricas**:
- Total de emails analisados: 1000+
- Emails relevantes identificados: ~10-20
- Tempo de execução: ~5-10 segundos

---

### 3. Detector de Fraudes

**Entrada**: CSV de transações + Emails corporativos
**Saída**: Relatório categorizado por severidade

**Tipos de Violações Detectadas**:

#### 3.1 Violações Simples (Rule-Based)

**Alto Valor Sem PO**:
- Transação: TX_1065 - Michael Scott - $223.10
- Regra: Seção 1.3 - Despesas acima de $500 requerem Purchase Order

**Item Proibido**:
- Transação: TX_1032 - Dwight Schrute - Walkie Talkies
- Regra: Seção 3.2 - Equipamento de vigilância proibido

**Smurfing**:
- Transações: TX_1100, TX_1101, TX_1102
- Total: $650 em 3 transações no mesmo dia
- Regra: Seção 1.3 - Estruturação para evitar aprovação

#### 3.2 Violações Contextuais (LLM-Based)

**Desvio Combinado**:
- Email: "Vamos dividir essa compra em duas notas..."
- Transação: 2x $450 no mesmo dia
- Tipo: Conspiração para fraude

**Conflito de Interesse**:
- Email: "Comprei velas da Jan para o escritório"
- Transação: $120 - Velas Serenity by Jan
- Tipo: Compra de cônjuge (Seção 3.3)

**Relatório Exemplo**:
```
================================================================================
RELATÓRIO DE AUDITORIA - DUNDER MIFFLIN SCRANTON
================================================================================

VIOLAÇÕES DETECTADAS POR REGRAS: 15

[CRITICAS] (3):
  - TX_1032: Dwight Schrute - Walkie Talkies
    Valor: $45.00 | Regra: Seção 3.2 - Equipamento de vigilância
  - TX_1033: Michael Scott - Binóculos visão noturna
    Valor: $180.00 | Regra: Seção 3.2 - Item proibido
  - TX_1156: Ryan Howard - WUPHF.com Investment
    Valor: $200.00 | Regra: Seção 3.3 - Investimento em startup

[ALTAS] (8):
  - TX_1100-1102: Andy Bernard - Smurfing suspeito
    Valor: $650.00 | Regra: Seção 1.3 - Estruturação

================================================================================
VIOLAÇÕES CONTEXTUAIS (EMAILS + TRANSAÇÕES):
--------------------------------------------------------------------------------
{
  "violations": [
    {
      "transaction_id": "TX_1156",
      "employee": "Ryan Howard",
      "fraud_type": "Investimento não autorizado",
      "evidence": "Email de 22/04: 'Investi $200 da empresa no WUPHF'",
      "severity": "CRÍTICA"
    }
  ]
}
```

---

## Troubleshooting

### Erro: "OPENAI_API_KEY not found"

**Solução**: Certifique-se de que o arquivo `.env` existe e contém pelo menos uma chave:
```bash
GROQ_API_KEY=gsk-sua-chave-aqui
```

### Erro: "No module named 'langchain'"

**Solução**: Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "File not found: data/politica_compliance.txt"

**Solução**: Verifique se os arquivos estão na pasta `data/`:
```bash
ls data/  # Linux/Mac
dir data\ # Windows
```

### Erro: Rate limit OpenAI

**Solução**: Use Groq (gratuito):
```bash
# No .env:
GROQ_API_KEY=gsk-sua-chave-aqui
```

### FAISS lento na primeira execução

**Normal**: A criação do índice vetorial leva ~10-30 segundos na primeira vez.
Execuções seguintes usam cache e são instantâneas.

### LLM retorna respostas genéricas

**Solução**: 
1. Aumente o `k` no retriever (linha ~97 do modulo1):
```python
search_kwargs={"k": 6}  # Era 4
```

2. Ou aumente o `chunk_size` (linha ~33):
```python
chunk_size=1500  # Era 1000
```

---

## Limitações Conhecidas

1. **Contexto do LLM**: Emails muito longos são truncados (limite ~8000 chars)
2. **Smurfing Detection**: Heurística simples (mesmo dia + categoria)
3. **Persistência**: FAISS usa arquivos locais (não é banco de dados)
4. **Embeddings**: Requer OpenAI (não há fallback para Groq nesta parte)
5. **Idioma**: Otimizado para português (política e emails em PT-BR)

