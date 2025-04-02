import streamlit as st
from auth import sign_out
from patient_link import render_pending_invitations, render_patient_invitations, render_invite_patient_section
from utils.gender_utils import adjust_gender_ending, get_professional_title
from utils.professional_utils import render_professional_enable_section, is_professional_enabled
from utils.goals_utils import render_patient_goals, render_add_goal_section 
from utils.scales_utils import render_add_scale_section, render_patient_scales
from utils.correction_utils import render_scale_correction_section 


# 🖥️ Função para renderiza a sidebar.
def render_sidebar(user):
    
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
    
    # Se o usuário não estiver autenticado...
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return # Retorna.
            
    # Renderiza a sidebar com informações do usuário.
    render_sidebar(user)

    # Ajusta a saudação conforme o gênero do usuário.
    saudacao = adjust_gender_ending("Bem-vindo", user.get("genero", "M"))

    # Obtém o primeiro nome do usuário para exibir na saudação.
    first_name = user.get("display_name", "Usuário").split()[0] 
        
    # Placeholder para manter o cabeçalho estável durante recarregamentos.
    header_placeholder = st.empty()
    header_placeholder.header(f"{saudacao}, {first_name}!")  
    st.divider()
        
    # Exibe os convites pendentes.
    with st.spinner("Processando..."):
        render_patient_invitations(user)

    # Apresenta um selectbox para escolher qual seção exibir.
    opcao = st.selectbox(
        "Selecione uma ação:",
        ["Minhas Metas", "Testes Psicométricos", "Relatórios"]
    )

    # Renderiza a seção escolhida.
    if opcao == "Minhas Metas":
        render_patient_goals(user["id"])
    elif opcao == "Testes Psicométricos":
        render_patient_scales(user["id"])
    elif opcao == "Relatórios":
        render_scale_correction_section(user["id"])


# 🖥️ Renderiza a dashboard do profissional...
def render_professional_dashboard(user):
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return # 1. Retorna.

    # 2. Renderiza a sidebar.
    render_sidebar(user)

    # 4. Obtém o título do profissional
    professional_title_first_name = get_professional_title(user)

    # 5. Ajusta a saudação conforme o gênero do profissional.
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, user.get("genero", "M"))

    # 6. Exibe a saudação personalizada com o primeiro nome.
    st.subheader(f"{saudacao}, {professional_title_first_name}!")

    # 7. Seletor de funcionalidades do painel profissional.
    st.markdown("##### Painel Profissional")
    opcao_selecionada = st.selectbox(
        "Selecione uma ação:",
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
       render_invite_patient_section(user)

    elif opcao_selecionada == "Visualizar Convites Pendentes":
        render_pending_invitations(user["id"])
    
    elif opcao_selecionada == "Adicionar Meta para Paciente":
        render_add_goal_section(user)
    
    elif opcao_selecionada == "Enviar Escala Psicometica":
        render_add_scale_section(user)