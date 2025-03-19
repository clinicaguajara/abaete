import streamlit as st
from auth import supabase_client

# ===============================
# Dados Normativos para BIS‑11
# ===============================
# Esses dados são fixos e representam os escores normativos para cada subescala e o total.
percentile_table_bis11 = {
    "Attention": [5, 6, 7, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 13, 13, 14, 16, 18],
    "Cognitive Instability": [3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 10, 12],
    "Motor": [7, 8, 9, 9, 10, 10, 11, 11, 12, 12, 12, 13, 13, 14, 14, 15, 15, 16, 18, 20, 23],
    "Perseverance": [4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 10, 12],
    "Cognitive Complexity": [6, 8, 9, 9, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 18],
    "Self-Control": [6, 8, 9, 10, 10, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 18, 19, 22],
    "Total": [40, 47, 50, 52, 53, 55, 56, 58, 59, 60, 62, 63, 64, 65, 67, 68, 70, 72, 76, 80, 90]
}

percentile_indices_bis11 = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]

# ===============================
# Configuração de Inversão de Itens e Mapeamento
# ===============================
# Itens que devem ser invertidos (números das questões BIS‑11)
itens_para_inverter = [1, 7, 8, 9, 10, 12, 13, 15, 20, 29, 30]

# Mapeamento para converter respostas em valores numéricos
answer_map = {
    "Raramente ou nunca": 1,
    "Às vezes": 2,
    "Frequentemente": 3,
    "Sempre ou quase sempre": 4
}

# Mapeamento das subescalas (1ª ordem) conforme Patton et al. (1995)
subscale_mapping = {
    "Attention": [5, 9, 11, 20, 28],
    "Cognitive Instability": [6, 24, 26],
    "Motor": [2, 3, 4, 17, 19, 22],
    "Perseverance": [16, 21, 23],
    "Cognitive Complexity": [10, 15, 18, 27, 29],
    "Self-Control": [1, 7, 8, 12, 13, 14, 30]
}

# ===============================
# Função para Encontrar Intervalos de Percentis
# ===============================
def find_percentile_interval(score, factor, percentile_table, percentile_indices):
    """
    Retorna um percentil ou um intervalo de percentis para 'score' (BIS-11).
    Ajustado para lidar com repetições de valores e manter consistência nos intervalos.
    """
    normative_scores = percentile_table[factor]

    # Localizar todos os índices em que o score "empata" com a tabela
    matching_indexes = [i for i, val in enumerate(normative_scores) if val == score]

    if matching_indexes:
        # Se houver empates exatos, pegue os valores de percentil para cada índice
        matched_percentiles = [percentile_indices[i] for i in matching_indexes]
        # Se só existe um índice, retorna aquele. Se tem vários, retorna min-max
        if len(matched_percentiles) == 1:
            return f"{matched_percentiles[0]}"
        else:
            return f"{min(matched_percentiles)}-{max(matched_percentiles)}"
    else:
        # Se não há match exato, vamos achar o primeiro valor maior (ou igual) a 'score'
        for i, val in enumerate(normative_scores):
            if score < val:
                # i = índice do primeiro valor maior que 'score'
                if i == 0:
                    # Score abaixo de todos os valores normativos
                    return f"<{percentile_indices[0]}"
                else:
                    # Intervalo entre o percentil do índice anterior e o atual
                    return f"{percentile_indices[i-1]}-{percentile_indices[i]}"

        # Se sai do laço, é porque 'score' é >= que todos os valores normativos
        # Fica acima do maior valor na tabela
        return f">{percentile_indices[-2]}"


# ===============================
# Função de Correção Automatizada para BIS‑11
# ===============================
def automated_correction_bis11(answers, normative_table, percentile_indices):
    """
    Realiza a correção automatizada do BIS‑11 com base nas respostas.
    Inclui a inversão de itens, cálculo de subescalas, total e determinação dos intervalos percentílicos.

    Args:
        answers (dict): Respostas do paciente (ex.: {"question_1": "Às vezes", ...}).
        normative_table (dict): Tabela normativa para o BIS‑11.
        percentile_indices (list): Lista de percentis.

    Returns:
        dict: Relatório com escores e intervalos percentílicos para cada subescala e para o total.
    """
    # Converter respostas e aplicar inversão se necessário
    numeric_answers = {}
    for key, value in answers.items():
        question_num = int(key.split("_")[1])
        base_value = answer_map.get(value, 0)
        if question_num in itens_para_inverter:
            base_value = 5 - base_value
        numeric_answers[question_num] = base_value

    # Calcular escores das subescalas
    scores = {}
    for factor, items in subscale_mapping.items():
        scores[factor] = sum(numeric_answers.get(i, 0) for i in items)
    
    # Calcular o total (soma de todas as 30 questões)
    total_score = sum(numeric_answers.get(i, 0) for i in range(1, 31))
    scores["Total"] = total_score

    # Calcular intervalos percentílicos
    report = {}
    for factor in normative_table.keys():
        if factor in scores:
            score = scores[factor]
            p_interval = find_percentile_interval(score, factor, normative_table, percentile_indices)
            report[factor] = {"score": score, "percentile": p_interval}
    
    return report

# ===============================
# Dicionário de Configuração para Correção
# ===============================
# Esse dicionário associa o nome da escala à sua função de correção e aos dados normativos.
correction_config = {
    "Escala de Impulsividade de Barrat": {
        "normative_table": percentile_table_bis11,
        "percentile_indices": percentile_indices_bis11,
        "correction_function": automated_correction_bis11
    },
    # Outras escalas podem ser adicionadas aqui
}

# ===============================
# Funções de Correção (Integradas ao Módulo)
# ===============================
def get_completed_scales(patient_id):
    """
    Retorna as escalas concluídas (completed=True) para o paciente.
    
    Fluxo:
      1. Busca o link_id do paciente na tabela professional_patient_link (status='accepted').
      2. Consulta a tabela scale_progress com join na tabela scales para trazer scale_name.
      3. Filtra registros com completed=True.
    
    Args:
      patient_id (str): ID do paciente.
    
    Returns:
      tuple: (lista de registros, mensagem de erro ou None)
    """
    try:
        link_resp = supabase_client.from_("professional_patient_link") \
            .select("id") \
            .eq("patient_id", patient_id) \
            .eq("status", "accepted") \
            .execute()
        if not link_resp.data:
            return [], "Nenhum vínculo ativo encontrado."
        link_id = link_resp.data[0]["id"]

        response = supabase_client.from_("scale_progress") \
            .select("id, link_id, completed, answers, date, scales!inner(scale_name)") \
            .eq("link_id", link_id) \
            .eq("completed", True) \
            .order("date", desc=True) \
            .execute()
        if hasattr(response, "error") and response.error:
            return [], f"Erro ao buscar escalas completadas: {response.error.message}"
        if not response.data:
            return [], "Nenhuma escala concluída encontrada."
        return response.data, None
    except Exception as e:
        return [], f"Erro inesperado: {str(e)}"

def render_scale_correction_section(user_id):
    """
    Renderiza a seção de correção de escalas para o paciente, permitindo que ele selecione qual escala corrigir.
    Depois, exibe o relatório de correção de forma mais amigável (em formato tabular).
    """
    st.header("📊 Correção de Escalas")
    completed_scales, err = get_completed_scales(user_id)
    if err:
        st.error(err)
        return
    if not completed_scales:
        st.info("Nenhuma escala respondida encontrada para correção.")
        return

    options = {}
    for record in completed_scales:
        if record.get("scales") and record["scales"].get("scale_name"):
            scale_label = record["scales"]["scale_name"] + f" - {record.get('date', '')}"
        else:
            scale_label = f"Escala (ID: {record['id']})"
        options[scale_label] = record

    selected_option = st.selectbox("Selecione a escala para correção:", list(options.keys()))
    selected_record = options[selected_option]

    if selected_record.get("scales") and selected_record["scales"].get("scale_name"):
        scale_type = selected_record["scales"]["scale_name"]
    else:
        st.error("Não foi possível identificar o tipo da escala para correção.")
        return

    if scale_type not in correction_config:
        st.info("Correção automatizada não disponível para essa escala.")
        return

    config = correction_config[scale_type]
    correction_function = config.get("correction_function")
    normative_table = config.get("normative_table")
    percentile_indices = config.get("percentile_indices")
    
    if not correction_function:
        st.error("Função de correção não definida para essa escala.")
        return

    answers = selected_record.get("answers", {})
    report = correction_function(answers, normative_table, percentile_indices)
    
    st.subheader("Relatório de Correção")

    # Exemplo de conversão do dicionário para uma lista de linhas e exibição em formato tabular
    # Cada chave do dicionário (ex.: "Attention", "Motor", etc.) vira uma linha
    # com as colunas: Fator, Score, Percentil
    table_data = []
    for factor, data in report.items():
        row = {
            "Fator": factor,
            "Pontuação": str(data["score"]),
            "Percentil": str(data["percentile"])
        }
        table_data.append(row)

    # Exibindo como tabela (st.table ou st.dataframe)
    import pandas as pd
    df = pd.DataFrame(table_data)
    st.table(df)  # ou st.dataframe(df)