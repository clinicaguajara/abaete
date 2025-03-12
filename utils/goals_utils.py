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
    
    

@st.cache_data(ttl=10)
def get_linked_patients(professional_id):
    """Retorna uma lista de pacientes vinculados a um profissional."""
    try:
        # Buscar os vínculos aceitos entre o profissional e pacientes
        response = supabase_client.from_("professional_patient_link") \
            .select("patient_id, status") \
            .eq("professional_id", professional_id) \
            .eq("status", "accepted") \
            .execute()  # 🔹 Agora está corretamente alinhado

        if hasattr(response, "error") and response.error:
            return [], f"Erro ao buscar pacientes vinculados: {response.error.message}"

        if not response.data:
            return [], "Nenhum vínculo encontrado."

        # Obter IDs de pacientes vinculados
        patient_ids = [item["patient_id"] for item in response.data]

        # Buscar os dados dos pacientes vinculados
        patients = []
        for patient_id in patient_ids:
            patient_info = get_user_info(patient_id, by_email=False, full_profile=False)  # 🔹 Forçando busca por ID
            if patient_info and patient_info.get("auth_user_id"):
                patients.append({
                    "id": patient_id,
                    "name": f"{patient_info['display_name']} ({patient_info['email']})"
                })
            else:
                st.warning(f"⚠️ Paciente com ID {patient_id} não encontrado no banco!")  # Log para debug

        return patients, None

    except Exception as e:  # 🔹 Certifique-se de que está na mesma indentação do `try`
        return [], f"Erro inesperado: {str(e)}"
    

@st.cache_data(ttl=10)
def get_patient_goals(patient_id):
    """Busca as metas designadas para o paciente."""
    try:
        # 🔗 Buscar o vínculo do paciente com um profissional
        link_response = supabase_client.from_("professional_patient_link") \
            .select("id") \
            .eq("patient_id", patient_id) \
            .eq("status", "accepted") \
            .execute()

        if hasattr(link_response, "error") and link_response.error:
            return [], f"Erro ao buscar vínculo: {link_response.error.message}"

        if not link_response.data:
            return [], "Nenhum vínculo ativo encontrado."

        link_id = link_response.data[0]["id"]

        # 📋 Buscar metas associadas ao link_id
        goals_response = supabase_client.from_("goals") \
            .select("goal, timeframe, created_at") \
            .eq("link_id", link_id) \
            .order("created_at", desc=True) \
            .execute()

        if hasattr(goals_response, "error") and goals_response.error:
            return [], f"Erro ao buscar metas: {goals_response.error.message}"

        if not goals_response.data:
            return [], "Nenhuma meta encontrada."

        return goals_response.data, None

    except Exception as e:
        return [], f"Erro inesperado: {str(e)}"



# 📌 Nova função para encapsular a lógica de adicionar metas
def render_add_goal_section(user):
    """
    Renderiza a seção de adição de metas para um paciente vinculado.

    Fluxo:
        1. Obtém a lista de pacientes vinculados ao profissional autenticado.
        2. Se não houver pacientes vinculados, exibe uma mensagem e retorna.
        3. Caso existam pacientes, exibe um selectbox para escolher um paciente.
        4. Permite ao profissional inserir uma meta e selecionar um prazo válido.
        5. Envia os dados para o banco de dados ao clicar no botão "Salvar Meta".

    Args:
        user (dict): Dicionário contendo os dados do usuário autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        goals_utils.py → get_linked_patients()
        goals_utils.py → add_goal_to_patient()
    """

    st.markdown("### 🎯 Adicionar Meta para Paciente")

    # 🔍 Buscar pacientes vinculados ao profissional
    patients, error_msg = get_linked_patients(user["id"])

    if error_msg:
        st.error(error_msg)
        return

    if not patients:
        st.warning("⚠️ Nenhum paciente vinculado encontrado.")
        return

    # Criar lista de nomes para exibição no selectbox
    patient_options = {p["name"]: p["id"] for p in patients}
    
    # Seleção do paciente vinculado
    selected_patient_name = st.selectbox("Selecione o paciente:", list(patient_options.keys()), key="select_patient")

    # Obtém o `patient_id` correspondente ao nome selecionado
    selected_patient_id = patient_options[selected_patient_name]

    # Campo para a meta
    goal_text = st.text_area("Descrição da meta:", key="goal_text")

    # ✅ Lista de prazos válidos com base na restrição do banco de dados
    valid_timeframes = {
        "Curto prazo (até 1 mês)": "curto",
        "Médio prazo (1 a 6 meses)": "medio",
        "Longo prazo (acima de 6 meses)": "longo"
    }

    # Selectbox com os nomes amigáveis
    selected_timeframe = st.selectbox("Selecione o prazo para a meta:", list(valid_timeframes.keys()), key="goal_timeframe")

    # Converte para o formato aceito pelo banco de dados
    timeframe = valid_timeframes[selected_timeframe]

    # 🔘 Botão para salvar a meta
    if st.button("Salvar Meta", key="save_goal", use_container_width=True):
        if selected_patient_id and goal_text and timeframe:
            success, msg = add_goal_to_patient(user["id"], selected_patient_id, goal_text, timeframe)
            if success:
                st.success("✅ Meta adicionada com sucesso!")
            else:
                st.error(f"Erro: {msg}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de salvar.")



def render_patient_goals(user_id):
    """
    Renderiza as metas atribuídas ao paciente.

    Fluxo:
        1. Obtém as metas do paciente a partir do banco de dados.
        2. Se não houver metas, exibe uma mensagem informando.
        3. Se houver metas, exibe cada uma dentro de um `st.expander()`.
        4. Mostra detalhes como prazo e data de criação.

    Args:
        user_id (str): ID do paciente autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        goals_utils.py → get_patient_goals()
    """

    st.subheader("🎯 Minhas Metas")

    # 🔍 Buscar as metas do paciente
    goals, error_msg = get_patient_goals(user_id)

    if error_msg:
        st.error(error_msg)
    elif not goals:
        st.info("⚠️ Nenhuma meta foi designada para você ainda.")
    else:
        for goal in goals:
            with st.expander(f"📝 {goal['goal']}"):
                st.markdown(f"📅 **Prazo:** {goal['timeframe']}")
                st.markdown(f"🕒 **Adicionada em:** {goal['created_at'].split('T')[0]}")  # Exibe apenas a data (YYYY-MM-DD)


