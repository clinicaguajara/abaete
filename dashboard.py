import streamlit as st
from auth import get_user, sign_out
from patient_link import render_pending_invitations, render_patient_invitations, create_patient_invitation
from utils.gender_utils import adjust_gender_ending, get_professional_title
from utils.professional_utils import render_professional_enable_section, is_professional_enabled, enable_professional_area, get_professional_data
from utils.goals_utils import render_patient_goals, render_add_goal_section 
from utils.scales_utils import render_add_scale_section, render_patient_scales
from utils.correction_utils import render_scale_correction_section 


# 🖥️ Função para renderiza a sidebar.
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
        None.

    Calls:
        - sign_out()
        - is_professional_enabled()
        - render_professional_enable_section()
    """
    with st.sidebar:
        
        # 1. Se o usuário não estiver autenticado...
        if not user or "id" not in user:
            st.warning("⚠️ Erro: Usuário não autenticado.")
            return # Retorna.

        # 2. Exibe informações básicas do usuário.
        st.markdown(f"**👤 {user['display_name']}**")
        st.markdown(f"✉️ {user['email']}")

        # 3. Botão de logout.
        if st.button("Logout 🚪", key="logout"):
            sign_out()

        st.markdown("---")

        # 4. Se a área do profissional estiver habilitada...
        if is_professional_enabled(user["id"]):
            st.success("✅ Área do profissional habilitada!")  # 4. Confirma a entrada.
        
        # 5. Caso contrário, exibe a opção para ativação.
        else:
            render_professional_enable_section(user)  


# 🖥️ Renderiza a dashboard do paciente...
def render_dashboard(user):
    """
    Renderiza a dashboard do paciente, mostrando convites, metas, escalas e relatórios.
    
    Fluxo:
        1. Verifica se o usuário está autenticado. Se não, retorna.
        2. Renderiza a sidebar com informações do usuário.
        3. Obtém o perfil completo do usuário.
        4. Ajusta a saudação conforme o gênero do usuário.
        5. Obtém o primeiro nome do usuário para exibir na saudação. A
        6. Exibe o cabeçalho do dashboard utilizando um placeholder.
        7. Exibe convites pendentes.
        8. Exibe um selectbox para escolher a seção a ser exibida.
        9. Renderiza a seção escolhida: "Minhas Metas", "Testes Psicométricos" ou "Relatórios".
    
    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None.

    Calls:
        - get_user() 
        - adjust_gender_ending()
        - render_sidebar() 
        - render_patient_invitations() 
        - render_patient_goals()
        - render_patient_scales()
        - render_scale_correction_section()
    """
    # 1. Se o usuário não estiver autenticado...
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return # 1. Retorna.
        
    # 2. Renderiza a sidebar com informações do usuário.
    render_sidebar(user)

    # 4. Ajusta a saudação conforme o gênero do usuário.
    saudacao = adjust_gender_ending("Bem-vindo", user.get("genero", "M"))

    # 5. Obtém o primeiro nome do usuário para exibir na saudação.
    first_name = user.get("display_name", "Usuário").split()[0] 
    
    # 6. Placeholder para manter o cabeçalho estável durante recarregamentos.
    header_placeholder = st.empty()
    header_placeholder.header(f"{saudacao}, {first_name}!")  
    st.divider()
    
    # 7. Exibe os convites pendentes.
    render_patient_invitations(user)
    
    # 8. Apresenta um selectbox para escolher qual seção exibir.
    opcao = st.selectbox(
        "🔽 Selecione uma ação:",
        ["Minhas Metas", "Testes Psicométricos", "Relatórios"]
    )

    # 9. Renderiza a seção escolhida.
    if opcao == "Minhas Metas":
        render_patient_goals(user["id"])
    elif opcao == "Testes Psicométricos":
        render_patient_scales(user["id"])
    elif opcao == "Relatórios":
        render_scale_correction_section(user["id"])


# 🖥️ Renderiza a dashboard do profissional...
def render_professional_dashboard(user):
    """
    Renderiza a dashboard para profissionais habilitados.

    Fluxo:
        1. Verifica se o usuário está autenticado. Se não, retorna.
        2. Renderiza a sidebar com informações do usuário.
        3. Obtém as informações completas do profissional.
        4. Obtém o título do profissional junto com o seu primeiro nome.
        5. Ajusta a saudação conforme o gênero do profissional.
        6. Exibe a saudação personalizada.
        7. Exibe um seletor de ações para o profissional.
        8. Executa a ação escolhida.

    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None.

    Calls:
        - render_sidebar()
        - get_professional_title()
        - adjust_gender_ending()
        - create_patient_invitation()
        - render_pending_invitations()
        - render_add_goal_section()
        - render_add_scale_section()
    """
    # 1. Se o usuário não estiver autenticado...
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return # 1. Retorna.

    # 2. Renderiza a sidebar.
    render_sidebar(user)

    # 4. Obtém o título do profissional.
    professional_title_first_name = get_professional_title(user)

    # 5. Ajusta a saudação conforme o gênero do profissional.
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, user.get("genero", "M"))

    # 6. Exibe a saudação personalizada com o primeiro nome.
    st.subheader(f"{saudacao}, {professional_title_first_name}!")

    # 7. Seletor de funcionalidades do painel profissional.
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

    # 8. Executa a ação escolhida.
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
        render_pending_invitations(user["id"])
    
    elif opcao_selecionada == "Adicionar Meta para Paciente":
        render_add_goal_section(user)
    
    elif opcao_selecionada == "Enviar Escala Psicometica":
        render_add_scale_section(user)
