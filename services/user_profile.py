
# 📦 IMPORTAÇÕES NECESSÁRIAS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging

from services.backend import upsert_record, fetch_records
from frameworks.sm    import StateMachine


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# 🔍 FUNÇÃO PARA CARREGAR O PERFIL DO USUÁRIO NA MÁQUINA DE ESTADOS ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def load_user_profile(user_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega o perfil do usuário e salva como variável auxiliar na máquina de estados.

    Args:
        user_id (str): UUID do usuário.
        sm (StateMachine): Instância da máquina de estados.

    Calls:
        fetch_records(): Busca o perfil do usuário na tabela | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        sm.set_variable(): Método da máquina de estado para armazenar dados locais | instanciado por StateMachine.

    Returns:
        None.

    """

    # Loga a tentativa de carregamento do perfil.
    logger.debug(f"🔍 USER_PROFILE → Carregando perfil de {user_id}")

    # Executa a busca por um único perfil vinculado ao auth_user_id.
    profile = fetch_records(
        "user_profile",
        filters={"auth_user_id": user_id},
        single=True
    )

    # Loga o resultado da busca para depuração.
    if profile:
        logger.debug(f"USER_PROFILE → Perfil encontrado: {profile}")
    else:
        logger.debug(f"USER_PROFILE → Nenhum perfil encontrado para {user_id}")

    # Armazena o resultado (ou None) como variável auxiliar na máquina de estados.
    auth_machine.set_variable("user_profile", profile or None)


# 💾 FUNÇÃO PARA SALVAR O PERFIL DO USUÁRIO ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def save_user_profile(auth_machine: StateMachine, data: dict) -> bool:
    """
    <docstrings> Insere ou atualiza os dados do perfil do usuário na tabela `user_profile`.

    Args:
        auth_machine (StateMachine): Máquina de estado contendo informações do usuário autenticado.
        data (dict): Campos adicionais do perfil a serem salvos ou atualizados.

    Calls:
        auth_machine.get_variable(): Recupera valores persistidos | instanciado por StateMachine.
        upsert_record(): Upsert de dados no Supabase | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.

    Returns:
        bool: True se sucesso, False como fallback.

    """

    # Recupera variáveis persistidas da máquina de estado.
    user_id = auth_machine.get_variable("user_id")
    email = auth_machine.get_variable("user_email")
    display_name = auth_machine.get_variable("user_display_name")

    # Prepara o payload com os dados obrigatórios e adicionais.
    payload = {
        "auth_user_id": user_id,
        "email": email,
        "display_name": display_name,
        **data
    }

    # Loga a tentativa de salvar os dados.
    logger.debug(f"💾 USER_PROFILE → Tentando salvar perfil para {user_id}: {data}")

    # Executa o upsert no Supabase.
    result = upsert_record(
        table_name="user_profile",
        payload=payload,
        on_conflict="auth_user_id",
        returning=True
    )

    # Loga o resultado para depuração...
    logger.debug(f"USER_PROFILE → Resultado da operação: {result}")

    # Retorna True se houve retorno ou False como fallback.
    return bool(result)


