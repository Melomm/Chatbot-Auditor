# QUICKRUN

### 1. Baixar os Arquivos
```bash
# Baixe todos os arquivos gerados para sua máquina
```

### 2. Organizar o Projeto
```bash
# Crie uma pasta para o projeto
mkdir dunder-mifflin-audit
cd dunder-mifflin-audit

# Coloque todos os arquivos .py, .md e .txt na raiz
```

### 3. Adicionar os Dados
```bash
# Copie os 3 arquivos fornecidos para a raiz:
# - politica_compliance.txt
# - transacoes_bancarias.csv
# - emails.txt
```

### 4. Setup do Ambiente
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 5. Configurar API Key
```bash
# Criar arquivo .env
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > .env

# Ou copie o .env.example e edite
cp .env.example .env
# Depois edite o .env com sua chave
```

### 6. Verificar Setup
```bash
python setup.py
# Deve mostrar todos [OK]
```

### 7. Testar o Sistema
```bash
# Rodar o sistema completo
python main.py

# Ou testar módulos individualmente:
python modulo1_rag_compliance.py
python modulo2_conspiracy_detector.py
python modulo3_fraud_detector.py
```
