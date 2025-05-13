
# 🏠 CONFIGURAÇÕES INICIAIS DA PÁGINA ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

st.set_page_config(
    page_title="Minhas Metas",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────────────────────────

from utils.logs                     import log_page_entry
from utils.design                   import load_css
from utils.session                  import AuthStates
from frameworks.sm                  import StateMachine
from services.user_profile          import load_user_profile
from components.auth_interface      import render_auth_interface
from components.onboarding          import render_onboarding_if_needed
from components.goals_interface     import render_goals_interface
from components.sidebar             import render_sidebar


# 🛤️ FUNÇÃO DE FLUXO DA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@log_page_entry("MY GOALS")
def main():
    
    load_css() # ⬅ Injeção de CSS.


    # 🔐 LÓGICA DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    auth_machine = StateMachine("auth_state", AuthStates.FORM.value)

    if auth_machine.current != AuthStates.AUTHENTICATED.value:
        render_auth_interface()
        st.stop()


    # 🌐 USUÁRIO LOGADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

    # Recupera o UUID do usuário na máquina de estados.
    user_id = auth_machine.get_variable("user_id")

    # Carrega os dados do perfil do usuário via UUID (apenas uma vez).
    if auth_machine.get_variable("user_profile") is None:
        load_user_profile(user_id, auth_machine)


    # 📋 ONBOARDING QUESTIONNAIRE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
    
    # Recupera o perfil do usuário.
    profile = auth_machine.get_variable("user_profile")

    render_onboarding_if_needed(user_id, profile)
    

    # ❤️ RECUPERAÇÃO DE VÍNCULOS ───────────────────────────────────────────────────────────────────────────────────────────────────────

    render_sidebar(auth_machine)

    render_goals_interface(auth_machine)

main()