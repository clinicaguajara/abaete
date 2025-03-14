import streamlit as st
from auth import get_user, sign_out
from patient_link import render_pending_invitations, render_patient_invitations, create_patient_invitation
from utils.gender_utils import adjust_gender_ending, get_professional_title
from utils.professional_utils import  render_professional_enable_section, is_professional_enabled, enable_professional_area, get_professional_data
from utils.user_utils import get_user_info
from utils.goals_utils import render_patient_goals, render_add_goal_section 
from utils.scales_utils import render_add_scale_section, render_patient_scales
from utils.correction_utils import render_scale_correction_section 


# 🖥️ Função para renderizar a sidebar.
def render_sidebar(user):
    """
    Renderiza a barra lateral do usuário autenticado.

    Fluxo:
        1. Obtém os dados do usuário autenticado.
        2. Exibe informações básicas como nome e e-mail.
        3. Adiciona um botão de logout.
        4. Se for um profissional, verifica se a área profissional está habilitada.
        5. Se a área profissional não estiver habilitada, exibe a opção para ativação.

    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        professional_utils.py → is_professional_enabled()
        professional_utils.py → render_professional_enable_section()
    """
    
    with st.sidebar:
        
        if not user or "id" not in user:
            st.warning("⚠️ Erro: Usuário não autenticado.")
            return

        st.markdown(f"**👤 {user['display_name']}**")
        st.markdown(f"✉️ {user['email']}")

        # Botão de logout
        if st.button("Logout 🚪", key="logout"):
            sign_out()

        st.markdown("---")

        # Se a área do profissional já estiver habilitada...
        if is_professional_enabled(user["id"]):
            st.success("✅ Área do profissional habilitada!")  # Confirma a entrada.
        
        # Caso contrário...
        else:
            render_professional_enable_section(user)  # Renderiza o bloqueio da área profissional.



# 🖥️ Função para renderizar a dashboard do paciente.
def render_dashboard():
    """
    Renderiza a dashboard do paciente, mostrando convites, metas, escalas e a seção de correção.
    
    Fluxo:
      1. Obtém os dados do usuário autenticado via get_user().
      2. Obtém as informações completas do perfil do usuário via get_user_info() e ajusta a saudação com adjust_gender_ending().
      3. Renderiza a sidebar com informações do usuário chamando render_sidebar().
      4. Exibe uma saudação personalizada.
      5. Exibe os convites pendentes do paciente usando render_patient_invitations().
         - Enquanto os convites são carregados, exibe um placeholder com a mensagem "Carregando convites pendentes...".
      6. Apresenta um selectbox para que o paciente escolha a seção a ser visualizada:
         - "Minhas Metas" (chama render_patient_goals())
         - "Testes Psicométricos" (chama render_patient_scales())
         - "Relatórios" (chama render_scale_correction_section())
         - Para cada opção, antes de renderizar a seção, é exibido um placeholder com a mensagem de carregamento.
    
    Args:
        None (obtém o usuário autenticado internamente).
    
    Returns:
        None (a interface é renderizada diretamente no Streamlit).
    
    Calls:
        - get_user() [em auth.py]
        - get_user_info() [em utils/user_utils.py]
        - adjust_gender_ending() [em utils/gender_utils.py]
        - render_sidebar() [em dashboard.py]
        - render_patient_invitations() [em utils/patient_link.py]
        - render_patient_goals() [em utils/goals_utils.py]
        - render_patient_scales() [em utils/scales_utils.py]
        - render_scale_correction_section() [em utils/correction_utils.py]
    """
    # 1. Obtém os dados do usuário autenticado.
    user = get_user()
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # 2. Obtém o perfil completo e ajusta a saudação.
    profile = get_user_info(user["id"], full_profile=True)
    saudacao = adjust_gender_ending("Bem-vindo", profile.get("genero", "M"))

    # 3. Renderiza a sidebar.
    render_sidebar(user)

    # 4. Exibe a saudação personalizada.
    st.header(f"{saudacao}, {user['display_name']}! 🎉")
    st.markdown("---")

    render_patient_invitations(user)

    # 6. Selectbox para escolher qual seção exibir.
    opcao = st.selectbox(
        "Selecione uma seção:",
        ["Minhas Metas", "Testes Psicométricos", "Relatórios"]
    )

    # 7. Dependendo da opção escolhida, exibe o placeholder e a respectiva seção.
    if opcao == "Minhas Metas":
        metas_placeholder = st.empty()
        metas_placeholder.info("⏳ Processando...")
        render_patient_goals(user["id"])
        metas_placeholder.empty()
    elif opcao == "Testes Psicométricos":
        testes_placeholder = st.empty()
        testes_placeholder.info("⏳ Processando...")
        render_patient_scales(user["id"])
        testes_placeholder.empty()
    elif opcao == "Relatórios":
        relatorios_placeholder = st.empty()
        relatorios_placeholder.info("⏳ Processando...")
        render_scale_correction_section(user["id"])
        relatorios_placeholder.empty()



# 🖥️ Função para renderizar a dashboard exclusiva para profissionais habilitados.
def render_professional_dashboard(user):
    """
    Renderiza a dashboard para profissionais habilitados.

    Fluxo:
        1. Obtém os dados do usuário autenticado.
        2. Renderiza a sidebar com informações do usuário.
        3. Exibe um seletor de ações para o profissional, agora utilizando um selectbox, com as opções:
           - "📩 Convidar Paciente"
           - "📜 Visualizar Convites Pendentes"
           - "🎯 Adicionar Meta para Paciente"
           - "📝 Enviar Escala Psicometica"
        4. Executa a ação escolhida:
           - Se for "Convidar Paciente", permite inserir o e-mail e enviar o convite.
           - Se for "Visualizar Convites Pendentes", exibe os convites pendentes.
           - Se for "Adicionar Meta para Paciente", chama render_add_goal_section().
           - Se for "Enviar Escala Psicometica", chama render_add_scale_section() para atribuir uma escala.
    
    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        render_sidebar()
        patient_link.py → create_patient_invitation()
        patient_link.py → render_pending_invitations()
        goals_utils.py → render_add_goal_section()
        scales_utils.py → render_add_scale_section()  (função a ser implementada para escalas)
    """
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # Renderiza a sidebar.
    render_sidebar(user)

    # Obtém as informações completas do profissional.
    profile = get_user_info(user["id"], full_profile=True)

    # Obtém o título do profissional.
    professional_title = get_professional_title(profile)

    # Ajusta a saudação conforme o gênero do profissional.
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

    st.subheader(f"{saudacao}, {professional_title}! 🎉")

    # --- Seletor de funcionalidades usando selectbox ---
    st.markdown("##### Painel Profissional")
    opcao_selecionada = st.selectbox(
        "🔽 Selecione uma ação:",
        [
            "📩 Convidar Paciente",
            "📜 Visualizar Convites Pendentes",
            "🎯 Adicionar Meta para Paciente",
            "📝 Enviar Escala Psicometica"
        ],
        key="action_select"
    )

    if opcao_selecionada == "📩 Convidar Paciente":
        st.markdown("##### 📩 Convidar Paciente")
        patient_email = st.text_input("Digite o email do paciente:", key="patient_email_input")
        if st.button("Enviar Convite", key="patientlink", use_container_width=True):
            if patient_email:
                success, msg = create_patient_invitation(user["id"], patient_email)
                if success:
                    st.success("✅ Convite enviado com sucesso!")
                else:
                    st.error(f"Erro: {msg}")
            else:
                st.warning("⚠️ Por favor, insira o email do paciente.")
    elif opcao_selecionada == "📜 Visualizar Convites Pendentes":
        st.markdown("##### 📜 Convites Pendentes")
        render_pending_invitations(user["id"])
    elif opcao_selecionada == "🎯 Adicionar Meta para Paciente":
        render_add_goal_section(user)
    elif opcao_selecionada == "📝 Enviar Escala Psicometica":
        # Chama a função para atribuir uma escala ao paciente.
        # Essa função deve ser implementada no módulo scales_utils.py.
        render_add_scale_section(user)