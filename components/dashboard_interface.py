
# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from frameworks.sm                      import StateMachine
from utils.session                      import FeedbackStates, RedirectStates, LoadStates
from utils.context                      import load_session_context
from utils.gender                       import render_header_by_role
from services.links                     import save_links, fetch_patient_info_by_email, accept_link, reject_link
from components.sidebar                 import render_sidebar


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Cria ou recupera uma instância do objeto Logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# 🔌 FUNÇÃO PARA A RENDERIZAR A HOMEPAGE DO APLICATIVO ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

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

    # 🛰️ ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────

    # Cria uma instancia da máquina de redirecionamento (dashboard).
    dashboard_redirect_machine = StateMachine("dashboard_redirect", RedirectStates.REDIRECT.value, enable_logging=True)
    
    # Se a máquina de redirecionamento estiver ligada...
    if dashboard_redirect_machine.current:
        dashboard_redirect_machine.to(RedirectStates.REDIRECTED.value, True) # ⬅ Desativa a flag e força a reincialização da interface.


    # 🚧 RENDERIZAÇÃO CONFORME PAPEL DO USUÁRIO ─────────────────────────────────────────────────────────────────────────────────────────

    # Recupera o papel do usuário da máquina de autenticação.
    role = auth_machine.get_variable("role")

    # Se o usuário for um profissional...
    if role == "professional":
        _render_professional_homepage(auth_machine) # ⬅ Desenha a homepage do profissional.
        
    # Caso contrário...
    else:
        _render_patient_homepage(auth_machine) # ⬅ Desenha a homepage do paciente.

    # Desenha a sidebar do aplicativo.
    render_sidebar(auth_machine)

    return None, None


# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR A DASHBOARD DO PROFISSIONAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

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

    # 🏠 HOMEPAGE/DASHBOARD ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Define as abas disponíveis.
    tabs = st.tabs(["Pacientes", "Agenda", "Planejamento"])
    

    # ABA DE VÍNCULOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Desenha a aba de vínculos.
    with tabs[0]:
        render_header_by_role(auth_machine)
        _render_professional_link_interface(auth_machine)
        

    # ABA DE COMPROMISSOS E AGENDAMENTOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with tabs[1]:
        st.write("Acompanhamento de escalas e metas...")
        

    # ABA DE PLANEJAMENTO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with tabs[2]:
        st.write("Status da assinatura e fatura...")
        
    return None, None


# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR A DASHBOARD DO PACIENTE ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_homepage(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza as abas da interface destinadas a usuários pacientes.

    Args:
        auth_machine (StateMachine): Instância da máquina de estados com dados do usuário autenticado.

    Calls:
        auth_machine.get_variable(): Método para obter variáveis da máquina de estados | instanciado por auth_machine.
        load_links_for_patient(): Função para carregar os vínculos do paciente | definida em services.links.py.
        st.tabs(): Componente de abas para navegação | definida em streamlit.
        render_header_by_role(): Função que desenha o cabeçalho conforme o perfil | definida em components.dashboard_interface.py.
        st.markdown(): Função para renderizar texto com HTML | definida em st.
        render_received_invites(): Função que exibe convites recebidos | definida em components.dashboard_interface.py.
        st.image(): Função para exibir imagem na interface | definida em st.

    Returns:
        None: Não retorna nenhum valor. Executa efeitos colaterais na interface.
    """

    # 🛰️ ESTABILIZAÇÃO PROATIVA DA INTERFACE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Cria a máquina de redirecionamento (dahsboard).
    redirect_machine = StateMachine("dashboard_redirect", RedirectStates.REDIRECT.value, enable_logging=True)
    
    # Se a máquina de redirecionamento estiver ligada...
    if redirect_machine.current:
        redirect_machine.to(RedirectStates.REDIRECTED.value, True) # ⬅ Desativa a flag e força a reinicialização da interface.
    

    # 🏠 HOMEPAGE/DASHBOARD ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Define as abas da homepage do paciente.
    tabs = st.tabs(["Início", "Planner", "Notas"])


    # ABA DE BOAS VINDAS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Desenha a aba de boas vindas.
    with tabs[0]:
        render_header_by_role(auth_machine)  # ⬅ Cabeçalho com base no perfil do usuário.
        st.markdown(
            "Cada jornada é única — <strong>como a sua</strong>. <br>"
            "Use seu tempo, no seu ritmo.",
            unsafe_allow_html=True
        )
        render_received_invites(auth_machine)
        st.image("assets/homepage.png", use_container_width=True)


    # ABA DE ORGANIZAÇÃO E PLANEJAMENTO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


    # ABA DE ANOTAÇÕES ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


# 📺 FUNÇÃO AUXILIAR PARA RENDERIZAR A INTERFACE DE VÍNCULOS PARA O PROFISSIONAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_link_interface(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza o painel de vínculos ativos, pendentes e o formulário de convite via e-mail.

    Args:
        auth_machine (StateMachine): Máquina de estado com o ID do profissional autenticado.

    Calls:
        load_links_for_professional(): Busca vínculos do profissional | definida em services.links.py.
        save_links(): Cria novo vínculo com paciente | definida em services.links.py.
        fetch_patient_info_by_email(): Busca dados do paciente pelo e-mail | definida em services.patients.py.

    Returns:
        None.

    """
    
    # Cria ou recupera a máquina de feedbacks.
    feedback_machine = auth_machine.get_variable("feedback", default=FeedbackStates.NONE.value)
    

    # Obtém vínculos e organiza por status
    links = auth_machine.get_variable("links", default=[])
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
    
    st.divider()

    st.markdown("##### 📩 Vincular pacientes")

    with st.form("form_vinculo_paciente"):

        email = st.text_input("Digite o email do paciente")
        feedback = st.empty()
        
        if feedback_machine == FeedbackStates.LINK_SENT.value:
            st.success("✅ Convite de vinculação enviado com sucesso!")
            auth_machine.set_variable("feedback", FeedbackStates.NONE.value)
    
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
                    vinculos = auth_machine.get_variable("links", default=[])
                    ja_existe = any(
                        v["patient_id"] == patient_info["auth_user_id"]
                        for v in vinculos
                    )

                    if ja_existe:
                        feedback.warning("⚠️ Convite de vinculação pendente.")
                    else:
                        sucesso = save_links(auth_machine, data)
                    
                    if sucesso:
                        auth_machine.set_variable("feedback", FeedbackStates.LINK_SENT.value)
                        load_session_context(auth_machine)
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
        accept_link(): Atualiza status do vínculo para "accepted" | definida em services.links.py.
        reject_link(): Atualiza status do vínculo para "rejected" | definida em services.links.py.
        load_links_for_patient(): Recarrega vínculos após ação | definida em services.links.py.
        st.button(): Renderiza botões de ação na interface | definida no módulo streamlit.
        st.markdown(): Exibe texto com formatação Markdown | definida no módulo streamlit.
        st.rerun(): Reinicia o ciclo do Streamlit para aplicar alterações | definida em streamlit.runtime.

    Returns:
        None.

    """
    
    # Cria ou recupera a máquina de vínculos (default: load).
    link_machine = StateMachine("link_machine", LoadStates.LOAD.value, enable_logging=True)
    
    feedback_machine = auth_machine.get_variable("feedback", default=FeedbackStates.NONE.value)   
    feedback = st.empty()
            
    if feedback_machine == FeedbackStates.LINK_ACCEPTED.value:
        feedback.success("✅ Convite de vinculação aceito.")
        st.markdown("<br>", unsafe_allow_html=True)
        auth_machine.set_variable("feedback", FeedbackStates.NONE.value)
            
    if feedback_machine == FeedbackStates.LINK_REJECTED.value:
        feedback.success("❌ Convite de vinculação rejeitado.")
        st.markdown("<br>", unsafe_allow_html=True)
        auth_machine.set_variable("feedback", FeedbackStates.NONE.value)

    # Recupera todos os vínculos armazenados e filtra os pendentes
    links = auth_machine.get_variable("links", default=[])
    pendentes = [l for l in links if l.get("status") == "pending"]

    # Se não houver convites pendentes...
    if not pendentes:
        return # Retorna para o fluxo principal.

    # Seleciona apenas o primeiro convite pendente.
    link = pendentes[0]
    nome_profissional = link.get("professional_name", "Profissional desconhecido")
    link_id = link.get("id")

    # Carrega vínculos, se necessário
    if not auth_machine.get_variable("links"):
        link_machine.reset()
        load_session_context(auth_machine)

    # Renderiza container com informações do convite e ações
    with st.container():
        st.divider()
        st.markdown("##### 📩 Convite recebido")
        st.markdown(f"**{nome_profissional} deseja se vincular à você**")

        # Define duas colunas com botões de ação.
        col1, col2 = st.columns(2)

        # Botão para aceitar o convite
        with col1:
            if st.button("Aceitar", key="accept", use_container_width=True):
                sucesso = accept_link(link_id)
                if sucesso:
                    auth_machine.set_variable("feedback", FeedbackStates.LINK_ACCEPTED.value)
                    link_machine.reset()
                    load_session_context(auth_machine)
                    st.rerun()
                else:
                    st.error("❌ Erro ao aceitar o convite.")

        # Botão para recusar o convite
        with col2:
            if st.button("Recusar", key="reject", use_container_width=True):
                sucesso = reject_link(link_id)
                if sucesso:
                    auth_machine.set_variable("feedback", FeedbackStates.LINK_REJECTED.value)
                    link_machine.reset()
                    load_session_context(auth_machine)
                    st.rerun()
                else:
                    st.error("❌ Erro ao recusar o convite.")
        
    st.markdown("<br>", unsafe_allow_html=True)