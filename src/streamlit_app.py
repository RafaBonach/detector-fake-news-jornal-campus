"""Ponto de entrada da interface Streamlit do projeto.

Este módulo configura a página principal, inicializa o estado da sessão
e delega a renderização do chat para a camada de apresentação.
"""

import streamlit as st

from presentation_streamlit import chat

def main():
    """Inicializa e renderiza a aplicação Streamlit.

    A função define metadados da página, aplica ajustes visuais para telas
    menores, garante a inicialização do histórico de mensagens e exibe o
    componente de conversa.

    Returns:
        None.
    """

    st.set_page_config(page_title="É verdade ou é mentira? Campusito Responde", page_icon="📰", layout="wide")

    # Ajustes mínimos para melhorar a leitura em telas menores.
    st.markdown("""
    <style>
        @media (max-width: 768px) {
            h1 {
                font-size: 1.5rem !important;
            }
        }
        @media (max-width: 380px) {
            h1 {
                font-size: 1.2rem !important;
            }
            img {
                max-width: 110px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    logo_col, title_col = st.columns([1, 6], vertical_alignment="center")
    with logo_col:
        st.image("src/static_streamlit/icon/campusito.png", width=210)
    with title_col:
        st.title("É verdade ou é mentira? Campusito Responde")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chatbot
    chat.show()

if __name__ == "__main__":
    main()