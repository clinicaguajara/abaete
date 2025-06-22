
# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from utils.load.design import get_base64_logo


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 📺 FUNÇÕES PARA RENDERIZAR CABEÇALHOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

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

    # Desenha texto conceitual da sessão.
    st.markdown("""
    <div style='text-align: justify;'>
    As metas no Abaeté são ferramentas de direção, não de cobrança. Elas ajudam a organizar o percurso, tornar <strong>objetivos</strong> mais claros e acompanhar os pequenos avanços ao longo do tempo. É um recurso de apoio — estruturado, compreensivo e autorregulado.
    </div>
    """, unsafe_allow_html=True)

    # Pula uma linha.
    st.markdown("<br>", unsafe_allow_html=True)


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

    # Desenha texto conceitual da sessão.
    st.markdown("""
        <div style='text-align: justify;'>
        As avaliações psicométricas não são apenas instrumentos de medida — são pontos de encontro entre a escuta e a precisão. Compreendemos que cada resposta carrega um ritmo, uma raiz, uma história. Por isso, torna-se fundamental reconhecer a complexidade da situação que requer um <strong>diagnóstico</strong>.
        </div>
        """, unsafe_allow_html=True)
    
    # Pula uma linha.
    st.markdown("<br>", unsafe_allow_html=True)


