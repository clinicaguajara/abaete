

# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging

from services.backend import upsert_record, fetch_records
from frameworks.sm    import StateMachine


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA O PROGRESSO ASSOCIADO A UMA META ───────────────────────────────────────────────────────────────────────────────────────────────────────

def load_goal_progress(goal_id: str = None, link_id: str = None, auth_machine: StateMachine = None) -> None:
    """
    <docstrings> Carrega os registros de progresso associados a uma meta específica ou a um vínculo (link_id).

    Args:
        goal_id (str, optional): UUID da meta. Se fornecido, busca progresso apenas dessa meta.
        link_id (str, optional): UUID do vínculo. Se fornecido, busca progresso de todas as metas vinculadas.
        auth_machine (StateMachine): Máquina de estado onde os dados serão armazenados.

    Calls:
        fetch_records(): Busca progresso na tabela `goal_progress` | definida em services.backend.py.
        auth_machine.set_variable(): Armazena os dados no escopo do StateMachine.

    Returns:
        None.
    """

    if auth_machine is None:
        logger.warning("GOAL_PROGRESS → auth_machine não fornecida.")
        return

    try:
        if link_id:
            logger.debug(f"GOAL_PROGRESS → Buscando progresso de todas as metas do link {link_id}")
            progresso = fetch_records("goal_progress", filters={"link_id": link_id})

            # Organiza por goal_id
            agrupado = {}
            for entry in progresso:
                gid = entry.get("goal_id")
                if gid:
                    agrupado.setdefault(gid, []).append(entry)

            # Armazena cada grupo de progresso por meta
            for gid, registros in agrupado.items():
                auth_machine.set_variable(f"goal_progress__{gid}", registros)

            logger.debug(f"GOAL_PROGRESS → Progresso agrupado por {len(agrupado)} metas")

        elif goal_id:
            logger.debug(f"GOAL_PROGRESS → Buscando progresso da meta {goal_id}")
            progresso = fetch_records("goal_progress", filters={"goal_id": goal_id})
            auth_machine.set_variable(f"goal_progress__{goal_id}", progresso)
            logger.debug(f"GOAL_PROGRESS → {len(progresso)} registro(s) encontrado(s) para {goal_id}")

    except Exception as e:
        logger.exception(f"GOAL_PROGRESS → Erro ao buscar progresso: {e}")


# 💾 FUNÇÃO PARA SALVAR O PROGRESSO DE UMA META ───────────────────────────────────────────────────────────────────────────────────────────────────────

def save_goal_progress(data: dict) -> bool:
    """
    <docstrings> Insere ou atualiza um registro de progresso de uma meta.

    Args:
        data (dict): Dados do progresso da meta (goal_id, link_id, date, completed, etc.).

    Calls:
        upsert_record(): Insere ou atualiza na tabela `goal_progress` | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.

    Returns:
        bool: True se salvo com sucesso, False como fallback.
    """

    # Loga a tentativa de salvar o progresso.
    logger.debug(f"GOAL_PROGRESS → Tentando salvar progresso: {data}")

    # Executa o upsert na tabela goal_progress.
    result = upsert_record(
        table_name="goal_progress",
        payload=data,
        on_conflict="goal_id,date",  # ← evita duplicidade por meta e dia
        returning=True
    )

    # Loga o resultado.
    logger.debug(f"GOAL_PROGRESS → Resultado do upsert: {result}")

    # Retorna True se houve retorno, ou False como fallback.
    return bool(result)
