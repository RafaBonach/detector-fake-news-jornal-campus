"""Interface Streamlit do chatbot do projeto.

Este módulo renderiza a tela de conversa, permite selecionar o modelo
e encaminha as perguntas do usuário para o serviço de LLM.
"""

import streamlit as st

from service_streamlit.llm import LLMService
from service_streamlit.utils import get_models

def show():
    """Renderiza a tela principal do chatbot no Streamlit."
    
    Responsabilidades:
        - Exibe o cabeçalho, aviso de feedback e seletor de modelo.
        - Mantém o histórico de mensagens em st.session_state.messages.
        - Ao receber uma pergunta, cria (ou reaproveita) uma instância de LLMService para o modelo selecionado e exibe a resposta.
        - Oferece um botão para limpar a conversa.
        
    Não recebe parâmetros nem retorna valor: toda a comunicação com o resto do app acontece via st.session_state.
    
    Observação:
        O chat é habilitado depois que o usuário escolhe um modelo diferente de "" no seletor.
    """
    
    st.header("💬 Chatbot")
    st.markdown(
        '<p style="font-size: 1.1rem; line-height: 1.6;">'
        'O que achou do resultado da IA? Aconteceu algum erro? Acha que a IA classificou de forma errada?<br>'
        '<a href="https://forms.gle/jygcee81PYFpYa8UA" target="_blank">Clique aqui para deixar seu feedback aqui</a>.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Inicializa a seleção para evitar acesso a chave inexistente no session_state.
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = ""

    # A opção vazia força a escolha explícita do usuário.
    model_options = [""] + get_models()

    with st.container(border=True):
        st.selectbox("Selecione um modelo", model_options, key="selected_model")
    model = st.session_state.selected_model

    # Exibe um aviso até que um modelo seja selecionado.
    if model == "":
        st.warning("⚠️ Por favor, selecione um modelo para continuar!")


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # O chat só fica ativo depois da escolha do modelo.
    if model != "":
        if prompt := st.chat_input("Faça uma pergunta..."):
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Processando..."):
                    if (
                        'llm_service' not in st.session_state
                        or st.session_state.llm_service.model_name != model
                    ):
                        # Recria o serviço quando o modelo muda.
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