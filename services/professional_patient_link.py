
# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging

from services.backend import upsert_record, fetch_records
from frameworks.sm    import StateMachine
from utils.gender import get_professional_title


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🔎 FUNÇÃO PARA CARREGAR TODOS OS VÍNCULOS DE UM PROFISSIONAL ──────────────────────────────────────────────────────────────────────────────────────────────

def load_links_for_professional(professional_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega todos os vínculos de um profissional com pacientes.

    Args:
        professional_id (str): UUID do profissional.
        auth_machine (StateMachine): Máquina de estado onde os dados serão armazenados.

    Calls:
        fetch_records(): Busca registros na tabela de vínculos | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        auth_machine.set_variable(): Armazena os dados recuperados na máquina de estado | instanciado por StateMachine.

    Returns:
        None.

    """

    # Loga a tentativa de busca de vínculos.
    logger.debug(f"LINK → Buscando vínculos do profissional {professional_id}")

    # Realiza a busca dos vínculos existentes na tabela.
    links = fetch_records(
        table_name="professional_patient_link",
        filters={"professional_id": professional_id}
    )

    # Loga o número de vínculos encontrados.
    logger.debug(f"LINK → {len(links)} vínculo(s) encontrado(s)")

    # Salva os vínculos na máquina de estados.
    auth_machine.set_variable("professional_patient_links", links)


# 🔎 FUNÇÃO PARA CARREGAR TODOS OS VÍNCULOS DE UM PACIENTE ─────────────────────────────────────────────────────────────────────────────────────────────────

def load_links_for_patient(patient_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Carrega todos os vínculos do paciente com profissionais cadastrados.

    Args:
        patient_id (str): UUID do paciente.
        auth_machine (StateMachine): Máquina de estado onde os dados serão armazenados.

    Calls:
        fetch_records(): Busca registros na tabela de vínculos | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        auth_machine.set_variable(): Armazena os dados recuperados na máquina de estado | instanciado por StateMachine.

    Returns:
        None.

    """

    # Loga a tentativa de busca dos vínculos do paciente.
    logger.debug(f"LINK → Buscando vínculos do paciente {patient_id}")

    # Realiza a busca na tabela com filtro por patient_id.
    links = fetch_records(
        table_name="professional_patient_link",
        filters={"patient_id": patient_id}
    )

    # Loga o número de vínculos encontrados.
    logger.debug(f"LINK → {len(links)} vínculo(s) encontrado(s) para o paciente")

    # Armazena os vínculos na máquina de estados.
    auth_machine.set_variable("patient_links", links)


# 🔎 FUNÇÃO PARA BUSCAR PERFIL DE PACIENTE POR EMAIL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def fetch_patient_info_by_email(email: str) -> dict | None:
    """
    <docstrings> Busca os dados de perfil de um paciente a partir do seu endereço de e-mail.

    Essa função consulta a tabela `user_profile` no Supabase para localizar um paciente pelo campo `email`.
    Retorna um dicionário com os campos essenciais para criação de vínculo (UUID e nome), ou None caso não encontrado.

    Args:
        email (str): Endereço de e-mail do paciente a ser buscado.

    Calls:
        fetch_records(): Função CRUD para buscas no backend | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        logger.exception(): Método do objeto Logger para registrar falhas e stacktrace | instanciado por logger.

    Returns:
        dict | None:
            - dict contendo `auth_user_id` e `display_name`, caso o paciente exista.
            - None, caso o email não seja localizado ou ocorra erro.
    """

    try:
        # Loga tentativa de busca por email.
        logger.debug(f"PATIENT_LOOKUP → Buscando paciente pelo e-mail: {email}")

        # Executa a busca na tabela de perfis com filtro por email, retornando único registro.
        result = fetch_records(
            table_name="user_profile",
            filters={"email": email},
            single=True
        )

        # Loga o resultado da operação.
        logger.debug(f"PATIENT_LOOKUP → Resultado da busca: {result}")

        # Se algo foi retornado, extrai apenas os dados necessários.
        if result:
            return {
                "auth_user_id": result.get("auth_user_id"),
                "display_name": result.get("display_name")
            }

        # Caso o resultado seja vazio, retorna None explicitamente.
        return None

    except Exception as e:
        # Loga o erro com traceback.
        logger.exception(f"PATIENT_LOOKUP → Erro ao buscar paciente por e-mail: {e}")
        return None


# 💾 FUNÇÃO PARA SALVAR VÍNCULO ENTRE PROFISSIONAL E PACIENTE ──────────────────────────────────────────────────────────────────────────────────────────────

def save_professional_patient_link(auth_machine: StateMachine, data: dict) -> bool:
    """
    <docstrings> Insere ou atualiza o vínculo entre profissional e paciente, incluindo o nome do profissional com título.

    Essa função é utilizada pelo profissional para convidar um paciente.  
    O `professional_name` é gerado dinamicamente com base no gênero e nome, usando a função `get_professional_title()`.

    Args:
        auth_machine (StateMachine): Máquina de estado contendo os dados do profissional autenticado.
        data (dict): Dados do vínculo (ex: patient_id, patient_name, status).

    Calls:
        auth_machine.get_variable(): Recupera dados do profissional autenticado | instanciado por StateMachine.
        get_professional_title(): Gera título personalizado com base no gênero | definida em utils.gender.py.
        upsert_record(): Salva ou atualiza o vínculo no Supabase | definida em services.backend.py.
        logger.debug(): Loga ações de fluxo normal | instanciado por logger.
        logger.exception(): Loga falhas com traceback | instanciado por logger.

    Returns:
        bool: True se o vínculo foi salvo com sucesso, False como fallback.
    """
    try:
        # Recupera dados do profissional autenticado
        professional_id = auth_machine.get_variable("user_id")
        display_name = auth_machine.get_variable("user_display_name", default="Profissional")
        gender = auth_machine.get_variable("user_gender", default="M")

        # Recupera perfis completos da máquina de estado
        professional_profile = {
            "display_name": auth_machine.get_variable("user_display_name", default="Profissional")
        }
        user_profile = {
            "gender": auth_machine.get_variable("user_gender", default="M")
        }

        # Gera título com base no gênero e nome
        professional_name = get_professional_title(professional_profile, user_profile)


        # Prepara payload com ID e nome com título
        payload = {
            "professional_id": professional_id,
            "professional_name": professional_name,
            **data
        }

        # Loga o payload de gravação
        logger.debug(f"LINK → Tentando salvar vínculo: {payload}")

        # Executa o upsert no Supabase
        result = upsert_record(
            table_name="professional_patient_link",
            payload=payload,
            on_conflict="professional_id,patient_id",
            returning=True
        )

        # Loga resultado da operação
        logger.debug(f"LINK → Resultado da operação: {result}")

        # Retorna True se o upsert foi bem-sucedido
        return bool(result)

    except Exception as e:
        logger.exception(f"LINK → Erro ao salvar vínculo: {e}")
        return False


# ✅ FUNÇÃO PARA ACEITAR UM VÍNCULO PENDENTE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def accept_link(link_id: str) -> bool:
    """
    <docstrings> Atualiza o status de um vínculo entre profissional e paciente para "accepted".

    Essa função é chamada quando o paciente clica em "Aceitar" um convite.  
    Ela atualiza o registro na tabela `professional_patient_link`, garantindo persistência via `upsert`.

    Args:
        link_id (str): UUID do vínculo entre profissional e paciente.

    Calls:
        upsert_record(): Função CRUD para inserção/atualização no backend | definida em services.backend.py.
        logger.debug(): Método do objeto Logger para registrar fluxo | instanciado por logger.
        logger.exception(): Método para registrar falhas com traceback | instanciado por logger.

    Returns:
        bool:
            - True se o status foi atualizado com sucesso.
            - False se ocorreu erro durante a operação.
    """

    try:
        # Loga o início da operação
        logger.debug(f"LINK → Aceitando vínculo com ID: {link_id}")

        # Define o payload de atualização
        payload = {
            "id": link_id,
            "status": "accepted"
        }

        # Executa o upsert no Supabase
        result = upsert_record(
            table_name="professional_patient_link",
            payload=payload,
            on_conflict="id",
            returning=True
        )

        # Loga o retorno do Supabase
        logger.debug(f"LINK → Resultado da aceitação: {result}")

        # Retorna sucesso se houve retorno
        return bool(result)

    except Exception as e:
        # Loga o erro com traceback completo
        logger.exception(f"LINK → Erro ao aceitar vínculo: {e}")
        return False
    

# ❌ FUNÇÃO PARA RECUSAR UM VÍNCULO PENDENTE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def reject_link(link_id: str) -> bool:
    """
    <docstrings> Atualiza o status de um vínculo para "rejected" quando o paciente recusa o convite.

    Essa função preserva o vínculo no banco de dados, marcando-o como recusado ao invés de deletá-lo.
    Ideal para manter histórico de interações entre profissionais e pacientes.

    Args:
        link_id (str): UUID do vínculo entre profissional e paciente.

    Calls:
        upsert_record(): Atualiza o status no backend | definida em services.backend.py.
        logger.debug(): Registra fluxo de execução | instanciado por logger.
        logger.exception(): Captura erros com traceback completo | instanciado por logger.

    Returns:
        bool:
            - True se o status foi atualizado com sucesso.
            - False em caso de erro.
    """
    try:
        # Loga a intenção da operação
        logger.debug(f"LINK → Recusando vínculo com ID: {link_id}")

        # Define o payload de atualização
        payload = {
            "id": link_id,
            "status": "rejected"
        }

        # Executa o upsert para marcar como rejeitado
        result = upsert_record(
            table_name="professional_patient_link",
            payload=payload,
            on_conflict="id",
            returning=True
        )

        logger.debug(f"LINK → Resultado da recusa: {result}")
        return bool(result)

    except Exception as e:
        logger.exception(f"LINK → Erro ao rejeitar vínculo: {e}")
        return False