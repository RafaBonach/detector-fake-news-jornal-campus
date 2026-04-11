import streamlit as st
from service_streamlit.llm import LLMService

def show():
    st.header("💬 Chatbot")

    if 'llm_service' not in st.session_state:
        st.session_state.llm_service = LLMService(model_name="Qwen/Qwen3-0.6B")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Faça uma pergunta..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                try:
                    response = st.session_state.llm_service.answer_question(prompt)
                except Exception as exc:
                    response = f"Erro ao gerar resposta: {exc}"
                    st.error(response)

                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("🗑 Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()