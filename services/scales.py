# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────

import logging

from datetime           import date
from services.backend   import fetch_records, upsert_record
from frameworks.sm      import StateMachine


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA CARREGAR ESCALAS ATRIBUÍDAS ────────────────────────────────────────────────────────────────────────────────────

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
        filters={"link_id": link_id, "status": "active"}
    )

    logger.debug(f"SCALES → {len(escalas)} escala(s) carregada(s) para o link {link_id}")

    auth_machine.set_variable("assigned_scales", escalas)
    
    return escalas

# 💾 FUNÇÃO PARA SALVAR UMA ESCALA ATRIBUÍDA ────────────────────────────────────────────────────────────────────────────────────

def save_scale_assignment(data: dict) -> str | bool:
    """
    <docstrings> Salva atribuição de escala, evitando duplicações no mesmo dia.

    Args:
        data (dict): Dados da atribuição da escala.

    Returns:
        str | bool:
            - "created": se foi criada nova atribuição.
            - "duplicate_today": se já existe uma atribuição para o mesmo dia.
            - False: se ocorreu erro.
    """

    try:
        # Verifica se já existe uma atribuição ATIVA da mesma escala para o mesmo vínculo no mesmo dia
        registros = fetch_records(
            table_name="scales",
            filters={
                "available_scale_id": data["available_scale_id"],
                "link_id": data["link_id"]
            }
        )

        hoje = str(date.today())
        for r in registros:
            criado_em = r.get("created_at", "")[:10]  # apenas a parte YYYY-MM-DD
            if criado_em == hoje and r.get("status") == "active":
                logger.warning(f"SCALES → Escala já atribuída hoje ao vínculo {data['link_id']}")
                return "duplicate_today"

        # Se não houver duplicata para hoje, cria novo registro
        resultado = upsert_record(
            table_name="scales",
            payload=data,
            on_conflict="id",
            returning=True
        )
        return "created" if resultado else False

    except Exception as e:
        logger.exception(f"SCALES → Erro ao salvar atribuição: {e}")
        return False


# 💾 FUNÇÃO PARA ATUALIZAR O REGISTO DE UMA ESCALA ────────────────────────────────────────────────────────────────────────────────────

def update_scale_status(scale_id: str, status: str) -> bool:
    """Atualiza o campo `status` na tabela `scales`."""
    return bool(upsert_record(
        table_name="scales",
        payload={"id": scale_id, "status": status},
        on_conflict="id",
        returning=True
    ))


# 📥 FUNÇÃO PARA CARREGAR ESCALAS ATIVAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def load_assigned_scales(
    link_id: str,
    auth_machine: StateMachine
) -> list[dict]:
    """
    <docstrings> Carrega e retorna escalas ativas atribuídas a um vínculo.

    Args:
        link_id (str): UUID do vínculo paciente-profissional.
        auth_machine (StateMachine): Máquina de estados para armazenar resultado.

    Calls:
        fetch_records(): Busca registros na tabela `scales` | definida em services.backend.
        logger.debug(): Log de depuração | instanciado por logger.
        auth_machine.set_variable(): Persiste 'assigned_scales' no session_state | instanciado por StateMachine.

    Returns:
        list[dict]: Lista de escalas com status ‘active’. Vazia em caso de erro.
    """
    
    logger.debug(f"SCALES → Carregando escalas ativas para link {link_id}")
    
    try:
        escalas = load_scales_by_link_id(link_id, auth_machine) or []
        # opcional: reafirma no state, mas já foi feito no load_scales_by_link_id
        auth_machine.set_variable("assigned_scales", escalas)
        return escalas  # retorna lista
    
    except Exception as e:
        
        logger.exception(f"SCALES → Falha ao carregar escalas: {e}") # log de erro
        return []   