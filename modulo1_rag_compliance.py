"""
Módulo 1: Chatbot RAG de Compliance
Sistema de consulta sobre políticas de compliance usando RAG
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from llm_config import get_llm
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import pickle


class ComplianceChatbot:
    def __init__(self, policy_file: str, persist_dir: str = "./faiss_index"):
        """
        Inicializa o chatbot RAG de compliance
        
        Args:
            policy_file: Caminho para o arquivo de política
            persist_dir: Diretório para persistir o banco vetorial
        """
        self.policy_file = policy_file
        self.persist_dir = persist_dir
        self.vectorstore = None
        self.qa_chain = None
        
    def load_and_index(self):
        """Carrega o documento e cria o índice vetorial"""
        print("[*] Carregando política de compliance...")
        
        # Ler arquivo
        with open(self.policy_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Dividir em chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n==", "\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        
        print(f"[*] Documento dividido em {len(chunks)} chunks")
        
        # Criar embeddings e vectorstore
        embeddings = OpenAIEmbeddings()
        
        # Criar metadados simples
        metadatas = [{"chunk": i, "source": "politica_compliance.txt"} 
                     for i in range(len(chunks))]
        
        self.vectorstore = FAISS.from_texts(
            texts=chunks,
            embedding=embeddings,
            metadatas=metadatas
        )
        
        # Salvar índice
        os.makedirs(self.persist_dir, exist_ok=True)
        self.vectorstore.save_local(self.persist_dir)
        
        print("[OK] Índice vetorial criado com sucesso!")
        
    def load_existing_index(self):
        """Carrega índice existente"""
        print("[*] Carregando índice existente...")
        embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local(
            self.persist_dir, 
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("[OK] Índice carregado!")
        
    def setup_qa_chain(self):
        """Configura a chain de Q&A"""
        
        # Template do prompt
        template = """Você é um assistente especializado em políticas de compliance da Dunder Mifflin.

Use as informações do contexto abaixo para responder a pergunta do funcionário.
Seja direto, claro e cite as seções relevantes quando apropriado.

Contexto:
{context}

Pergunta: {question}

Resposta detalhada:"""

        PROMPT = PromptTemplate(
            template=template, 
            input_variables=["context", "question"]
        )
        
        # LLM
        llm = get_llm()
        
        # Chain de retrieval
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("[OK] Chain de Q&A configurada!")
        
    def ask(self, question: str) -> dict:
        """
        Faz uma pergunta ao chatbot
        
        Args:
            question: Pergunta sobre compliance
            
        Returns:
            Dict com resposta e documentos fonte
        """
        if self.qa_chain is None:
            raise ValueError("Chain não inicializada. Execute setup_qa_chain() primeiro.")
            
        result = self.qa_chain.invoke({"query": question})
        return result


def demo_chatbot():
    """Demonstração do chatbot"""
    print("\n" + "="*60)
    print("CHATBOT DE COMPLIANCE - DUNDER MIFFLIN")
    print("="*60 + "\n")
    
    # Inicializar
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
    
    # Perguntas de teste
    test_questions = [
        "Qual é o limite para despesas menores que não precisam de aprovação?",
        "Posso usar o dinheiro da empresa para comprar equipamentos de mágica?",
        "Quem pode aprovar despesas entre $50 e $500?",
    ]
    
    for q in test_questions:
        print(f"\n[?] Pergunta: {q}")
        print("-" * 60)
        result = chatbot.ask(q)
        print(f"[A] Resposta: {result['result']}\n")
    
    # Modo interativo
    print("\n" + "="*60)
    print("Modo interativo (digite 'sair' para encerrar)")
    print("="*60 + "\n")
    
    while True:
        question = input("\n[?] Sua pergunta: ").strip()
        
        if question.lower() in ['sair', 'exit', 'quit']:
            print("\n[*] Até logo!")
            break
            
        if not question:
            continue
            
        result = chatbot.ask(question)
        print(f"\n[A] Resposta: {result['result']}")


if __name__ == "__main__":
    demo_chatbot()