import streamlit as st
import supabase
from utils.user_utils import get_user_info

# Recupera as credenciais do Supabase Auth a partir do arquivo de secrets do Streamlit.
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Cria o client de autenticação do Supabase.
# Esse client é utilizado para realizar operações de login, cadastro, recuperação de senha e logout.
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)


# 🕵️‍♂️ Função que busca o usuário que fez a conexão.
def get_user():
    """
    Recupera o usuário atualmente armazenado na sessão do Streamlit.

    Fluxo:
      1. Obtém o valor associado à chave "user" no st.session_state.

    Args:
        None.

    Returns:
        dict or None: Dados do usuário autenticado, se existir; caso contrário, None.

    Calls:
        None.
    """
    return st.session_state.get("user")


# 🔐 Função que verifica o login e deixa o usuário passar. 
def sign_in(email, password):
    """
    Realiza o login do usuário utilizando email e senha, e armazena os dados do usuário na sessão.

    Fluxo:
      1. Tenta autenticar o usuário com o Supabase através de sign_in_with_password().
      2. Se a autenticação for bem-sucedida:
         a. Obtém `email` e `id` do usuário autenticado.
         b. Tenta buscar `display_name` do `user_profile` no banco.
         c. Se não encontrar o perfil, usa o `display_name` dos metadados do Supabase Auth.
         d. Armazena `user_data` em `st.session_state["user"]`.
      3. Retorna o usuário autenticado e uma mensagem de erro caso haja falha.

    Args:
        email (str): O email do usuário.
        password (str): A senha do usuário.

    Returns:
        tuple: (user_data, None) em caso de sucesso ou (None, mensagem_de_erro) se ocorrer erro.

    Calls:
        - supabase_client.auth.sign_in_with_password()
        - get_user_info() (para buscar o perfil completo do banco)
    """
    try:
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
       
        if response and hasattr(response, "user") and response.user:
            user_obj = response.user  # Objeto do usuário autenticado.

            user_id = user_obj.id
            email = user_obj.email

            # 🔥 Busca o perfil completo do usuário no banco
            user_profile = get_user_info(user_id, full_profile=True)

            # Se o perfil existir no banco, usamos esse nome. Se não, pegamos dos metadados do Supabase.
            display_name = user_profile.get("display_name") if user_profile else user_obj.user_metadata.get("display_name", "Usuário")

            # Criamos um dicionário com os dados do usuário autenticado.
            user_data = {
                "email": email,
                "id": user_id,
                "display_name": display_name  # Agora pegamos do banco, se disponível.
            }

            # 🔥 Armazena o usuário autenticado na sessão e limpa o cache.
            st.session_state["user"] = user_data
            st.session_state["user_profile"] = user_profile  # 🔥 Agora o perfil completo já está salvo.
            st.cache_data.clear()
            st.session_state["refresh"] = True
            
            return user_data, None

    except Exception as e:
        return None, f"❌ Erro ao logar: {str(e)}"
    

# 📝 Função para o usuário se registrar.
def sign_up(email, password, confirm_password, display_name):
    """
    Registra um novo usuário no Supabase e envia um email de confirmação.

    Fluxo:
      1. Verifica se a senha e a confirmação são iguais.
      2. Tenta criar a conta no Supabase com sign_up(), enviando também o display_name como metadado.
      3. Se a criação for bem-sucedida, retorna o objeto do usuário e uma mensagem de confirmação.
      4. Caso contrário, retorna None e uma mensagem de erro.

    Args:
        email (str): Email do novo usuário.
        password (str): Senha do novo usuário.
        confirm_password (str): Confirmação da senha.
        display_name (str): Nome completo ou exibição do usuário.

    Returns:
        tuple: (user_obj, mensagem) – user_obj se o cadastro for bem-sucedido; None e mensagem de erro caso contrário.

    Calls:
        - supabase_client.auth.sign_up()
    """
    if password != confirm_password:
        return None, "❌ As senhas não coincidem!"
    try:
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name}}
        })
        if response and hasattr(response, "user") and response.user:
            return response.user, "📩 Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada."
        return None, "⚠️ Não foi possível criar a conta. Tente novamente."
    except Exception as e:
        return None, f"❌ Erro ao criar conta: {str(e)}"


# 🔓 Função para a senha recuperar.
def reset_password(email):
    """
    Inicia o processo de recuperação de senha enviando um email de redefinição.

    Fluxo:
      1. Chama supabase_client.auth.reset_password_for_email() com o email e a URL de redirecionamento.
      2. Retorna uma mensagem informando que o email de recuperação foi enviado.
      3. Se ocorrer um erro, retorna uma mensagem de erro.

    Args:
        email (str): Email do usuário que deseja redefinir a senha.

    Returns:
        str: Mensagem de sucesso ou de erro.

    Calls:
        - supabase_client.auth.reset_password_for_email()
    """
    try:
        supabase_client.auth.reset_password_for_email(
            email,
            options={"redirect_to": "https://resetpassword-3fou6u.flutterflow.app/resetPasswordPage"}
        )
        return f"📩 Um email de recuperação foi enviado para {email}."
    except Exception as e:
        return f"⚠️ Erro ao solicitar recuperação de senha: {str(e)}"


# 🚪 Função para sair e limpar a sessão.
def sign_out():
    """
    Realiza o logout do usuário, limpa a sessão e reinicia a interface do Streamlit.

    Fluxo:
      1. Chama supabase_client.auth.sign_out() para realizar o logout no Supabase.
      2. Remove o usuário da sessão (st.session_state["user"]).
      3. Atualiza as variáveis de sessão (refresh, processing, show_prof_input) e limpa o cache.
      4. Chama st.rerun() para reiniciar a aplicação e refletir as mudanças imediatamente.

    Args:
        None

    Returns:
        None (a função realiza operações de limpeza e reinicia a interface).

    Calls:
        - supabase_client.auth.sign_out() 
        - st.rerun()
    """
    supabase_client.auth.sign_out()
    st.session_state.pop("user", None)
    st.session_state["refresh"] = True
    st.session_state["processing"] = False
    st.session_state["show_prof_input"] = False
    st.cache_data.clear() 
    st.rerun()  # Reinicia a interface para refletir o logout.


