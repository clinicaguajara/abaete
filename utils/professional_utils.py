import streamlit as st
import uuid
from auth import supabase_client, sign_out
from patient_link import create_patient_invitation 
from utils.date_utils import format_date


# 💾 Função para cachear o estado da área profissional.
@st.cache_data
def get_professional_data(auth_user_id):
    
    # Busca os dados do usuário no banco de dados <professional>
    response = supabase_client.from_("professional") \
        .select("auth_user_id, area_habilitada") \
        .eq("auth_user_id", auth_user_id) \
        .execute()

    # Se houver algum registro...
    if response and hasattr(response, "data") and response.data:
        return response.data[0]  # Retorna um booleano.
    return None  # Se não, retorna o conjunto vazio.


# 🩺 Função para verificar se a área do profissional está habilitada.
def is_professional_enabled(auth_user_id):

    # Verifica, sem gastar requisições ao banco de dados, se a área está ativa ou não.
    professional_data = get_professional_data(auth_user_id)

    # Se houver algum registro...
    if professional_data:
        return professional_data.get("area_habilitada", False)  # Retorna um booleano.
    return False  # Se não, retorna uma resposta negativa.


# ⚒️ Função para habilitar a área do profissional.
def enable_professional_area(auth_user_id, email, display_name):
    try:
        # 🔍 Verifica se o usuário já existe na tabela "professional"
        professional_data = get_professional_data(auth_user_id)

        if professional_data is not None:
            # Se o usuário já existe, apenas atualiza "area_habilitada"
            update_response = supabase_client.from_("professional") \
                .update({"area_habilitada": True}) \
                .eq("auth_user_id", auth_user_id) \
                .execute()

            if "error" in update_response and update_response["error"]:
                st.error(f"Erro ao atualizar: {update_response['error']['message']}")
                print("Erro ao atualizar:", update_response["error"])
                return False, f"Erro ao atualizar: {update_response['error']['message']}"

        else:
            # 🆕 Se o usuário NÃO existir, cria um novo registro
            insert_response = supabase_client.from_("professional") \
                .insert({
                    "auth_user_id": auth_user_id,
                    "email": email,
                    "display_name": display_name,
                    "area_habilitada": True
                }) \
                .execute()

            if "error" in insert_response and insert_response["error"]:
                st.error(f"Erro ao criar registro: {insert_response['error']['message']}")
                print("Erro ao criar registro:", insert_response["error"])
                return False, f"Erro ao criar registro: {insert_response['error']['message']}"

        # 🧹 **LIMPA O CACHE PARA FORÇAR A ATUALIZAÇÃO**
        get_professional_data.clear()
        is_professional_enabled.clear()

        # ✅ Atualização bem-sucedida -> Força o refresh da UI
        st.session_state["refresh"] = True
        st.rerun()
        return True, None  

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        print("Erro inesperado:", e)
        return False, f"Erro inesperado: {str(e)}"


