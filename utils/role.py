
# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

from frameworks.sm import StateMachine
from services.professional_profile import load_professional_profile


# ⚙️ FUNÇÃO PARA VERIFICAR SE O USUÁRIO É UM PROFISSIONAL ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def is_professional_user(auth_machine: StateMachine) -> bool:
    """
    <docstrings> Verifica se o usuário atual é um profissional ativo, validando a presença e o status no perfil profissional.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do usuário autenticado.

    Returns:
        bool: True se o usuário tem perfil profissional e está com status ativo.
              False se o perfil estiver ausente ou inativo.
    """

    # Tenta recuperar do estado
    profile = auth_machine.get_variable("professional_profile")

    # Se ainda não tiver carregado, tenta carregar do Supabase
    if not profile:
        load_professional_profile(auth_machine)
        profile = auth_machine.get_variable("professional_profile")

    # Valida status explicitamente como booleano True
    return profile.get("professional_status") is True if profile else False