
# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import sys
import os
import logging
import functools
import time

from pathlib    import Path
from typing     import TypeVar, ParamSpec, Callable, Union


# 💻 FUNÇÃO PARA CONFIGURAR LOGS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def configure_logging() -> None:
    """
    <docstrings> Configura o sistema de logs para a aplicação. Ativa saída em console e, em modo desenvolvimento,
    grava em arquivo local.

    Args:
        None.

    Calls:
        Path.mkdir(): Cria diretório de logs | instanciado por Path.
        logging.StreamHandler: Classe para handler de console | instanciada manualmente.
        logging.FileHandler: Classe para handler de arquivo | instanciada manualmente.
        logging.basicConfig(): Configura sistema de logging | definida em logging.
        os.getenv(): Lê variável de ambiente | definida em os.
        logger.exception(): Registra erros e stacktrace | instanciado por logger.

    Returns:
        None.
    """
    try:
        # Cria pasta 'logs/' no diretório pai, se não existir
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # Handlers básicos: console sempre ativo
        handlers = [
            logging.StreamHandler(sys.stdout),  # ⬅ console
        ]

        # Se estiver em modo de debug local, adiciona gravação em arquivo
        if os.getenv("LOCAL_DEBUG", "false").lower() in ("1", "true", "yes"):
            handlers.append(
                logging.FileHandler(log_dir / "app.log", mode="a", encoding="utf-8")  # ⬅ arquivo
            )

        # Define nível de log: DEBUG se debug local, senão INFO
        level = logging.DEBUG if os.getenv("LOCAL_DEBUG", "false").lower() in ("1", "true", "yes") else logging.INFO

        # Configura o logging global
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=handlers
        )

        # Reduz verbosidade de bibliotecas HTTP
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpcore.http2").setLevel(logging.WARNING)
        logging.getLogger("hpack").setLevel(logging.WARNING)             
        logging.getLogger("hpack.hpack").setLevel(logging.WARNING)
        logging.getLogger("hpack.table").setLevel(logging.WARNING)

    except Exception:
        # Em caso de falha, registra o erro
        logger.exception("Erro ao configurar logging")


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Configura o logging assim que o módulo é importado.
configure_logging()

# Cria ou recupera uma instância do objeto logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# 📒 DECORADOR PARA RASTREAR EXECUÇÕES ENTRE PÁGINAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def log_page_entry(page_name: str):
    """
    <docstrings> Decorador para logar a entrada em uma página do app.

    Args:
        page_name (str): Nome da página (ex: 'Página Inicial').

    Returns:
        Callable: Função decoradora.

    """
    def decorator(func):
        
        # Função interna que intercepta a chamada original que recebe uma função como argumento.
        def wrapper(*args, **kwargs):

            # Registra no log que a página foi acessada
            logger.info(f" 🛤️  Executando {page_name}.py")
            
             # Executa a função original, repassando todos os argumentos.
            return func(*args, **kwargs)
        
        # Retorna a função wrapper para substituir a função original.
        return wrapper
    
    # Retorna o decorado.
    return decorator


# 📒 DECORADOR PARA RASTREAR OPERAÇÕES DE BANCO DE DADOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

P = ParamSpec('P')
R = TypeVar('R')

def track_db_operation(
    op_type: str,
    fallback: Union[Callable[P, R], R] = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    <docstrings> Decorator tipado para rastrear operações de banco de dados (fetch/upsert), incluindo tempo de execução e erros.

    Args:
        op_type (str): Tipo da operação ("FETCH" ou "UPSERT").
        fallback (Callable[P, R] | R, optional): Valor de retorno ou função de fallback em caso de exceção.

    Calls:
        functools.wraps(): Preserva metadata da função decorada | built-in.
        time.perf_counter(): Timestamp de alta resolução para medir duração | instanciada manualmente.
        logger.debug(): Registra mensagens de debug | instanciado por logger.
        logger.exception(): Registra erros e stacktrace | instanciado por logger.

    Returns:
        Callable: Função decoradora que aplica o wrapper tipado.

    """
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            logger.debug(f"{op_type} → Iniciando {func.__name__}() com args={args}, kwargs={kwargs}")
            try:
                result: R = func(*args, **kwargs)
                duration = time.perf_counter() - start
                logger.debug(f"{op_type} → {func.__name__}() retornou {result} (tempo: {duration:.3f}s)")
                return result
            except Exception:
                logger.exception(f"{op_type} → Erro em {func.__name__}()")
                # Retorna o fallback, chamando se for callable
                return fallback(*args, **kwargs) if callable(fallback) else fallback  # type: ignore
        return wrapper  # type: ignore
    return decorator