
# 🏠 CONFIGURAÇÕES INICIAIS DA PÁGINA ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import streamlit as st

st.set_page_config(
    page_title="Abaeté",
    page_icon="🌵",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

from frameworks.sm                  import StateMachine
from utils.session                  import AuthStates, LoadStates
from utils.logs                     import log_page_entry
from utils.design                   import load_css, render_abaete_header
from services.user_profile          import load_user_profile
from components.auth_interface      import render_auth_interface
from components.onboarding          import render_onboarding_if_needed
from components.dashboard_interface import render_dashboard


# 🛤️ DEFINIÇÃO DE FLUXO DA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@log_page_entry("1_Caixa_de_Areia")
def page_1():
    
    load_css()              # ⬅ Injeção de CSS.
    render_abaete_header()  # ⬅ Desenha o cabeçalho da página.
    page = st.empty()       # ⬅ Contêiner para renderizar as componentes da interface.


    # 🔐 LÓGICA DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Cria a máquina de autenticação (default: form).
    auth_machine = StateMachine("auth_state", AuthStates.FORM.value, enable_logging=True)

    # Se o estado da máquina de autenticação for diferente de 'authenticated'...
    if auth_machine.current != AuthStates.AUTHENTICATED.value:
        
        # Ativa o container da página.
        with page.container():
            render_auth_interface(auth_machine) # ⬅ Desenha a interface de autenticação.
            st.stop()                           # ⬅ Interrompe a execução do programa.
    

    # 🌐 USUÁRIO LOGADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

    # Cria a máquina de perfis de usuário (default: load).
    profile_machine = StateMachine("profile_machine", LoadStates.LOAD.value, enable_logging=True)

    # Recupera o UUID do usuário da máquina de autenticação.
    user_id = auth_machine.get_variable("user_id")

    # Se houver UUID autenticado...
    if user_id:
        profile_machine.init_once(  
            load_user_profile,                    # ⬅ Carrega o perfil do usuário na máquina de autenticação.
            user_id,                              # ⬅ UUID do usuário autenticado (*args).
            auth_machine,                         # ⬅ Máquina de autenticação (*kwargs).
            done_state = LoadStates.LOADED.value  # ⬅ Desliga a flag da máquina de perfis de usuário para impedir reexecução.
        )                           


    # 📋 ONBOARDING QUESTIONNAIRE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
    
    # Recupera o perfil do usuário.
    profile = auth_machine.get_variable("user_profile")

    # Atia o container da página.
    with page.container():
        render_onboarding_if_needed(auth_machine, profile) # ⬅ Desenha o formulário de boas vindas, se necessário.
    

    # ❤️ DASHBOARD ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with page.container():
        render_dashboard(auth_machine)

page_1()