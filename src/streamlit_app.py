import streamlit as st
from dotenv import load_dotenv

from presentation_streamlit import chat

# --- Setup ---
load_dotenv()

def main():
    """Main Streamlit Application."""
    st.set_page_config(page_title="Campus Multiplataforma - LLM", page_icon="📰", layout="wide")
    st.title("📰 Campus Multiplataforma - Monitoramento de Desinformação")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Chatbot
    chat.show()

if __name__ == "__main__":
    main()