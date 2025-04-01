import streamlit as st
from auth import sign_in, sign_up, reset_password

# 🏗️ Função para renderizar o layout principal.
def render_main_layout():
    """
    Renderiza o layout principal da página de autenticação.
    
    Fluxo:
      1. Exibe o título e subtítulo do sistema.
      2. Exibe uma linha divisória.
      3. Permite a escolha entre Login ou Cadastro.
      4. Exibe os campos para email, senha e (se for cadastro) os campos adicionais.
      5. Exibe o botão principal para autenticação com spinner.
      6. Exibe o botão para recuperação de senha (apenas no modo Login).
      7. Exibe mensagens de feedback e confirmação.
    """
    
    # Título do sistema
    st.markdown("# Abaeté 🧠")
    
    # Subtítulo chamativo
    st.markdown(
        """
        <h2>
        O sistema inteligente que cuida de você!</h2>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Escolha entre Login ou Cadastro
    option = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)
    
    # Campos para email e senha
    email = st.text_input("Email:", key="email_input")
    password = st.text_input("Senha:", type="password", key="password_input")
    
    # Variáveis utilizadas apenas para Cadastro.
    display_name = None
    confirm_password = None
    if option == "Cadastro":
        confirm_password = st.text_input("Confirme a senha:", type="password", key="confirm_password_input")
        display_name = st.text_input("Nome completo:", key="display_name_input")
    
    # Se estiver em Login e a conta foi criada anteriormente, remove a mensagem de "conta criada"
    if option == "Login" and "account_created" in st.session_state:
        del st.session_state["account_created"]
    
    # Define o texto do botão com base na opção selecionada
    action_text = "Entrar" if option == "Login" else "🪄 Criar Conta"
    
    # ===============================================================
    # AQUI: Após os campos de email, senha e, se for o caso, os campos para cadastro
    # ===============================================================
    
    # Placeholder para feedback da ação de autenticação
    auth_message = st.empty()
    
    # Botão principal de autenticação (Login ou Cadastro) com spinner
    if st.button(action_text, key="authaction", use_container_width=True, disabled=st.session_state.get("processing", False)):
        st.session_state["processing"] = True  
        try:
            with st.spinner("🔐 Processando..."):
                if not email or not password:
                    auth_message.warning("⚠️ Por favor, complete o formulário antes de continuar e não utilize o preenchimento automático.")
                else:
                    if option == "Login":
                        user, message = sign_in(email, password)
                        if user:
                            st.session_state["user"] = user  
                            st.session_state["refresh"] = True  
                            st.rerun()
                        else:
                            auth_message.error(f"{message}")
                    else:
                        if not display_name or not confirm_password:
                            auth_message.warning("⚠️ Por favor, complete o formulário antes de continuar e não utilize o preenchimento automático.")
                        elif password != confirm_password:
                            auth_message.error("❌ As senhas não coincidem. Tente novamente.")
                        else:
                            user, message = sign_up(email, password, confirm_password, display_name)
                            if user:
                                st.session_state["account_created"] = True  
                                st.session_state["confirmation_message"] = "📩 Um e-mail de verificação foi enviado para a sua caixa de entrada."
                                st.rerun()
                            else:
                                auth_message.error(message)
        finally:
            st.session_state["processing"] = False  
    
    # Placeholder exclusivo para feedback da recuperação de senha
    reset_message = st.empty()
    
    # Botão para recuperação de senha (apenas no modo Login)
    if option == "Login":
        if st.button("🔓 Recuperar Senha", key="resetpassword", use_container_width=True):
            if email:  # O email deve estar preenchido para recuperação de senha
                message = reset_password(email)
                st.session_state["confirmation_message"] = message
                st.rerun()
            else:
                reset_message.warning("⚠️ Por favor, insira seu email antes de redefinir a senha.")
    
    # Exibe mensagens de confirmação, se houver
    if "confirmation_message" in st.session_state:
        reset_message.success(st.session_state["confirmation_message"])
        del st.session_state["confirmation_message"]
