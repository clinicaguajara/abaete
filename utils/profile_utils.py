import streamlit as st
from datetime import date
from auth import supabase_client
from utils.user_utils import get_user_info


def create_user_profile(auth_user_id, email, genero, data_nascimento):
    """Cria um perfil do usuário no Supabase e limpa o cache após a inserção."""
    try:
        # Obtém o display_name diretamente do perfil, se já existir no Supabase
        display_name = get_user_info(auth_user_id).get("display_name", "Usuário")

        # Mapeamento de gênero
        genero_map = {"Masculino": "M", "Feminino": "F", "Não-binário": "N"}
        genero_abreviado = genero_map.get(genero, "N")

        # Converte data de nascimento para o formato esperado
        data_nascimento_str = data_nascimento.strftime("%Y-%m-%d") if data_nascimento else None

        # Dados para inserção no banco
        data = {
            "auth_user_id": auth_user_id,
            "email": email,
            "genero": genero_abreviado,
            "data_nascimento": data_nascimento_str,
            "display_name": display_name
        }

        response = supabase_client.from_("user_profile").insert(data).execute()
        if hasattr(response, "error") and response.error:
            return False, response.error.message

        # Limpa o cache para garantir que o sistema reconheça o novo perfil
        st.cache_data.clear()

        return True, None

    except Exception as e:
        return False, str(e)


def render_onboarding_questionnaire(user_id, user_email):
    """Renderiza o questionário inicial do usuário."""
    st.title("Queremos saber um pouco mais sobre você!")
    st.markdown("<hr style='border:1px solid gray; margin: 30px 0;'>", unsafe_allow_html=True)

    genero = st.selectbox("Qual seu gênero?", ["Masculino", "Feminino", "Não-binário"])

    max_date = date.today()
    min_date = date(1900, 1, 1)


    data_nascimento = st.date_input(
        "Quando você nasceu?",
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY"
    )

    # Criando botão estilizado
    st.markdown(
        """
        <style>
            div.stButton > button {
                width: 100%;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("Salvar", key="profile-save", use_container_width=True):
        # Verifica se o usuário está autenticado antes de salvar
        if not user_id:
            st.error("Erro: usuário não autenticado. Faça login novamente.")
            return

        success, msg = create_user_profile(user_id, user_email, genero, data_nascimento)
        if success:
            st.session_state["refresh"] = True
            st.rerun()
        else:
            st.error(f"Ocorreu um erro: {msg}")