import streamlit as st
from supabase_config import supabase_client


# 💾 Função para cachear o perfil do usuário e evitar buscas repetitivas.
@st.cache_data
def get_user_info(identifier, by_email=False, full_profile=False):
    """
    Obtém informações de um usuário (paciente ou profissional) do banco de dados.

    Fluxo:
        1. Cria uma função interna para gerar um cache único por usuário.
        2. Se identifier for nulo, retorna None para evitar consultas desnecessárias.
        3. Define os campos que serão retornados dependendo da necessidade:
            3.1 Se full_profile=True, retorna todos os campos.
            3.2 Se full_profile=False, retorna apenas auth_user_id, display_name e email.
        4. Configura a consulta à tabela user_profile:
            4.1 Se `by_email=True`, filtra pelo email.
            4.2 Se `by_email=False`, filtra pelo ID.
        5. Na tabela user_profile, retorna os dados e não consulta o Supabase Auth se eles forem encontrados.
        6. Consulta o Supabase Auth para obter os dados do usuário enquanto ele não for cadastrado em user_profile.
        7. Se os dados do Supabase Auth forem encontrados, retorna um dicionário com auth_user_id, display_name e email.
        8. Se nenhuma informação for encontrada, retorna valores padrão.

    Args:
        identifier (str): auth_user_id ou email do usuário.
        by_email (bool): Se True, faz a busca pelo e-mail. Se False, usa auth_user_id.
        full_profile (bool): Se True, retorna todos os campos do usuário. Se False, retorna apenas display_name e email.

    Returns:
        dict: Dados do usuário.
            - Se full_profile=True: Retorna todos os campos do usuário.
            - Se full_profile=False: Retorna apenas auth_user_id, display_name e email.
    """
    # 1. Cria uma chave única de cache por usuário.
    cache_key = f"user_info_{identifier}_{full_profile}"

    # 🔄 Função interna para buscar os dados no Supabase...
    @st.cache_data
    def fetch_user_info(identifier, by_email, full_profile):

        # 2. Se identifier for nulo...
        if not identifier:
            return None  # Evita consultas desnecessárias.

        # 3. Se full_profile for True...
        if full_profile:
            select_fields = "*" # 3.1 Retorna todos os campos.
        # 3. Caso contrário...
        else:
            select_fields = "auth_user_id, display_name, email" # 3.2 Retorna uma busca parcial.

        # 4. Define a query base na tabela user_profile.
        query = supabase_client.from_("user_profile").select(select_fields)

        # 4. Se by_email for True...
        if by_email:
            response = query.eq("email", identifier).execute() # 4.1 Filtra por email.
        # 4. Caso contrário...
        else: 
            response = query.eq("auth_user_id", identifier).execute() # 4.2 Filtra pelo ID.

        # 5. Se o perfil do usuário existir em user_profile...
        if response and hasattr(response, "data") and response.data:
            return response.data[0] # 5. Retorna esses dados e não consulta o Supabase Auth.

        # 6. Busca os dados do Supabase Auth se o perfil não existir.
        auth_response = supabase_client.auth.get_user()
        
        # 7. Se os dados forem encontrados no Supabase Auth...
        if auth_response and auth_response.user:
            user_metadata = auth_response.user.user_metadata if auth_response.user.user_metadata else {}
            return {
                "auth_user_id": identifier,
                "display_name": user_metadata.get("display_name", "Usuário"),
                "email": auth_response.user.email
            } # 7. Retorna um dicionário com as informações.

        # 8. Se ainda assim nenhum dado foi encontrado, retorna valores padrões.
        return {"auth_user_id": None, "display_name": "Usuário Desconhecido", "email": "Email não disponível"}

    # 1. Executa a função cacheada.
    return fetch_user_info(identifier, by_email, full_profile)
