
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
from utils.variables.session        import AuthStates
from utils.logs                     import log_page_entry
from utils.design                   import load_css, render_abaete_header
from utils.context                  import load_session_context
from components.auth_interface      import auth_interface_entrypoint
from components.dashboard_interface import dashboard_interface_entrypoint


# 🛤️ DEFINIÇÃO DE FLUXO DA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@log_page_entry("1_Agenda.py")
def page_1():
    
    load_css()              # ⬅ Injeção de CSS.
    render_abaete_header()  # ⬅ Desenha o cabeçalho da página.
    page = st.empty()       # ⬅ Placeholder para renderizar as componentes da interface dinamicamente.


    # 🔐 LÓGICA DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Cria a máquina de autenticação (default: "form").
    auth_machine = StateMachine("auth_state", AuthStates.FORM.value, enable_logging=True)

    # Se o estado da máquina de autenticação for diferente de "authenticated"...
    if auth_machine.current != AuthStates.AUTHENTICATED.value:
        
        # Ativa o container da página, transformando o placeholder em um escopo de múltiplos widgets.
        with page.container():
            auth_interface_entrypoint(auth_machine) # ⬅ Desenha a interface de autenticação.
            st.stop()                           # ⬅ Interrompe a execução do programa.
    

    # 🌐 USUÁRIO LOGADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

    # Ativa o container da página, transformando o placeholder em um escopo de múltiplos widgets.
    with page.container():
        load_session_context(auth_machine) # ⬅ Carrega o contexto da sessão.
        dashboard_interface_entrypoint(auth_machine)     # ⬅ Desenha a área de trabalho do usuário.

page_1()