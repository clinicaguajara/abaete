
# 📦 IMPORTAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from frameworks.sm                      import StateMachine
from utils.variables.session            import FeedbackStates, RedirectStates, LoadStates
from utils.load.context                 import load_session_context
from utils.gender                       import render_helloworld
from services.links                     import save_links, fetch_patient_info_by_email, accept_link, reject_link
from components.sidebar                 import render_sidebar


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Cria ou recupera uma instância do objeto Logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# 🔌 ENTRYPOINT DA INTERFACE DO PAINEL PRINCIPAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def dashboard_interface_entrypoint(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a dashboard com tabs específicas para profissionais ou pacientes.

    Args:
        auth_machine (StateMachine): Instância da máquina de autenticação.

    Calls:
        render_header_by_role(): Renderiza cabeçalho personalizado | definida em utils/gender.py.
        is_professional_user(): Verifica se o usuário é profissional | definida em dashboard_interface.py.
        _render_professional_tabs(): Tabs exclusivas para profissionais | definida em dashboard_interface.py.
        _render_patient_tabs(): Tabs exclusivas para pacientes | definida em dashboard_interface.py.

    Returns:
        None.
            
    """

    # 🛰️ ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────

    # Cria uma instancia da máquina de redirecionamento (default: True).
    redirect_machine = StateMachine("dashboard_redirect_state", RedirectStates.REDIRECT.value, enable_logging=True)
    
    # Se a máquina de redirecionamento estiver ligada...
    if redirect_machine.current:
        redirect_machine.to(RedirectStates.REDIRECTED.value, True) # ⬅ Desativa a flag e força rerun().


    # 📶 ROTEAMENTO CONFORME PAPEL DO USUÁRIO ─────────────────────────────────────────────────────────────────────────────────────────

    # Recupera o papel do usuário da máquina de autenticação.
    role = auth_machine.get_variable("role")

    # Se o usuário for um profissional...
    if role == "professional":
        _render_professional_dashboard(auth_machine) # ⬅ Desenha a homepage do profissional.
        
    # Caso contrário...
    else:
        _render_patient_dashboard(auth_machine) # ⬅ Desenha a homepage do paciente.

    # Desenha a sidebar do aplicativo.
    render_sidebar(auth_machine)


# 📺 FUNÇÃO PARA RENDERIZAR A DASHBOARD DO PROFISSIONAL ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_dashboard(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza as abas da interface destinadas a usuários profissionais.

    Args:
        None.

    Calls:
        st.tabs(): Componente de abas para navegação | definida em streamlit.
        st.write(): Escreve conteúdo textual | definida em streamlit.

    Returns:
        None.

    """

    # Desenha as abas da dashboard do profissional.
    tabs = st.tabs(["Pacientes", "Agenda", "Planejamento"])
    

    # 🔗 ABA DE VÍNCULOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Desenha a aba de vínculos.
    with tabs[0]:
        render_helloworld(auth_machine)
        _render_professional_link_interface(auth_machine)
        

    # 📆 ABA DE PLANEJAMENTO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with tabs[1]:
        st.write("Acompanhamento de escalas e metas...")
        

    # 📝 ABA DE PLANEJAMENTO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with tabs[2]:
        st.write("Status da assinatura e fatura...")


# 📺 FUNÇÃO PARA RENDERIZAR A DASHBOARD DO PACIENTE ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_dashboard(auth_machine: StateMachine) -> None:
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

    # Desenha as abas da dashboard do paciente.
    tabs = st.tabs(["Painel", "Planner", "Anotações"])


    # 🔗 ABA DE VÍNCULOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Ativa a aba de boas vindas.
    with tabs[0]:
        _render_patient_link_interface(auth_machine)


    # 📆 ABA DE PLANEJAMENTO ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Ativa a aba de planejamento.
    with tabs[1]:
        st.write("Seu planejamento semanal, diário e mensal...")


    # 📝 ABA DE ANOTAÇÕES ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Ativa a aba de anotações.
    with tabs[2]:
        st.write("Anotações importantes...")


# 🔗 FUNÇÃO AUXILIAR PARA RENDERIZAR A INTERFACE DE VÍNCULOS DO PROFISSIONAL ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

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
    
    # Cria ou recupera a máquina de feedbacks (deafult: True).
    feedbacks_machine = StateMachine("feedback_state", FeedbackStates.CLEAR.value, enable_logging = True)
    
    # Obtém vínculos do profissional e organiza por status do convite.
    links = auth_machine.get_variable("links", default=[])
    active = sorted([l for l in links if l.get("status") == "accepted"], key=lambda x: x.get("patient_name", "").lower())
    pending = sorted([l for l in links if l.get("status") == "pending"], key=lambda x: x.get("patient_name", "").lower())
    rejected = sorted([l for l in links if l.get("status") == "rejected"], key=lambda x: x.get("patient_name", "").lower())

    # Reúne vínculos aceitos, rejeitados e pendentes, adicionando a descrição de status na UX.
    active_pending = [
        {"Nome do Paciente": l.get("patient_name", "—"), "Status": "Ativo"}
        for l in active
    ] + [
        {"Nome do Paciente": l.get("patient_name", "—"), "Status": "Pendente"}
        for l in pending
    ] + [
        {"Nome do Paciente": l.get("patient_name", "—"), "Status": "Rejeitado"}
        for l in rejected
    ]

    # Ordena a lista combinada de forma alfabética.
    sorted_links = sorted(active_pending, key=lambda x: x["Nome do Paciente"].lower())

    # Se houver lista ordenada...
    if sorted_links:
        st.markdown("#### Vínculos ativos") # ⬅ Desenha o subtítulo da sessão.
        st.table(sorted_links)              # ⬅ Desenha a tabela de vínculos do profissional, completa.
    
    # Caso contrário...
    else:
        st.info("⚠️ Nenhum paciente vinculado.")
    
    st.divider()

    # Desenha o subtítulo da sessão.
    st.markdown("#### 📩 Vincular pacientes")

    # Desenha o formulário de vinculação.
    with st.form("form_vinculo_paciente"):

        # Campo de preenchimento do formulário.
        email = st.text_input("Digite o email do paciente")
        
        # Placeholder para feedback visual.
        feedback = st.empty()
        
        # Se a máquina de feedbacks estiver ligada...
        if feedbacks_machine.current:
            st.success("✅ Convite de vinculação enviado com sucesso!")
            auth_machine.set_variable("feedback", FeedbackStates.DONE.value)

        # Desenha o botão do formulário de vinculação.
        enviar = st.form_submit_button("Enviar", use_container_width=True)

        # Se o botão for apertado..
        if enviar:

            # Se o email não for informado...
            if not email:
                feedback.warning("⚠️ Informe o e-mail do paciente.")
            
            # Caso contrário...
            else:
                patient_info = fetch_patient_info_by_email(email)
                
                # Se não houver paciente cadastrado no sistema...
                if not patient_info:
                    feedback.error("❌ Paciente não encontrado. Verifique o email digitado.")
                
                # Caso contrário...
                else:
                    data = {
                        "patient_id": patient_info["auth_user_id"],           # ⬅ UUID do paciente.
                        "patient_name": patient_info["display_name"],         # ⬅ Nome do paciente.
                        "status": "pending"                                   # ⬅ Status do convite.
                    }                                                           
                    professional_links = auth_machine.get_variable("links", default = []) 
                    already_has = any(
                        v["patient_id"] == patient_info["auth_user_id"]    
                        for v in professional_links
                    )                                                          

                    # Se já houver convite cadastrado...
                    if already_has:
                        feedback.warning("⚠️ Convite de vinculação pendente.")
                    
                    # Caso contrário...
                    else:
                        sucesso = save_links(auth_machine, data)
                    
                    # Se o convite for enviado com sucesso...
                    if sucesso:
                        load_session_context(auth_machine)              # ⬅ Carrega o contexto da sessão.                      
                        feedbacks_machine.to(FeedbackStates.SHOW.value) # ⬅ Transiciona o estado da máquina de feedbacks e força rerun().

                    # Caso contrário...
                    else:
                        feedback.error("❌ Não foi possível enviar o convite de vinculação.")


# 🔗 FUNÇÃO AUXILIAR PARA RENDERIZAR A INTERFACE DE VINCÚLOS DO PACIENTE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_link_interface(auth_machine: StateMachine) -> None:
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
    
    # Desenha o cabeçalho de boas-vindas conforme papel do usuário e gênero.
    render_helloworld(auth_machine)
        
    # Desenha o texto conceitual da aba.
    st.markdown(
        "Cada jornada é única — <strong>como a sua</strong>. <br>"
        "Use seu tempo, no seu ritmo.",
        unsafe_allow_html=True
    )

    # Cria ou recupera a máquina de vínculos (default: True).
    link_machine = StateMachine("link_state", LoadStates.LOAD.value, enable_logging=True)
    
    # Cria ou recupera a máquina de feedbacks (default: None).
    feedback_machine = StateMachine("feedback_state", FeedbackStates.CLEAR.value, enable_logging=True)
    
    # Placeholder para feedback visual.
    feedback = st.empty()

    # Se o estado atual da máquina de feedbacks for "accepted"...
    if feedback_machine.get_variable("response", default = None) == FeedbackStates.ACCEPTED.value:
        feedback.success("✅ Convite de vinculação aceito.")
        st.markdown("<br>", unsafe_allow_html=True)
        feedback_machine.set_variable("response", FeedbackStates.DONE.value)
            
    if feedback_machine.get_variable("response", default = None) == FeedbackStates.REJECTED.value:
        feedback.success("❌ Convite de vinculação rejeitado.")
        st.markdown("<br>", unsafe_allow_html=True)
        feedback_machine.set_variable("response", FeedbackStates.DONE.value)

    # Recupera todos os vínculos armazenados e filtra os pendentes
    links = auth_machine.get_variable("links", default=[])
    pending_invites = [l for l in links if l.get("status") == "pending"]

    # Se não houver convites pendentes...
    if not pending_invites:
        return # Retorna para o fluxo principal.

    # Seleciona apenas o primeiro convite pendente.
    link = pending_invites[0]
    nome_profissional = link.get("professional_name", "Profissional desconhecido")
    link_id = link.get("id")

    # Ativa um container persistente para adicionar elementos.
    with st.container():

        # Desenha o convite de vinculação.
        st.divider()
        st.markdown("#### 📩 Convite recebido")
        st.markdown(f"**{nome_profissional} deseja se vincular à você**")

        # Define duas colunas com botões de ação.
        col1, col2 = st.columns(2)

        # Ativa a primeira coluna.
        with col1:

            # Se o botão "Aceitar" for pressionado...
            if st.button("Aceitar", key="accept", use_container_width=True):
                done = accept_link(link_id)
                
                # Se o aceite for efetuado com sucesso...
                if done:
                    auth_machine.set_variable("feedback", FeedbackStates.LINK_ACCEPTED.value)
                    link_machine.reset()
                    load_session_context(auth_machine)
                    st.rerun()
                
                # Caso contrário...
                else:
                    st.error("❌ Erro ao aceitar o convite.")

        # Ativa a segunda coluna.
        with col2:

            # Se o botão "Recusar" for pressionado...
            if st.button("Recusar", key="reject", use_container_width=True):
                done = reject_link(link_id)
                
                # Se a recusa for efetuada com sucesso...
                if done:
                    auth_machine.set_variable("feedback", FeedbackStates.LINK_REJECTED.value)
                    link_machine.reset()
                    load_session_context(auth_machine)
                    st.rerun()
                
                # Caso contrário...
                else:
                    st.error("❌ Erro ao recusar o convite.")
        
    st.markdown("<br>", unsafe_allow_html=True)

    st.image("assets/homepage.png", use_container_width=True)