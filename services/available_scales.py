# 📦 IMPORTAÇÕES ─────────────────────────────────────────────────────────────────────────────

import logging
from services.backend import fetch_records
from frameworks.sm import StateMachine

logger = logging.getLogger(__name__)


# 🔍 FUNÇÃO PARA CARREGAR ESCALAS BASE NA MÁQUINA DE ESTADO ─────────────────────────────────

def load_available_scales(auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega todas as escalas disponíveis do sistema e armazena na máquina de estados.

    Args:
        auth_machine (StateMachine): Instância da máquina onde o dado será persistido.

    Calls:
        fetch_records(): Busca dados da tabela `available_scales` | definida em services.backend.py.
        auth_machine.set_variable(): Armazena as escalas como variável local | instanciado por StateMachine.
        logger.debug(): Registra progresso da operação | instanciado por logger.

    Returns:
        None.

    """
    
    # Tenta executar a ação principal...
    try:
        logger.debug("AVAILABLE_SCALES → Carregando escalas base do sistema")
        escalas = fetch_records("available_scales")
        logger.debug(f"AVAILABLE_SCALES → {len(escalas)} escalas base carregadas")
        auth_machine.set_variable("available_scales", escalas)

    except Exception as e:
        logger.exception(f"AVAILABLE_SCALES → Erro ao carregar escalas disponíveis: {e}")
        auth_machine.set_variable("available_scales", [])  # fallback vazio
