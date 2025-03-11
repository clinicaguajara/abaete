import streamlit as st
from auth import supabase_client

def add_goal(link_id, goal, timeframe):
    """Adiciona uma nova meta ao banco de dados."""
    try:
        data = {
            "link_id": link_id,
            "goal": goal,
            "timeframe": timeframe
        }
        response = supabase_client.from_("goals").insert(data).execute()
        
        if hasattr(response, "error") and response.error:
            return False, f"Erro ao adicionar meta: {response.error.message}"

        return True, "Meta adicionada com sucesso!"
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"

@st.cache_data(ttl=10)
def get_goals(link_id):
    """Recupera todas as metas de um paciente vinculadas a um profissional."""
    response = supabase_client.from_("goals") \
        .select("*") \
        .eq("link_id", link_id) \
        .order("created_at", desc=True) \
        .execute()

    if hasattr(response, "error") and response.error:
        return [], f"Erro ao buscar metas: {response.error.message}"

    return response.data, None
