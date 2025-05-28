
# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

from streamlit.delta_generator      import DeltaGenerator
from frameworks.sm                  import StateMachine
from utils.session                  import VerifyStates, LoadStates
from services.professional_profile  import load_professional_profile
from services.user_profile          import load_user_profile
from services.links                 import load_links_by_role
from components.onboarding          import render_onboarding_if_needed

# 🚧 FUNÇÃO PARA VERIFICAR SE O USUÁRIO É UM PROFISSIONAL ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def is_professional_user(auth_machine: StateMachine) -> bool:
    """
    <docstrings> Verifica se o usuário atual é um profissional ativo, validando a presença e o status no perfil profissional.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do usuário autenticado.

    Returns:
        bool: True se o usuário tem perfil profissional e está com status ativo.
              False se o perfil estiver ausente ou inativo.
    """

    # Cria ou recupera a máquina de papéis de usuário (default: load).
    role_machine = StateMachine("role_machine", VerifyStates.VERIFY.value, enable_logging=True)

    # Tenta recuperar o perfil profissional da máquina de autenticação.
    professional_profile = auth_machine.get_variable("professional_profile")

    # Se não houver perfil profissional carregado na máquina de autenticação...
    if not professional_profile:
        role_machine.init_once(  
            load_professional_profile,              # ⬅ Carrega o perfil profissional na máquina de autenticação.
            auth_machine,                           # ⬅ Alvo do carregamento (*args).
            done_state= VerifyStates.VERIFIED.value # ⬅ Desliga a flag na máquina de papéis de usuário.
        )

    # Valida status explicitamente como booleano.
    return professional_profile.get("professional_status") is True if professional_profile else False


# 🧭 FUNÇÃO PARA CARREGAR CONTEXTO COMPLETO DA SESSÃO ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def load_session_context(auth_machine: StateMachine, page: DeltaGenerator) -> str:
    """
    <docstrings> Carrega os dados completos da sessão: user_profile, professional_profile e vínculos (se paciente).
    Define o papel ('professional' ou 'patient') e salva tudo na máquina de estados.

    Args:
        auth_machine (StateMachine): Máquina de estado contendo user_id.

    Calls:
        auth_machine.get_variable(): Recupera user_id | instanciado por StateMachine.
        fetch_records(): CRUD para buscar dados no Supabase | definida em services.backend.py.
        auth_machine.set_variable(): Salva variáveis na máquina | instanciado por StateMachine.
        logger.debug(): Registro de logs para acompanhamento | instanciado por logger.

    Returns:
        str: Papel do usuário ('professional' ou 'patient').
    """

    # Cria a máquina de perfis de usuário (default: load).
    profile_machine = StateMachine("profile_machine", LoadStates.LOAD.value, enable_logging=True)

    # Recupera o UUID do usuário da máquina de autenticação.
    user_id = auth_machine.get_variable("user_id")
 
    # Se houver UUID autenticado...
    if user_id:
        profile_machine.init_once(  
            load_user_profile,                    # ⬅ Carrega o perfil do usuário na máquina de autenticação.
            user_id,                              # ⬅ UUID do usuário autenticado (*args).
            auth_machine,                         # ⬅ Máquina de autenticação (*kwargs).
            done_state = LoadStates.LOADED.value  # ⬅ Desliga a flag da máquina de perfis de usuário para impedir reexecução.
        )                           

    # 📋 ONBOARDING QUESTIONNAIRE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
    
    # Recupera o perfil do usuário.
    profile = auth_machine.get_variable("user_profile")

    # Atia o container da página.
    with page.container():
        render_onboarding_if_needed(auth_machine, profile) # ⬅ Desenha o formulário de boas vindas, se necessário.
    

    # 👨‍⚕️ PERFIL PROFISSIONAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
    
    # Cria ou recupera a máquina de papéis de usuário (default: load).
    role_machine = StateMachine("role_machine", VerifyStates.VERIFY.value, enable_logging=True)

    # Tenta recuperar o perfil profissional da máquina de autenticação.
    professional_profile = auth_machine.get_variable("professional_profile")

    # Se não houver perfil profissional carregado na máquina de autenticação...
    if not professional_profile:
        role_machine.init_once(  
            load_professional_profile,              # ⬅ Carrega o perfil profissional na máquina de autenticação.
            auth_machine,                           # ⬅ Alvo do carregamento (**kwargs).
            done_state= VerifyStates.VERIFIED.value # ⬅ Desliga a flag da máquina de perfis de usuário para impedir reexecução.
        )

    if not professional_profile:
        role = "patient_id"
    else:
        role = "professional_id"


    # 🔗 VÍNCULOS ENTE PACIENTES E PROFISSIONAIS ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Cria a máquina de vínculos (default: load).
    link_machine = StateMachine("link_machine", LoadStates.LOAD.value, enable_logging=True)

    # Recupera o UUID do paciente na máquina de autenticação.
    uuid = auth_machine.get_variable("user_id")

    # Se houver UUID autenticado...
    if uuid:
        link_machine.init_once(  
            load_links_by_role,                 # ⬅ Carrega os vínculos do usuário na máquina de autenticação.
            uuid,                               # ⬅ UUID do usuário autenticado (*args).
            role,                               # ⬅ Filtragem conforme papel do usuário (*args).
            auth_machine,                       # ⬅ Máquina de autenticação (**kwargs).
            done_state= LoadStates.LOADED.value # ⬅ Desliga a flag da máquina de vínculos para impedir reexecução.
        )  
