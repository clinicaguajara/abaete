
# 📦 IMPORTAÇÕES NECESSÁRIAS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import streamlit as st
import logging

from frameworks.sm   import StateMachine
from utils.variables.session   import AuthStates, RedirectStates, LoadStates
from services.auth   import auth_sign_in, auth_sign_up, auth_reset_password


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Cria ou recupera uma instância do objeto Logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# 🔌 ENTYPOINT DA INTERFACE DE AUTENTICAÇÃO ───────────────────────────────────────────────────────────────────────────────────────────────────

def auth_interface_entrypoint(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a interface de autenticação que protege todas as páginas.

    Args:
        auth_machine (StateMachine): Instância da máquina de autenticação.

    Calls:
        StateMachine(): Instancia ou recupera máquina de estado | definida em framework.sm.py

    Returns:
        None.
        
    """
    
    # 🛰️ ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Cria a máquina de redirecionamento (dafult: True).
    redirect_machine = StateMachine("auth_redirect_state", RedirectStates.REDIRECT.value, enable_logging=True)
    
    # Se a máquina de redirecionamento estiver ligada...
    if redirect_machine.current:
        redirect_machine.to(RedirectStates.REDIRECTED.value, True) # ⬅ Desativa flag e força rerun().
    

    # 🔐 INTERFACE DE AUTENTICAÇÃO ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    _render_auth_interface(auth_machine)


# 📺 FUNÇÃO PARA RENDERIZAR A INTERFACE DE AUTENTICAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_auth_interface(auth_machine: StateMachine) -> None:
    """
    <docstrings> Componente reativo de autenticação com abas de login, cadastro e reset.

    Args:
        auth_machine (StateMachine): Instância da máquina de autenticação.

    Calls:
        auth_sign_in(): Realiza login com email e senha | definida em services.auth.py
        auth_sign_up(): Cadastra novo usuário | definida em services.auth.py
        auth_reset_password(): Dispara email de redefinição | definida em services.auth.py
        st.rerun(): Reinicializa a aplicação | definida em streamlit.runtime

    Returns:
        None;

    """

    # Desenha as abas da interface de autenticação.
    tabs = st.tabs(["Entrar", "Cadastrar", "Esqueci minha senha"])


    # 🔑 ABA DE LOGIN ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Ativa a aba de login.
    with tabs[0]:

        # Desenha o formulário de login.
        with st.form("login_form"):
            
            # Campos para preenchimento do formulário.
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            feedback = st.empty()
            sign_in_button = st.form_submit_button("Entrar", use_container_width=True)

        # Se o botão de login for apertado...
        if sign_in_button:
            
            # Se o email ou senha não estiverem preenchidos...
            if not email or not password:
                feedback.warning("⚠️ Email ou senha inválidos.")
            
            # Caso contrário...
            else:
                auth_machine.to(LoadStates.LOADING.value, rerun=False) # ⬅ Transiciona a máquina de autenticação.
                user = auth_sign_in(email, password)                   # ⬅ Autenticação via Supabase.
                
                # Se houver usuário autenticado...
                if user:
                    auth_machine.set_variable("user_email", user.email)                                     # ⬅ Recupera o email do usuário autenticado.
                    auth_machine.set_variable("user_id", user.id)                                           # ⬅ Recupera o UUID do usuário autenticado.
                    auth_machine.set_variable("user_display_name", user.user_metadata.get("display_name"))  # ⬅ Recupera o nome completo do usuário autenticado.
                    auth_machine.to(AuthStates.AUTHENTICATED.value)                                         # ⬅ Transiciona a máquina de autenticação.
                
                # Caso contrário...
                else:
                    feedback.error("⛔ Erro de autenticação, tente novamente.") # ⬅ Feedback visual.


    # 📋 ABA DE CADASTRO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Ativa a aba de cadastro.
    with tabs[1]:

        # Desenha o formulário de cadastro.
        with st.form("signup_form"):
            nome = st.text_input("Nome completo", key="signup_nome")
            email = st.text_input("Email para cadastro", key="signup_email")
            senha = st.text_input("Senha (mín. 6 dígitos)", type="password", key="signup_senha")
            confirmar = st.text_input("Confirme a senha", type="password", key="signup_confirmar")
            feedback = st.empty()
            sign_up_button = st.form_submit_button("Cadastrar", use_container_width=True)

        # Se o botão de cadastro for apertado...
        if sign_up_button:
            
            # Se o nome, email, senha ou confirmação de senha não estiverem corretamente preenchidos...
            if not nome or not email or not senha or not confirmar:
                feedback.info("📋 Preencha todos os campos do formulário para se cadastrar.")
            
            # E se a senha não for igual à confirmação de senha...
            elif senha != confirmar:
                feedback.warning("⚠️ As senhas não coincidem!")
            
            # Caso contrário...
            else:
                user = auth_sign_up(email, senha, user_metadata={"display_name": nome}) # ⬅ Cadastro via Supabase.
                
                # Se o cadastro for efetuado com sucesso...
                if user:
                    feedback.success("📩 Um email de confirmação foi enviado para a sua caixa de entrada.")
                
                # Caso contrário...
                else:
                    feedback.error("⛔ Não foi possível realizar o cadastro. Verifique suas informações e tente novamente.")


    # 🔓 ABA DE RECUPERAR SENHA ─────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Ativa a aba de recuperar senha.
    with tabs[2]:

        # Desenha o formulário para recuperar senha.
        with st.form("reset_form"):
            email = st.text_input("Digite seu email de cadastro", key="reset_email")
            feedback = st.empty()
            reset_button = st.form_submit_button("Enviar link de recuperação", use_container_width=True)

        # Se o botão de recuperar senha for apertado...
        if reset_button:

            # Se o email não estiver corretamente preenchido...
            if not email:
                feedback.info("📬 Informe seu e-mail para recuperar a senha.")
            
            # Caso contrário...
            else:
                sent = auth_reset_password(email) # ⬅ Recuperação de senha via Supabase.
                
                # Se a recuperação de senha for executada com sucesso...
                if sent:
                    feedback.success("📩 Email de recuperação enviado com sucesso!")
                
                # Caso contrário...
                else:
                    feedback.error("Erro: Verifique o endereço de email informado e tente novamente.")
    
