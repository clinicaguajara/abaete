import streamlit as st
from auth import sign_in, sign_up, reset_password
from utils.system_utils import update_global_processing_message  # Função para atualizar a mensagem global de processamento

# 🏗️ Função para renderizar o layout principal.
def render_main_layout():
    """
    Renderiza o layout principal do aplicativo (página de Login/Cadastro).

    Fluxo:
      1. Exibe o título e o subtítulo do sistema com formatação HTML.
      2. Exibe uma introdução com as vantagens do sistema.
      3. Cria uma linha divisória para organizar o conteúdo.
      4. Permite ao usuário escolher entre "Login" e "Cadastro" por meio de um radio button.
      5. Exibe os campos de entrada para email e senha (e, se necessário, confirmação de senha e nome completo).
      6. Exibe uma mensagem de "Processando..." enquanto a ação (login ou cadastro) é executada.
      7. Executa a ação correspondente (login ou cadastro) e, se for necessário, reinicia a interface.
      8. Exibe um botão para recuperação de senha (apenas para login).
      9. Exibe mensagens de sucesso ou erro conforme o resultado da operação.

    Args:
        None.

    Returns:
        None (a interface é renderizada diretamente no Streamlit).

    Calls:
        - sign_in(), sign_up(), reset_password() (em auth.py)
        - update_global_processing_message() (em utils/system_utils.py)
    """
    # Título e subtítulo do sistema
    st.markdown("# Abaeté 🌱")
    st.markdown(
        """
        <h1 style='color: #FFA500; font-size: 28px; font-weight: bold;'>
        O sistema inteligente que cuida de você!</h1>
        """,
        unsafe_allow_html=True
    )

    # Introdução com vantagens do sistema
    st.markdown(
        """
        ##### 💻 **Transforme a sua prática clínica com tecnologia avançada:**
        
        - **Crie uma conta profissional** e acesse um ambiente especializado para profissionais da saúde mental.
        - **Cadastre pacientes e acompanhe sua trajetória clínica** com dados organizados em tempo real.
        - **Aplique avaliações informatizadas** e obtenha resultados rápidos e padronizados.
        - **Utilize nossas correções automatizadas** para garantir mais precisão na interpretação dos dados.
        - **Monitore a evolução longitudinalmente** observando padrões ao longo do tempo.
        
        🎯 **Tenha em mãos um sistema inteligente e baseado em evidências.**  
        🔍 **Eleve sua prática profissional e ofereça um acompanhamento mais eficaz e personalizado.**  
        """
    )

    st.divider()  # Linha divisória

    # Permite escolher entre Login e Cadastro
    option = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)

    # Campos de entrada
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Senha", type="password", key="password_input")

    # Variáveis para o fluxo de cadastro
    display_name = None
    confirm_password = None

    # Se o usuário escolher "Cadastro", exibe campos adicionais
    if option == "Cadastro":
        confirm_password = st.text_input("Confirme a Senha", type="password", key="confirm_password_input")
        display_name = st.text_input("Nome Completo", key="display_name_input")

    # Remoção de "account_created" para evitar mensagens repetidas no Login
    if option == "Login" and "account_created" in st.session_state:
        del st.session_state["account_created"]

    # Define o texto do botão de acordo com a opção escolhida
    action_text = "Entrar" if option == "Login" else "🪄 Criar Conta"

    # Espaço para exibir mensagens (erro, sucesso ou processamento)
    message_placeholder = st.empty()

    # Botão principal para Login ou Cadastro (as keys permanecem inalteradas para manter o CSS)
    if st.button(action_text, key="authaction", use_container_width=True, disabled=st.session_state.get("processing", False)):
        st.session_state["processing"] = True  
        try:
            if not email or not password:
                message_placeholder.warning("⚠️ Por favor, complete o formulário antes de continuar e não utilize o preenchimento automático.")
            else:
                # Exibe mensagem de processamento no container global
                update_global_processing_message("⏳ Processando...")
                if option == "Login":
                    user, message = sign_in(email, password)
                    if user:
                        st.session_state["user"] = user  
                        st.session_state["refresh"] = True  
                        st.rerun()
                    else:
                        message_placeholder.error(message)
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
            update_global_processing_message("")  # Limpa a mensagem de processamento

    # Botão para recuperação de senha (para a opção Login)
    if option == "Login":
        if st.button("🔓 Recuperar Senha", key="resetpassword", use_container_width=True):
            if email:
                message = reset_password(email)
                st.session_state["confirmation_message"] = message
                st.rerun()
            else:
                message_placeholder.warning("⚠️ Por favor, insira seu email antes de redefinir a senha.")

    # Exibe mensagem de confirmação (se houver)
    if "confirmation_message" in st.session_state:
        message_placeholder.success(st.session_state["confirmation_message"])
        del st.session_state["confirmation_message"]

