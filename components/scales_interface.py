# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from frameworks.sm import StateMachine
from utils.gender import render_header_by_role


# 👨‍💻 LOGGER ESPECÍFICO PARA A PÁGINA DE AVALIAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 📋 FUNÇÃO PRINCIPAL PARA A PÁGINA DE AVALIAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_scales_interface(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a interface da página de avaliações (escalas), com variações para profissional e paciente.

    Args:
        auth_machine (StateMachine): Máquina de estado com os dados do usuário autenticado.

    Calls:
        render_header_by_role(): Renderiza cabeçalho personalizado | definida em utils/gender.py.
        is_professional_user(): Verifica se o usuário é profissional | definida localmente.
        _render_professional_scales(): Interface exclusiva para profissionais | definida em 3_Avaliação.py.
        _render_patient_scales(): Interface exclusiva para pacientes | definida em 3_Avaliação.py.

    Returns:
        Tuple[None, str | None]:
            - None: Em caso de sucesso.
            - str | None: Mensagem de erro em caso de falha.
    """
    try:
        logger.info("SCALES → Acessando página de avaliações.")

        st.title("📋 Avaliações")

        render_header_by_role(auth_machine)

        if is_professional_user(auth_machine):
            _render_professional_scales()
        else:
            _render_patient_scales()

        return None, None

    except Exception as e:
        return None, str(e)


# 👤 FUNÇÃO PARA VERIFICAR PERFIL PROFISSIONAL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def is_professional_user(auth_machine: StateMachine) -> bool:
    """
    <docstrings> Verifica se o usuário atual é um profissional ativo.

    Args:
        auth_machine (StateMachine): Instância da máquina de estado atual.

    Returns:
        bool: True se profissional ativo, False caso contrário.
    """
    profile = auth_machine.get_variable("professional_profile")
    return bool(profile.get("professional_area")) if profile else False


# 📑 TABS PARA PROFISSIONAIS ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_scales() -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a seção de escalas para profissionais.

    Returns:
        Tuple[None, str | None]: Resultado da operação.
    """
    try:
        tabs = st.tabs(["Aplicar Escalas", "Resultados dos Pacientes"])

        with tabs[0]:
            st.write("🧠 Aplicar escalas disponíveis para pacientes vinculados.")
        with tabs[1]:
            st.write("📑 Resultados obtidos nas avaliações anteriores.")

        return None, None

    except Exception as e:
        return None, str(e)


# 📑 TABS PARA PACIENTES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_scales() -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a seção de escalas para pacientes.

    Returns:
        Tuple[None, str | None]: Resultado da operação.
    """
    try:
        tabs = st.tabs(["Responder Escalas", "Histórico"])

        with tabs[0]:
            st.write("📝 Avaliações disponíveis para você responder.")
        with tabs[1]:
            st.write("📚 Histórico de avaliações que você completou.")

        return None, None

    except Exception as e:
        return None, str(e)
