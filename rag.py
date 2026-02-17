# ===============================
# RAGロジック本体
# ===============================
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def create_rag_chain(documents):

    # --------------------------
    # ① テキスト分割
    # --------------------------
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    split_docs = text_splitter.split_documents(documents)

    # --------------------------
    # ② Embeddingモデル
    # --------------------------
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = FAISS.from_documents(split_docs, embeddings)

    # Retriever生成（上位8件取得）
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 8}
    )

    # --------------------------
    # ③ OpenAI LLM
    # --------------------------
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    # --------------------------
    # ④ RAG専用プロンプト
    # --------------------------
    prompt = ChatPromptTemplate.from_template("""
あなたは設計書専門アシスタントです。
必ずコンテキストに記載された情報のみから回答してください。
推測は禁止です。
情報が無い場合は「設計書内に記載がありません」と答えてください。

【コンテキスト】
{context}

【質問】
{question}

【回答】
""")

    # --------------------------
    # ⑤ RAGチェーン構築
    # --------------------------
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": lambda x: x,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
