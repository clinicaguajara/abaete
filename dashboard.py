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
      1. Obtém os dados do usuário autenticado via get_user().
      2. Obtém as informações completas do perfil via get_user_info() e ajusta a saudação com adjust_gender_ending().
      3. Renderiza a parte estática (sidebar e cabeçalho) apenas uma vez e guarda uma flag no st.session_state.
      4. Exibe os convites pendentes.
      5. Usa um selectbox para que o usuário escolha qual seção dinâmica exibir (Minhas Metas, Testes Psicométricos ou Relatórios).
         Essa parte é renderizada a cada mudança no selectbox.
      
    Args:
        None (obtém o usuário autenticado internamente).

    Returns:
        None (a interface é renderizada diretamente no Streamlit).

    Calls:
        - get_user()              [em auth.py]
        - get_user_info()         [em utils/user_utils.py]
        - adjust_gender_ending()  [em utils/gender_utils.py]
        - render_sidebar()        [em dashboard.py]
        - render_patient_invitations()  [em utils/patient_link.py]
        - render_patient_goals()        [em utils/goals_utils.py]
        - render_patient_scales()       [em utils/scales_utils.py]
        - render_scale_correction_section() [em utils/correction_utils.py]
    """
    # 1. Obtém os dados do usuário autenticado.
    user = get_user()
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # 2. Obtém o perfil completo e define a saudação.
    profile = get_user_info(user["id"], full_profile=True)
    saudacao = adjust_gender_ending("Bem-vindo", profile.get("genero", "M"))
    first_name = user["display_name"].split()[0]

    # 3. Renderiza a parte estática (sidebar e cabeçalho) somente se ainda não foram "fixados" no estado.
    if "dashboard_initialized" not in st.session_state:
        render_sidebar(user)
        # Cria o cabeçalho e o guarda no estado.
        st.session_state["dashboard_header"] = f"{saudacao}, {first_name}!"
        st.header(st.session_state["dashboard_header"])
        st.session_state["dashboard_initialized"] = True
    else:
        st.header(st.session_state["dashboard_header"]) # Evita a renderização repetida da dashboard.
        

    st.markdown("---")
    
    # 4. Renderiza os convites pendentes (isso é dinâmico e pode mudar)
    render_patient_invitations(user)

    # 5. Utiliza um selectbox para escolher a seção dinâmica a ser exibida.
    # Armazena a escolha no estado para que a mesma opção seja preservada entre reexecuções.
    if "dashboard_section" not in st.session_state:
        st.session_state["dashboard_section"] = "Minhas Metas"
    options = ["Minhas Metas", "Testes Psicométricos", "Relatórios"]
    # Define o índice inicial com base na opção salva
    index = options.index(st.session_state.dashboard_section) if st.session_state.dashboard_section in options else 0
    opcao = st.selectbox("🔽 Selecione uma ação:", options, index=index)
    st.session_state.dashboard_section = opcao

    # 6. Renderiza somente a seção dinâmica escolhida.
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
    first_name = user['display_name'].split()[0]

    # 4. Obtém o título do profissional.
    professional_title = get_professional_title(profile)

    # 5. Ajusta a saudação conforme o gênero do profissional.
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

    # 6. Exibe a saudação personalizada com o primeiro nome.
    st.subheader(f"{saudacao}, {first_name}!")

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
