# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st


from datetime                   import date, timedelta
from frameworks.sm              import StateMachine
from services.user_profile      import save_user_profile, load_user_profile
from utils.variables.constants            import SALARIO_MINIMO, TCLE


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Cria ou recupera uma instância do objeto Logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# ⚙️ FUNÇÃO PARA DECIDIR SE O QUESTIONÁRIO SERÁ RENDERIZADO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_onboarding_if_needed(auth_machine: StateMachine, user_profile: dict) -> None:
    """
    Verifica se o perfil precisa de onboarding e, se necessário, exibe o formulário.
    """
    perfil_incompleto = (
        not user_profile or
        any(
            user_profile.get(k) is None
            for k in ["gender", "birthdate", "race", "income_range", "disabilities", "consent"]
        )
    )

    if perfil_incompleto:
        render_onboarding_questionnaire(auth_machine, user_profile)
        st.stop()


# 📺 FUNÇÃO PARA RENDERIZAR ONBOARDING DO USUÁRIO ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_onboarding_questionnaire(auth_machine: StateMachine, user_profile: dict) -> tuple[None, str | None]:
    """
    <docstrings> Exibe o questionário de onboarding com campos dinâmicos, usando os dados da máquina de autenticação.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do usuário autenticado.
        user_profile (dict): Dados do perfil carregados previamente.

    Calls:
        save_user_profile(): Persiste os dados no backend | definida em services/user_profile.py.
        load_user_profile(): Recarrega perfil após salvar | definida em services/user_profile.py
        auth_machine.get_variable(): Recupera variáveis do usuário | instanciado por StateMachine.
        st.form(): Cria formulário com validação e envio | definida em streamlit.
        st.rerun(): Força rerun após transição de estado | definida em streamlit.runtime.

    Returns:
        Tuple[None, str | None]:
            - None: Se execução ocorrer normalmente.
            - str | None: Mensagem de erro em caso de falha.
    """
    
    CAMPOS_OBRIGATORIOS = ["display_name", "birthdate", "gender", "race", "income_range", "disabilities", "consent"]

    # Filtra campos ainda não preenchidos (apenas None).
    campos_pendentes = [k for k in CAMPOS_OBRIGATORIOS if user_profile.get(k) is None]

    # 🔒 Se não há campos pendentes, não há formulário a renderizar.
    if not campos_pendentes:
        return
    
    st.markdown("<h4>Antes de continuar, gostaríamos de saber mais sobre você...</h4>", unsafe_allow_html=True)

    respostas = {}

    with st.form("form_onboarding"):
                
        if user_profile.get("display_name") is None:
            nome = st.text_input("Nome completo", placeholder="Ex: Anna O.")
            respostas["display_name"] = nome

        if user_profile.get("gender") is None:
            genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Não-binário"])
            genero_map = {"Masculino": "M", "Feminino": "F", "Não-binário": "N"}
            respostas["gender"] = genero_map[genero]

        if user_profile.get("birthdate") is None:
            hoje = date.today()
            limite_min = hoje - timedelta(days=120 * 365)
            nascimento = st.date_input("Data de nascimento", min_value=limite_min, max_value=hoje)
            respostas["birthdate"] = str(nascimento)

        if user_profile.get("race") is None:
            raca = st.selectbox("Etnia", ["Branca", "Preta", "Parda", "Amarela", "Indígena"])
            respostas["race"] = raca

        if user_profile.get("income_range") is None:
            faixas = [
                f"Até 1 salário mínimo (até R$ {1 * SALARIO_MINIMO:,.2f})",
                f"Entre 1 e 2 salários mínimos (até R$ {2 * SALARIO_MINIMO:,.2f})",
                f"Entre 2 e 3 salários mínimos (até R$ {3 * SALARIO_MINIMO:,.2f})",
                f"Entre 3 e 5 salários mínimos (até R$ {5 * SALARIO_MINIMO:,.2f})",
                f"Mais de 5 salários mínimos (acima de R$ {5 * SALARIO_MINIMO:,.2f})"
            ]
            renda = st.selectbox("Renda mensal familiar", faixas)
            respostas["income_range"] = renda

        if user_profile.get("disabilities") is None:
            diagnostico = st.text_input(
                "Você possui algum diagnóstico, transtorno ou condição médica?",
                placeholder="Ex: TDAH, Transtorno de Ansiedade, Nenhum, etc."
            )
            respostas["disabilities"] = diagnostico

        if user_profile.get("consent") is None:
            if TCLE:
                st.divider()
                st.markdown(TCLE, unsafe_allow_html=True)
            st.info("🪶 Termo de Consentimento")
            respostas["consent"] = st.checkbox(
                "**Autorizo a utilização dos meus dados para fins de pesquisa.**"
            )

        enviar = st.form_submit_button("Submeter formulário", use_container_width=True)

    if enviar:
        success = save_user_profile(auth_machine, respostas)
        if success:
            user_id = auth_machine.get_variable("user_id")
            load_user_profile(user_id, auth_machine)
            st.rerun()
        else:
            st.error("❌ Não foi possível salvar o formulário. Tente novamente.")

    return None, None
