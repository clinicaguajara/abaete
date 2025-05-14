# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date
from frameworks.sm import StateMachine


# 👨‍💻 LOGGER DO MÓDULO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 📈 GRÁFICO DE PROGRESSO ACUMULADO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_goal_progress_chart(goal_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza o gráfico de progresso acumulado de uma meta específica ao longo do tempo.

    Args:
        goal_id (str): UUID da meta.
        auth_machine (StateMachine): Máquina de estado contendo os dados carregados.

    Calls:
        auth_machine.get_variable(): Acessa registros de progresso por meta | instanciado por StateMachine.
        pd.DataFrame(): Conversão tabular de dados | instanciado por pandas.
        st.plotly_chart(): Exibe gráfico na interface | definida em streamlit.

    Returns:
        None.
    """
    progress = auth_machine.get_variable(f"goal_progress__{goal_id}", default=[])
    if not progress:
        return

    df = pd.DataFrame(progress)
    df = df[df["completed"] == True]
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates(subset="date")
    df = df.sort_values("date")
    df["Contagem"] = 1
    df = df.groupby("date")["Contagem"].sum().cumsum().reset_index()
    df = df.rename(columns={"date": "Data", "Contagem": "Total acumulado"})

    hoje = pd.to_datetime(date.today())
    if df["Data"].max() < hoje:
        ultimo_valor = df["Total acumulado"].iloc[-1]
        df.loc[len(df.index)] = [hoje, ultimo_valor]

    fig = px.line(
        df,
        x="Data",
        y="Total acumulado",
        labels={"Data": "Linha do tempo", "Total acumulado": "Esforço"}
    )
    fig.update_traces(line_color="#1E3D59")

    # 📏 Altura ajustada para manter proporção 3:6 (ex: 300px de altura)
    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)


# ⏳ ESTIMATIVA DE CONCLUSÃO DA META ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def estimate_completion_time(goal_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Estima em quantos dias o usuário concluirá uma meta de curto prazo, com base em 30 esforços.

    Args:
        goal_id (str): UUID da meta.
        auth_machine (StateMachine): Máquina de estado contendo os dados carregados.

    Calls:
        auth_machine.get_variable(): Acessa progresso salvo | instanciado por StateMachine.
        pd.DataFrame(): Manipulação de dados | instanciado por pandas.
        st.write(): Apresentação de dados na interface | definida em streamlit.

    Returns:
        None.
    """
    progress = auth_machine.get_variable(f"goal_progress__{goal_id}", default=[])
    if not progress:
        st.info("Nenhum progresso registrado ainda.")
        return

    df = pd.DataFrame(progress)
    df = df[df["completed"] == True]
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates(subset="date")
    df = df.sort_values("date")

    total_esforcos = df.shape[0]
    data_inicio = df["date"].min()
    hoje = pd.to_datetime(date.today())
    total_dias = (hoje - data_inicio).days or 1
    media_dias_por_esforco = total_dias / total_esforcos
    faltam = max(30 - total_esforcos, 0)
    estimativa_final = round(media_dias_por_esforco * faltam)

    st.write("**Projeção de conclusão da meta**")
    st.write(f"Atualmente, você completou 🏆 **{total_esforcos} de 30 esforços**. "
             f"Passaram-se **{total_dias} dias** desde o início da meta. "
             f"Você se dedicou ativamente uma vez a cada **{media_dias_por_esforco:.2f} dias**. "
             f"Se mantiver esse ritmo, você atingirá seu objetivo em aproximadamente **{estimativa_final} dias**.")


# ⏱️ PROGRESSO ACUMULADO EM MINUTOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def estimate_accumulated_effort(goal_id: str, effort_target: int, auth_machine: StateMachine) -> None:
    """
    <docstrings> Exibe o esforço total acumulado em minutos e compara com a meta de dedicação.

    Args:
        goal_id (str): UUID da meta.
        effort_target (int): Total esperado em minutos.
        auth_machine (StateMachine): Máquina de estado com dados já carregados.

    Calls:
        auth_machine.get_variable(): Acessa progresso salvo | instanciado por StateMachine.
        pd.DataFrame(): Manipulação de dados | instanciado por pandas.
        st.markdown(), st.write(): Apresentação na interface | definidas em streamlit.

    Returns:
        None.
    """
    progress = auth_machine.get_variable(f"goal_progress__{goal_id}", default=[])
    if not progress:
        st.info("Nenhum progresso registrado ainda.")
        return

    df = pd.DataFrame(progress)
    df = df[df["completed"] == True]

    total_minutes = df["duration_minutes"].sum()
    percentage = (total_minutes / effort_target) * 100 if effort_target else 0
    remaining_minutes = max(effort_target - total_minutes, 0)

    st.markdown("---")
    st.markdown("**Progresso de Dedicação Acumulada**")
    st.write(f"Você acumulou **{total_minutes} minutos** de esforço.")
    st.write(f"Meta definida: **{effort_target} minutos**.")
    st.write(f"Progresso: **{percentage:.1f}%** completo.")
    st.write(f"Faltam aproximadamente **{remaining_minutes} minutos** para atingir o objetivo.")
