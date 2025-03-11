import streamlit as st
from auth import sign_in, sign_up, reset_password

# 🏗️ Função para renderizar o layout principal.
def render_main_layout():

    # O título do sistema que aparece no cabeçalho.
    st.markdown("# Abaeté 🌱")
    
    # Criamos um subtítulo chamativo e destacado.
    st.markdown(
        """
        <h1 style='color: #FFA500; font-size: 28px; font-weight: bold;'>
        O sistema inteligente que cuida de você!</h1>
        """,
        unsafe_allow_html=True # Usando HTML para deixar o texto mais marcado.
    )

    # Introdução ao sistema e suas principais funções. Explicamos ao usuário as vantagens e aplicações.
    st.markdown("""
    ##### 💻 **Transforme a sua prática clínica com tecnologia avançada:**
    
    - **Crie uma conta profissional** e acesse um ambiente especializado para profissionais da saúde mental.
    - **Cadastre pacientes e acompanhe sua trajetória clínica** com dados organizados em tempo real.
    - **Aplique avaliações informatizadas** e obtenha resultados rápidos e padronizados.
    - **Utilize nossas correções automatizadas** para garantir mais precisão na interpretação dos dados.
    - **Monitore a evolução longitudinalmente** observando padrões ao longo do tempo.
    
    🎯 **Tenha em mãos um sistema inteligente e baseado em evidências.**  
    🔍 **Eleve sua prática profissional e ofereça um acompanhamento mais eficaz e personalizado.**  
    """)

    st.divider()  # Uma linha divisória para organizar o conteúdo

    # Escolha entre Login ou Cadastro com um botão interativo.
    option = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)

    # Campos para o email e senha do usuário.
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Senha", type="password", key="password_input")

    # Inicializamos variáveis que só serão usadas no Cadastro.
    display_name = None
    confirm_password = None

    # Se o usuário escolher "Cadastro"...
    if option == "Cadastro": # Mostramos mais campos de preenchimento.
        confirm_password = st.text_input("Confirme a Senha", type="password", key="confirm_password_input")
        display_name = st.text_input("Nome Completo", key="display_name_input")

    # Se o usuário escolher "Login"...
    if option == "Login" and "account_created" in st.session_state:
        del st.session_state["account_created"]  # Evita que a mensagem de "conta criada com sucesso" continue aparecendo em alguns casos.

    # Assim, o texto do botão muda dependendo da ação escolhida.
    action_text = "Entrar" if option == "Login" else "🪄 Criar Conta"

    # Criamos um espaço vazio para exibir mensagens de erro ou sucesso no mesmo lugar.
    message_placeholder = st.empty()

    # Botão principal para "Login" ou "Cadastro".
    if st.button(action_text, key="authaction", use_container_width=True, disabled=st.session_state.get("processing", False)):
        st.session_state["processing"] = True  

        try:
            with st.spinner("Processando..."):
                if not email or not password:
                    message_placeholder.warning("⚠️ Por favor, complete o formulário antes de continuar e não utilize o preenchimento automático.")
                else:
                    if option == "Login":
                        user, message = sign_in(email, password)
                        if user:
                            st.session_state["user"] = user  
                            st.session_state["refresh"] = True  
                            st.rerun()  
                        else:
                            message_placeholder.error(f"{message}")
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
            st.session_state["processing"] = False  # ✅ Garante que sempre volta a permitir novos cliques


    # 🔓 Botão para recuperação de senha (somente na opção Login)
    if option == "Login":
        if st.button("🔓 Recuperar Senha", key="resetpassword", use_container_width=True):
            if email:  # O email deve estar preenchido para recuperação de senha
                message = reset_password(email)  # Chama a função do auth.py
                st.session_state["confirmation_message"] = message
                st.rerun()
            else:
                message_placeholder.warning("⚠️ Por favor, insira seu email antes de redefinir a senha.")

    # ✅ Exibir mensagens de sucesso abaixo dos botões
    if "confirmation_message" in st.session_state:
        message_placeholder.success(st.session_state["confirmation_message"])
        del st.session_state["confirmation_message"]  # Remove para evitar exibições repetidas
