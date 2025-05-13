

# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging

from services.backend import upsert_record, fetch_records
from frameworks.sm    import StateMachine


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA CARREGAR METAS ASSOCIADAS A UM LINK ───────────────────────────────────────────────────────────────────────────────────────────────────────

def load_goals_by_link_id(link_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega todas as metas (goals) associadas a um vínculo entre paciente e profissional.

    Args:
        link_id (str): UUID da tabela de vínculo `professional_patient_link`.
        auth_machine (StateMachine): Máquina de estado onde os dados serão armazenados.

    Calls:
        fetch_records(): Busca metas na tabela `goals` | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        auth_machine.set_variable(): Armazena metas na máquina de estado | instanciado por StateMachine.

    Returns:
        None
    """

    # Loga a tentativa de carregamento de metas.
    logger.debug(f"GOALS → Buscando metas vinculadas ao link_id {link_id}")

    # Executa a busca na tabela goals.
    goals = fetch_records(
        table_name="goals",
        filters={"link_id": link_id}
    )

    # Loga a quantidade de metas encontradas.
    logger.debug(f"GOALS → {len(goals)} meta(s) carregada(s) para o link {link_id}")

    # Armazena os dados na máquina de estado.
    auth_machine.set_variable("goals", goals)


# 💾 FUNÇÃO PARA SALVAR UMA NOVA META ──────────────────────────────────────────────────────────────────────────────

def save_goal(data: dict) -> bool:
    """
    <docstrings> Insere ou atualiza uma meta associada a um vínculo (link_id).

    Args:
        data (dict): Dados da meta (goal, timeframe, effort_type, priority_level, link_id).

    Calls:
        upsert_record(): Insere ou atualiza na tabela `goals` | definida em services.backend.py.
        logger.debug(): Loga tentativa de operação | instanciado por logger.

    Returns:
        bool: True se salvo com sucesso, False como fallback.
    """
    
    logger.debug(f"GOALS → Tentando salvar meta: {data}")
    result = upsert_record(
        table_name="goals",
        payload=data,
        on_conflict="id",
        returning=True
    )
    logger.debug(f"GOALS → Resultado do upsert: {result}")
    return bool(result)
