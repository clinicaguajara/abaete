
# 📦 IMPORTAÇÕES NECESSÁRIAS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging

from services.backend   import upsert_record, fetch_records
from frameworks.sm      import StateMachine


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🔍 FUNÇÃO PARA CARREGAR PERFIL PROFISSIONAL NA MÁQUINA DE ESTADOS ──────────────────────────────────────────────────────────────────────────────────────────────

def load_professional_profile(auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega o perfil profissional do usuário e armazena como variável auxiliar na máquina de estados.

    Args:
        auth_machine (StateMachine): Instância da máquina de estado contendo o user_id.

    Calls:
        auth_machine.get_variable(): Recupera o UUID do usuário | instanciado por StateMachine.
        fetch_records(): Busca perfil profissional na tabela | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        auth_machine.set_variable(): Armazena perfil encontrado no session_state | instanciado por StateMachine.

    Returns:
        None.
    
    """

    # Recupera o ID do usuário a partir da máquina de estados.
    user_id = auth_machine.get_variable("user_id")

    # Se o ID estiver ausente...
    if user_id is None:
        logger.debug("PROFESSIONAL_PROFILE → user_id ausente na máquina de estados") # ⬅ Loga um aviso para depuração.
        return                                                                       # ⬅ Retorna.

    # Loga a tentativa de carregamento de perfil.
    logger.debug(f"PROFESSIONAL_PROFILE → Carregando perfil profissional de {user_id}")

    # Realiza a busca por um único registro na tabela.
    profile = fetch_records(
        "professional_profile",
        filters={"auth_user_id": user_id},
        single=True
    )

    # Loga se o perfil foi encontrado ou não.
    if profile:
        logger.debug(f"PROFESSIONAL_PROFILE → Perfil encontrado: {profile}")
    else:
        logger.debug(f"PROFESSIONAL_PROFILE → Nenhum perfil encontrado para {user_id}")

    # Armazena o resultado como variável auxiliar na máquina de estados.
    auth_machine.set_variable("professional_profile", profile or None)


# 💾 FUNÇÃO PARA SALVAR DADOS DO PERFIL PROFISSIONAL ────────────────────────────────────────────────────────────────────────────────────────────────────────

def save_professional_profile(auth_machine: StateMachine, data: dict) -> bool:
    """
    <docstrings> Insere ou atualiza os dados do profissional na tabela `professional_profile`.

    Args:
        auth_machine (StateMachine): Máquina de estado contendo informações do usuário autenticado.
        data (dict): Campos adicionais do perfil profissional.

    Calls:
        auth_machine.get_variable(): Recupera variáveis persistidas | instanciado por StateMachine.
        upsert_record(): Upsert de dados no Supabase | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.

    Returns:
        bool: True se sucesso, False como fallback.
    
    """

    # Recupera variáveis obrigatórias da máquina de autenticação.
    user_id = auth_machine.get_variable("user_id")
    email   = auth_machine.get_variable("user_email")

    # Prepara o payload com os dados padrão e adicionais.
    payload = {
        "auth_user_id": user_id,
        "email": email,
        **data
    }

    # Loga a tentativa de gravação no banco.
    logger.debug(f"PROFESSIONAL_PROFILE → Tentando salvar perfil para {user_id}: {data}")

    # Executa o upsert no Supabase.
    result = upsert_record(
        table_name="professional_profile",
        payload=payload,
        on_conflict="auth_user_id",
        returning=True
    )

    # Loga o resultado para depuração.
    logger.debug(f"PROFESSIONAL_PROFILE → Resultado da operação: {result}")

    # Retorna True se houve retorno, ou False como fallback.
    return bool(result)