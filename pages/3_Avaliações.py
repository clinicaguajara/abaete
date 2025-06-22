
# 🏠 CONFIGURAÇÕES INICIAIS DA PÁGINA ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

st.set_page_config(
    page_title="Avaliações",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────────────────────────

from frameworks.sm                  import StateMachine
from utils.variables.session        import AuthStates
from utils.load.context             import load_session_context
from utils.logs                     import log_page_entry
from utils.load.design              import load_css
from components.headers             import render_scales_header
from components.auth_interface      import auth_interface_entrypoint
from components.scales_interface    import scales_interface_entrypoint


# 🛤️ FUNÇÃO DE FLUXO DA PÁGINA ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@log_page_entry("3_Avaliações.py")
def main():
    
    load_css()              # ⬅ Injeção de CSS.
    render_scales_header()  # ⬅ Desenha o cabeçalho da página.
    page = st.empty()       # ⬅ Contêiner para renderizar a interface.


    # 🔐 LÓGICA DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Cria a máquina de autenticação (default: "form").
    auth_machine = StateMachine("auth_state", AuthStates.FORM.value)

    # Se o estado da máquina de autenticação for diferente de "authenticated"...
    if auth_machine.current != AuthStates.AUTHENTICATED.value:
        with page.container():
            auth_interface_entrypoint(auth_machine) # ⬅ Renderiza a interface de autenticação.
            st.stop()                           # ⬅ Interrompe a execução do programa.


    # 🌐 USUÁRIO LOGADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

    
    # Ativa o container da página.
    with page.container():
        load_session_context(auth_machine)    # ⬅ Carrega o contexto da sessão.
        scales_interface_entrypoint(auth_machine) # ⬅ Renderiza a interface de avaliações.

main()