import streamlit as st
from auth import sign_in, sign_up, reset_password, sign_in_with_google, get_google_login_url


# 🏗️ Função para renderizar o layout principal.
def render_main_layout():
    """
    Renderiza o layout principal da página de autenticação.
    
    Fluxo:
      1. Exibe o título e o subtítulo utilizando placeholders para manter a interface estável.
      2. Exibe a introdução com as principais funções.
      3. Permite a escolha entre Login ou Cadastro, com os respectivos campos.
      4. Processa a ação de login ou cadastro e exibe mensagens de feedback.
    
    Args:
      None.
    
    Returns:
      None.
    
    Calls:
      - sign_in() para login.
      - sign_up() para cadastro.
      - reset_password() para recuperação de senha.
    """
    # Se estiver processando, mostra spinner e esconde o layout.
    if st.session_state.get("processing"):
        with st.spinner("🔐 Autenticando..."):
            st.empty()
        return

    # Placeholder para manter o título estável durante recarregamentos.
    title_placeholder = st.empty()
    title_placeholder.markdown("# Abaeté 🧠")
    
    # Placeholder para o subtítulo.
    subtitle_placeholder = st.empty()
    subtitle_placeholder.markdown(
        """
        <h1 style='color: #FFA500; font-size: 28px; font-weight: bold;'>
        O sistema inteligente que cuida de você!</h1>
        """,
        unsafe_allow_html=True
    )
    
    # Exibe a introdução com as principais funções.
    st.markdown(
        """
        ##### 💻 **No Abaeté você pode:**
        
        - **Monitorar e avaliar suas metas e desempenho a longo prazo.
        - **Compartilhar dados fundamentais com o seu terapeuta.
        - **Realizar testes e avaliações automatizadas.
        - **Receber relatórios personalizados sobre o seu desenovolvimento.
        
        🎯 **Tenha em mãos um sistema inteligente e baseado em evidências.** 
        
        🔍 **Acompanhe o passo a passo da sua evolução clínica.**  
        """
    )
    
    st.divider()
    
    # Escolha entre Login ou Cadastro.
    option = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)

    # Campos para email e senha.
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Senha", type="password", key="password_input")

    # Variáveis utilizadas apenas para Cadastro.
    display_name = None
    confirm_password = None

    if option == "Cadastro":
        confirm_password = st.text_input("Confirme a Senha", type="password", key="confirm_password_input")
        display_name = st.text_input("Nome Completo", key="display_name_input")

    if option == "Login" and "account_created" in st.session_state:
        del st.session_state["account_created"]

    action_text = "Entrar" if option == "Login" else "🪄 Criar Conta"
    message_placeholder = st.empty()

    if st.button(action_text, key="authaction", use_container_width=True, disabled=st.session_state.get("processing", False)):
        st.session_state["processing"] = True
        try:
            if not email or not password:
                message_placeholder.warning("⚠️ Por favor, complete o formulário antes de continuar e não utilize o preenchimento automático.")
            else:
                # Processamento sem aviso visual, pois o spinner padrão foi desativado.
                if option == "Login":
                    sign_in(email, password)
                else:
                    if not display_name or not confirm_password:
                        message_placeholder.warning("⚠️ Por favor, complete o formulário antes de continuar e não utilize o preenchimento automático.")
                    elif password != confirm_password:
                        message_placeholder.error("❌ As senhas não coincidem. Tente novamente.")
                    else:
                        user, message = sign_up(email, password, confirm_password, display_name)
                        if user:
                            st.session_state["account_created"] = True
                            st.session_state["confirmation_message"] = "📩 Um e-mail de verificação foi enviado para a sua caixa de entrada."
                            st.rerun()
                        else:
                            message_placeholder.error(message)
        finally:
            st.session_state["processing"] = False

    # Botão para recuperação de senha (apenas para Login).
    if option == "Login":
        if st.button("🔓 Recuperar Senha", key="resetpassword", use_container_width=True):
            if email:
                message = reset_password(email)
                st.session_state["confirmation_message"] = message
                st.rerun()
            else:
                message_placeholder.warning("⚠️ Por favor, insira seu email antes de redefinir a senha.")

    if "confirmation_message" in st.session_state:
        message_placeholder.success(st.session_state["confirmation_message"])
        del st.session_state["confirmation_message"]

    st.divider()

    # 🔵 Adicionando login via Google
    st.markdown(f"[🔵 Entrar com Google](<{get_google_login_url()}>)")
