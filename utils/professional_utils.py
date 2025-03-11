import streamlit as st
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


# ⚒️ Função para habilitar área do profissional.
def enable_professional_area(auth_user_id, email, display_name):
    try:
        data = {
            "auth_user_id": auth_user_id,
            "email": email,
            "display_name": display_name,
            "area_habilitada": True
        }

        response = supabase_client.from_("professional") \
            .upsert(data) \
            .execute()

        if hasattr(response, "error") and response.error:
            st.error(f"Erro ao criar/atualizar registro: {response.error.message}")
            print("Erro:", response.error)
            return False, f"Erro ao criar/atualizar registro: {response.error.message}"

        return True, None  # Operação bem-sucedida

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        print("Erro inesperado:", e)
        return False, f"Erro inesperado: {str(e)}"

    
# 🔑 Função para renderizar o bloqueio da área profissional.
def render_professional_enable_section(user):
    """Renderiza a seção de ativação da área profissional."""
    
    # Se já estiver processando, exibe uma mensagem e não permite nova ação.
    if st.session_state.get("processing", False):
        st.info("Processando... Aguarde um momento.")
        st.session_state["processing"] = False  # Libera o fluxo para o próximo run.
        st.session_state["refresh"] = True # Força a reinicialização da interface.
        return

    if st.button("🔐 Habilitar área do profissional", key="professional"):
        st.session_state["show_prof_input"] = True  # Ativa o campo de senha.

    # Se o campo de senha foi ativado...
    if st.session_state.get("show_prof_input", False):
        prof_key = st.text_input("Digite a senha do profissional:", key="prof_key_input")

        if prof_key:  # Se o usuário digitou algo...
            if prof_key == "AUTOMATIZEJA":  # Se a chave estiver correta...
                st.session_state["processing"] = True  # Bloqueia novas submissões.
                success, msg = enable_professional_area(user["id"], user["email"], user["display_name"])
                
                if success:
                    get_professional_data.clear()  # Limpa o cache.
                    st.session_state["refresh"] = True  # Força atualização.
                    st.rerun()
                else:
                    st.session_state["processing"] = False  # Libera o bloqueio em caso de erro.
                    st.error(msg)
            else:
                st.error("❌ Chave incorreta!")


