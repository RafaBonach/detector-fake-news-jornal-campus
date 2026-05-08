import streamlit as st
from service_streamlit.llm import LLMService
import config_base as config

def show():
    st.header(f"💬 Chatbot")
    st.markdown(
        '<p style="font-size: 1.1rem; line-height: 1.6;">'
        'O que achou do resultado da IA? Aconteceu algum erro? Acha que a IA classificou de forma errada?<br>'
        '<a href="https://forms.gle/jygcee81PYFpYa8UA" target="_blank">Clique aqui para deixar seu feedback aqui</a>.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Seletor de modelos: achata listas em `config.MODELS` e remove duplicatas preservando ordem
    seen = set()
    model_options = []
    for models in config.MODELS.values():
        for m in models:
            if m not in seen:
                seen.add(m)
                model_options.append(m)
    
    model_options.sort()  # Ordena alfabeticamente
    model_options.insert(0, "")  # Opção padrão no topo

    with st.container(border=True):
        model = st.selectbox("Selecione um modelo", model_options, index=0)
    
    # Verificador: avisa se nenhum modelo foi selecionado
    if model == "":
        st.warning("⚠️ Por favor, selecione um modelo para continuar!")



    

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Só executa o bloco de chat se um modelo foi selecionado
    if model != "":
        if prompt := st.chat_input("Faça uma pergunta..."):
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Processando..."):
                    if 'llm_service' not in st.session_state:
                        st.session_state.llm_service = LLMService(model_name=str(model))
                    
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