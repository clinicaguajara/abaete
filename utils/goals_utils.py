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
def get_patient_link_id(patient_id):
    """Recupera o vínculo do paciente com um profissional."""
    response = supabase_client.from_("professional_patient_link") \
        .select("id") \
        .eq("patient_id", patient_id) \
        .eq("status", "aceito") \
        .execute()

    if hasattr(response, "error") and response.error:
        return None, f"Erro ao buscar vínculo: {response.error.message}"

    if response.data:
        return response.data[0]["id"], None  # Retorna o link_id

    return None, None  # Nenhum vínculo encontrado

