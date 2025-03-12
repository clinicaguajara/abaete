import streamlit as st
from datetime import date
from auth import supabase_client
from utils.user_utils import get_user_info
from utils.date_utils import format_date


# 📜 Função para listar os pacientes que estejam vinculados a um profissional.
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
    

# 💎 Função para adicionar metas.
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


# ⛏️ Função para registrar o progresso de uma meta.
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
    

# 🖨️ Função para buscar as metas designadas para um paciente.
@st.cache_data(ttl=10)
def get_patient_goals(patient_id):
    """Busca as metas designadas para o paciente."""
    try:
        # Buscar o vínculo do paciente com um profissional
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

        # Buscar metas associadas ao link_id
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


# 📦 Função para agrupar metas na dashboard
def group_goals_by_timeframe(goals):
    """
    Agrupa a lista de metas por prazo (curto, medio, longo).

    Fluxo:
        1. Inicializa um dicionário com chaves "curto", "medio" e "longo".
        2. Percorre cada meta na lista.
        3. Se o campo "timeframe" da meta corresponder a uma das chaves, adiciona a meta à lista correspondente.

    Args:
        goals (list): Lista de dicionários com dados das metas.

    Returns:
        dict: Dicionário com as metas agrupadas por prazo.
    """
    grouped = {"curto": [], "medio": [], "longo": []}
    for goal in goals:
        if goal.get("timeframe") in grouped:
            grouped[goal["timeframe"]].append(goal)
    return grouped


# 🖥️ Função para renderizar a seção "Adicionar Meta para Paciente".
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

    # Buscar pacientes vinculados ao profissional
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

    # Lista de prazos válidos com base na restrição do banco de dados
    valid_timeframes = {
        "Curto prazo (até 1 mês)": "curto",
        "Médio prazo (1 a 6 meses)": "medio",
        "Longo prazo (acima de 6 meses)": "longo"
    }

    # Selectbox com os nomes amigáveis
    selected_timeframe = st.selectbox("Selecione o prazo para a meta:", list(valid_timeframes.keys()), key="goal_timeframe")

    # Converte para o formato aceito pelo banco de dados
    timeframe = valid_timeframes[selected_timeframe]

    # Botão para salvar a meta
    if st.button("Salvar Meta", key="save_goal", use_container_width=True):
        if selected_patient_id and goal_text and timeframe:
            success, msg = add_goal_to_patient(user["id"], selected_patient_id, goal_text, timeframe)
            if success:
                st.success("✅ Meta adicionada com sucesso!")
            else:
                st.error(f"Erro: {msg}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de salvar.")


# 🖥️ Função para renderizar o checkbox de uma meta de curto prazo.
def render_goal_checkbox(goal):
    """
    Renderiza o checkbox para uma meta de curto prazo, permitindo marcar o progresso diário.
    
    Fluxo:
        1. Consulta a tabela 'goal_progress' para verificar se a meta já foi marcada hoje.
        2. Se já estiver concluída, exibe um checkbox desabilitado.
        3. Caso contrário, exibe um checkbox interativo.
        4. Se o usuário marcar a meta, chama update_goal_progress() para atualizar o status no banco.
    
    Args:
        goal (dict): Dicionário contendo os dados da meta, com campos "id" e "link_id".
    
    Returns:
        None (apenas atualiza a interface e o banco de dados).
    
    Calls:
        goals_utils.py → update_goal_progress()
    """
    today = date.today().isoformat()
    progress_response = supabase_client.from_("goal_progress") \
        .select("completed") \
        .eq("goal_id", goal["id"]) \
        .eq("date", today) \
        .execute()
    completed_today = False
    if progress_response.data:
        completed_today = progress_response.data[0]["completed"]

    # Se a meta já estiver concluída, exibe o checkbox desabilitado
    if completed_today:
        st.checkbox("Meta concluída hoje", value=True, disabled=True, key=f"goal_{goal['id']}_final")
    else:
        # Exibe o checkbox interativo
        checked = st.checkbox("Marcar como cumprida hoje", value=False, key=f"goal_{goal['id']}")
        if checked:
            success, msg = update_goal_progress(goal["id"], goal["link_id"], True)
            if success:
                st.success(msg)
            else:
                st.error(msg)


# 🖥️ Função para renderizar o expander de metas.
def render_goal_expander(goal, prazo):
    """
    Renderiza o expander para uma meta, exibindo seus detalhes e, se for de curto prazo, o checkbox acima do expander.
    Além disso, se for meta de curto prazo, exibe dentro do expander o gráfico de progresso dos últimos 30 dias.

    Fluxo:
        1. Formata a data de criação da meta com a função format_date().
        2. Se o prazo for "curto":
            a. Chama render_goal_checkbox() para exibir o checkbox fora do expander.
        3. Cria um expander com o título da meta.
        4. Dentro do expander:
            a. Exibe a data formatada.
            b. Se a meta for de curto prazo, chama render_goal_progress_chart() para exibir o gráfico.
            c. Se não for curto, exibe uma mensagem informativa.
    
    Args:
        goal (dict): Dicionário contendo os dados da meta, incluindo 'goal' (descrição) e 'created_at' (data de atribuição).
        prazo (str): Tipo da meta ("curto", "medio" ou "longo").

    Returns:
        None: A função apenas renderiza componentes na interface.
    
    Calls:
        - format_date(): Para formatar a data da meta.
        - render_goal_checkbox(): Para exibir o checkbox (caso a meta seja de curto prazo).
        - render_goal_progress_chart(): Para renderizar o gráfico de progresso (para metas de curto prazo).
        - st.expander(): Para criar a seção expansível com os detalhes da meta.
    """
    dia, mes, ano = format_date(goal['created_at'])
    data_formatada = f"{dia:02d}/{mes:02d}/{ano}" if dia else "Data inválida"
    
    # Se a meta for de curto prazo, renderiza o checkbox fora do expander
    if prazo == "curto":
        render_goal_checkbox(goal)
    
    # Cria o expander para exibir os detalhes da meta
    with st.expander(f"📝 {goal['goal']}"):
        st.markdown(f"🕒 **Adicionada em:** {data_formatada}")
        if prazo == "curto":
            # Exibe o gráfico de progresso dos últimos 30 dias dentro do expander
            render_goal_progress_chart(goal)
        else:
            st.info("Esta meta não pode ser marcada como cumprida a curto prazo.")



# 🖥️ Função para renderizar as metas de um paciente.
def render_patient_goals(user_id):
    """
    Renderiza as metas atribuídas ao paciente, permitindo que ele registre o progresso diário 
    (apenas para metas de curto prazo).

    Fluxo:
        1. Obtém as metas do paciente a partir do banco de dados.
        2. Agrupa as metas por prazo (curto, médio e longo) utilizando group_goals_by_timeframe().
        3. Para cada grupo, exibe um cabeçalho e, para cada meta, chama render_goal_expander() para exibir seus detalhes.
    
    Args:
        user_id (str): ID do paciente autenticado.
    
    Returns:
        None (apenas renderiza a interface).
    
    Calls:
        goals_utils.py → get_patient_goals()
        date_utils.py → format_date()
        Internamente, chama:
            group_goals_by_timeframe()
            render_goal_expander()
    """
    st.header("🎯 Minhas Metas")

    # 1. Buscar as metas do paciente
    goals, error_msg = get_patient_goals(user_id)
    if error_msg:
        st.error(error_msg)
        return
    if not goals:
        st.info("⚠️ Nenhuma meta foi designada para você ainda.")
        return

    # 2. Agrupar as metas por prazo
    grouped_goals = group_goals_by_timeframe(goals)
    prazo_labels = {
        "curto": "Metas de Curto Prazo (até 1 mês)",
        "medio": "Metas de Médio Prazo (1 a 6 meses)",
        "longo": "Metas de Longo Prazo (acima de 6 meses)"
    }
    
    # 3. Exibir cada grupo de metas
    for prazo, metas in grouped_goals.items():
        if metas:
            st.markdown(f"### {prazo_labels[prazo]}")
            for goal in metas:
                render_goal_expander(goal, prazo)


# 🖥️ Função para renderizar o gráfico de metas de curto prazo.
def render_goal_progress_chart(goal):
    """
    Renderiza um gráfico de barras de 30 dias que contabiliza a frequência de True's (metas cumpridas)
    ao longo dos 30 dias, a partir da data em que a meta foi atribuída.

    Fluxo:
        1. Converte a data de criação da meta (goal['created_at']) para um objeto date.
        2. Calcula o intervalo de 30 dias, definindo a data de término como a data de início + 29 dias.
        3. Inicializa um dicionário (progress_dict) com cada dia do intervalo (no formato ISO) como chave e valor 0.
        4. Consulta a tabela "goal_progress" para obter registros cujo goal_id seja o da meta e cuja data esteja dentro do intervalo.
        5. Para cada registro retornado, se o campo "completed" for True, incrementa o contador correspondente à data.
        6. Prepara os dados (lista de datas e contagens) para a plotagem.
        7. Utiliza matplotlib para criar um gráfico de barras com as datas no eixo X e a contagem de True's no eixo Y.
        8. Renderiza o gráfico na interface usando st.pyplot().

    Args:
        goal (dict): Dicionário contendo os dados da meta, devendo incluir:
                     - "id": identificador único da meta.
                     - "created_at": data de atribuição da meta (em formato ISO, por exemplo, "YYYY-MM-DDTHH:MM:SS...").

    Returns:
        None: A função apenas renderiza o gráfico na interface, não retornando nenhum valor explícito.

    Calls:
        - supabase_client.from_("goal_progress").select(...).gte(...).lte(...).execute() para buscar os registros.
        - matplotlib.pyplot para criação e renderização do gráfico.
    """
    # Converter a data de criação para um objeto date (assumindo que o campo seja ISO e a data esteja nos 10 primeiros caracteres)
    start_date = datetime.strptime(goal['created_at'][:10], "%Y-%m-%d").date()
    end_date = start_date + timedelta(days=29)  # 30 dias ao total

    # Inicializa um dicionário para armazenar a contagem de True's para cada dia
    progress_dict = {}
    current_date = start_date
    while current_date <= end_date:
        progress_dict[current_date.isoformat()] = 0
        current_date += timedelta(days=1)

    # Consulta registros de progresso para essa meta no intervalo de datas
    response = supabase_client.from_("goal_progress") \
        .select("date, completed") \
        .eq("goal_id", goal["id"]) \
        .gte("date", start_date.isoformat()) \
        .lte("date", end_date.isoformat()) \
        .execute()

    if response and hasattr(response, "data") and response.data:
        for record in response.data:
            # Considera apenas os registros com 'completed' True
            record_date = record["date"][:10]  # extrai a parte da data (YYYY-MM-DD)
            if record_date in progress_dict and record["completed"]:
                progress_dict[record_date] += 1

    # Prepara os dados para o gráfico
    dates = list(progress_dict.keys())
    counts = list(progress_dict.values())

    # Cria o gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(dates, counts)
    ax.set_xlabel("Data")
    ax.set_ylabel("Quantidade de Conclusões (True)")
    ax.set_title("Progresso da Meta nos Últimos 30 Dias")
    ax.tick_params(axis='x', rotation=45)

    # Renderiza o gráfico na interface do Streamlit
    st.pyplot(fig)
