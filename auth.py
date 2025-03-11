import streamlit as st
import supabase


# 🔑 Estabelece as credenciais do Supabase Auth no sectes do Streamlit.
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Cria o client de auticação. É por aqui que o usuário vai logar.
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)


# 🕵️‍♂️ Função que busca o usuário que fez a conexão.
def get_user():
    return st.session_state.get("user")


# 🔐 Função que verifica o login e deixa o usuário passar.  
def sign_in(email, password):
    try:
        # Tenta logar com email e senha, mesmo se não funcionar.
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
       
        # Se deu certo e usuário há...
        if response and hasattr(response, "user") and response.user: 
            user_obj = response.user # Pegamos seus dados para armazenar. 

            # Criamos um dicionário para tudo guardar. Retorna ID, nome e email para autenticar.
            user_data = {
                "email": user_obj.email,
                "id": user_obj.id,
                "display_name": user_obj.user_metadata.get("display_name", "Usuário") if hasattr(user_obj, "user_metadata") else "Usuário"
            }

            # 🔄 Guardamos os dados do usuário na sessão.
            st.session_state["user"] = user_data
            st.cache_data.clear()
            st.session_state["refresh"] = True # E reiniciamos o fluxo sem frustração.
            return user_data, None

    except Exception as e:
        return None, f"❌ Erro ao logar: {str(e)}"


# 📝 Função para o usuário se registrar.
def sign_up(email, password, confirm_password, display_name):
    # Se as senhas não coincidem...
    if password != confirm_password:
        return None, "❌ As senhas não coincidem!" # Vamos de avisar!

    try:
        # 📤 Criamos a conta no Supabase. 
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name}} 
        })

         # 🎉 Se tudo deu certo...
        if response and hasattr(response, "user") and response.user:
            # Resposta ele dá, e um email para confirmar.
            return response.user, "📩 Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada."
        return None, "⚠️ Não foi possível criar a conta. Tente novamente."

    except Exception as e:
        return None, f"❌ Erro ao criar conta: {str(e)}"


# 🔓 Função para a senha recuperar.
def reset_password(email):
    try:
        supabase_client.auth.reset_password_for_email(
            email,
            options={"redirect_to": "https://resetpassword-3fou6u.flutterflow.app/resetPasswordPage"} # 🔹 Define o redirecionamento!
        )
        return f"📩 Um email de recuperação foi enviado para {email}."
    except Exception as e:
        return f"⚠️ Erro ao solicitar recuperação de senha: {str(e)}"


# 🚪 Função para sair e limpar a sessão.
def sign_out():
    supabase_client.auth.sign_out()
    st.session_state.pop("user", None)
    st.session_state["refresh"] = True
    st.session_state["processing"] = False
    st.cache_data.clear() 
    st.rerun() # Desconecta o usuário sem gerar confusão.

