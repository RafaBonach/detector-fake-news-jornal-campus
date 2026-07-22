"""Ponto de entrada da interface Streamlit do projeto.

Este módulo configura a página principal, inicializa o estado da sessão
e delega a renderização do chat para a camada de apresentação.
"""

import streamlit as st
from base64 import b64encode
from pathlib import Path

from presentation_streamlit import chat

def main():
    """Inicializa e renderiza a aplicação Streamlit.

    A função define metadados da página, aplica ajustes visuais para telas
    menores, garante a inicialização do histórico de mensagens e exibe o
    componente de conversa.

    Returns:
        None.
    """

    st.set_page_config(page_title="É verdade ou é mentira? Campusito Responde", page_icon="src/static_streamlit/icon/campusito.png", layout="wide")

    # Ajustes mínimos para melhorar a leitura em telas menores.
    st.markdown("""
    <style>
        .logo-title-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .logo-title-container img {
            width: 100%;
            height: auto;
            max-width: 90px;
            object-fit: contain;
            display: block;
        }
        .logo-title-container h1 {
            margin: 0;
            font-size: clamp(1.7rem, 2.2vw + 1.3rem, 1.5rem);
            line-height: 1.15;
        }
        @media (max-width: 480px) {
            p, li {
                font-size: 0.68rem !important;
            }
            div[data-testid="stImage"] img {
                width: 100% !important;
                max-width: 120px !important;
                height: auto !important;
                object-fit: contain !important;
            }
            .logo-title-container img { max-width: 60px; }
        }
        @media (max-width: 380px) {
            div[data-testid="stImage"] img {
                max-width: 100px !important;
            }
            .logo-title-container img { max-width: 48px; }
        }
        
    </style>
    """, unsafe_allow_html=True)

    logo_path = Path("src/static_streamlit/icon/campusito.png")
    logo_data_uri = ""
    if logo_path.exists():
        logo_base64 = b64encode(logo_path.read_bytes()).decode("ascii")
        logo_data_uri = f"data:image/png;base64,{logo_base64}"

    st.markdown(f"""
    <div class="logo-title-container">
        <img src="{logo_data_uri}" alt="Campusito" />
        <h1>É verdade ou é mentira? Campusito Responde</h1>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chatbot
    chat.show()

if __name__ == "__main__":
    main()