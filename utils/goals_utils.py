import streamlit as st
from auth import supabase_client
from utils.user_utils import get_user_info


def add_goal_to_patient(professional_id, patient_email, goal, timeframe):
    """Adiciona uma meta para um paciente vinculado a um profissional."""
    try:
        # 🔍 Buscar ID do paciente pelo email
        patient_info = get_user_info(patient_email, by_email=True, full_profile=True)
        if not patient_info or not patient_info.get("auth_user_id"):
            return False, "Paciente não encontrado."

        patient_id = patient_info["auth_user_id"]

        # 🔗 Buscar link_id do vínculo entre profissional e paciente
        link_response = supabase_client.from_("professional_patient_link") \
            .select("id") \
            .eq("professional_id", professional_id) \
            .eq("patient_id", patient_id) \
            .eq("status", "accepted") \
            .execute()

        if not link_response.data:
            return False, "Nenhum vínculo ativo encontrado com este paciente."

        link_id = link_response.data[0]["id"]

        # 📝 Criar a meta
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
    
    
@st.cache_data(ttl=60)
def get_linked_patients(professional_id):
    """Retorna uma lista de pacientes vinculados a um profissional."""
    try:
        st.write(f"🔍 Buscando pacientes vinculados para o profissional: {professional_id}")  # Log para debug

        # 🔍 Buscar vínculos ativos entre o profissional e pacientes
        response = supabase_client.from_("professional_patient_link") \
            .select("patient_id, status") \
            .eq("professional_id", professional_id) \
            .execute()

        st.write("📊 Resposta do Supabase:", response)  # Log para debug

        if hasattr(response, "error") and response.error:
            return [], f"Erro ao buscar pacientes vinculados: {response.error.message}"

        if not response.data:
            return [], "Nenhum vínculo encontrado."

        # Verificar os status reais retornados
        valid_links = [item for item in response.data if item["status"].lower() == "accepted"]  # <-- pode precisar ajustar esse filtro
        st.write("✅ Vínculos filtrados:", valid_links)  # Log para ver se o filtro está correto

        if not valid_links:
            return [], "Nenhum paciente vinculado com status 'aceito'."

        # 🔍 Obter os nomes e emails dos pacientes vinculados
        patients = []
        for item in valid_links:
            patient_id = item["patient_id"]
            patient_info = get_user_info(patient_id, full_profile=False)  # Obtém apenas nome e email
            if patient_info:
                patients.append({
                    "id": patient_id,
                    "name": f"{patient_info['display_name']} ({patient_info['email']})"
                })

        st.write("📋 Pacientes vinculados formatados:", patients)  # Ver se pacientes foram carregados corretamente

        return patients, None

    except Exception as e:
        st.write("❌ Erro inesperado:", str(e))  # Log para debug
        return [], f"Erro inesperado: {str(e)}"

