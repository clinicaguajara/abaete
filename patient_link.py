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
      1. Busca o paciente no banco pelo e-mail usando get_user_info().
      2. Se o paciente não for encontrado, exibe um erro.
      3. Verifica se já existe um convite pendente para o mesmo vínculo.
      4. Se não houver convite, gera um ID único e insere um novo registro na tabela 'professional_patient_link'
         com status "pending".
      5. Limpa o cache e retorna True se a inserção for bem-sucedida; caso contrário, retorna False e uma mensagem de erro.

    Args:
        professional_id (str): ID do profissional que envia o convite.
        patient_email (str): E-mail do paciente a ser convidado.

    Returns:
        tuple: (True, None) em caso de sucesso ou (False, mensagem_de_erro).

    Calls:
        - get_user_info() [em utils/user_utils.py]
        - supabase_client.from_("professional_patient_link").select()/insert()/execute() [do Supabase]
    """
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
    """
    Atualiza o status do convite para 'accepted' quando um paciente aceita o vínculo com um profissional.

    Fluxo:
      1. Atualiza o registro correspondente na tabela 'professional_patient_link' definindo o status para "accepted".
      2. Retorna True se a operação foi bem-sucedida; caso contrário, retorna False e uma mensagem de erro.

    Args:
        professional_id (str): ID do profissional vinculado.
        patient_id (str): ID do paciente que aceita o convite.

    Returns:
        tuple: (True, None) se a atualização foi bem-sucedida, ou (False, mensagem_de_erro).

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


# 🔴 Função para rejeitar um convite de vínculação.
def reject_invitation(professional_id: str, patient_id: str):
    """
    Atualiza o status do convite para 'rejected' quando um paciente recusa o vínculo.

    Fluxo:
      1. Atualiza o registro correspondente na tabela 'professional_patient_link' definindo o status para "rejected".
      2. Retorna True se a operação foi bem-sucedida; caso contrário, retorna False e uma mensagem de erro.

    Args:
        professional_id (str): ID do profissional vinculado.
        patient_id (str): ID do paciente que rejeita o convite.

    Returns:
        tuple: (True, None) se a atualização foi bem-sucedida, ou (False, mensagem_de_erro).

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


# ⏳ Função para listar convites pendentes.
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


# 📜 Função para listar convites de um paciente.
def list_invitations_for_patient(patient_id: str):
    """
    Retorna todos os convites recebidos por um paciente.

    Fluxo:
      1. Consulta a tabela "professional_patient_link" filtrando por patient_id.
      2. Retorna a lista de convites (pendentes ou não).

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


# 📜 Função para listar convites enviados por um profissional.
def list_invitations_for_professional(professional_id: str):
    """
    Retorna todos os convites enviados por um profissional.

    Fluxo:
      1. Consulta a tabela "professional_patient_link" filtrando por professional_id.
      2. Retorna a lista completa de convites.

    Args:
        professional_id (str): ID do profissional.

    Returns:
        list[dict]: Lista de convites enviados pelo profissional.

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


# 🖥️ Renderiza os convites pendentes para o paciente aceitar ou recusar.
def render_patient_invitations(user):
    """
    Renderiza os convites pendentes para o paciente.

    Fluxo:
      1. Busca os convites recebidos para o paciente a partir do ID do usuário.
      2. Filtra apenas os convites com status "pending".
      3. Se houver convites pendentes, seleciona o primeiro convite.
      4. Cria um container para exibir os detalhes do convite.
      5. Exibe informações do profissional que enviou o convite.
      6. Exibe a data de envio do convite.
      7. Organiza botões para o paciente aceitar ou recusar o convite.
      8. Após a ação (aceitar ou recusar), limpa o cache e força a reinicialização da interface.
    
    Args:
      user (dict): Dicionário contendo os dados do usuário autenticado, incluindo seu ID.
    
    Returns:
      None: A função renderiza a interface diretamente no Streamlit.
    
    Calls:
      - list_invitations_for_patient() para obter os convites.
      - get_user_info() para obter os dados do profissional.
      - get_professional_title() para formatar o nome do profissional.
      - format_date() para formatar a data de envio.
      - accept_invitation() e reject_invitation() para atualizar o status do convite.
      - st.rerun() para atualizar a interface.
    """
    # Obtém os convites recebidos para o paciente através do ID do usuário.
    invitations = list_invitations_for_patient(user["id"])
    if not invitations:
        return  # Se não houver convites, finaliza a função.

    # Filtra somente os convites com status "pending" (pendentes).
    pending_invitations = [inv for inv in invitations if inv["status"] == "pending"]
    if not pending_invitations:
        return  # Se não houver convites pendentes, finaliza a função.

    # Seleciona o primeiro convite pendente.
    inv = pending_invitations[0]
    
    # Cria um container exclusivo para exibir os detalhes do convite.
    invitation_container = st.container()
    
    with invitation_container:
        # Obtém as informações do profissional que enviou o convite.
        professional_profile = get_user_info(inv["professional_id"], full_profile=True)
        if professional_profile:
            # Formata o nome do profissional utilizando a função get_professional_title().
            professional_name = get_professional_title(professional_profile)
            st.markdown(f"##### {professional_name} deseja se vincular a você.")
        
        # Formata a data de envio do convite.
        dia, mes, ano = format_date(inv["created_at"])
        formatted_date = f"**Data de Envio:** {dia}/{mes}/{ano}" if dia else "Data inválida"
        st.write(formatted_date)
        
        # Organiza os botões de ação em duas colunas.
        col1, col2 = st.columns(2)
        
        with col1:
            # Botão para aceitar o convite.
            if st.button("Aceitar", key="accept"):
                # Atualiza o status do convite para "accepted".
                accept_invitation(inv["professional_id"], inv["patient_id"])
                st.cache_data.clear()  # Limpa o cache para garantir que os dados atualizados sejam carregados.
                st.rerun()  # Reinicia a interface para que o convite não seja mais renderizado.
                
        with col2:
            # Botão para recusar o convite.
            if st.button("Recusar", key="reject"):
                # Atualiza o status do convite para "rejected".
                reject_invitation(inv["professional_id"], inv["patient_id"])
                st.cache_data.clear()  # Limpa o cache.
                st.rerun()  # Reinicia a interface para remover o convite da exibição.



# 🖥️ Renderiza os convites pendentes para o profissional.
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
        - list_pending_invitations()
        - get_user_info() 
        - format_date()
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