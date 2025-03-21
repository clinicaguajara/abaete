import streamlit as st
import supabase
from urllib.parse import urlencode

# 🔑 Configuração inicial do Supabase e autenticação OAuth.
# Obtém as credenciais a partir do Streamlit.
SUPABASE_URL = st.secrets["auth.streamlit"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["auth.streamlit"]["SUPABASE_KEY"]
GOOGLE_CLIENT_ID = st.secrets["auth.google"]["CLIENT_ID"]
GOOGLE_REDIRECT_URI = st.secrets["auth"]["REDIRECT_URI"]


# Cria o client de autenticação do Supabase.
# Esse client é utilizado para realizar operações de login, cadastro, recuperação de senha e logout.
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)


# 🔐  Função que verifica o login e deixa o usuário passar.
def sign_in(email, password):
    """
    Realiza o login do usuário utilizando email e senha, e armazena os dados na sessão.

    Fluxo:
        1. Tenta autenticar o usuário com o Supabase através de sign_in_with_password().
        2. Se a autenticação for bem-sucedida e o objeto usuário estiver presente:
            2.1 Busca as informações completas do usuário a partir do objeto.
            2.2 Mescla as informações em user_data.
            2.3 Armazena user_data em st.session_state["user"].
            2.4 Limpa o cache e marca st.session_state["refresh"] como True para reinicializar a interface.
            2.5 Força a reinicialização da interface.
        3. Se houver uma exceção no fluxo, explica o problema.

    Args:
        email (str): Email do usuário.
        password (str): Senha do usuário.

    Returns:
        tuple: (user_data, None) em caso de sucesso ou (None, mensagem_de_erro) se ocorrer falha.

    Calls:
        - supabase_client.auth.sign_in_with_password()
        - get_user()
    """
    from utils.user_utils import get_user_info
    try:
        # 1. Tenta logar com email e senha.
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
       
        # 2. Se conseguir autenticar, processa os dados do usuário no Supabase Auth.
        if response and hasattr(response, "user") and response.user: 
            user_obj = response.user
            
            # 2.1 Obtém os dados completos do perfil do usuário na tabela user_profile.
            user_profile = get_user_info(user_obj.id, full_profile=True)

            # 2.2 Mescla as informações em um dicionário.
            user_data = {
                "id": user_obj.id,
                "email": user_obj.email,
                "display_name": user_obj.user_metadata.get("display_name", "Usuário"),
                **user_profile  # Mescla os dados do perfil
            }

            # 2.3 Armazena o usuário na sessão.
            st.session_state["user"] = user_data
            st.cache_data.clear() # 2.4 Limpa o cache e atualiza refresh.
            st.session_state["refresh"] = True
            st.rerun() # 2.5 Força a reinicialização da interface imediatamente.

    # 3. Se houver uma exceção no fluxo...
    except Exception as e:
        st.error(f"❌ Erro ao logar: {str(e)}") # 3. Explica o problema.


# 🔓 Função para a senha recuperar.
def reset_password(email):
    """
    Inicia o processo de recuperação de senha enviando um email de redefinição.

    Fluxo:
        1. Chama supabase_client.auth.reset_password_for_email() com o email e a URL de redirecionamento.
        2. Retorna uma mensagem informando que o email de recuperação foi enviado.
        3. Se houver um exceção no fluxo, explica o problema.

    Args:
        email (str): Email do usuário que deseja redefinir a senha.

    Returns:
        str: Mensagem de sucesso ou de erro.

    Calls:
        - supabase_client.auth.reset_password_for_email()
    """
    try:
        # 1. Recebe o email e chama o client do Supabase para redefinição de senha.
        supabase_client.auth.reset_password_for_email(
            email,
            options={"redirect_to": "https://resetpassword-3fou6u.flutterflow.app/resetPasswordPage"}
        )

        # 2. Retorna uma mensagem de confirmação.
        return f"📩 Um email de recuperação foi enviado para {email}." 

    # 3. Se houver um exceção...
    except Exception as e:
        return f"⚠️ Erro ao solicitar recuperação de senha: {str(e)}" # 3. Explica o problema.


# 📝  Função para o usuário se registrar.
def sign_up(email, password, confirm_password, display_name):
    """
    Registra um novo usuário no Supabase e envia um email de confirmação.

    Fluxo:
        1. Verifica se a senha e a confirmação de senha são iguais.
        2. Tenta criar a conta no Supabase com sign_up(), enviando também o display_name como metadado.
        3. Se a criação for bem-sucedida:
            3.1 Retorna o objeto do usuário e uma mensagem de confirmação.
        4. Caso contrário:
            4.1 Retorna None e uma mensagem de erro.
        5. Se houver uma exceção no fluxo, explica o problema.

    Args:
        email (str): Email do novo usuário.
        password (str): Senha do novo usuário.
        confirm_password (str): Confirmação da senha.
        display_name (str): Nome do usuário.

    Returns:
        tuple: (user_obj, mensagem) se o cadastro for bem-sucedido ou (None, mensagem_de_erro) se houver falha.

    Calls:
        - supabase_client.auth.sign_up()
    """
    # 1. Se as senhas não forem iguais...
    if password != confirm_password:
        return None, "❌ As senhas não coincidem!" # 1. Retorna um erro.
    
    try:
        # 2. Cria a conta no Supabase.
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name}}
        })

        # 3. Se der certo...
        if response and hasattr(response, "user") and response.user:
            # 3.1 Retorna o objeto do usuário e uma mesnagem de confirmação.
            return response.user, "📩 Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada." 

        # 4. Caso contrário... 
        return None, "⚠️ Não foi possível criar a conta. Tente novamente." # 4.1 Retorna none e uma mensagem de erro.

    # 5. Se houver ume exceção...
    except Exception as e:
        return None, f"❌ Erro ao criar conta: {str(e)}" # 5. Explica o problema.


# 🕵️‍♂️ Função que busca o usuário que fez a conexão.
def get_user():
    """
    Recupera o usuário atualmente armazenado na sessão do Streamlit.

    Fluxo:
      1. Obtém o valor associado à chave "user" no st.session_state.

    Args:
        None.

    Returns:
        dict or None: Dados do usuário autenticado, se existir. Caso contrário, None.

    Calls:
        None.
    """
    # 1. Obtém e retorna o valor associado à chave "user" no st.session_state.
    return st.session_state.get("user")


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
    supabase_client.auth.sign_out() # 1. Realiza o logout no Supabase.
    st.session_state.pop("user", None) # 2. Remove o usuário da sessão.
    st.session_state["refresh"] = True # 3. Atualiza refresh.
    st.session_state["processing"] = False # 3. Atualiza processing.
    st.session_state["show_prof_input"] = False # 3. Atualiza show_prof_input.
    st.cache_data.clear() # 3. Limpa o cache.
    st.rerun()  # 4. Reinicia a interface para refletir o logout.


def get_google_login_url():
    """
    Gera a URL para autenticação via Google no Supabase.

    Returns:
        str: URL de autenticação do Google.
    """
    params = {
        "provider": "google",
        "redirect_to": GOOGLE_REDIRECT_URI
    }
    return f"{SUPABASE_URL}/auth/v1/authorize?{urlencode(params)}"


def sign_in_with_google():
    """
    Processa o callback do Google OAuth trocando o 'code' por um access_token,
    e autentica o usuário no Supabase, mesclando com os dados da tabela `user_profile`.
    """
    from utils.user_utils import get_user_info
    import requests

    query_params = st.query_params

    if "code" in query_params:
        code = query_params["code"][0]

        # ⚙️ Troca o code por access_token no Supabase
        token_url = f"{SUPABASE_URL}/auth/v1/token"
        response = requests.post(
            token_url,
            headers={"Content-Type": "application/json"},
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": GOOGLE_REDIRECT_URI
            }
        )

        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")

            # ✅ Pega o usuário usando o token
            user_response = supabase_client.auth.get_user(access_token)

            if user_response and "user" in user_response:
                user_obj = user_response["user"]

                # 🔄 Consulta o perfil
                user_profile = get_user_info(user_obj["id"], full_profile=True)

                user_data = {
                    "id": user_obj["id"],
                    "email": user_obj["email"],
                    "display_name": user_obj.get("user_metadata", {}).get("display_name", "Usuário"),
                    **user_profile
                }

                st.session_state["user"] = user_data
                st.cache_data.clear()
                st.session_state["refresh"] = True
                st.rerun()
            else:
                st.error("❌ Não foi possível obter os dados do usuário.")
        else:
            st.error("❌ Erro ao trocar o código por token de acesso.")