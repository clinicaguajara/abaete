import streamlit as st
from auth import supabase_client


# 💾 Função para buscar e cachear o perfil do usuário.
@st.cache_data
def get_user_info(identifier, by_email=False, full_profile=False):
    
    # Verificação de segurança: se o ID ou email estiver vazio
    if not identifier:
        return None

    # Define quais campos buscar no banco de dados
    select_fields = "*" if full_profile else "auth_user_id, display_name, email"

    # Monta a query na tabela user_profile
    query = supabase_client.from_("user_profile").select(select_fields)
    response = query.eq("email", identifier).execute() if by_email else query.eq("auth_user_id", identifier).execute()

    # Se encontrar dados no banco de perfis
    if response and hasattr(response, "data") and response.data:
        return response.data[0]

    # Caso não haja dados no user_profile, busca no Supabase Auth
    auth_response = supabase_client.auth.get_user()

    if auth_response and auth_response.user:
        user_metadata = auth_response.user.user_metadata or {}
        return {
            "auth_user_id": identifier,
            "display_name": user_metadata.get("display_name", "Usuário"),
            "email": auth_response.user.email
        }

    # Retorno padrão se tudo falhar
    return {
        "auth_user_id": None,
        "display_name": "Usuário Desconhecido",
        "email": "Email não disponível"
    }
