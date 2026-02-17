# ===============================
# 設計書RAGチャットボット - UI部分
# ===============================
import streamlit as st
from loader import load_documents_from_files
from rag import create_rag_chain

# -------------------------------
# 🔹 ページ基本設定
# -------------------------------
st.set_page_config(
    page_title="📚設計書RAGチャットボット",
    layout="wide"
)

st.title("📚設計書RAGチャットボット")

# ============================
# 📂 サイドバー：ファイルアップロード
# ============================
st.sidebar.header("📂 設計書アップロード")

uploaded_files = st.sidebar.file_uploader(
    "Word / Excel を選択してください",
    type=["docx", "xlsx"],
    accept_multiple_files=True
)

# ============================
# 🔐 セッション初期化
# ============================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# ============================
# 📚 ファイルがアップロードされたらRAG生成
# ============================
if uploaded_files:

    with st.spinner("📂 ドキュメント解析中..."):
        documents = load_documents_from_files(uploaded_files)
        st.session_state.qa_chain = create_rag_chain(documents)

    st.sidebar.success("✅ 読み込み完了")

# 🔁 セッションリセット
if st.sidebar.button("🔄 会話をリセット"):
    st.session_state.messages = []
    st.rerun()

# ============================
# 💬 履歴表示
# ============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================
# 📝 入力
# ============================
if prompt := st.chat_input("質問を入力してください"):

    if not st.session_state.qa_chain:
        st.warning("⚠ 先に設計書をアップロードしてください")
        st.stop()

    # ユーザー表示
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # アシスタント回答
    with st.chat_message("assistant"):
        with st.spinner("🤔 回答生成中..."):
            response = st.session_state.qa_chain.invoke(prompt)

        st.markdown(response)

    # AIメッセージ保存
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
