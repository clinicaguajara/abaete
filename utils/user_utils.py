import streamlit as st
from auth import supabase_client


# 💾 Função para cachear o perfil do usuário e evitar buscas repetitivas.
@st.cache_data
def get_user_info(identifier, by_email=False, full_profile=False):
    """
    Obtém informações de um usuário (paciente ou profissional) do banco de dados.

     Fluxo:
        1. Se `by_email=True`, busca o usuário pelo e-mail.
        2. Se `by_email=False`, busca o usuário pelo ID.
        3. Se `full_profile=True`, retorna todos os dados do usuário.
        4. Se `full_profile=False`, retorna apenas `display_name` e `email`.
        5. Se o usuário não estiver cadastrado em `user_profile`, tenta obter `display_name` do Supabase Auth.

     Args:
        identifier (str): `auth_user_id` ou `email` do usuário.
        by_email (bool): Se `True`, faz a busca pelo e-mail. Se `False`, usa `auth_user_id`.
        full_profile (bool): Se `True`, retorna todos os campos do usuário. Se `False`, retorna apenas `display_name` e `email`.

     Returns:
        dict: Dados do usuário.
            - Se `full_profile=True`: Retorna todos os campos do usuário.
            - Se `full_profile=False`: Retorna apenas `auth_user_id`, `display_name` e `email`.
    """
    # Garante que o cache seja separado por usuário.
    cache_key = f"user_info_{identifier}_{full_profile}"
    
    @st.cache_data
    def fetch_user_info(identifier, by_email, full_profile):
        """Busca os dados no banco de dados do Supabase."""
        
        # Se identifier for None, retorna None imediatamente (evita consultas desnecessárias).
        if not identifier:
            return None

        # Define os campos que serão retornados dependendo da necessidade
        select_fields = "*" if full_profile else "auth_user_id, display_name, email"

        # Define a query base
        query = supabase_client.from_("user_profile").select(select_fields)

        # Aplica o filtro adequado (busca por email ou ID)
        if by_email:
            response = query.eq("email", identifier).execute()
        else:
            response = query.eq("auth_user_id", identifier).execute()

        # Se encontrou dados, retorna o resultado correto
        if response and hasattr(response, "data") and response.data:
            return response.data[0]  # Retorna o primeiro resultado encontrado

        # Se o usuário não estiver na tabela `user_profile`, buscamos nos metadados do Supabase Auth
        user_response = supabase_client.auth.get_user()
        if user_response and user_response.user:
            user_metadata = user_response.user.user_metadata if user_response.user.user_metadata else {}
            return {
                "auth_user_id": identifier,
                "display_name": user_metadata.get("display_name", "Usuário"),
                "email": user_response.user.email
            }

        # Se ainda assim não encontrou, retorna valores padrões
        return {"auth_user_id": None, "display_name": "Usuário Desconhecido", "email": "Email não disponível"}

    # Executa a função cacheada para garantir cache individual por usuário
    return fetch_user_info(identifier, by_email, full_profile)