import streamlit as st
from auth import get_user
from main_layout import render_main_layout
from dashboard import render_dashboard, render_professional_dashboard
from utils.profile_utils import render_onboarding_questionnaire
from utils.design_utils import load_css
from utils.professional_utils import is_professional_enabled
from utils.user_utils import get_user_info


# 📬 Configuração inicial.
# Define título, ícone e o layout central.
st.set_page_config(
    page_title="Abaeté",
    page_icon="🪴",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 🌐 Função para inicializar a sessão e evitar erros de navegação.
def initialize_session_state():
    """
    Inicializa as variáveis de estado da sessão do Streamlit para garantir que o aplicativo funcione corretamente.

    Fluxo:
        1. Se "user" não existir no `st.session_state`, inicializa como `None`, indicando que o usuário não está autenticado.
        2. Se "processing" não existir, inicializa como `False`, indicando que nenhuma operação está em andamento.
        3. Se "refresh" não existir, inicializa como `False`, evitando atualizações desnecessárias na interface.

    Args:
        None.

    Returns:
        None(as variáveis são configuradas diretamente no `st.session_state`).

    Calls:
        None (modifica apenas `st.session_state`).
    """
    # 1. Se a sessão ainda não estiver definida...
    if "user" not in st.session_state:
        st.session_state["user"] = None  # O usuário é inicializado como não autenticado.
   
    # 2. Se o processamento das páginas ainda não foi executado...
    if "processing" not in st.session_state:
        st.session_state["processing"] = False # É porque não há nada para ser processado.
   
    # 3. Se a interface do aplicativo ainda não foi atualizada...
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False # Aguarda alguma interação do usuário antes de continuar.


# 🧭 Função principal que tudo controla.
def main():
    """
    Controla o fluxo de navegação e renderização do aplicativo.

    Fluxo:
        1. Inicializa as variáveis de sessão com initialize_session_state(), garantindo que as chaves "user", "processing" e "refresh" estejam definidas.
        2. Carrega o CSS customizado com load_css() para configurar a aparência do aplicativo.
        3. Obtém o usuário autenticado através de get_user().
            3.1 Se o usuário não estiver logado, exibe a tela principal com render_main_layout().
        4. Se um usuário autenticado for identificado:
            4.1 Armazena seu ID e obtém as informações do perfil com get_user_info().
            4.2 Verifica se o usuário é um profissional cadastrado usando is_professional_enabled().
            4.3 Se o perfil estiver incompleto (exemplo: ausência do campo "genero"), exibe o questionário de cadastro com render_onboarding_questionnaire().
            4.4 Caso contrário, exibe um dashboard:
                4.4.1 Se for profissional, chama render_professional_dashboard().
                4.4.2 Caso contrário, chama render_dashboard() para um usuário padrão.

    Args:
        Nenhum.

    Returns:
        Nenhum (a função apenas renderiza a interface do Streamlit).

    Calls:
        - initialize_session_state() → Inicializa o estado da sessão.
        - load_css() → Carrega o estilo visual do aplicativo.
        - get_user() → Obtém o usuário autenticado.
        - get_user_info(user_id, full_profile=True) → Recupera informações completas do usuário.
        - is_professional_enabled(user_id) → Verifica se o usuário é profissional.
        - render_onboarding_questionnaire(user_id, user["email"]) → Exibe o questionário de cadastro, se necessário.
        - render_professional_dashboard(user) → Renderiza o dashboard para profissionais.
        - render_dashboard() → Renderiza o dashboard padrão para usuários não profissionais.
        - render_main_layout() → Renderiza a tela principal caso ninguém esteja autenticado.
    """
    # 1. Inicializa a sessão.
    initialize_session_state()
    # 2. Cria o visual.
    load_css()
    # 3. Verifica quem está navegando.
    user = get_user() 
    
    # 4. Se existir um ID logado na sessão...
    if user and "id" in user:
        user_id = user["id"]  # 4.1 Guarda o ID em uma variável do tipo string.

        # 4.1 Busca as informações do perfil do usuário com user_id e salva em um dicionário.
        user_profile = get_user_info(user_id, full_profile=True)
        
        # 4.2 Busca quais usuários são profissionais e salva em um dicionário.
        is_professional = is_professional_enabled(user_id)

        # 4.3 Se o questionário de cadastro ainda não foi respondido...
        if not user_profile or not user_profile.get("genero"):
            render_onboarding_questionnaire(user_id, user["email"]) # 4.3 Renderiza o questionário de cadastro.

        # 4.4 Mas...
        else:
            # 4.4.1 Se o usuário for um profissional cadastrado...
            if is_professional:
                render_professional_dashboard(user) # 4.4.1 Exibe um dashboard especial.
            # 4.4.2 Caso contrário...
            else:
                render_dashboard() # 4.4.2 Renderiza a página normal.

    # 3.1 Entretanto, se ninguém está logado...
    else:
        render_main_layout()  # 3.1 Renderiza o layout principal.


# ⏯️ Executa o código, sem mais demora.
if __name__ == "__main__":
    main() # Chama a função principal.
