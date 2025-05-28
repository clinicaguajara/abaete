
# 📦 IMPORTAÇÕES NECESSÁRIAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import streamlit as st

from supabase             import create_client, Client
from utils.logs           import track_db_operation, logger
from postgrest.exceptions import APIError

# 🔑 FUNÇÃO CACHEADA PARA ESTABELECER A CONEXÃO COM O SUPABASE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def _init_supabase() -> Client:
    """
    <docstrings> Inicializa e retorna o Client Supabase usando as credenciais escondidas no secrets.

    Args:
        None.

    Calls:
        create_client(): Função para cria um objeto Client de comunicação. Não pertence a nenhum objeto | definida no SDK do Supabase.
        logger.exception(): Método do objeto Logger para registrar mensagens de erro e stacktrace automático | instanciado por logger.

    Returns:
        Client:
            Instância conectada do Supabase Client.
            Em caso de erro, retorna None como fallback de execução.
            
    """
    
    # Tenta executar a operação principal...
    try:
        
        # Recupera a URL e o token JWT do projeto (anon key).
        url = st.secrets["SUPABASE_URL"]     
        anon_key = st.secrets["SUPABASE_KEY"] 

        # Retorna o client com as credencias do backend dedicado.
        return create_client(url, anon_key)
        
    # Se houver exceções...
    except Exception as e:
        
        # Loga o erro completo com traceback.
        logger.exception(f"Falha ao inicializar o client: {e}") 

        # Fallback de execução.           
        return None                                                        


# 🛡️ INICIALIZAÇÃO DO CLIENT SUPABASE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Instância única do Client disponível para todo o sistema.
supabase: Client = _init_supabase()

# Se a conexão falhar...
if supabase is None:
    st.stop() # ⬅ Interrompe a execução do programa.


# 📤 CRUD DE BUSCAS ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@track_db_operation(
    "📤 FETCH",
    fallback=lambda *args, **kwargs: {}
    if kwargs.get("single", False) else []
)
def fetch_records(
    table_name: str,
    filters: dict | None = None,
    *,
    single: bool = False,
    columns: str = "*"
) -> dict | list[dict]:
    """
    <docstrings> Busca registros em qualquer tabela do Supabase.

    Args:
        table_name (str): Nome da tabela.
        filters (dict | None, optional): Filtros para otimizar a busca. Default = None.
    
    Keyword-only:
        single (bool, optional): Se True, retorna um único registro. Default = False.
        columns (str, optional): Colunas a selecionar. Default = "*".

    Calls:
        supabase.from_(): Seleciona o dataframe| instanciado por supabase.
        .select(): Define as colunas de busca| instanciado por QueryBuilder.
        .eq(): Adiciona filtro por coluna | instanciado por QueryBuilder.
        .single(): Define que o retorno esperado é único | instanciado por QueryBuilder.
        .execute(): Executa a query no servidor | instanciado por QueryBuilder.
    
    Returns:
        dict | list[dict]: Registro único (dict) ou lista de registros. Fallback via decorator.
    
    """
    
    # Garante um dicionário vazio se nenhum filtro for informado.
    filters = filters or {}

    # Inicia a query sobre a tabela informada, selecionando as colunas desejadas.
    query = supabase.from_(table_name).select(columns)
    
    # Para cada par coluna:valor fornecido nos filtros...
    for col, val in filters.items():
        query = query.eq(col, val) # ⬅ Adiciona um critério de igualdade à query.

    # Se apenas um resultado for solicitado...
    if single:
        
        # Tenta executar a operação principal...
        try:
            response = query.single().execute() # ⬅ Adiciona .single() à query e executa.
            return response.data or {}          # ⬅ Retorna o resultado da busca ou dicionário vazio como fallback.
        
        # Na exceção...
        except APIError as e:
            
            # Recebe a mensagem de erro.
            message = getattr(e, "message", "") or str(e)
            
            # Se uma dessas strings estiver contida na mensagem de erro...
            if "JSON object requested" in message or "multiple rows returned" in message:
                logger.debug(f"FETCH → Nenhum registro retornado de '{table_name}' com filtros {filters}") # ⬅ Loga uma mensagem informativa no lugar da exceção.
                return {}                                                                                  # ⬅ Retorna um dicionário vazio como fallback de execução.
            
            # Relança a exceção original, propagando-a para quem chamou a função.
            raise 
    
    # Executa a query.
    response = query.execute()
    
    # Retorna o resultado da busca ou uma lista vazia como fallback (Single = False).
    return response.data or []
  

# 📥 CRUD DE CRIAÇÃO E ATUALIZAÇÃO (UPSERT) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

@track_db_operation(
    "📥 UPSERT",
    fallback=lambda *args, **kwargs: {}
    if kwargs.get("returning", True) else []
)
def upsert_record(
    table_name: str,
    payload: dict,
    *,
    on_conflict: str | None = None,
    returning: bool = True
) -> dict | list[dict]:
    """
    <docstrings> Insere ou atualiza registros em qualquer tabela do Supabase.

    Args:
        table_name (str): Nome da tabela.
        payload (dict): Dados a inserir ou atualizar.
    
    Keyword-only:
        on_conflict (str | None, optional): Coluna para resolução de conflitos. Default = None.
        returning (bool, optional): Se True, retorna dados afetados. Default = True.

    Calls:
        supabase.from_(): Seleciona tabela | instanciado por supabase.
        .upsert(): Prepara comando de inserção ou atualização | instanciado por QueryBuilder.
        .execute(): Executa a query | instanciado por QueryBuilder.
    
    Returns:
        dict | list[dict]: Registro ou lista. Fallback de execução via decorator.

    """

    # Prepara a operação de upsert com os dados e conflito opcional.
    query = supabase.from_(table_name).upsert(payload, on_conflict=on_conflict)

    # Executa a operação no servidor.
    response = query.execute()

    # Garante um valor default se não houver retorno.
    data = response.data or []
    
    # Se não for necessário retornar os dados afetados...
    if not returning:
        return {} # ⬅ Retorna dicionário vazio como fallback.
    
    # Se houver um único item na lista de dados afetados..
    if isinstance(data, list) and len(data) == 1:
        return data[0] # ⬅ Retorna apenas esse item.
    
    # Retorna a lista completa dos dados afetados.
    return data
