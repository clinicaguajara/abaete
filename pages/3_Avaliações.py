# 🏠 CONFIGURAÇÕES INICIAIS DA PÁGINA ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

st.set_page_config(
    page_title="Avaliações",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────────────────────────

from utils.logs                     import log_page_entry
from utils.design                   import load_css, render_scales_header
from utils.session                  import AuthStates
from frameworks.sm                  import StateMachine
from services.user_profile          import load_user_profile
from components.auth_interface      import render_auth_interface
from components.onboarding          import render_onboarding_if_needed
from components.sidebar             import render_sidebar
from components.scales_interface    import render_scales_interface


# 🛤️ FUNÇÃO DE FLUXO DA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@log_page_entry("SCALES")
def main():
    
    load_css()              # ⬅ Injeção de CSS.
    render_scales_header()  # ⬅ Desenha o cabeçalho da página.
    page = st.empty()       # ⬅ Contêiner para renderizar a interface.


    # 🔐 LÓGICA DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    auth_machine = StateMachine("auth_state", AuthStates.FORM.value)

    if auth_machine.current != AuthStates.AUTHENTICATED.value:
        with page.container():
            render_auth_interface(auth_machine)
            st.stop()


    # 🌐 USUÁRIO LOGADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

    # Recupera o UUID do usuário na máquina de estados.
    user_id = auth_machine.get_variable("user_id")

    # Carrega os dados do perfil do usuário via UUID (apenas uma vez).
    if user_id and auth_machine.get_variable("user_profile") is None:
        load_user_profile(user_id, auth_machine)


    # 📋 ONBOARDING QUESTIONNAIRE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
    
    # Recupera o perfil do usuário.
    profile = auth_machine.get_variable("user_profile")

    with page.container():
        render_onboarding_if_needed(user_id, profile)
    

    # ❤️ RECUPERAÇÃO DE VÍNCULOS ───────────────────────────────────────────────────────────────────────────────────────────────────────

    with page.container():
        render_scales_interface(auth_machine)

main()