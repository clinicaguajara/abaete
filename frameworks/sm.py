
# 📦 IMPORTAÇÕES NECESSÁRIAS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import streamlit as st
import logging

from typing import Callable


# 🏗️ CLASSE PARA NAVEGAÇÃO REATIVA EM STREAMLIT ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

class StateMachine:
    """
    <docstrings> Framework para controle de estados baseado em session_state para navegação reativa em Streamlit.

    <docstrings> Essa classe encapsula a manipulação de estados dentro do session_state,
    permitindo controle reativo, inicialização condicional e reinicializações previsíveis em aplicações Streamlit.
    Também oferece um sistema de variáveis auxiliares que persistem manutenção de estados.
    
    """

    # 🛠️ MÉTODO CONSTRUTOR DE CLASSE ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    def __init__(self, key: str, initial_state: str, enable_logging: bool = False):
        """
        <docstrings> Método construtor de classe.

        Args:
            key (str): Nome da chave no session_state onde o estado será armazenado.
            initial_state (str): Valor padrão atribuído à chave ao iniciar a aplicação.
            enable_logging (bool): Se True, ativa mensagens de log no console. Default = False.

        Attributes:
            key (str): Chave usada para armazenar o estado no session_state.
            initial_state (str): Valor inicial definido no construtor.
            enable_logging (bool): Flag para ativar logs de depuração.

        Calls:
            st.session_state.setdefault(): Inicializa a chave no session | instanciado por st.

        """
        self.key = key
        self.initial_state = initial_state
        self.enable_logging = enable_logging

        st.session_state.setdefault(self.key, initial_state)


    # 📐 PROPRIEDADE QUE RETORNA O ESTADO ATUAL DA MÁQUINA DE ESTADOS ────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    @property
    def current(self) -> str:
        """
        <docstrings> Retorna dinamicamente o estado atual da máquina no session_state.

        Returns:
            str: Estado atual associado à chave definida.
            
        """
        
        # Retorna o valor associado à chave definida na sessão.
        return st.session_state[self.key]
    

    # 🕹️ MÉTODO PARA TRANSICIONAR ESTADOS (CUSTOM) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
   
    def to(self, new_state: str, rerun: bool = True) -> None:
        """
        <docstrings> Transiciona explicitamente o estado da máquina para outro valor.

        Args:
            new_state (str): Novo estado a ser atribuído.
            rerun (bool, optional): Se True, força um st.rerun(). Valor padrão é True.

        Calls:
            st.session_state.__setitem__(): Atualiza o estado | instanciado por st.session_state.
            st.rerun(): Reinicia o ciclo do Streamlit se rerun=True | definida em streamlit.runtime.

        Returns:
            None.

        """
        
        # Se "enable_logging" estiver habilitado (True)...
        if self.enable_logging:
            logging.debug(f"[StateMachine/{self.key}] Transição: {self.current} → {new_state}")

        # Transiciona a máquina de estados.
        st.session_state[self.key] = new_state

        # Se "rerun" estiver habilitado (True), reinicia o app.
        if rerun:
            st.rerun()


    # 🎬 MÉTODO PARA REINICIAR ESTADOS (DEFAULT) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
   
    def reset(self, rerun: bool = True) -> None:
        """
        <docstrings> Retorna a máquina ao estado inicial e limpa todas as variáveis auxiliares.

        Args:
            rerun (bool, optional): Se True, reinicia o app. Valor padrão é True.

        Calls:
            st.session_state.pop(): Remove variáveis auxiliares | instanciado por st.session_state.
            self.to(): Método da própria classe para transição de estado.

        Returns:
            None.
        """
        
        # Remove todas as variáveis auxiliares do session_state.
        prefix = f"{self.key}__"
        
        for k in list(st.session_state.keys()):
            if k.startswith(prefix):
                st.session_state.pop(k)

        # Retorna ao estado inicial
        self.to(self.initial_state, rerun=rerun)


    # 🕥 FUNÇÃO PARA EXECUTAR CALLBACK UMA ÚNICA VEZ ────────────────────────────────────────────────────────────────────────────────────────────────────────────

    def init_once(self, callback: Callable, *args, done_state: str = "done", **kwargs) -> None:
        """
        <docstrings> Executa uma função (callback) apenas se a máquina de estados estiver no estado inicial (default).

        Args:
            callback (Callable): Função a ser chamada.
            *args: Argumentos posicionais para o callback.
            done_state (str): Estado a ser definido após execução. Default = "done".
            **kwargs: Argumentos nomeados para o callback.

        Calls:
            callback(): Função do usuário.
            self.to(): Transiciona estado após execução.

        Returns:
            None.

        """

        # Se o estado atual for igual ao estado inicial (default)...
        if self.current == self.initial_state:
            
            # Tenta executar a ação principal...
            try:

                # Se "enable_logging" estiver habilitado (True)...
                if self.enable_logging:
                    logging.debug(f"[StateMachine/{self.key}] Executando callback único.")

                # Executa o callback com os argumentos fornecidos.  
                callback(*args, **kwargs)
                
                # Transiciona a máquina de estados para sinalizar que o callback já foi executado.
                self.to(done_state)
            
            # Caso contrário...
            except Exception as e:
                logging.exception(f"[StateMachine:{self.key}] Erro em callback do init_once: {e}")
                raise

    
    # 🕥 MÉTODO PARA TRANSICIONAR ESTADOS UMA ÚNICA VEZ (DEFAULT > CUSTOM) ────────────────────────────────────────────────────────────────────────────────────────────────────────────

    def set_once(self, value: str, rerun: bool = False) -> None:
        """
        <docstrings> Define o estado apenas se a máquina ainda estiver em default mode.
        Útil para marcar um estado como 'carregado' ou 'ativo', sem sobrescrever estados já definidos anteriormente.

        Args:
            value (str): Novo estado desejado.
            rerun (bool, optional): Se True, força rerun. Valor padrão é False.

        Calls:
            self.to(): Método da própria classe para transição de estado.

        Returns:
            None.

        """
        
        # Se o estado atual for igual ao estado inicial (default)...
        if self.current == self.initial_state:
            self.to(value, rerun=rerun) # ⬅ Transiciona para o novo estado definido.


    # 📥 MÉTODO PARA SALVAR VARIÁVEIS AUXILIARES NO ESTADO ──────────────────────────────────────────────────────────────────────────────────────────────

    def set_variable(self, var_name: str, value) -> None:
        """
        <docstrings> Salva uma variável auxiliar com escopo da máquina no session_state.

        Essa função permite armazenar qualquer tipo de dado relacionado ao estado atual da interface,
        como perfis de usuário, listas temporárias, cache de buscas, entre outros.

        Args:
            var_name (str): Nome curto da variável a ser associada ao escopo da máquina.
            value (any): Valor a ser armazenado (pode ser qualquer tipo de dado).

        Calls:
            st.session_state.__setitem__(): Método do objeto SessionStateProxy para armazenar valores | instanciado por st.session_state.

        Returns:
            None.

        """
        
        # Cria uma chave única no formato: "estado__variavel".
        scoped_key = f"{self.key}__{var_name}"

        # Salva essa chave única na sessão associada a um valor passado como argumento.
        st.session_state[scoped_key] = value

    # 📤 MÉTODO PARA RECUPERAR VARIÁVEIS AUXILIARES DO ESTADO ──────────────────────────────────────────────────────────────────────────────────────────────

    def get_variable(self, var_name: str, default=None):
        """
        <docstrings> Recupera uma variável auxiliar vinculada ao escopo da máquina de estado.

        Essa função acessa variáveis armazenadas previamente com set_variable(), permitindo
        reutilização de dados sem reprocessar ou refazer chamadas externas.

        Args:
            var_name (str): Nome da variável auxiliar.
            default (any, optional): Valor padrão se a variável não estiver presente. Default = None.

        Calls:
            st.session_state.get(): Método do objeto SessionStateProxy para acessar valores | instanciado por st.session_state.

        Returns:
            any:
                Valor armazenado no session_state ou o valor padrão informado.

        """
        
        scoped_key = f"{self.key}__{var_name}"             # ⬅ Usa o mesmo padrão de chave composta.
        return st.session_state.get(scoped_key, default)   # ⬅ Retorna o valor ou o fallback informado.
    

    # 📋 MÉTODO PARA LISTAR VARIÁVEIS DO SESSION_STATE COM PREFIXO ──────────────────────────────────────────────────────────────

    def list_variables_with_prefix(self, startswith: str = "") -> dict:
        """
        <docstrings> Retorna todas as variáveis auxiliares da máquina que começam com determinado prefixo.

        Args:
            startswith (str): Subprefixo da variável (sem o prefixo da máquina). Ex: 'scale_progress__'.

        Returns:
            dict: Mapeamento chave → valor de todas variáveis auxiliares que combinam com o prefixo.

        Example:
            state.list_variables_with_prefix(\"scale_progress__\") →
            {
                \"scale_progress__abc123\": [...],
                \"scale_progress__def456\": [...],
            }
        """
        
        prefix = f"{self.key}__{startswith}"
        scoped_vars = {}

        for key in st.session_state.keys():
            if key.startswith(prefix):
                raw = key[len(self.key) + 2:]  
                scoped_vars[raw] = st.session_state[key]
        return scoped_vars
