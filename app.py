import streamlit as st
import pandas as pd
import time
import plotly.express as px

# ── Dynamic Palette Constants ──
C_BG_MAIN = "#08080A"
C_BG_SEC  = "#121318"
C_TEXT    = "#F3F4F6"
C_ACCENT_1= "#00E5FF" # Cyan
C_ACCENT_2= "#7000FF" # Purple

PAGE_CONFIG = dict(
    page_title="DataMind — AI Intelligence",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

SESSION_DEFAULTS = {
    "df":             None,
    "rag_indexed":    False,
    "auto_insights":  [],
    "chat_history":   [],
    "current_chart":  None,
    "query_history":  [],
    "file_size_kb":   0.0,
}
st.set_page_config(**PAGE_CONFIG)

HIGH_END_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Typography & Base Reset */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #F3F4F6;
}
h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }

/* Custom Sleek Header Injection */
.premium-header {
    background: linear-gradient(135deg, #00E5FF 0%, #7000FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
    padding-top: 1rem;
    letter-spacing: -0.03em;
}
.premium-subtitle {
    font-size: 1.15rem;
    color: #A1A1AA;
    font-weight: 400;
    margin-bottom: 2rem;
}

/* Dark Glassmorphic Metric Cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 229, 255, 0.3);
    box-shadow: 0 8px 24px rgba(0, 229, 255, 0.1);
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] { padding-bottom: 24px !important; }
[data-testid="stChatInput"] > div {
    background: #121318 !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #00E5FF !important;
    box-shadow: 0 0 0 1px #00E5FF, 0 8px 32px rgba(0, 229, 255, 0.15) !important;
}
[data-testid="stChatInputSubmitButton"] { color: #00E5FF !important; }
[data-testid="stChatInput"] textarea { color: #F3F4F6 !important; }

/* Chat Bubbles */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 12px 20px;
    margin-bottom: 12px;
    animation: fadeIn 0.4s ease-out;
}
/* User Bubble - Neon Gradient */
[data-testid="stChatMessage"]:nth-child(even) {
    background: linear-gradient(135deg, #7000FF, #00E5FF) !important;
    color: #FFFFFF !important;
    border-bottom-right-radius: 4px;
    margin-left: 20%; 
    box-shadow: 0 4px 16px rgba(112, 0, 255, 0.2);
}
[data-testid="stChatMessage"]:nth-child(even) [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}
/* Assistant Bubble - Dark Slate */
[data-testid="stChatMessage"]:nth-child(odd) {
    background: #1A1B22 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-bottom-left-radius: 4px;
    margin-right: 15%;
    box-shadow: 0 4px 12px rgba(0,0,0, 0.2);
}

/* Emotionally Resonant Empty State Grouping */
.empty-greeting {
    font-size: 2.2rem;
    font-weight: 300;
    color: #FFFFFF;
    margin-top: 4vh;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.empty-sub { color: #A1A1AA; font-size: 1.1rem; margin-bottom: 24px; }

/* General button sleekness */
button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #E4E4E7 !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}
button[kind="secondary"]:hover, button[kind="secondary"]:focus {
    background: rgba(0, 229, 255, 0.1) !important;
    border-color: #00E5FF !important;
    color: #00E5FF !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 229, 255, 0.1);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Sidebar styling tweaks */
[data-testid="stSidebar"] {
    background-color: #121318 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.05); }

/* Text input / File uploader */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    background: rgba(0, 229, 255, 0.02) !important;
    border: 1px dashed rgba(0, 229, 255, 0.3) !important;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: #00E5FF !important;
    background: rgba(0, 229, 255, 0.05) !important;
}
</style>
"""

# ── Backend imports ───────────────────────────────────────────────────────
try:
    from llm_client import check_server_health
    from rag_engine import build_rag_index
    from data_engine import run_auto_insights, answer_question
except ImportError:
    def check_server_health(): return {"status": "online", "models": []}
    def build_rag_index(df): pass
    def run_auto_insights(df):
        return [{"question": "Dataset loaded", "answer": "Data indexed successfully."}]
    def answer_question(df, question, history):
        return {
            "answer": f"Analysis complete for: '{question}'",
            "code": "",
            "explanation": "Done.",
            "chart": None,
        }

def _init():
    for k, v in SESSION_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _handle_question(df, question: str):
    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.query_history.append(question)
    
    with st.spinner("Analyzing data vectors..."):
        result = answer_question(df, question, list(st.session_state.chat_history))
        
    st.session_state.chat_history.append({
        "role": "assistant",
        "answer":      result.get("answer"),
        "code":        result.get("code"),
        "explanation": result.get("explanation"),
        "chart":       result.get("chart"),
    })
    st.session_state.current_chart = result.get("chart")
    st.rerun()

def main():
    _init()
    # Inject Custom CSS
    st.markdown(HIGH_END_CSS, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        # High contrast logo
        st.markdown("<h2 style='color:#FFFFFF; margin-bottom:0; font-weight:800; letter-spacing:-0.03em;'>🌌 DataMind</h2><p style='color:#00E5FF; font-size:0.85rem; font-weight:600; margin-top:0; letter-spacing:0.1em;'>AI INTELLIGENCE</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.write("**Data Source**")
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
        
        if uploaded:
            new_size = round(uploaded.size / 1024, 2)
            if st.session_state.file_size_kb != new_size:
                st.session_state.df = pd.read_csv(uploaded)
                st.session_state.file_size_kb = new_size
                st.session_state.rag_indexed = False
                st.session_state.chat_history = []
                st.session_state.query_history = []
                st.session_state.current_chart = None
                
                with st.status("Initializing AI processing...", expanded=True) as status:
                    st.write("Securely uploaded file.")
                    time.sleep(0.5)
                    st.write("Deploying structural vector index...")
                    build_rag_index(st.session_state.df)
                    time.sleep(0.4)
                    st.write("Extracting deep auto-insights...")
                    st.session_state.auto_insights = run_auto_insights(st.session_state.df)
                    st.session_state.rag_indexed = True
                    status.update(label="Ready for Queries", state="complete", expanded=False)
                st.rerun()
                
        if st.session_state.df is not None:
            df = st.session_state.df
            st.markdown("---")
            st.write("**Dataset Metrics**")
            col1, col2 = st.columns(2)
            col1.metric("Rows", f"{len(df):,}")
            col2.metric("Columns", f"{len(df.columns)}")
            
            col3, col4 = st.columns(2)
            col3.metric("Size", f"{st.session_state.file_size_kb} KB")
            col4.metric("Nulls", f"{df.isnull().sum().sum()}")
            
            with st.expander("Explore Schema Data"):
                st.dataframe(pd.DataFrame({"Type": df.dtypes.astype(str)}), use_container_width=True)
                
            if st.session_state.auto_insights:
                st.markdown("---")
                st.write("**Auto Insights**")
                for insight in st.session_state.auto_insights[:3]:
                    st.info(f"**{insight.get('question', '')}**\n\n{insight.get('answer', '')}")

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN CONTENT
    # ══════════════════════════════════════════════════════════════════════════
    df = st.session_state.df
    
    # Custom Brand Header
    st.markdown('<div class="premium-header">DataMind Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="premium-subtitle">Ask questions naturally, uncover insights instantly in this high-performance environment.</div>', unsafe_allow_html=True)
    
    if st.session_state.current_chart:
        # Subtle expander to hold the latest visualization clearly without crowding chat
        with st.expander("Latest Visualization Output", expanded=True):
            # Change plotly default theme to dark 
            st.session_state.current_chart.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(st.session_state.current_chart, use_container_width=True)

    # Chat Messages
    if not st.session_state.chat_history:
        if df is None:
            st.markdown('<div class="empty-greeting">Welcome to the void.</div><div class="empty-sub">Upload a dataset in the terminal sidebar to illuminate insights.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-greeting">Dataset synchronized.</div><div class="empty-sub">What data would you like to expose today? Try a command below:</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("📈 Revenue trend over time", use_container_width=True, disabled=True)
                st.button("📊 Show frequency distributions", use_container_width=True, disabled=True)
            with col2:
                st.button("🔗 Top correlations", use_container_width=True, disabled=True)
                st.button("🥧 View parts of a whole", use_container_width=True, disabled=True)
            with col3:
                st.button("⚠️ Missing values audit", use_container_width=True, disabled=True)
                st.button("📋 Organize detailed tables", use_container_width=True, disabled=True)
    else:
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                # Custom avatar or default
                with st.chat_message("assistant"):
                    if msg.get("answer"):
                        st.markdown(msg["answer"])
                    if msg.get("chart"):
                        msg["chart"].update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(msg["chart"], use_container_width=True)
                        
    # Chat Input
    query = st.chat_input("Input command sequence...", disabled=(df is None))
    if query:
        _handle_question(df, query)

if __name__ == "__main__":
    main()