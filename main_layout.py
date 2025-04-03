import streamlit as st
from auth import sign_in, sign_up, reset_password

# 🏗️ Função para renderizar o layout principal
import streamlit as st
from auth import sign_in, sign_up, reset_password

def render_main_layout():
    st.markdown("# Abaeté 🧠")
    st.markdown("<h2> O sistema inteligente que cuida de você!</h2>", unsafe_allow_html=True)
    st.divider()

    option = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)

    email = st.text_input("Email", key="email_input")
    password = st.text_input("Senha", type="password", key="password_input")

    display_name = None
    confirm_password = None
    if option == "Cadastro":
        confirm_password = st.text_input("Confirme a senha", type="password", key="confirm_password_input")
        display_name = st.text_input("Nome completo", key="display_name_input")

    if option == "Login" and "account_created" in st.session_state:
        del st.session_state["account_created"]

    action_text = "Entrar" if option == "Login" else "🪄 Criar Conta"
    message_placeholder = st.empty()

    # Botão principal de ação
    if st.button(action_text, key="authaction", use_container_width=True):
        with message_placeholder.container():
            with st.spinner("Processando..."):
                if option == "Login":
                    try:
                        user, message = sign_in(email, password)
                        if user:
                            st.rerun()
                        else:
                            message_placeholder.error(message)
                    except Exception as e:
                        message_placeholder.error(f"Erro inesperado: {str(e)}")

                elif option == "Cadastro":
                    if not display_name or not confirm_password:
                        message_placeholder.warning("⚠️ Complete todos os campos.")
                    elif password != confirm_password:
                        message_placeholder.error("❌ As senhas não coincidem.")
                    else:
                        try:
                            user, message = sign_up(email, password, confirm_password, display_name)
                            if user:
                                st.session_state["account_created"] = True
                                st.session_state["confirmation_message"] = "📩 Um e-mail de verificação foi enviado."
                                st.rerun()
                            else:
                                message_placeholder.error(message)
                        except Exception as e:
                            message_placeholder.error(f"Erro ao criar conta: {str(e)}")

    # Recuperação de senha
    if option == "Login":
        if st.button("🔓 Recuperar Senha", key="resetpassword", use_container_width=True):
            if email:
                with message_placeholder.container():
                    with st.spinner("Enviando instruções de recuperação..."):
                        message = reset_password(email)
                        st.session_state["confirmation_message"] = message
                        st.rerun()
            else:
                message_placeholder.warning("⚠️ Por favor, insira seu email.")

    # Mensagens de confirmação
    if "confirmation_message" in st.session_state:
        message_placeholder.success(st.session_state["confirmation_message"])
        del st.session_state["confirmation_message"]
