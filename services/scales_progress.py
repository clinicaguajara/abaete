# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────

import logging
from datetime import date

from services.backend import fetch_records, upsert_record
from frameworks.sm import StateMachine

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA CARREGAR PROGRESSO DE ESCALAS ──────────────────────────────────────────

def load_scale_progress(link_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega os registros de progresso das escalas para um vínculo.

    Agrupa por `scale_id` e armazena na máquina de estados com prefixo.

    Args:
        link_id (str): UUID do vínculo.
        auth_machine (StateMachine): Instância onde os dados serão armazenados.

    Calls:
        fetch_records(): Busca registros da tabela `scale_progress` | definida em services.backend.py.
        auth_machine.set_variable(): Armazena dados agrupados | instanciado por StateMachine.
        logger.debug(): Logs do processo | instanciado por logger.

    Returns:
        None
    """
    try:
        logger.debug(f"SCALE_PROGRESS → Buscando progresso para o link {link_id}")

        progresso = fetch_records("scale_progress", filters={"link_id": link_id})

        agrupado = {}
        for entry in progresso:
            sid = entry.get("scale_id")
            if sid:
                agrupado.setdefault(sid, []).append(entry)

        for sid, registros in agrupado.items():
            auth_machine.set_variable(f"scale_progress__{sid}", registros)

        logger.debug(f"SCALE_PROGRESS → Progresso agrupado para {len(agrupado)} escalas")

    except Exception as e:
        logger.exception(f"SCALE_PROGRESS → Erro ao buscar progresso: {e}")


# 💾 FUNÇÃO PARA SALVAR PROGRESSO DE ESCALA ─────────────────────────────────────────────

def save_scale_progress(data: dict) -> bool:
    """
    <docstrings> Salva ou atualiza um registro de progresso de escala.

    Args:
        data (dict): Dados do progresso (scale_id, link_id, date, mood_rating, etc.)

    Calls:
        upsert_record(): Insere ou atualiza progresso em `scale_progress` | definida em services.backend.py.
        logger.debug(): Loga operações | instanciado por logger.

    Returns:
        bool: True se salvo com sucesso, False como fallback.
    """
    logger.debug(f"SCALE_PROGRESS → Tentando salvar progresso: {data}")

    result = upsert_record(
        table_name="scale_progress",
        payload=data,
        on_conflict="scale_id,date,link_id",
        returning=True
    )

    logger.debug(f"SCALE_PROGRESS → Resultado do upsert: {result}")
    return bool(result)
