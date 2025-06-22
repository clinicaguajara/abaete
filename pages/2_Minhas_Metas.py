
# 🏠 CONFIGURAÇÕES INICIAIS DA PÁGINA ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

st.set_page_config(
    page_title="Minhas Metas",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────────────────────────

from frameworks.sm                  import StateMachine
from utils.variables.session        import AuthStates
from utils.logs                     import log_page_entry
from utils.load.design              import load_css
from utils.load.context             import load_session_context
from components.headers             import render_goals_header
from components.auth_interface      import auth_interface_entrypoint
from components.goals_interface     import render_goals_interface


# 🛤️ FUNÇÃO DE FLUXO DA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@log_page_entry("2_Minhas_Metas.py")
def page_2():
    
    load_css()              # ⬅ Injeção de CSS.
    render_goals_header()   # ⬅ Desenha o cabeçalho da página.
    page = st.empty()       # ⬅ Contêiner para renderizar as componentes da interface.

    # 🔐 LÓGICA DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Cria a máquina de autenticação (default: "form").
    auth_machine = StateMachine("auth_state", AuthStates.FORM.value, enable_logging=True)

    # Se o estado da máquina de autenticação for diferente de "authenticated"...
    if auth_machine.current != AuthStates.AUTHENTICATED.value:
        
        # Ativa o container da página.
        with page.container():
            auth_interface_entrypoint(auth_machine) # ⬅ Desenha a interface de autenticação.
            st.stop()                               # ⬅ Interrompe a execução do programa.
    

    # 🌐 USUÁRIO LOGADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

    # Ativa o container da página.
    with page.container():
        load_session_context(auth_machine)   # ⬅ Carrega o contexto da sessão.
        render_goals_interface(auth_machine) # ⬅ Desenha a interface de metas.

page_2()