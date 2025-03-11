import uuid
import streamlit as st
from auth import supabase_client
from utils.date_utils import format_date
from utils.user_utils import get_user_info
from utils.design_utils import load_css
from utils.gender_utils import get_professional_title


# 📩 Função para criar um convite de vinculação entre um profissional e um paciente.
def create_patient_invitation(professional_id: str, patient_email: str):
    """
    Cria um convite para um paciente se vincular a um profissional.

    Fluxo:
        1. Busca o paciente no banco pelo e-mail.
        2. Se o paciente não existir, exibe um erro.
        3. Verifica se já existe um convite pendente.
        4. Se não houver convite, cria um novo com status "pending".
        5. Retorna True se a inserção for bem-sucedida, ou False se houver erro.

    Args:
        professional_id (str): O ID do profissional que está enviando o convite.
        patient_email (str): O e-mail do paciente que será convidado.

    Returns:
        tuple (bool, str or None)
            - (True, None): Se o convite foi criado com sucesso.
            - (False, "Paciente não encontrado."): Se o paciente não foi encontrado.
            - (False, "Convite já enviado."): Se o convite já existe.
            - (False, mensagem_de_erro): Se houve erro na inserção.

    Calls:
        dashboard.py → render_professional_dashboard()
    """

    st.write(f"🔍 Buscando {patient_email} no banco de dados do sistema.")

    # Buscar informações do paciente pelo e-mail
    patient_info = get_user_info(patient_email, by_email=True, full_profile=True)

    # Se o ID não foi encontrado...
    if not patient_info["auth_user_id"]: 
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
    """
    Atualiza o status do convite para 'accepted' quando um paciente aceita um vínculo com um profissional.

     Fluxo:
        1. Busca a entrada no banco.
        2. Atualiza o status para "accepted".
        3. Retorna True se a operação for bem-sucedida, False se houver erro.

     Args:
        professional_id (str): ID do profissional vinculado ao convite.
        patient_id (str): ID do paciente que aceita o convite.

     Returns:
        tuple (bool, str or None)
            - (True, None): Se a atualização foi bem-sucedida.
            - (False, mensagem_de_erro): Se houve erro.
     
     Calls:
        patient_link.py → render_patient_invitations(user)
    """

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
    """
    Atualiza o status do convite para 'rejected' quando um paciente recusa um vínculo.

     Fluxo:
        1. Busca a entrada no banco.
        2. Atualiza o status para "rejected".
        3. Retorna True se a operação for bem-sucedida, False se houver erro.

     Args:
        professional_id (str): ID do profissional vinculado ao convite.
        patient_id (str): ID do paciente que rejeita o convite.

     Returns:
        tuple (bool, str or None)
            - (True, None): Se a atualização foi bem-sucedida.
            - (False, mensagem_de_erro): Se houve erro.
    
     Calls:
        patient_link.py → render_patient_invitations(user)
    """

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
    """
    Retorna todos os convites pendentes de um profissional.

     Fluxo:
        1. Consulta a tabela "professional_patient_link".
        2. Filtra apenas os convites onde `status="pending"` e `professional_id` corresponde.
        3. Retorna a lista de convites pendentes.

     Args:
        professional_id (str): ID do profissional.

     Returns:
        list[dict]: Lista de convites pendentes.

     Calls:
        patient_link.py → render_pending_invitations(professional_id)
    """
    
    response = supabase_client.from_("professional_patient_link") \
        .select("id, patient_id, status, created_at") \
        .eq("professional_id", professional_id) \
        .eq("status", "pending") \
        .execute()

    return response.data if response and hasattr(response, "data") else []



# 📜 Função para listar convites de um paciente.
def list_invitations_for_patient(patient_id: str):
    """
    Retorna todos os convites recebidos por um paciente.

     Fluxo:
        1. Consulta a tabela "professional_patient_link".
        2. Filtra todos os registros onde `patient_id` corresponde.
        3. Retorna a lista completa de convites (pendentes ou não).

     Args:
        patient_id (str): ID do paciente.

     Returns:
        list[dict]: Lista de convites associados ao paciente.

     Calls:
        patient_link.py → render_patient_invitations(user)
    """

    response = supabase_client.from_("professional_patient_link") \
        .select("*") \
        .eq("patient_id", patient_id) \
        .execute()

    if response and hasattr(response, "data"):
        return response.data
    return []


# 📜 Função para listar convites enviados por um profissional.
def list_invitations_for_professional(professional_id: str):
    """
    Retorna todos os convites enviados por um profissional.

     Fluxo:
        1. Consulta a tabela "professional_patient_link".
        2. Filtra todos os registros onde `professional_id` corresponde.
        3. Retorna a lista completa de convites (pendentes ou não).

     Args:
        professional_id (str): ID do profissional.

     Returns:
        list[dict]: Lista de convites associados ao profissional.

     Calls:
        Não chamada diretamente no código atual. Pode ser útil para um painel administrativo.
    """

    response = supabase_client.from_("professional_patient_link") \
        .select("*") \
        .eq("professional_id", professional_id) \
        .execute()

    if response and hasattr(response, "data"):
        return response.data
    return []


# 🖥️ Renderiza os convites pendentes para o paciente aceitar ou recusar.
def render_patient_invitations(user):
    """
    Renderiza os convites recebidos para o paciente aceitar ou recusar.

    Fluxo:
        1. Obtém os convites pendentes do paciente.
        2. Exibe informações sobre o profissional que enviou o convite.
        3. Cria botões estilizados para aceitar ou recusar.
        4. Atualiza a interface ao interagir com os botões.

    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        dashboard.py → render_dashboard()
    """

    invitations = list_invitations_for_patient(user["id"])
    if not invitations:
        return

    st.markdown("##### 📩 Convites Pendentes")

    for inv in invitations:
        if inv["status"] == "pending":
            professional_profile = get_user_info(inv["professional_id"], full_profile=True)
            if professional_profile:
                professional_name = get_professional_title(professional_profile)
                st.markdown(f"##### {professional_name} deseja se vincular a você.")

            # Criamos colunas para organizar os botões
            col1, col2 = st.columns(2)

            with col1:
                # ✅ Aqui garantimos que a chave do botão está associada ao CSS correto!
                if st.button("Aceitar", key="accept"):
                    success, msg = accept_invitation(inv["professional_id"], inv["patient_id"])
                    if success:
                        st.success("Convite aceito com sucesso!")
                        st.rerun()
                    else:
                        st.error(msg)

            with col2:
                # ✅ Aqui garantimos que a chave do botão está associada ao CSS correto!
                if st.button("Recusar", key="reject"):
                    success, msg = reject_invitation(inv["professional_id"], inv["patient_id"])
                    if success:
                        st.success("Convite recusado.")
                        st.rerun()
                    else:
                        st.error(msg)


# 🖥️ Renderiza os convites pendentes para o profissional
def render_pending_invitations(professional_id):
    """
    Renderiza os convites recebidos para o profissional ver os pacientes convidados.

    Fluxo:
        1. Obtém os convites pendentes do profissional.
        2. Exibe informações sobre o paciente convidado.
        3. Formata e exibe os dados corretamente.

    Args:
        professional_id (str): ID do profissional autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        dashboard.py → render_professional_dashboard()
    """

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