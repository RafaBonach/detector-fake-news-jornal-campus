import streamlit as st
from dotenv import load_dotenv

from presentation_streamlit import chat

# --- Setup ---
load_dotenv()

def main():
    """Main Streamlit Application."""
    st.set_page_config(page_title="É verdade ou é mentira? Campusito Responde", page_icon="📰", layout="wide")

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