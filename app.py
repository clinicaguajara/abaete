import streamlit as st
from auth import get_user
from main_layout import render_main_layout
from dashboard import render_dashboard, render_professional_dashboard
from utils.profile_utils import render_onboarding_questionnaire
from utils.design_utils import load_css
from utils.professional_utils import is_professional_enabled
from utils.user_utils import get_user_info
from utils.system_utils import initialize_session_state, update_global_processing_message

# Configuração inicial.
st.set_page_config(
    page_title="Abaeté",
    page_icon="🪴",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 🧭 Função principal que tudo controla.
def main():
    """
    Função principal que controla o fluxo de navegação e renderização do aplicativo.

    Fluxo:
      1. Inicializa as variáveis de sessão utilizando initialize_session_state(), garantindo que as chaves
         "user", "processing", "refresh", "processing_message" e "global_process_container" estejam definidas.
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
        None.
    
    Returns:
        None (a interface é renderizada diretamente no Streamlit).
    
    Calls:
        - initialize_session_state()  [em app.py]
        - load_css()                  [em utils/design_utils.py]
        - get_user()                  [em auth.py]
        - get_user_info()             [em utils/user_utils.py]
        - is_professional_enabled()   [em utils/professional_utils.py]
        - render_onboarding_questionnaire() [em utils/profile_utils.py]
        - render_professional_dashboard() [em dashboard.py]
        - render_dashboard()          [em dashboard.py]
        - render_main_layout()        [em main_layout.py]
    """
    initialize_session_state()  # Inicializa o estado da sessão.
    load_css()  # Carrega os estilos customizados.
    
    # Atualiza o container global (caso haja uma mensagem previamente definida)
    update_global_processing_message(st.session_state.get("processing_message", ""))
    
    user = get_user()  # Recupera o usuário autenticado.
    
    if user and "id" in user:
        user_id = user["id"]
        user_profile = get_user_info(user_id, full_profile=True)
        is_professional = is_professional_enabled(user_id)
        
        if not user_profile or not user_profile.get("genero"):
            render_onboarding_questionnaire(user_id, user["email"])
        else:
            if is_professional:
                render_professional_dashboard(user)
            else:
                render_dashboard()
    else:
        render_main_layout()


# ⏯️ Executa o código, sem mais demora.
if __name__ == "__main__":
    main() # Chamando main e começando a história!
