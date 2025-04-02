import streamlit as st
import supabase

# 🔑 Configuração inicial do Supabase e autenticação OAuth.
# Obtém as credenciais a partir do Streamlit.
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


# Cria o client de autenticação do Supabase.
# Esse client é utilizado para realizar operações de login, cadastro, recuperação de senha e logout.
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)


# 🔐  Função que verifica o login e deixa o usuário passar.
def sign_in(email, password):
    
    from utils.user_utils import get_user_info
    try:
        with st.spinner("Processando..."):
            # Tenta logar com email e senha.
            response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        
            # Se conseguir autenticar, processa os dados do usuário no Supabase Auth.
            if response and hasattr(response, "user") and response.user: 
                user_obj = response.user
                
                # Obtém os dados completos do perfil do usuário na tabela user_profile.
                user_profile = get_user_info(user_obj.id, full_profile=True)

                # Mescla as informações em um dicionário.
                user_data = {
                    "id": user_obj.id,
                    "email": user_obj.email,
                    "display_name": user_obj.user_metadata.get("display_name", "Usuário"),
                    **user_profile  # Mescla os dados do perfil
                }

                # Armazena o usuário na sessão.
                st.session_state["user"] = user_data
                st.cache_data.clear() # Limpa o cache e atualiza refresh.
                st.session_state["refresh"] = True
                return user_data, None # Retorna.

    # Se houver uma exceção no fluxo...
    except Exception as e:
        st.error(f"❌ Erro ao logar: {str(e)}") # 3. Explica o problema.


# 🔓 Função para a senha recuperar.
def reset_password(email):
    
    try:
        # Recebe o email e chama o client do Supabase para redefinição de senha.
        supabase_client.auth.reset_password_for_email(
            email,
            options={"redirect_to": "https://resetpassword-3fou6u.flutterflow.app/resetPasswordPage"}
        )

        # 2. Retorna uma mensagem de confirmação.
        return f"📩 Um email de recuperação foi enviado para {email}." 

    # Se houver um exceção...
    except Exception as e:
        return f"⚠️ Erro ao solicitar recuperação de senha: {str(e)}" # Explica o problema.


# 📝  Função para o usuário se registrar.
def sign_up(email, password, confirm_password, display_name):
   
    # Se as senhas não forem iguais...
    if password != confirm_password:
        return None, "❌ As senhas não coincidem!" # 1. Retorna um erro.
    
    try:
        # Cria a conta no Supabase.
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name}}
        })

        # Se der certo...
        if response and hasattr(response, "user") and response.user:
            # Retorna o objeto do usuário e uma mesnagem de confirmação.
            return response.user, "📩 Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada." 

        # Caso contrário... 
        return None, "⚠️ Não foi possível criar a conta. Tente novamente." # 4.1 Retorna none e uma mensagem de erro.

    # Se houver ume exceção...
    except Exception as e:
        return None, f"❌ Erro ao criar conta: {str(e)}" # 5. Explica o problema.


# 🕵️‍♂️ Função que busca o usuário que fez a conexão.
def get_user():
    # Obtém e retorna o valor associado à chave "user" no st.session_state.
    return st.session_state.get("user")


# 🚪 Função para sair e limpar a sessão.
def sign_out():
    
    supabase_client.auth.sign_out() # Realiza o logout no Supabase.
    st.session_state.pop("user", None) # Remove o usuário da sessão.
    st.session_state["refresh"] = True # Atualiza refresh.
    st.session_state["processing"] = False # Atualiza processing.
    st.session_state["show_prof_input"] = False # Atualiza show_prof_input.
    st.cache_data.clear() # Limpa o cache.
    st.rerun()  # Reinicia a interface para refletir o logout.