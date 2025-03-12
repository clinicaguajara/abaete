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


# 🦄 Carrega o CCS para estilizar o visual, aplicando no Streamlit um design mais legal.
def load_css():
    css_content = load_css_file("assets/styles.css") # Chama a função cacheada load_css_file para obter o conteúdo do arquivo CSS.
    # Se houver conteúdo...
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True) # Aplica o CSS na página.


def inject_expander_style():
    st.markdown("""
    <style>
    /* Estiliza o título do expander */
    div[data-testid="stExpander"] > div > div > summary {
        font-size: 30px !important;
        font-weight: bold;
        color: #7159c1 !important;
    }
    /* Estiliza a borda do expander */
    div[data-testid="stExpander"] {
        border: 2px solid #7159c1 !important;
        border-radius: 5px;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)


