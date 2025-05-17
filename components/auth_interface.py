# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from utils.design  import render_abaete_header
from frameworks.sm import StateMachine
from services.auth import auth_sign_in, auth_sign_up, auth_reset_password
from utils.session import AuthStates


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 📺 FUNÇÃO PARA RENDERIZAR A INTERFACE DE AUTENTICAÇÃO ───────────────────────────────────────────────────────────────────────────────────────────────────

def render_auth_interface(auth_machine: StateMachine):
    """
    <docstrings> Componente reativo de autenticação com abas de login, cadastro e reset.

    Args:
        None (a máquina de estado auth_state será usada diretamente).

    Calls:
        StateMachine(): Instancia ou recupera máquina de estado | definida em framework.sm.py
        auth_sign_in(): Realiza login com email e senha | definida em services.auth.py
        auth_sign_up(): Cadastra novo usuário | definida em services.auth.py
        auth_reset_password(): Dispara email de redefinição | definida em services.auth.py
        st.rerun(): Reinicializa a aplicação | definida em streamlit.runtime

    Returns:
        None.
        
    """

    # ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Cria uma instancia da máquina de redirecionamento.
    redirect = StateMachine("auth_redirect", True)
    
    if redirect.current:
        logger.info("Estabilização proativa da interface de autenticação.")
        redirect.to(False, True) # desativa flag.
    
    
    # INTERFACE DE AUTENTICAÇÃO ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    logger.info("Desenhando a interface de autenticação.")
    render_abaete_header()

    tabs = st.tabs(["Entrar", "Cadastrar", "Esqueci minha senha"])


    # ABA PARA LOGIN ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    with tabs[0]:

        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            feedback = st.empty()
            sign_in_button = st.form_submit_button("Entrar", use_container_width=True)

        if sign_in_button:
            if not email or not password:
                feedback.warning("⚠️ Email ou senha inválidos.")
            else:
                auth_machine.to(AuthStates.LOADING.value, rerun=False)
                user = auth_sign_in(email, password)
                if user:
                    auth_machine.set_variable("user_email", user.email)
                    auth_machine.set_variable("user_id", user.id)
                    auth_machine.set_variable("user_display_name", user.user_metadata.get("display_name"))
                    logger.info(f"{user.email} logado com sucesso.")
                    auth_machine.to(AuthStates.AUTHENTICATED.value)
                else:
                    feedback.error("⛔ Erro de autenticação, tente novamente.")


    # ABA PARA CADASTRO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    with tabs[1]:

        with st.form("signup_form"):
            nome = st.text_input("Nome completo", key="signup_nome")
            email = st.text_input("Email para cadastro", key="signup_email")
            senha = st.text_input("Senha (mín. 6 dígitos)", type="password", key="signup_senha")
            confirmar = st.text_input("Confirme a senha", type="password", key="signup_confirmar")
            feedback = st.empty()
            sign_up_button = st.form_submit_button("Cadastrar", use_container_width=True)

        if sign_up_button:
            if not nome or not email or not senha or not confirmar:
                feedback.info("📋 Preencha todos os campos do formulário para se cadastrar.")
            elif senha != confirmar:
                feedback.warning("⚠️ As senhas não coincidem!")
            else:
                user = auth_sign_up(email, senha, user_metadata={"display_name": nome})
                if user:
                    feedback.success("📩 Um email de confirmação foi enviado para a sua caixa de entrada.")
                else:
                    feedback.error("⛔ Não foi possível realizar o cadastro. Verifique suas informações e tente novamente.")


    # ABA PARA RECUPERAR A SENHA ─────────────────────────────────────────────────────────────────────────────────────────────────────
    
    with tabs[2]:

        with st.form("reset_form"):
            email = st.text_input("Digite seu email de cadastro", key="reset_email")
            feedback = st.empty()
            reset_button = st.form_submit_button("Enviar link de recuperação", use_container_width=True)

        if reset_button:
            if not email:
                feedback.info("📬 Informe seu e-mail para recuperar a senha.")
            else:
                sucesso = auth_reset_password(email)
                if sucesso:
                    feedback.success("📩 Email de recuperação enviado com sucesso!")
                else:
                    feedback.error("Erro: Verifique o endereço de email informado e tente novamente.")
    
    st.markdown("<br>", unsafe_allow_html=True)
