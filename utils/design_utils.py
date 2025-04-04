import streamlit as st
import pathlib


# 💾 Função para cachear o conteúdo do arquivo CSS.
@st.cache_data
def load_css_file(css_path: str):
    path = pathlib.Path(css_path) # Cria um objeto Path para o caminho do arquivo CSS.
    # Se o caminho existir...
    if path.exists():
        with open(path, "r") as f: # Abre o arquivo em modo de leitura.
            return f.read() # Retorna o conteúdo do arquivo.
    return "" # Se o arquivo não existir, retorna uma string vazia.


# 🦄 Carrega o CSS e injeta estilos personalizados para o expander
def load_css():
    css_content = load_css_file("assets/styles.css")  # Obtém o conteúdo do arquivo CSS

    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)  # Aplica o CSS na página.

    st.markdown(
        """
        <style>
            /* Classe para o título com sombra e efeito personalizado */
            .purple-title {
                color: #7159c1 !important; 
                font-size: 32px !important; 
                font-weight: bold !important;
                margin-bottom: 20px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    hide_default_spinner = """
        <style>
            div[role="status"] { display: none !important; }
        </style>
    """
    st.markdown(hide_default_spinner, unsafe_allow_html=True)
