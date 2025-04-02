import streamlit as st
from auth import supabase_client


# 💾 Função para buscar e cachear o perfil do usuário.
@st.cache_data
def get_user_info(identifier, by_email=False, full_profile=False):
    if not identifier:
        return None

    # Define os campos a buscar
    select_fields = "*" if full_profile else "auth_user_id, display_name, email"

    # Cria a consulta
    query = supabase_client.from_("user_profile").select(select_fields)
    response = query.eq("email", identifier).execute() if by_email else query.eq("auth_user_id", identifier).execute()

    # Se encontrou dados na tabela user_profile
    if response and hasattr(response, "data") and response.data:
        return response.data[0]

    # Caso contrário, tenta buscar no Supabase Auth
    auth_response = supabase_client.auth.get_user()

    if auth_response and auth_response.user:
        user_metadata = auth_response.user.user_metadata or {}
        return {
            "auth_user_id": identifier,
            "display_name": user_metadata.get("display_name", "Usuário"),
            "email": auth_response.user.email
        }

    # Retorno padrão se nada for encontrado
    return {
        "auth_user_id": None,
        "display_name": "Usuário Desconhecido",
        "email": "Email não disponível"
    }