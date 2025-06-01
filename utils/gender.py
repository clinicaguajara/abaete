# 📦 IMPORTAÇÕES NECESSÁRIAS ─────────────────────────────────────────────────────────────

import logging
import re
import streamlit as st

from frameworks.sm import StateMachine


# 👨‍💻 LOGGER LOCAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# 🧑‍💼 FUNÇÃO PARA RENDERIZAR CABEÇALHO ADAPTADO ────────────────────────────────────────────────────────────────────────────────────────────

def render_helloworld(auth_machine: StateMachine) -> None:
    """
    <docstrings> Exibe uma saudação personalizada no cabeçalho da interface com base
    no perfil do usuário e, se aplicável, no título profissional adaptado ao gênero.

    Args:
        sm (StateMachine): Instância da máquina de estado `auth_state`.

    Calls:
        sm.get_variable(): Recupera 'professional_profile' e 'user_profile' do estado | definida em frameworks.sm.py.
        get_professional_title(): Gera o título com base em nome e gênero | definida neste módulo.
        adjust_gender_ending(): Ajusta a saudação textual ao gênero | definida neste módulo.
        st.markdown(): Renderiza o cabeçalho no front-end | definida em streamlit.

    Returns:
        None:
            Exibe o cabeçalho na interface Streamlit.
    """
    
    prof = auth_machine.get_variable("professional_profile")
    user = auth_machine.get_variable("user_profile")

    # Usuário com perfil profissional ativo →
    if prof and prof.get("professional_status") is True:
        genero = user.get("gender", "M")
        helloworld = adjust_gender_ending("Bem-vindo", genero)
        header = get_professional_title(prof, user)
        st.markdown(f"#### {helloworld}, {header}!")

    # Usuário comum (paciente) →
    elif user:
        nome_completo = user.get("display_name", "Usuário")
        primeiro_nome = nome_completo.split(" ")[0] if nome_completo else "Usuário"
        genero = user.get("gender", "M")
        helloworld = adjust_gender_ending("Bem-vindo", genero)
        st.markdown(f"#### {helloworld}, {primeiro_nome}!")

    # Caso nenhum dado esteja disponível →
    else:
        st.markdown("## Olá!")


# 🩺 FUNÇÃO QUE GERA TÍTULO FORMAL COM BASE NO GÊNERO ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def get_professional_title(professional_profile: dict, user_profile: dict) -> str:
    """
    <docstrings> Retorna o título formal com base no gênero armazenado no perfil do usuário,
    usando o nome de exibição definido pelo profissional.

    Args:
        professional_profile (dict): Contém 'display_name' (nome público do profissional).
        user_profile (dict): Contém 'gender' do usuário autenticado.

    Calls:
        dict.get(): Método do objeto dict para acessar chaves com fallback | instanciado por ambos os perfis.
        logger.debug(): Loga o título gerado e o gênero usado | instanciado por logger.

    Returns:
        str:
            Título completo com prefixo (Dr., Dra., Drx.) e nome.
            Exemplo: "Dra. Juliana", "Drx. Alex", "Dr. Henrique"
    """
    
    name = professional_profile.get("display_name", "Profissional")
    gender = user_profile.get("gender", "M")

    # Verifica o gênero para definir o título apropriado →
    if gender == "F":
        title = "Dra."  # → feminino
    elif gender == "N":
        title = "Drx."  # → não-binário
    else:
        title = "Dr."   # → masculino (default)

    logger.debug(f"Título gerado: {title} {name} (gênero='{gender}')")
    return f"{title} {name}"


# ♀️ FUNÇÃO PARA AJUSTAR TERMINAÇÃO GRAMATICAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def adjust_gender_ending(text: str, gender: str) -> str:
    """
    <docstrings> Ajusta sufixos gramaticais como "o"/"os" com base no gênero informado.

    Args:
        text (str): Palavra ou expressão que deve ser flexionada.
        gender (str): Gênero do usuário ("M", "F" ou "N").

    Calls:
        str.strip(): Remove espaços laterais | built-in.
        str.upper(): Converte o gênero para caixa alta | built-in.
        re.search(): Verifica presença de padrões gramaticais | definida em re.
        re.sub(): Substitui os padrões localizados | definida em re.
        logger.debug(): Loga se o gênero for inválido ou não reconhecido | instanciado por logger.

    Returns:
        str:
            Palavra ou expressão com terminação flexionada.
            Retorna o texto original se o gênero for inválido.
    """
    gender = gender.strip().upper()

    SUB = {
        "M": {"o": "o", "os": "os"},
        "F": {"o": "a", "os": "as"},
        "N": {"o": "e", "os": "es"}
    }

    # Gênero não reconhecido →
    if gender not in SUB:
        logger.debug(f"Gênero não reconhecido: {gender}.")
        return text

    # Texto no plural →
    if re.search(r"os\b", text):
        return re.sub(r"os\b", SUB[gender]["os"], text)

    # Texto no singular →
    if re.search(r"o\b", text):
        return re.sub(r"o\b", SUB[gender]["o"], text)

    return text
