
# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import httpx
import logging

from services.backend import supabase
from gotrue.errors import AuthRetryableError
from frameworks.sm import StateMachine


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Cria ou recupera uma instância do objeto logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# 🔐 FUNÇÃO PARA LOGIN ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def auth_sign_in(email: str, password: str):
    """
    <docstrings> Realiza login com email e senha.

    Args:
        email (str): Email do usuário.
        password (str): Senha do usuário.

    Calls:
        supabase.auth.sign_in_with_password(): Método do objeto AuthClient para autenticar usuário | instanciado por supabase.auth.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        logger.exception(): Método do objeto Logger para registrar erros e stacktrace automático | instanciado por logger.


    Returns:
        user (obj) | None: Objeto User autenticado, ou None como fallback.
    
    """
    
    # Tenta realizar a ação principal...
    try:

        # Loga tentativa de login com o email informado.
        logger.debug(f"AUTH → Tentando login de {email}")

        # Executa a autenticação via Supabase.
        response = supabase.auth.sign_in_with_password({
            "email": email,      
            "password": password 
        })

        # Retorna o objeto do usuário autenticado.
        return response.user
    
    # Na exceção...
    except Exception as e:

        # Loga o erro completo com traceback.
        logger.exception(f"AUTH → Erro ao tentar login: {e}")

        # Fallback de execução.
        return None                                           


# 🔓 FUNÇÃO PARA RECUPERAR A SENHA ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def auth_reset_password(email: str) -> bool:
    """
    <docstrings> Dispara email de redefinição de senha.

    Args:
        email (str): Endereço para envio do link de redefinição.

    Calls:
        supabase.auth.reset_password_email(): Método do objeto AuthClient para enviar link de redefinição | instanciado por supabase.auth.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        logger.exception(): Método do objeto Logger para registrar erros e stacktrace automático | instanciado por logger.

    Returns:
        bool: True se o email for enviado com sucesso, e False como fallback.
    
    """
    
    # Tenta realizar a ação principal...
    try:

        #  Loga a solicitação de redefinição.
        logger.debug(f"AUTH → Solicitando redefinição de senha para {email}")
        
        # Dispara o email de redefinição via Supabase.
        supabase.auth.reset_password_email(email)
        
        # Retorna True se o email foi enviado corretamente.
        return True
    
    # Na exceção...
    except Exception as e:
        
        # Loga o erro completo com traceback.
        logger.exception(f"AUTH → Erro ao enviar email de redefinição: {e}") 
        
        # Fallback de execução.
        return False                                                         


# 📋 FUNÇÃO PARA CADASTRO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def auth_sign_up(email: str, password: str, user_metadata: dict = {}):
    """
    <docstrings> Cadastra novo usuário com metadados opcionais.

    Args:
        email (str): Email do novo usuário.
        password (str): Senha do usuário.
        user_metadata (dict, optional): Dados adicionais como nome, etc.

    Calls:
        supabase.auth.sign_up(): Método do objeto AuthClient para registrar novo usuário | instanciado por supabase.auth.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        logger.exception(): Método do objeto Logger para registrar erros e stacktrace automático | instanciado por logger.

    Returns:
        user (obj) | "pending" | None:
            - Objeto do usuário criado.
            - "pending" se o Supabase respondeu com erro de timeout mas o email de verificação foi enviado.
            - None como fallback.

    """
    
    # Tenta executar a operação principal...
    try:

        logger.debug(f"AUTH → Tentando cadastro de {email}")

        # Força timeout maior apenas para esta requisição
        with httpx.Client(timeout=20.0) as client:
            supabase.auth._http_client = client # Monkey patch temporário

            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": user_metadata}
            })

        return response.user

    # Na exceção do tipo timeout...
    except AuthRetryableError as e:
        logger.warning(f"AUTH → Timeout no retorno, mas provavelmente criado: {e}")
        return "pending"

    # Em outras exceções...
    except Exception as e:
        logger.exception(f"AUTH → Erro ao tentar cadastrar {email}: {e}")
        return None
    

# 🚪 FUNÇÃO PARA LOGOUT ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def auth_sign_out(auth_machine: StateMachine) -> bool:
    """
    <docstrings> Finaliza a sessão do usuário logado.

    Calls:
        supabase.auth.sign_out(): Método do objeto AuthClient para encerrar sessão atual | instanciado por supabase.auth.
        logger.debug(): Método do objeto Logger para registrar mensagens de depuração | instanciado por logger.
        logger.exception(): Método do objeto Logger para registrar erros e stacktrace automático | instanciado por logger.

    Returns:
        bool: True se logout realizado, False como fallback de execução.

    """
    
    # Tenta realizar a ação principal...
    try:
        
        # Loga a solicitação de logout.
        logger.debug("AUTH → Logout solicitado")
        
        # Encerra sessão ativa no Supabase
        supabase.auth.sign_out()
        
        # Reinicia a máquina de estados.
        auth_machine.reset()

        # Retorna True se logout ocorreu sem erros.
        return True
    
    # Na exceção...
    except Exception as e:

        # Loga o erro completo com traceback.
        logger.exception(f"AUTH → Erro no logout: {e}")

        # Fallback de execução.
        return False
