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
def render_dashboard(user):
    """
    Renderiza a dashboard do paciente, mostrando convites, metas, escalas e a seção de correção.
    
    Fluxo:
      1. Utiliza o usuário passado como argumento, sem sobrescrevê-lo com `get_user()`.
      2. Obtém o perfil do usuário do `session_state`, garantindo que não seja buscado novamente.
      3. Ajusta a saudação com base no gênero do usuário.
      4. Exibe o cabeçalho do dashboard utilizando um `st.container()` para manter a interface estável.
      5. Exibe convites pendentes e apresenta um selectbox para escolher a seção a ser exibida.
      6. Renderiza a seção escolhida: "Minhas Metas", "Testes Psicométricos" ou "Relatórios".
    
    Args:
      user (dict): Dicionário contendo os dados do usuário autenticado.
    
    Returns:
      None (apenas renderiza a interface).
    
    Calls:
      - render_sidebar()
      - render_patient_invitations() 
      - render_patient_goals()
      - render_patient_scales()
      - render_scale_correction_section()
    """
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # Renderiza a sidebar com as informações do usuário.
    render_sidebar(user)

    # Garante que os dados do usuário estão no session_state
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = get_user_info(user["id"], full_profile=True) or {}

    profile = st.session_state["user_profile"]

    # Mantém a saudação fixa no session_state para evitar blinks
    if "dashboard_header" not in st.session_state:
        saudacao = adjust_gender_ending("Bem-vindo", profile.get("genero", "M"))
        first_name = profile.get("display_name", "Usuário").split()[0]  
        st.session_state["dashboard_header"] = f"{saudacao}, {first_name}!"

    with st.container():
        st.header(st.session_state["dashboard_header"])  # Saudação agora é fixa e não pisca
        st.divider()

    # Convites pendentes
    render_patient_invitations(user)

    # Garante que a opção do selectbox seja persistente no session_state
    if "selected_option" not in st.session_state:
        st.session_state["selected_option"] = "Minhas Metas"

    opcao = st.selectbox(
        "🔽 Selecione uma ação:",
        ["Minhas Metas", "Testes Psicométricos", "Relatórios"],
        index=["Minhas Metas", "Testes Psicométricos", "Relatórios"].index(st.session_state["selected_option"]),
        key="action_select"
    )

    if opcao != st.session_state["selected_option"]:
        st.session_state["selected_option"] = opcao  # Atualiza o session_state sem recarregar a página

    # Renderiza a seção escolhida
    if opcao == "Minhas Metas":
        render_patient_goals(user["id"])
    elif opcao == "Testes Psicométricos":
        render_patient_scales(user["id"])
    elif opcao == "Relatórios":
        render_scale_correction_section(user["id"])


# 🖥️ Função para renderizar a dashboard exclusiva para profissionais habilitados.
def render_professional_dashboard(user):
    """
    Renderiza a dashboard para profissionais habilitados.

    Fluxo:
        1. Obtém os dados do usuário autenticado.
        2. Renderiza a sidebar com informações do usuário.
        3. Obtém o título profissional e ajusta a saudação conforme o gênero.
        4. Exibe um seletor de ações para o profissional com as opções:
           - "Convidar Paciente"
           - "Visualizar Convites Pendentes"
           - "Adicionar Meta para Paciente"
           - "Enviar Escala Psicometica"
        5. Executa a ação escolhida.

    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        - render_sidebar()
        - get_user_info()
        - get_professional_title()
        - adjust_gender_ending()
        - create_patient_invitation()
        - render_pending_invitations()
        - render_add_goal_section()
        - render_add_scale_section()
    """
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # 1. Renderiza a sidebar.
    render_sidebar(user)

    # 2. Obtém as informações completas do profissional.
    profile = st.session_state.get("user_profile", {})
    saudacao = adjust_gender_ending("Bem-vindo", profile.get("genero", "M"))
    professional_title_with_first_name = get_professional_title(profile)

    # Mantém o cabeçalho estável durante atualizações
    with st.container():
        st.header(f"{saudacao}, {professional_title_with_first_name}!")  
        st.divider()
    
    # --- Seletor de funcionalidades usando selectbox ---
    st.markdown("##### Painel Profissional")
    
    opcao_selecionada = st.selectbox(
        "🔽 Selecione uma ação:",
        [
            "Convidar Paciente",
            "Visualizar Convites Pendentes",
            "Adicionar Meta para Paciente",
            "Enviar Escala Psicometica"
        ],
        key="action_select"
    )

    if opcao_selecionada == "Convidar Paciente":
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
    
    elif opcao_selecionada == "Visualizar Convites Pendentes":
        st.markdown("##### 📜 Convites Pendentes")
        render_pending_invitations(user["id"])
    
    elif opcao_selecionada == "Adicionar Meta para Paciente":
        render_add_goal_section(user)
    
    elif opcao_selecionada == "Enviar Escala Psicometica":
        render_add_scale_section(user)
