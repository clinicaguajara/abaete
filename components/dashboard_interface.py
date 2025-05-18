
# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from frameworks.sm                      import StateMachine
from utils.session                      import FeedbackState
from utils.role                         import is_professional_user
from services.professional_patient_link import load_links_for_professional, save_professional_patient_link, fetch_patient_info_by_email, load_links_for_patient, accept_link, reject_link
from utils.design                       import render_abaete_header
from utils.gender                       import render_header_by_role


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 📺 FUNÇÃO PARA A RENDERIZAR A HOMEPAGE DO APLICATIVO ──────────────────────────────────────────────────────────

def render_dashboard(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a dashboard com tabs específicas para profissionais ou pacientes.

    Args:
        sm (StateMachine): Instância da máquina de estado usada para determinar o tipo de usuário.

    Calls:
        render_header_by_role(): Renderiza cabeçalho personalizado | definida em utils/gender.py.
        is_professional_user(): Verifica se o usuário é profissional | definida em dashboard_interface.py.
        _render_professional_tabs(): Tabs exclusivas para profissionais | definida em dashboard_interface.py.
        _render_patient_tabs(): Tabs exclusivas para pacientes | definida em dashboard_interface.py.

    Returns:
        Tuple[None, str | None]:
            - None: Em caso de execução bem-sucedida.
            - str | None: Mensagem de erro em caso de falha.
            
    """

    # ESTABILIZAÇÃO PROATIVA DA INTERFACE ──────────────────────────────────────────────────────────────────────────────

    redirect = StateMachine("auth_redirect", True)
    if redirect.current:
        logger.info(f"Estabilização proativa da interface (dashboard_interface)")
        redirect.to(False, True)  # ⬅ Desliga a flag.


    # INTERFACE CONFORME PAPEL DO USUÁRIO ──────────────────────────────────────────────────────────────────────────────

    render_abaete_header()

    role = is_professional_user(auth_machine)

    if role:
        _render_professional_homepage(auth_machine)
    else:
        _render_patient_homepage(auth_machine)

    return None, None


# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR A DASHBOARD DO PROFISSIONAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_homepage(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza as abas da interface destinadas a usuários profissionais.

    Args:
        None.

    Calls:
        st.tabs(): Componente de abas para navegação | definida em streamlit.
        st.write(): Escreve conteúdo textual | definida em streamlit.

    Returns:
        Tuple[None, str | None]:
            - None: Em caso de sucesso.
            - str | None: Mensagem de erro em caso de falha.

    """

    # Define as abas disponíveis.
    tabs = st.tabs(["Pacientes", "Agenda", "Planejamento"])
    
    # Aba de vínculos.
    with tabs[0]:
        render_header_by_role(auth_machine)
        _render_professional_link_interface(auth_machine)
    
    with tabs[1]:
        st.write("Acompanhamento de escalas e metas...")
    
    with tabs[2]:
        st.write("Status da assinatura e fatura...")
    
    return None, None



# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR A DASHBOARD DO PACIENTE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_homepage(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza as abas da interface destinadas a usuários pacientes.

    Args:
        None

    Calls:
        st.tabs(): Componente de abas para navegação | definida em streamlit.
        st.write(): Escreve conteúdo textual | definida em streamlit.

    Returns:
        Tuple[None, str | None]:
            - None: Em caso de sucesso.
            - str | None: Mensagem de erro em caso de falha.
    """
    
    # Se patient_links não for uma variável auxiliar de auth_machine...
    if not auth_machine.get_variable("patient_links"):
        patient_id = auth_machine.get_variable("user_id")   
        load_links_for_patient(patient_id, auth_machine)

    # Tenta realizar a operação principal.
    try:

        # Define as abas visíveis
        tabs = st.tabs(["Início", "Planner", "Notas"])

        with tabs[0]:
            # Cabeçalho com base no perfil do usuário.
            render_header_by_role(auth_machine) 
            st.markdown("Cada jornada é única — <strong>como a sua</strong>. <br>"
                 "Use seu tempo, no seu ritmo.", unsafe_allow_html=True)
            render_received_invites(auth_machine)
            st.image("assets/homepage.png", use_container_width=True)

        return None, None

    # Em exceções...
    except Exception as e:
        return None, str(e)


# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR A INTERFACE DE VÍNCULOS PARA O PROFISSIONAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_link_interface(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza o painel de vínculos ativos, pendentes e o formulário de convite via e-mail.

    Args:
        auth_machine (StateMachine): Máquina de estado com o ID do profissional autenticado.

    Calls:
        load_links_for_professional(): Busca vínculos do profissional | definida em services.professional_patient_link.py.
        save_professional_patient_link(): Cria novo vínculo com paciente | definida em services.professional_patient_link.py.
        fetch_patient_info_by_email(): Busca dados do paciente pelo e-mail | definida em services.patients.py.

    Returns:
        None.
    """
    
    # Cria uma instancia da máquina de autenticação.
    feedback_machine = auth_machine.get_variable("feedback", default=FeedbackState.NONE.value)

    # Recupera ID do profissional autenticado.
    professional_id = auth_machine.get_variable("user_id")

    # Se patient_links não for uma variável auxiliar de auth_machine...
    if not auth_machine.get_variable("professional_patient_links"):
        load_links_for_professional(professional_id, auth_machine)

    # Obtém vínculos e organiza por status
    links = auth_machine.get_variable("professional_patient_links", default=[])
    ativos = sorted([l for l in links if l.get("status") == "accepted"], key=lambda x: x.get("patient_name", "").lower())
    pendentes = sorted([l for l in links if l.get("status") == "pending"], key=lambda x: x.get("patient_name", "").lower())

    # Junta vínculos aceitos e pendentes, adicionando a descrição de status.
    todos = [
        {"Nome do Paciente": l.get("patient_name", "—"), "Status": "Ativo"}
        for l in ativos
    ] + [
        {"Nome do Paciente": l.get("patient_name", "—"), "Status": "Pendente"}
        for l in pendentes
    ]

    # Ordena a lista combinada por nome do paciente
    todos_ordenados = sorted(todos, key=lambda x: x["Nome do Paciente"].lower())

    # Exibe tabela única
    if todos_ordenados:
        st.markdown("#### Vínculos ativos")
        st.table(todos_ordenados)
    else:
        st.info("⚠️ Nenhum paciente vinculado.")

    st.markdown("#### Enviar convites de vinculação")

    with st.form("form_vinculo_paciente"):

        email = st.text_input("Digite o email do paciente")
        feedback = st.empty()
        
        if feedback_machine == FeedbackState.LINK_SENT.value:
            st.success("✅ Convite de vinculação enviado com sucesso!")
            auth_machine.set_variable("feedback", FeedbackState.NONE.value)
    
        enviar = st.form_submit_button("Enviar", use_container_width=True)

        if enviar:
            if not email:
                feedback.warning("⚠️ Informe o e-mail do paciente.")
            else:
                patient_info = fetch_patient_info_by_email(email)
                if not patient_info:
                    feedback.error("❌ Paciente não encontrado. Verifique o email digitado.")
                else:
                    data = {
                        "patient_id": patient_info["auth_user_id"],
                        "patient_name": patient_info["display_name"],
                        "status": "pending"
                    }
                    vinculos = auth_machine.get_variable("professional_patient_links", default=[])
                    ja_existe = any(
                        v["patient_id"] == patient_info["auth_user_id"]
                        for v in vinculos
                    )

                    if ja_existe:
                        feedback.warning("⚠️ Convite de vinculação pendente.")
                    else:
                        sucesso = save_professional_patient_link(auth_machine, data)
                    
                    if sucesso:
                        auth_machine.set_variable("feedback", FeedbackState.LINK_SENT.value)
                        load_links_for_professional(professional_id, auth_machine)
                        st.rerun()
                    else:
                        feedback.error("❌ Não foi possível enviar o convite. Tente novamente.")


# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR CONVITES DE VINCULAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_received_invites(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza o convite de vínculo mais recente recebido por um paciente, com botões para aceitar ou recusar.

    Exibe apenas um convite pendente por vez, priorizando simplicidade de navegação e evitando o uso de chaves dinâmicas no Streamlit.

    Args:
        auth_machine (StateMachine): Máquina de estado do paciente autenticado.

    Calls:
        auth_machine.get_variable(): Recupera variáveis persistidas | instanciado por StateMachine.
        accept_link(): Atualiza status do vínculo para "accepted" | definida em services.professional_patient_link.py.
        reject_link(): Atualiza status do vínculo para "rejected" | definida em services.professional_patient_link.py.
        load_links_for_patient(): Recarrega vínculos após ação | definida em services.professional_patient_link.py.
        st.button(): Renderiza botões de ação na interface | definida no módulo streamlit.
        st.markdown(): Exibe texto com formatação Markdown | definida no módulo streamlit.
        st.rerun(): Reinicia o ciclo do Streamlit para aplicar alterações | definida em streamlit.runtime.

    Returns:
        None.

    """

    feedback_machine = auth_machine.get_variable("feedback", default=FeedbackState.NONE.value)
    feedback = st.empty()
        
    if feedback_machine == FeedbackState.LINK_ACCEPTED.value:
        feedback.success("✅ Convite de vinculação aceito.")
        auth_machine.set_variable("feedback", FeedbackState.NONE.value)
        
    if feedback_machine == FeedbackState.LINK_REJECTED.value:
        feedback.success("❌ Convite de vinculação rejeitado.")
        auth_machine.set_variable("feedback", FeedbackState.NONE.value)

    # Recupera todos os vínculos armazenados e filtra os pendentes
    links = auth_machine.get_variable("patient_links", default=[])
    pendentes = [l for l in links if l.get("status") == "pending"]

    # Se não houver convites pendentes...
    if not pendentes:
        return # Retorna para o fluxo principal.

    # Seleciona apenas o primeiro convite pendente.
    link = pendentes[0]
    nome_profissional = link.get("professional_name", "Profissional desconhecido")
    link_id = link.get("id")
    patient_id = auth_machine.get_variable("user_id")

    # Carrega vínculos, se necessário
    if not auth_machine.get_variable("professional_patient_links"):
        load_links_for_professional(patient_id, auth_machine)

    # Renderiza container com informações do convite e ações
    with st.container():
        st.subheader("**Convite recebido**")
        st.markdown(f"**{nome_profissional} deseja se vincular à você**")

        # Define duas colunas com botões de ação.
        col1, col2 = st.columns(2)

        # Botão para aceitar o convite
        with col1:
            if st.button("Aceitar", key="accept", use_container_width=True):
                sucesso = accept_link(link_id)
                if sucesso:
                    auth_machine.set_variable("feedback", FeedbackState.LINK_ACCEPTED.value)
                    load_links_for_patient(patient_id, auth_machine)
                    st.rerun()
                else:
                    st.error("❌ Erro ao aceitar o convite.")

        # Botão para recusar o convite
        with col2:
            if st.button("Recusar", key="reject", use_container_width=True):
                sucesso = reject_link(link_id)
                if sucesso:
                    auth_machine.set_variable("feedback", FeedbackState.LINK_REJECTED.value)
                    load_links_for_patient(patient_id, auth_machine)
                    st.rerun()
                else:
                    st.error("❌ Erro ao recusar o convite.")