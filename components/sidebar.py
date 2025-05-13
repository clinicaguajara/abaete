import streamlit as st
from services.auth import auth_sign_out
from frameworks.sm import StateMachine


def render_sidebar(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a barra lateral com o botão de logout e o nome do usuário autenticado.

    Args:
        auth_machine (StateMachine): Máquina de estado com os dados da sessão atual.

    Calls:
        auth_machine.get_variable(): Recupera dados do usuário | instanciado por StateMachine.
        auth_machine.reset(): Reinicia a máquina de estado e força rerun | instanciado por StateMachine.
        auth_sign_out(): Encerra sessão de autenticação | definida em services.auth.py.
        st.sidebar.button(): Botão na barra lateral | definida no módulo streamlit.

    Returns:
        None.
    """

    # Botão de logout
    if st.sidebar.button("Sair", key="logout", use_container_width=True):
        sucesso = auth_sign_out(auth_machine)
        if sucesso:
            auth_machine.reset()
        else:
            st.sidebar.error("Erro ao sair. Tente novamente.")
