import streamlit as st
import pathlib
from auth import get_user, sign_out
from patient_link import render_pending_invitations, render_patient_invitations, create_patient_invitation
from utils.gender_utils import adjust_gender_ending, get_professional_title
from utils.professional_utils import is_professional_enabled, enable_professional_area
from utils.user_utils import get_user_info


# 🖥️ Função para renderizar a sidebar.
def render_sidebar(user):
    with st.sidebar:
        if not user or "id" not in user:
            st.warning("⚠️ Erro: Usuário não autenticado.")
            return

        profile = get_user_info(user["id"], full_profile=True) or {}
        saudacao_base = "Bem-vindo"
        saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

        st.markdown(f"**👤 {saudacao}, {user['display_name']}**")
        st.markdown(f"✉️ {user['email']}")

        # Botão de logout
        if st.button("Logout 🚪", key="logout"):
            sign_out()

        st.markdown("---")

        # Opção para habilitar a área do profissional
        if not is_professional_enabled(user["id"]):
            if st.button("🔐 Habilitar área do profissional", key="professional"):
                st.session_state["show_prof_input"] = True

            if st.session_state.get("show_prof_input", False):
                prof_key = st.text_input("Digite 'AUTOMATIZEJA' para confirmar:", key="prof_key_input")
                if prof_key:
                    if prof_key == "AUTOMATIZEJA":
                        success, msg = enable_professional_area(user["id"], user["email"], user["display_name"])
                        if success:
                            st.session_state["refresh"] = True
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("❌ Chave incorreta!")
        else:
            st.success("✅ Área do profissional habilitada!")


# 🖥️ Função para renderizar a dashboard.
def render_dashboard():
    """Renderiza o dashboard para usuários autenticados."""
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

    st.markdown("---")
    st.info("🔍 Novos recursos serão adicionados em breve!")


# 🖥️ Função para renderizar a dashboard exclusiva para profissionais habilitados.
def render_professional_dashboard(user):

    if not user or "id" not in user:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    profile = get_user_info(user["id"], full_profile=True)
    saudacao_base = "Bem-vindo"
    saudacao = adjust_gender_ending(saudacao_base, profile.get("genero", "M"))

    render_sidebar(user)

    st.subheader(f"{saudacao}, {user['display_name']}! 🎉")
    st.markdown("### 📊 Área do Profissional")

    st.markdown("---")

    st.markdown("##### Convidar Paciente")
    patient_email = st.text_input("Digite o email do paciente para enviar um convite de vinculação:", key="patient_email_input")
    
    if st.button("Enviar Convite", key="patientlink", use_container_width=True):
        if patient_email:
            success, msg = create_patient_invitation(user["id"], patient_email)
            if success:
                st.success("✅ Convite enviado com sucesso!")
            else:
                st.error(f"Erro: {msg}")
        else:
            st.warning("Por favor, insira o email do paciente.")

    # Verificação para evitar erro de `KeyError`
    if user and "id" in user:
        render_pending_invitations(user["id"])
    else:
        st.warning("⚠️ Usuário inválido. Não foi possível carregar os convites.")

    st.markdown("---")
    st.info("🔍 Novos recursos serão adicionados em breve!")
