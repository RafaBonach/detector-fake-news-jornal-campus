import streamlit as st

from presentation_streamlit import chat

def main():
    """Ponto de entrada da aplicação Streamlit.
    
    Configura a página (título, ícone, layout), aplica ajustes de CSS para telas pequenas, inicializa o histórico de mensagens em st.session_state e delega o restante da interface para presentation_streamlit.chat.show().
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