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
      - get_user() para obter o usuário.
      - get_user_info() para obter os dados do perfil.
      - adjust_gender_ending() para ajustar a saudação.
      - render_sidebar() para exibir a barra lateral.
      - render_patient_invitations() para exibir os convites pendentes.
      - render_patient_goals(), render_patient_scales() e render_scale_correction_section() para renderizar as seções específicas.
    """
    # 1. Obtém os dados do usuário autenticado.
    user = get_user()
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # 2. Obtém o perfil completo e ajusta a saudação.
    profile = get_user_info(user["id"], full_profile=True)
    saudacao = adjust_gender_ending("Bem-vindo", profile.get("genero", "M"))
    
    # 3. Renderiza a sidebar com informações do usuário.
    render_sidebar(user)
    
    # 4. Placeholder para manter o cabeçalho estável durante recarregamentos.
    header_placeholder = st.empty()
    header_placeholder.header(f"{saudacao}, {user['display_name']}! 🎉")
    st.markdown("---")
    
    # 5. Exibe os convites pendentes.
    render_patient_invitations(user)
    
    # 6. Apresenta um selectbox para escolher qual seção exibir.
    opcao = st.selectbox(
        "Selecione uma seção:",
        ["Minhas Metas", "Testes Psicométricos", "Relatórios"]
    )
    
    # 7. Renderiza a seção escolhida.
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