import streamlit as st
from auth import get_user, sign_out
from patient_link import render_pending_invitations, render_patient_invitations, create_patient_invitation
from utils.gender_utils import adjust_gender_ending, get_professional_title
from utils.professional_utils import  render_professional_enable_section, is_professional_enabled, enable_professional_area, get_professional_data
from utils.user_utils import get_user_info
from utils.goals_utils import add_goal_to_patient


# 🖥️ Função para renderizar a sidebar.
def render_sidebar(user):
    
    with st.sidebar:
        if not user or "id" not in user:
            st.warning("⚠️ Erro: Usuário não autenticado.")
            return

        profile = get_user_info(user["id"], full_profile=True) or {}
        saudacao_base = "Bem-vindo"
        saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

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


# 🖥️ Função para renderizar a dashboard.
def render_dashboard():
    
    user = get_user()

    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    profile = get_user_info(user["id"], full_profile=True)
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

    render_sidebar(user)

    st.subheader(f"{saudacao}, {user['display_name']}! 🎉")
    
    st.markdown("---")

    render_patient_invitations(user)

    st.subheader("🎯 Minhas Metas")

    st.markdown("---")

    st.info("🔍 Novos recursos serão adicionados em breve!")


# 🖥️ Função para renderizar a dashboard exclusiva para profissionais habilitados.
def render_professional_dashboard(user):
    """Renderiza a dashboard para profissionais habilitados."""
    
    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # Renderiza a sidebar corretamente
    render_sidebar(user)

    # Obtém perfil completo do profissional
    profile = get_user_info(user["id"], full_profile=True)

    # Obtém título profissional correto
    professional_title = get_professional_title(profile)

    # Saudação personalizada ajustada pelo gênero
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

    st.subheader(f"{saudacao}, {professional_title}! 🎉")

    # --- Melhorando a caixa de seleção ---
    st.markdown("### 🔽 Selecione uma ação:")
    opcao_selecionada = st.radio(
        "",  
        ["📩 Convidar Paciente", "📜 Visualizar Convites Pendentes", "🎯 Adicionar Meta para Paciente"],
        horizontal=True
    )

    # --- Opção 1: Convidar Paciente ---
    if opcao_selecionada == "📩 Convidar Paciente":
        st.markdown("### 📩 Convidar Paciente")
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

    # --- Opção 2: Visualizar Convites Pendentes ---
    elif opcao_selecionada == "📜 Visualizar Convites Pendentes":
        st.markdown("### 📜 Convites Pendentes")
        render_pending_invitations(user["id"]) 

    # --- Opção 3: Adicionar Meta para Paciente ---
    elif opcao_selecionada == "🎯 Adicionar Meta para Paciente":
        st.markdown("### 🎯 Adicionar Meta para Paciente")
        
        patient_email = st.text_input("Email do paciente:", key="goal_patient_email")
        goal_text = st.text_area("Descrição da meta:", key="goal_text")
        timeframe = st.text_input("Prazo ou período:", key="goal_timeframe")

        if st.button("Salvar Meta", key="save_goal", use_container_width=True):
            if patient_email and goal_text and timeframe:
                success, msg = add_goal_to_patient(user["id"], patient_email, goal_text, timeframe)
                if success:
                    st.success("✅ Meta adicionada com sucesso!")
                else:
                    st.error(f"Erro: {msg}")
            else:
                st.warning("⚠️ Preencha todos os campos antes de salvar.")