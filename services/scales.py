# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────

import logging
from services.backend import fetch_records, upsert_record
from frameworks.sm import StateMachine

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA CARREGAR ESCALAS ATRIBUÍDAS ─────────────────────────────────────────────

def load_scales_by_link_id(link_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega todas as escalas atribuídas a um vínculo profissional-paciente.

    Args:
        link_id (str): UUID do vínculo.
        auth_machine (StateMachine): Máquina de estados onde os dados serão armazenados.

    Calls:
        fetch_records(): Busca escalas atribuídas | definida em services.backend.py.
        logger.debug(): Log de progresso | instanciado por logger.
        auth_machine.set_variable(): Armazena escalas carregadas | instanciado por StateMachine.

    Returns:
        None
    """
    logger.debug(f"SCALES → Buscando escalas atribuídas ao link {link_id}")

    escalas = fetch_records(
        table_name="scales",
        filters={"link_id": link_id}
    )

    logger.debug(f"SCALES → {len(escalas)} escala(s) carregada(s) para o link {link_id}")

    auth_machine.set_variable("assigned_scales", escalas)


# 💾 FUNÇÃO PARA SALVAR UMA ESCALA ATRIBUÍDA ─────────────────────────────────────────────

# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────

import logging
from services.backend import fetch_records, upsert_record

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA CARREGAR ESCALAS ATRIBUÍDAS ─────────────────────────────────────────────

def load_scales_by_link_id(link_id: str, auth_machine) -> None:
    """
    <docstrings> Carrega todas as escalas atribuídas a um vínculo profissional-paciente.

    Args:
        link_id (str): UUID do vínculo.
        auth_machine (StateMachine): Máquina de estados onde os dados serão armazenados.

    Returns:
        None
    """
    logger.debug(f"SCALES → Buscando escalas atribuídas ao link {link_id}")

    escalas = fetch_records(
        table_name="scales",
        filters={"link_id": link_id}
    )

    logger.debug(f"SCALES → {len(escalas)} escala(s) carregada(s) para o link {link_id}")

    auth_machine.set_variable("assigned_scales", escalas)


# 💾 FUNÇÃO PARA SALVAR UMA ESCALA ATRIBUÍDA ─────────────────────────────────────────────

def save_scale_assignment(data: dict) -> bool:
    """
    <docstrings> Atribui uma escala a um vínculo apenas se ainda não houver essa combinação registrada.

    Args:
        data (dict): Dados da atribuição (scale_id, scale_name, link_id).

    Returns:
        bool: True se a atribuição foi salva com sucesso. False se já existia ou ocorreu erro.
    """
    try:
        scale_id = data["scale_id"]
        link_id = data["link_id"]

        # Verifica se já existe essa atribuição
        existente = fetch_records(
            table_name="scales",
            filters={"scale_id": scale_id, "link_id": link_id},
            single=True
        )

        if existente:
            logger.warning(f"SCALES → Escala {scale_id} já atribuída ao vínculo {link_id}.")
            return False

        logger.debug(f"SCALES → Tentando salvar atribuição de escala: {data}")

        result = upsert_record(
            table_name="scales",
            payload=data,
            returning=True  # ← sem on_conflict, pois id será novo
        )

        logger.debug(f"SCALES → Resultado do upsert: {result}")
        return bool(result)

    except Exception as e:
        logger.exception(f"SCALES → Erro ao salvar atribuição: {e}")
        return False
