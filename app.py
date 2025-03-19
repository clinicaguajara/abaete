import streamlit as st
from auth import get_user
from main_layout import render_main_layout
from dashboard import render_dashboard, render_professional_dashboard
from utils.profile_utils import render_onboarding_questionnaire
from utils.design_utils import load_css
from utils.professional_utils import is_professional_enabled
from utils.user_utils import get_user_info


# Configuração inicial.
# Definimos título, ícone e o layout central.
st.set_page_config(
    page_title="Abaeté",
    page_icon="🪴",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 🌐 Função para inicializar a sessão e evitar erros de navegação.
def initialize_session_state():
    """
    Inicializa as variáveis de sessão do Streamlit para controlar o estado do app.
    
    Fluxo:
        1. Se a chave "user" não existir em st.session_state, define-a como None.
        2. Se a chave "processing" não existir, inicializa como False (nenhuma operação em andamento).
        3. Se a chave "refresh" não existir, inicializa como False (sem necessidade de atualização imediata).
    
    Args:
        None.
    
    Returns:
        None (Configura variáveis diretamente no st.session_state).
    
    Calls:
        None.
    """
    # Se a sessão ainda não estiver definida...
    if "user" not in st.session_state:
        st.session_state["user"] = None  # O usuário é inicializado como não autenticado.
   
    # Se o processamento das páginas ainda não foi executado...
    if "processing" not in st.session_state:
        st.session_state["processing"] = False # É porque não há nada para ser processado.
   
    # Se a interface do aplicativo ainda não foi atualizada...
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False # Devemos aguardar alguma interação do usuário.


# 🧭 Função principal que tudo controla.
def main():
    """
    Função principal que controla o fluxo de navegação e renderização do aplicativo.

    Fluxo:
      1. Inicializa as variáveis de sessão utilizando initialize_session_state(), garantindo que as chaves
         "user", "processing" e "refresh" estejam definidas.
      2. Carrega o CSS customizado com load_css() para configurar a aparência do aplicativo.
      3. Recupera o usuário autenticado usando get_user().
         - Se nenhum usuário estiver logado, chama render_main_layout() para exibir a tela principal.
      4. Se um usuário estiver autenticado (com campo "id"):
         a. Armazena o ID do usuário para uso no fluxo.
         b. Obtém as informações completas do perfil do usuário via get_user_info().
         c. Verifica se o usuário é um profissional com is_professional_enabled().
         d. Se o perfil não tiver sido completado (ex.: falta o campo "genero"), exibe o questionário de cadastro
            chamando render_onboarding_questionnaire().
         e. Caso o usuário seja um profissional, chama render_professional_dashboard() para renderizar um dashboard especializado.
         f. Se o usuário não for profissional, chama render_dashboard() para renderizar o dashboard padrão do paciente.

    Args:
        None (a função utiliza o estado de sessão e funções globais para determinar o fluxo).

    Returns:
        None (a função renderiza a interface diretamente no Streamlit e não retorna valores).

    Calls:
        - initialize_session_state()  
        - load_css()                  
        - get_user()                  
        - get_user_info()             
        - is_professional_enabled()   
        - render_onboarding_questionnaire() 
        - render_professional_dashboard() 
        - render_dashboard()          
        - render_main_layout()        
    """
    initialize_session_state() # Inicializa a sessão.
    load_css() # Cria o visual.
    user = get_user()  # E verifica quem está navegando.
    
    # Se temos um ID logado na sessão...
    if user and "id" in user:
        user_id = user["id"]  # Guardamos o ID para ser utilizado no fluxo.

        # Busca as informações do perfil do usuário.
        if "user_profile" not in st.session_state:
            st.session_state["user_profile"] = get_user_info(user_id, full_profile=True)

        
        # Busca quais usuários são profissionais.
        is_professional = is_professional_enabled(user_id)

        # Se o questionário de cadastro ainda não foi respondido...
        if not user_profile or not user_profile.get("genero"):
            render_onboarding_questionnaire(user_id, user["email"]) # Renderizamos o questionário de cadastro.

        # Mas...
        else:
            # Se o usuário for um profissional cadastrado...
            if is_professional:
                render_professional_dashboard(user) # Exibe um dashboard especial.
            # Caso contrário...
            else:
                render_dashboard() # Renderiza a página normal.

    # Entretanto, se ninguém está logado...
    else:
        render_main_layout()  # Renderizamos o layout principal.


# ⏯️ Executa o código, sem mais demora.
if __name__ == "__main__":
    main() # Chamando main() e começando a história!
