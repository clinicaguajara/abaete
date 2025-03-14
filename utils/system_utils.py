import streamlit as st

# 🌐 Função para inicializar a sessão e evitar erros de navegação.
def initialize_session_state():
    """
    Inicializa as variáveis de sessão do Streamlit para controlar o estado do app.
    
    Fluxo:
      1. Se a chave "user" não existir em st.session_state, define-a como None.
      2. Se a chave "processing" não existir, inicializa como False.
      3. Se a chave "refresh" não existir, inicializa como False.
      4. Se a chave "processing_message" não existir, inicializa como uma string vazia.
      5. Se a chave "global_process_container" não existir, define-a como um container vazio (st.empty()).
    
    Args:
        None.
    
    Returns:
        None (configura o st.session_state diretamente).
    
    Calls:
        None.
    """
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "processing" not in st.session_state:
        st.session_state["processing"] = False
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False
    if "processing_message" not in st.session_state:
        st.session_state["processing_message"] = ""
    if "global_process_container" not in st.session_state:
        st.session_state["global_process_container"] = st.empty()
        

def update_global_processing_message(message):
    """
    Atualiza o container global com a mensagem de processamento.
    
    Fluxo:
      1. Atualiza a chave "processing_message" em st.session_state.
      2. Se houver mensagem, exibe-a no container global; caso contrário, limpa o container.
    
    Args:
        message (str): Mensagem a ser exibida (ex.: "⏳ Processando...").
    
    Returns:
        None.
    
    Calls:
        st.empty(), st.info(), st.empty()
    """
    st.session_state["processing_message"] = message
    if message:
        st.session_state["global_process_container"].info(message)
    else:
        st.session_state["global_process_container"].empty()