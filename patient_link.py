import uuid
import streamlit as st
from auth import supabase_client
from utils.date_utils import format_date
from utils.user_utils import get_user_info
from utils.design_utils import load_css
from utils.gender_utils import get_professional_title


# 📩 Função para criar um convite de vinculação entre um profissional e um paciente.
def create_patient_invitation(professional_id: str, patient_email: str):

    # Buscar informações do paciente pelo e-mail
    patient_info = get_user_info(patient_email, by_email=True, full_profile=True)

    if not patient_info.get("auth_user_id"):
        st.error(f"🚨 Paciente {patient_email} não encontrado no banco.")
        return False, "Paciente não encontrado."

    patient_auth_id = patient_info["auth_user_id"]

    # Verificar se já existe um convite pendente
    existing_link = supabase_client.from_("professional_patient_link") \
        .select("id, status") \
        .eq("professional_id", professional_id) \
        .eq("patient_id", patient_auth_id) \
        .execute()

    if existing_link and existing_link.data:
        st.warning("📩 Convite já foi enviado.")
        return False, "Convite já enviado."

    # Criar um novo convite de vinculação
    invitation_id = str(uuid.uuid4())
    data = {
        "id": invitation_id,
        "professional_id": professional_id,
        "patient_id": patient_auth_id,
        "status": "pending"
    }

    response = supabase_client.from_("professional_patient_link").insert(data).execute()

    if hasattr(response, "error") and response.error:
        st.error(f"❌ Erro ao criar convite: {response.error.message}")
        return False, f"Erro ao criar convite: {response.error.message}"

    st.cache_data.clear()
    return True, None


# 🟢 Função para aceitar um convite de vínculação.
def accept_invitation(professional_id: str, patient_id: str):

    update_response = supabase_client.from_("professional_patient_link") \
        .update({"status": "accepted"}) \
        .eq("professional_id", professional_id) \
        .eq("patient_id", patient_id) \
        .execute()

    if hasattr(update_response, "error") and update_response.error:
        return False, f"Erro ao aceitar convite: {update_response.error.message}"

    return True, None


# 🔴 Função para rejeitar um convite de vínculação.
def reject_invitation(professional_id: str, patient_id: str):
    
    update_response = supabase_client.from_("professional_patient_link") \
        .update({"status": "rejected"}) \
        .eq("professional_id", professional_id) \
        .eq("patient_id", patient_id) \
        .execute()

    if hasattr(update_response, "error") and update_response.error:
        return False, f"Erro ao recusar convite: {update_response.error.message}"

    return True, None


# ⏳ Função para listar convites pendentes.
def list_pending_invitations(professional_id: str):
    
    response = supabase_client.from_("professional_patient_link") \
        .select("id, patient_id, status, created_at") \
        .eq("professional_id", professional_id) \
        .eq("status", "pending") \
        .execute()

    return response.data if response and hasattr(response, "data") else []


# 📜 Função para listar convites de um paciente.
def list_invitations_for_patient(patient_id: str):
    
    response = supabase_client.from_("professional_patient_link") \
        .select("*") \
        .eq("patient_id", patient_id) \
        .execute()
    
    if response and hasattr(response, "data"):
        return response.data
    return []


# 📜 Função para listar convites enviados por um profissional.
def list_invitations_for_professional(professional_id: str):
    
    response = supabase_client.from_("professional_patient_link") \
        .select("*") \
        .eq("professional_id", professional_id) \
        .execute()
    
    if response and hasattr(response, "data"):
        return response.data
    return []


# 🖥️ Renderiza os convites pendentes para o paciente aceitar ou recusar.
def render_patient_invitations(user):
    
    # Inicializa as chaves no session_state, se ainda não estiverem definidas.
    if "invitation_processed" not in st.session_state:
        st.session_state.invitation_processed = False
    if "invitation_placeholder" not in st.session_state:
        st.session_state.invitation_placeholder = st.empty()

    # Se o convite já foi processado, esvazia o placeholder e não renderiza nada
    if st.session_state.invitation_processed:
        st.session_state.invitation_placeholder.empty()
        return

    # Obtém os convites recebidos para o paciente através do ID do usuário
    invitations = list_invitations_for_patient(user["id"])
    if not invitations:
        return  # Se não houver convites, finaliza a função

    # Filtra somente os convites com status "pending" (pendentes)
    pending_invitations = [inv for inv in invitations if inv["status"] == "pending"]
    if not pending_invitations:
        return  # Se não houver convites pendentes, finaliza a função

    # Seleciona o primeiro convite pendente
    inv = pending_invitations[0]

    # Utiliza o placeholder armazenado no session_state para exibir os detalhes do convite
    with st.session_state.invitation_placeholder.container():
        
        with st.spinner("Processando..."):
            # Obtém as informações do profissional que enviou o convite
            professional_profile = get_user_info(inv["professional_id"], full_profile=True)
        
            if professional_profile:
                # Formata o nome do profissional utilizando a função get_professional_title()
                professional_name = get_professional_title(professional_profile)
                st.markdown(f"##### {professional_name} deseja se vincular a você.")

            # Formata a data de envio do convite
            dia, mes, ano = format_date(inv["created_at"])
            formatted_date = f"**Data de Envio:** {dia}/{mes}/{ano}" if dia else "Data inválida"
            st.write(formatted_date)

            # Organiza os botões de ação em duas colunas, desabilitando-os se o convite já foi processado
            col1, col2 = st.columns(2)
            with col1:
                # Botão para aceitar o convite com parâmetro disabled
                accept_clicked = st.button("Aceitar", key="accept", disabled=st.session_state.invitation_processed)
                if accept_clicked:
                    # Atualiza o status do convite para "accepted"
                    accept_invitation(inv["professional_id"], inv["patient_id"])
                    st.cache_data.clear()  # Limpa o cache para garantir a atualização dos dados
                    st.session_state.invitation_processed = True  # Marca o convite como processado
            with col2:
                # Botão para recusar o convite com parâmetro disabled
                reject_clicked = st.button("Recusar", key="reject", disabled=st.session_state.invitation_processed)
                if reject_clicked:
                    # Atualiza o status do convite para "rejected"
                    reject_invitation(inv["professional_id"], inv["patient_id"])
                    st.cache_data.clear()  # Limpa o cache.
                    st.session_state.invitation_processed = True  # Marca o convite como processado

    # Se o convite foi processado, esvazia o placeholder para remover os botões e informações
    if st.session_state.invitation_processed:
        st.session_state.invitation_placeholder.empty()

# 🖥️ Renderiza a sessão do profissional para se vincular a novos pacientes
def render_invite_patient_section(user):

    st.subheader("📩 Convidar Paciente")

    # Input do email
    patient_email = st.text_input("Digite o email do paciente:", key="patient_email_input")

    # Placeholder centralizado para feedback
    feedback_placeholder = st.empty()

    # Botão de envio de convite
    if st.button("Enviar Convite", key="patientlink", use_container_width=True, disabled=st.session_state.get("processing", False)):
        st.session_state["processing"] = True
        try:
            with feedback_placeholder.container():
                with st.spinner("Processando..."):
                    if patient_email:
                        success, msg = create_patient_invitation(user["id"], patient_email)
                        if success:
                            st.success("✅ Convite enviado com sucesso!")
                        else:
                            st.error(f"Erro: {msg}")
                    else:
                        st.warning("⚠️ Por favor, insira o email do paciente.")
        finally:
            st.session_state["processing"] = False


# 🖥️ Renderiza os convites pendentes para o profissional.
def render_pending_invitations(professional_id):

    st.subheader("📩 Convites Pendentes")

    pending_invitations = list_pending_invitations(professional_id)

    if not pending_invitations:
        st.info("✅ Nenhum convite pendente no momento.")
        return

    for invitation in pending_invitations:
        # Buscar nome e e-mail do paciente pelo ID
        patient_info = get_user_info(invitation['patient_id'], full_profile=True)
        patient_name = patient_info["display_name"]
        patient_email = patient_info["email"]

        # Formatar a data
        dia, mes, ano = format_date(invitation['created_at'])
        formatted_date = f"{dia}/{mes}/{ano}" if dia else "Data inválida"

        # Exibir as informações formatadas
        st.write(f"👤 **Paciente:** {patient_name}")
        st.write(f"📅 **Data de Envio:** {formatted_date}")
        st.write(f"✉️ **E-mail:** {patient_email}")
        st.markdown("---")

