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
def render_dashboard():
    """
    Renderiza a dashboard do paciente, mostrando convites, metas, escalas e a seção de correção.
    
    Fluxo:
      1. Obtém os dados do usuário autenticado.
      2. Ajusta a saudação com base no gênero do usuário.
      3. Renderiza a sidebar com informações do usuário.
      4. Exibe o cabeçalho do dashboard utilizando um placeholder para manter a interface estável.
      5. Exibe convites pendentes e apresenta um selectbox para escolher a seção a ser exibida.
      6. Renderiza a seção escolhida: "Minhas Metas", "Testes Psicométricos" ou "Relatórios".
    
    Args:
      None (obtém o usuário autenticado internamente).
    
    Returns:
      None.
    
    Calls:
      - get_user() 
      - get_user_info() 
      - adjust_gender_ending()
      - render_sidebar() 
      - render_patient_invitations() 
      - render_patient_goals()
    """
    # 1. Obtém os dados do usuário autenticado.
    user = get_user()
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # 2. Obtém o perfil completo e ajusta a saudação.
    profile = get_user_info(user["id"], full_profile=True)
    saudacao = adjust_gender_ending("Bem-vindo", profile.get("genero", "M"))

    # 3. Pega apenas o primeiro nome do usuário para exibir na saudação.
    first_name = profile.get("display_name", "Usuário").split()[0] 
    
    # 4. Renderiza a sidebar com informações do usuário.
    render_sidebar(user)
    
    # 5. Placeholder para manter o cabeçalho estável durante recarregamentos.
    header_placeholder = st.empty()
    header_placeholder.header(f"{saudacao}, {first_name}!")  # Exibe apenas o primeiro nome
    st.divider()
    
    # 6. Exibe os convites pendentes.
    render_patient_invitations(user)
    
    # 7. Apresenta um selectbox para escolher qual seção exibir.
    opcao = st.selectbox(
        "🔽 Selecione uma ação:",
        ["Minhas Metas", "Testes Psicométricos", "Relatórios"]
    )
    

    # 8. Renderiza a seção escolhida.
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
    profile = get_user_info(user["id"], full_profile=True)

    # 3. Obtém apenas o primeiro nome do profissional.
    first_name = profile.get("display_name", "Usuário").split()[0] 

    # 4. Obtém o título do profissional.
    professional_title_first_name = get_professional_title(profile)

    # 5. Ajusta a saudação conforme o gênero do profissional.
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

    # 6. Exibe a saudação personalizada com o primeiro nome.
    st.subheader(f"{saudacao}, {professional_title_first_name}!")

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