import streamlit as st

st.set_page_config(
    page_title="LetterLoop",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    /* Global styles */
    [data-testid="stAppViewContainer"] {
        background-color: #fdf8f0;
    }
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    [data-testid="stSidebar"] * {
        color: #eee !important;
    }
    .stRadio label {
        color: #eee !important;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
    }

    /* Titre principal */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-green { background: #d4edda; color: #155724; }
    .badge-orange { background: #fff3cd; color: #856404; }
    .badge-blue { background: #cce5ff; color: #004085; }

    /* Response cards in digest */
    .response-card {
        background: #f8f9ff;
        border-left: 4px solid #6c63ff;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .response-author {
        font-weight: 700;
        color: #6c63ff;
        font-size: 0.9rem;
    }
    .response-text {
        color: #333;
        margin-top: 0.3rem;
        font-size: 1rem;
        line-height: 1.5;
    }

    /* Question header */
    .question-header {
        background: linear-gradient(135deg, #6c63ff, #a78bfa);
        color: white;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Sidebar nav */
    div[data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6c63ff, #a78bfa);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar logo + navigation
with st.sidebar:
    st.markdown("## ✉️ LetterLoop")
    st.markdown("*Votre newsletter de groupe*")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🛠️ Admin — Questions du mois", "✍️ Répondre aux questions", "📖 Digest du groupe"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Fait avec ❤️ par votre groupe")

# Route pages
if page == "🛠️ Admin — Questions du mois":
    from pages_app.admin import show
    show()
elif page == "✍️ Répondre aux questions":
    from pages_app.repondre import show
    show()
elif page == "📖 Digest du groupe":
    from pages_app.digest import show
    show()
