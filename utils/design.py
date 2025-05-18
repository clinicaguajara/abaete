
# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import base64
import pathlib
import streamlit as st
import logging


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🎨 FUNÇÃO CACHEADA PARA LER O CONTEÚDO DE UM ARQUIVO CSS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_css_file(css_path: str):
    """
    <docstrings> Lê o conteúdo de um arquivo CSS e retorna como string.

    Args:
        css_path (str): Caminho para o arquivo CSS a ser carregado.

    Calls:
        pathlib.Path():Construtor da classe Path para manipular caminhos no sistema de arquivos | instanciado por Path.
        pathlib.Path.exists(): Método do objeto Path para verificar a existência de um arquivo | instanciado por Path.
        open(): Função para abrir arquivos | built-in.
        logger.exception(): Método do objeto Logger para registra uma mensagem de erro junto com a stacktrace automática | instanciado por logger.

    Returns:
        str:
            Conteúdo do arquivo CSS como string.
            Retorna uma string vazia caso o arquivo não exista.
    """
    
    # Tenta ler o conteúdo do arquivo CSS...
    try:

        # Transforma uma variável do tipo string para um objeto do tipo pathlib.Path rico em métodos.
        path = path = pathlib.Path(__file__).parent.parent / "assets" / "styles.css"
    
        # Se o caminho existir...
        if path.exists():
            with open(path, "r", encoding="utf-8", errors="replace") as f:  # ⬅ Força leitura em UTF-8 em vez do cp1252 padrão do Windows.
                return f.read()                                             # ⬅ Retorna o conteúdo do arquivo CSS.
    
        # Caso contrário...
        else:
            return ""   # ⬅ Retorna uma string vazia como fallback.
        
    # Se houver exceções...
    except Exception as e:
        
        # Loga o erro para depuração.
        logger.exception(f"Erro ao carregar arquivo CSS: {e}")

        # Fallback de execução
        return ""


# 🦄 FUNÇÃO PARA INJETAR ESTILOS PERSONALIZADOS NA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def load_css():
    """
    Injeta o conteúdo do arquivo CSS e estilos adicionais diretamente na página Streamlit.

    Args:
        None.

    Calls:
        load_css_file(): Função interna para ler e cachear o conteúdo de um arquivo CSS | definida em modules.design.py
        st.markdown(): Função para injetar código HTML (wrapper de método interno) | definida no módulo st.

    Returns:
        None:
            Apenas aplica o CSS na página atual.
    """
    
    # Obtém o conteúdo do arquivo CSS.
    css_content = load_css_file("assets/styles.css")

    # Se o conteúdo for encontrado...
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True) # ⬅ Aplica o CSS na página.

    # Fontes externas (mantidas aqui por dependerem de carregamento da web)
    st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Marcellus&display=swap" rel="stylesheet">""", unsafe_allow_html=True)
    st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@500&display=swap" rel="stylesheet">""", unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlock"] {
        background-color: white !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def get_base64_logo(path="assets/logo.png") -> str:
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def render_abaete_header(title="Abaeté", logo_path="assets/logo.png"):
    encoded_logo = get_base64_logo(logo_path)
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Marcellus&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 0.2rem; margin-bottom: 1.2rem;'>
            <img src='data:image/png;base64,{encoded_logo}' width='55' />
            <h1 style='
                font-size: 48px;
                font-weight: 100;
                font-family: "Marcellus", serif;
                line-height: 0;
                margin: 0;
                padding: 0;
            '>{title}</h1>
        </div>
    """, unsafe_allow_html=True)


def render_goals_header(title="Metas", logo_path="assets/logo2.png"):
    encoded_logo = get_base64_logo(logo_path)
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Marcellus&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;'>
            <img src='data:image/png;base64,{encoded_logo}' width='55' />
            <h1 style='
                font-size: 50px;
                font-weight: 100;
                font-family: "Marcellus", serif;
                line-height: 1.2;
                margin: 0;
                padding: 0;
            '>{title}</h1>
        </div>
    """, unsafe_allow_html=True)


def render_scales_header(title="Testes", logo_path="assets/logo3.png"):
    encoded_logo = get_base64_logo(logo_path)
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Marcellus&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.5rem;'>
            <img src='data:image/png;base64,{encoded_logo}' width='65' />
            <h1 style='
                font-size: 50px;
                font-weight: 100;
                font-family: "Marcellus", serif;
                line-height: 1.2;
                margin: 0;
                padding: 0;
            '>{title}</h1>
        </div>
    """, unsafe_allow_html=True)







