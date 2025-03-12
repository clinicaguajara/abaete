import streamlit as st
from datetime import date
from auth import supabase_client
from utils.user_utils import get_user_info
from utils.date_utils import format_date


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
            .select("id, link_id, goal, timeframe, created_at") \
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
    Renderiza as metas atribuídas ao paciente, permitindo que ele registre o progresso diário 
    (apenas para metas de curto prazo).

    Fluxo:
        1. Obtém as metas do paciente a partir do banco de dados.
        2. Agrupa as metas por prazo (curto, médio e longo).
        3. Para cada meta, se for de curto prazo, exibe um checkbox dentro do expander 
           para marcar se a meta foi cumprida no dia.
        4. Atualiza o banco de dados com a informação ao clicar.
        5. Para metas de médio e longo prazo, exibe uma mensagem informativa dentro do expander.

    Args:
        user_id (str): ID do paciente autenticado.

    Returns:
        None (apenas renderiza a interface).

    Calls:
        goals_utils.py → get_patient_goals()
        goals_utils.py → update_goal_progress()
        date_utils.py → format_date()
        Supabase → Tabela 'goal_progress'
    """

    st.header("🎯 Minhas Metas")

    # 🔍 Buscar as metas do paciente
    goals, error_msg = get_patient_goals(user_id)
    if error_msg:
        st.error(error_msg)
        return
    if not goals:
        st.info("⚠️ Nenhuma meta foi designada para você ainda.")
        return

    # Agrupar as metas por prazo
    grouped_goals = {"curto": [], "medio": [], "longo": []}
    for goal in goals:
        if goal["timeframe"] in grouped_goals:
            grouped_goals[goal["timeframe"]].append(goal)

    prazo_labels = {
        "curto": "Metas de Curto Prazo (até 1 mês)",
        "medio": "Metas de Médio Prazo (1 a 6 meses)",
        "longo": "Metas de Longo Prazo (acima de 6 meses)"
    }

    # Percorre cada grupo de metas
    for prazo, metas in grouped_goals.items():
        if metas:
            st.markdown(f"### {prazo_labels[prazo]}")
            for goal in metas:
                dia, mes, ano = format_date(goal['created_at'])
                data_formatada = f"{dia:02d}/{mes:02d}/{ano}" if dia else "Data inválida"

                # Coloca tudo dentro de um expander para exibir a meta e seus detalhes
                with st.expander(f"📝 {goal['goal']}"):
                    st.markdown(f"🕒 **Adicionada em:** {data_formatada}")
                    
                    # Se for meta de curto prazo, exibe o checkbox dentro do expander
                    if prazo == "curto":
                        today = date.today().isoformat()
                        progress_response = supabase_client.from_("goal_progress") \
                            .select("completed") \
                            .eq("goal_id", goal["id"]) \
                            .eq("date", today) \
                            .execute()
                        completed_today = False
                        if progress_response.data:
                            completed_today = progress_response.data[0]["completed"]
                        
                        checked = st.checkbox(
                            "Marcar como cumprida hoje",
                            value=completed_today,
                            key=f"goal_{goal['id']}"
                        )
                        if checked != completed_today:
                            success, msg = update_goal_progress(goal["id"], goal["link_id"], checked)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
                    else:
                        st.info("Esta meta não pode ser marcada como cumprida a curto prazo.")





def update_goal_progress(goal_id, link_id, completed):
    """
    Atualiza ou insere o progresso da meta para o paciente no dia atual.

    Fluxo:
        1. Verifica se já existe um registro para essa meta (`goal_id`) no dia atual.
        2. Se existir, atualiza o campo `completed` (marcando ou desmarcando a meta).
        3. Se não existir, insere um novo registro no banco de dados.
        4. Garante que apenas um registro seja feito por dia por meta.

    Args:
        goal_id (str): ID da meta.
        link_id (str): ID do vínculo paciente-profissional.
        completed (bool): Status da meta (True para cumprida, False para não cumprida).

    Returns:
        bool, str: Sucesso da operação e mensagem de erro/sucesso.

    Calls:
        Supabase → `goal_progress`
    """

    today = date.today().isoformat()  # Obtém a data atual no formato YYYY-MM-DD

    try:
        # 🔍 Verifica se já existe um registro para essa meta no dia atual
        response = supabase_client.from_("goal_progress") \
            .select("id") \
            .eq("goal_id", goal_id) \
            .eq("date", today) \
            .execute()

        if hasattr(response, "error") and response.error:
            return False, f"Erro ao verificar progresso: {response.error.message}"

        if response.data:  # Se já existir um registro, faz um update
            progress_id = response.data[0]["id"]
            update_response = supabase_client.from_("goal_progress") \
                .update({"completed": completed}) \
                .eq("id", progress_id) \
                .execute()

            if hasattr(update_response, "error") and update_response.error:
                return False, f"Erro ao atualizar progresso: {update_response.error.message}"
        else:  # Se não existir, cria um novo registro
            insert_response = supabase_client.from_("goal_progress") \
                .insert({"goal_id": goal_id, "link_id": link_id, "date": today, "completed": completed}) \
                .execute()

            if hasattr(insert_response, "error") and insert_response.error:
                return False, f"Erro ao registrar progresso: {insert_response.error.message}"

        return True, "Progresso atualizado com sucesso!"

    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"