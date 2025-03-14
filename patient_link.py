import uuid
import streamlit as st
from auth import supabase_client
from utils.date_utils import format_date
from utils.user_utils import get_user_info
from utils.design_utils import load_css
from utils.gender_utils import get_professional_title
from utils.system_utils import update_global_processing_message

# ------------------------------------------------------------------------------
# Função: create_patient_invitation
# ------------------------------------------------------------------------------
def create_patient_invitation(professional_id: str, patient_email: str):
    """
    Cria um convite para um paciente se vincular a um profissional.

    Fluxo:
      1. Atualiza o container global com a mensagem "⏳ Processando..." enquanto executa a função.
      2. Busca informações do paciente usando get_user_info() com base no e-mail.
      3. Se o paciente não for encontrado (não possui "auth_user_id"), limpa a mensagem e exibe um erro.
      4. Verifica se já existe um convite pendente para o mesmo vínculo (usando uma consulta na tabela 'professional_patient_link').
      5. Se já houver convite, limpa a mensagem e exibe um aviso de que o convite já foi enviado.
      6. Caso contrário, gera um ID único para o convite, monta o dicionário de dados e insere o registro no banco.
      7. Limpa o container global de mensagem e, se houver erro na inserção, exibe o erro.
      8. Limpa o cache e retorna (True, None) em caso de sucesso ou (False, mensagem_de_erro) em caso de falha.

    Args:
        professional_id (str): ID do profissional que envia o convite.
        patient_email (str): E-mail do paciente a ser convidado.

    Returns:
        tuple: (True, None) em caso de sucesso, ou (False, mensagem_de_erro) se ocorrer erro.

    Calls:
        - get_user_info() [em utils/user_utils.py]
        - supabase_client.from_("professional_patient_link").select()/insert()/execute() [do Supabase]
        - update_global_processing_message() [em utils/system_utils.py]
    """
    # Exibe a mensagem de processamento no container global
    update_global_processing_message("⏳ Processando...")

    # Buscar informações do paciente pelo e-mail
    patient_info = get_user_info(patient_email, by_email=True, full_profile=True)

    if not patient_info.get("auth_user_id"):
        update_global_processing_message("")  # Limpa a mensagem
        st.error(f"🚨 Paciente {patient_email} não encontrado no banco.")
        return False, "Paciente não encontrado."

    patient_auth_id = patient_info["auth_user_id"]

    # Verifica se já existe um convite pendente
    existing_link = supabase_client.from_("professional_patient_link") \
        .select("id, status") \
        .eq("professional_id", professional_id) \
        .eq("patient_id", patient_auth_id) \
        .execute()

    if existing_link and existing_link.data:
        update_global_processing_message("")
        st.warning("📩 Convite já foi enviado.")
        return False, "Convite já enviado."

    # Gera um ID único para o convite e prepara os dados para inserção
    invitation_id = str(uuid.uuid4())
    data = {
        "id": invitation_id,
        "professional_id": professional_id,
        "patient_id": patient_auth_id,
        "status": "pending"
    }

    # Insere o registro na tabela 'professional_patient_link'
    response = supabase_client.from_("professional_patient_link").insert(data).execute()
    update_global_processing_message("")  # Limpa a mensagem de processamento

    if hasattr(response, "error") and response.error:
        st.error(f"❌ Erro ao criar convite: {response.error.message}")
        return False, f"Erro ao criar convite: {response.error.message}"

    st.cache_data.clear()
    return True, None


# ------------------------------------------------------------------------------
# Função: accept_invitation
# ------------------------------------------------------------------------------
def accept_invitation(professional_id: str, patient_id: str):
    """
    Atualiza o status do convite para 'accepted' quando um paciente aceita o vínculo com um profissional.

    Fluxo:
      1. Atualiza o registro na tabela 'professional_patient_link' definindo o status para "accepted".
      2. Retorna (True, None) se a operação for bem-sucedida; caso contrário, retorna (False, mensagem_de_erro).

    Args:
        professional_id (str): ID do profissional vinculado.
        patient_id (str): ID do paciente que aceita o convite.

    Returns:
        tuple: (True, None) em caso de sucesso ou (False, mensagem_de_erro).

    Calls:
        - supabase_client.from_("professional_patient_link").update()/execute() [do Supabase]
    """
    update_response = supabase_client.from_("professional_patient_link") \
        .update({"status": "accepted"}) \
        .eq("professional_id", professional_id) \
        .eq("patient_id", patient_id) \
        .execute()

    if hasattr(update_response, "error") and update_response.error:
        return False, f"Erro ao aceitar convite: {update_response.error.message}"

    return True, None


# ------------------------------------------------------------------------------
# Função: reject_invitation
# ------------------------------------------------------------------------------
def reject_invitation(professional_id: str, patient_id: str):
    """
    Atualiza o status do convite para 'rejected' quando um paciente recusa o vínculo.

    Fluxo:
      1. Atualiza o registro na tabela 'professional_patient_link' definindo o status para "rejected".
      2. Retorna (True, None) se a operação for bem-sucedida; caso contrário, retorna (False, mensagem_de_erro).

    Args:
        professional_id (str): ID do profissional vinculado.
        patient_id (str): ID do paciente que rejeita o convite.

    Returns:
        tuple: (True, None) em caso de sucesso ou (False, mensagem_de_erro).

    Calls:
        - supabase_client.from_("professional_patient_link").update()/execute() [do Supabase]
    """
    update_response = supabase_client.from_("professional_patient_link") \
        .update({"status": "rejected"}) \
        .eq("professional_id", professional_id) \
        .eq("patient_id", patient_id) \
        .execute()

    if hasattr(update_response, "error") and update_response.error:
        return False, f"Erro ao recusar convite: {update_response.error.message}"

    return True, None


# ------------------------------------------------------------------------------
# Função: list_pending_invitations
# ------------------------------------------------------------------------------
def list_pending_invitations(professional_id: str):
    """
    Retorna todos os convites pendentes para um profissional.

    Fluxo:
      1. Consulta a tabela "professional_patient_link" filtrando por professional_id e status "pending".
      2. Retorna a lista de convites pendentes.

    Args:
        professional_id (str): ID do profissional.

    Returns:
        list[dict]: Lista de convites pendentes.

    Calls:
        - supabase_client.from_("professional_patient_link").select()/execute() [do Supabase]
    """
    response = supabase_client.from_("professional_patient_link") \
        .select("id, patient_id, status, created_at") \
        .eq("professional_id", professional_id) \
        .eq("status", "pending") \
        .execute()

    return response.data if response and hasattr(response, "data") else []


# ------------------------------------------------------------------------------
# Função: list_invitations_for_patient
# ------------------------------------------------------------------------------
def list_invitations_for_patient(patient_id: str):
    """
    Retorna todos os convites recebidos por um paciente.

    Fluxo:
      1. Consulta a tabela "professional_patient_link" filtrando por patient_id.
      2. Retorna a lista de convites (independentemente do status).

    Args:
        patient_id (str): ID do paciente.

    Returns:
        list[dict]: Lista de convites associados ao paciente.

    Calls:
        - supabase_client.from_("professional_patient_link").select()/execute() [do Supabase]
    """
    response = supabase_client.from_("professional_patient_link") \
        .select("*") \
        .eq("patient_id", patient_id) \
        .execute()

    if response and hasattr(response, "data"):
        return response.data
    return []


# ------------------------------------------------------------------------------
# Função: list_invitations_for_professional
# ------------------------------------------------------------------------------
def list_invitations_for_professional(professional_id: str):
    """
    Retorna todos os convites enviados por um profissional.

    Fluxo:
      1. Consulta a tabela "professional_patient_link" filtrando por professional_id.
      2. Retorna a lista completa de convites enviados pelo profissional.

    Args:
        professional_id (str): ID do profissional.

    Returns:
        list[dict]: Lista de convites enviados.

    Calls:
        - supabase_client.from_("professional_patient_link").select()/execute() [do Supabase]
    """
    response = supabase_client.from_("professional_patient_link") \
        .select("*") \
        .eq("professional_id", professional_id) \
        .execute()

    if response and hasattr(response, "data"):
        return response.data
    return []


# ------------------------------------------------------------------------------
# Função: render_patient_invitations
# ------------------------------------------------------------------------------
def render_patient_invitations(user):
    """
    Renderiza os convites recebidos para o paciente aceitar ou recusar.

    Fluxo:
      1. Obtém os convites do paciente (usando list_invitations_for_patient()) e filtra apenas os pendentes.
      2. Se houver convites pendentes, seleciona o primeiro e verifica se ele já foi processado (usando uma flag no st.session_state).
      3. Se o convite não foi processado, cria um container (invitation_container) para exibir os dados do convite e os botões "Aceitar" e "Recusar".
      4. Os botões possuem keys fixas ("accept" e "reject") para preservar os estilos definidos via CSS.
      5. Ao clicar em um dos botões, o ID do convite é registrado em st.session_state["invitation_processed"],
         o container exibe a mensagem "⏳ Processando..." (usando update_global_processing_message) e, em seguida, o convite é removido do container.
         Não é usado st.rerun(), para evitar duplicação de botões, e a mensagem de processamento aparece antes dos botões.
    
    Args:
        user (dict): Dados do paciente autenticado (contendo pelo menos "id").

    Returns:
        None (a interface é renderizada diretamente no Streamlit).

    Calls:
        - list_invitations_for_patient() [em utils/patient_link.py]
        - get_user_info() [em utils/user_utils.py]
        - get_professional_title() [em utils/gender_utils.py]
        - accept_invitation() / reject_invitation() [em utils/patient_link.py]
        - update_global_processing_message() [em utils/system_utils.py]
    """
    invitations = list_invitations_for_patient(user["id"])
    if not invitations:
        return

    # Filtra somente os convites com status "pending"
    pending_invitations = [inv for inv in invitations if inv["status"] == "pending"]
    if not pending_invitations:
        return

    # Seleciona apenas o primeiro convite pendente
    inv = pending_invitations[0]

    # Inicializa a variável no estado para identificar convites processados
    if "invitation_processed" not in st.session_state:
        st.session_state["invitation_processed"] = None

    # Se o convite já foi processado, não exibe nada
    if st.session_state["invitation_processed"] == inv["id"]:
        return

    # Cria um container para exibir o convite
    invitation_container = st.container()
    with invitation_container:
        # Exibe os dados do convite: nome do profissional e data de envio
        professional_profile = get_user_info(inv["professional_id"], full_profile=True)
        if professional_profile:
            professional_name = get_professional_title(professional_profile)
            st.markdown(f"##### {professional_name} deseja se vincular a você.")
        
        dia, mes, ano = format_date(inv["created_at"])
        formatted_date = f"**Data de Envio:** {dia}/{mes}/{ano}" if dia else "Data inválida"
        st.write(formatted_date)

        # Exibe o placeholder global de processamento (antes dos botões)
        update_global_processing_message("⏳ Processando...")

        # Cria duas colunas para os botões, mantendo as keys fixas para preservar os estilos
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Aceitar", key="accept"):
                st.session_state["invitation_processed"] = inv["id"]
                accept_invitation(inv["professional_id"], inv["patient_id"])
                st.cache_data.clear()
                # Limpa o container para remover o convite da tela
                invitation_container.empty()
                update_global_processing_message("")  # Limpa a mensagem
        with col2:
            if st.button("Recusar", key="reject"):
                st.session_state["invitation_processed"] = inv["id"]
                reject_invitation(inv["professional_id"], inv["patient_id"])
                st.cache_data.clear()
                invitation_container.empty()
                update_global_processing_message("")


# ------------------------------------------------------------------------------
# Função: render_pending_invitations
# ------------------------------------------------------------------------------
def render_pending_invitations(professional_id: str):
    """
    Renderiza os convites pendentes para o profissional ver os pacientes convidados.

    Fluxo:
      1. Obtém os convites pendentes filtrando por professional_id e status "pending".
      2. Exibe informações de cada convite, incluindo nome do paciente, data de envio e e-mail.

    Args:
        professional_id (str): ID do profissional autenticado.

    Returns:
        None

    Calls:
        - list_pending_invitations() [em utils/patient_link.py]
        - get_user_info() [em utils/user_utils.py]
        - format_date() [em utils/date_utils.py]
    """
    st.subheader("📩 Convites Pendentes")
    pending_invitations = list_pending_invitations(professional_id)
    if not pending_invitations:
        st.info("✅ Nenhum convite pendente no momento.")
        return

    for invitation in pending_invitations:
        patient_info = get_user_info(invitation['patient_id'], full_profile=True)
        patient_name = patient_info["display_name"]
        patient_email = patient_info["email"]

        dia, mes, ano = format_date(invitation['created_at'])
        formatted_date = f"{dia}/{mes}/{ano}" if dia else "Data inválida"

        st.write(f"👤 **Paciente:** {patient_name}")
        st.write(f"📅 **Data de Envio:** {formatted_date}")
        st.write(f"✉️ **E-mail:** {patient_email}")
        st.markdown("---")