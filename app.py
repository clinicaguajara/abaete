import streamlit as st
import time
from auth import get_user
from dashboard import render_dashboard, render_professional_dashboard
from main_layout import render_main_layout
from utils.design_utils import load_css
from utils.professional_utils import is_professional_enabled
from utils.profile_utils import render_onboarding_questionnaire

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
    
    # Se a sessão ainda não estiver definida...
    if "user" not in st.session_state:
        st.session_state["user"] = None  # O usuário é inicializado como não autenticado.
   
    # Se nada foi processado...
    if "processing" not in st.session_state:
        st.session_state["processing"] = False # Aguarde alguma interação do usuário.
   
    # Se a interface do aplicativo ainda não foi atualizada...
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False # Aguarde alguma interação do usuário antes de continuar.


# 🛣️ Processa o fluxo de usuários autenticados.
def handle_authenticated_user(user):
    
    # Se o usuário ainda não possuir um gênero definido...
    if not user.get("genero"):
        render_onboarding_questionnaire(user["id"], user["email"]) # Renderiza o questionário de boas vindas
    
    # Se o usuário for um profissional...
    elif is_professional_enabled(user["id"]):
        render_professional_dashboard(user) # Renderiza o dashboard especial
    
    # Caso contrário...
    else:
        render_dashboard(user) # Renderiza o dashboard normal.


# 🧭 Função principal que tudo controla.
def main():
    initialize_session_state()
    load_css()

    # Transição controlada após login/cadastro/onboarding.
    if st.session_state.get("refresh", False):
        
        st.session_state["refresh"] = False  # Limpa o refresh.
        with st.spinner("Processando..."):
            time.sleep(0.2)  # Tempo para o spinner renderizar.
            st.rerun()       
        return

    user = get_user()

    if user and "id" in user:
        handle_authenticated_user(user)
    else:
        render_main_layout()


# ⏯️ Executa o código, sem mais demora.
if __name__ == "__main__":
    main() # Chama a função principal.