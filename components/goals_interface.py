
# 📦 IMPORTAÇÕES NECESSÁRIAS ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import logging
import streamlit as st

from datetime                        import date, datetime
from frameworks.sm                   import StateMachine
from utils.variables.session         import FeedbackStates, RedirectStates
from services.goals                  import load_goals_by_link_id, save_goal
from services.goals_progress         import load_goal_progress, save_goal_progress
from services.links                  import load_links_for_professional
from components.sidebar              import render_sidebar
from components.charts.goals_charts  import render_goal_progress_chart, estimate_completion_time


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Cria ou recupera uma instância do objeto Logger com o nome do módulo atual.
logger = logging.getLogger(__name__)


# 🔌 FUNÇÃO PARA RENDERIZAR A INTERFACE DE METAS ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_goals_interface(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a interface da página "Minhas Metas", com variações para profissional e paciente.

    Args:
        auth_machine (StateMachine): Instância da máquina de estados com os dados do usuário autenticado.

    Calls:
        StateMachine(): Cria uma máquina de estados auxiliar para controle da navegação | definida em frameworks.sm.py.
        goals_redirect_machine.current: Atributo da máquina de estados para verificar o estado atual | instanciado por goals_redirect_machine.
        goals_redirect_machine.to(): Método para transicionar o estado da máquina | instanciado por goals_redirect_machine.
        logger.info(): Função para registrar logs de informações | definida em utils.logs.py.
        st.markdown(): Função para renderizar texto com HTML | definida em streamlit.
        is_professional_user(): Função que verifica se o usuário autenticado é profissional | definida em modules.user_profile.py.
        _render_professional_goals(): Renderiza a interface de metas para profissionais | definida em 2_Minhas_Metas.py.
        _render_patient_goals(): Renderiza a interface de metas para pacientes | definida em 2_Minhas_Metas.py.
        render_sidebar(): Renderiza a barra lateral da interface | definida em components.dashboard_interface.py.

    Returns:
        None: Não retorna nenhum valor. Executa efeitos colaterais na interface.
    """

    # 🛰️ ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Cria a máquina de redirecionamento (default: True).
    redirect_machine = StateMachine("goals_redirect", RedirectStates.REDIRECT.value, enable_logging=True)

    # Se a máquina de redirecionamento estiver ligada...
    if redirect_machine.current: 
        redirect_machine.to(RedirectStates.REDIRECTED.value, True) # ⬅ Desliga a máquina de redirecionamento e força rerun().


    # 📶 ROTEIA CONFORME PAPEL DO USUÁRIO ───────────────────────────────────────────────────────────────────────────────────────────────────

    # Recupera o papel do usuário da máquina de autenticação.
    role = auth_machine.get_variable("role")

    # Se o usuário for um profissional...
    if role == "professional":
        _render_professional_goals(auth_machine) # ⬅ Desenha a interface de metas do profissional.
    
    # Caso contrário...
    else:
        _render_patient_goals(auth_machine) # ⬅ Desenha a interface de metas do paciente.

    # Desenha a sidebar.
    render_sidebar(auth_machine)


# 📺 FUNÇÃO PARA RENDERIZAR AS TABS DO PROFISSIONAL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_goals(auth_machine: StateMachine) -> None:
    """
    Exibe dois painéis principais:
    - Um formulário funcional para cadastro de metas.
    - Um painel reservado para futuras visualizações de histórico.

    Args:
        auth_machine (StateMachine): Instância da máquina de estado com dados do usuário profissional.

    Calls:
        auth_machine.get_variable(): Recupera variáveis de estado persistentes | instanciado por StateMachine.
        auth_machine.set_variable(): Armazena variáveis locais do frontend | instanciado por StateMachine.
        load_links_for_professional(): Carrega vínculos ativos com pacientes | definida em services.professional_patient_link.py.
        load_goals_by_link_id(): Recarrega metas após inserção | definida em services.goals.py.
        save_goal(): Salva meta na tabela `goals` do Supabase | definida em services.goals.py.
        st.selectbox(): Componente de seleção de opções | definida no módulo streamlit.
        st.select_slider(): Componente de slider com rótulos personalizados | definida no módulo streamlit.
        st.form(): Formulário com validação integrada | definida no módulo streamlit.
        st.rerun(): Reinicializa o ciclo do Streamlit após submissão | definida em streamlit.runtime.

    Returns:
        Tuple[None, str | None]: 
            - None: Em caso de execução bem-sucedida.
            - str | None: Mensagem de erro em caso de falha.

    """

    # Cria ou recupera a máquina de feedbacks (default: None).
    feedback_machine = auth_machine.get_variable("feedback", default=FeedbackStates.CLEAR.value)

    # Desenha as abas da sessão de metas do profissional.
    tabs = st.tabs(["Cadastrar metas", "Monitorar histórico de metas"])

    
    # ABA DE ATIBUIÇÃO DE METAS PARA PACIENTES ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with tabs[0]:
        st.subheader("Cadastrar metas")

        # Carrega vínculos se ainda não estiverem armazenados.
        if not auth_machine.get_variable("professional_patient_links"):
            professional_id = auth_machine.get_variable("user_id")
            load_links_for_professional(professional_id, auth_machine)

        # Recupera vínculos aceitos.
        links = auth_machine.get_variable("professional_patient_links", default=[])
        accepted_links = [l for l in links if l.get("status") == "accepted"]

        # Caso não haja pacientes vinculados.
        if not accepted_links:
            st.info("⚠️ Nenhum paciente vinculado.")
            return None, None

        # Mapeia nomes → link_id.
        patient_names = [l["patient_name"] for l in accepted_links]
        link_map = {l["patient_name"]: l["id"] for l in accepted_links}

        # Formulário para cadastrar nova meta.
        with st.form("form_create_goal"):
            patient_name = st.selectbox("Paciente", patient_names)
            description = st.text_area("Descrição", placeholder="E.g., Praticar mindfulness diariamente.")
            timeframe = st.selectbox("Qual é o prazo de conclusão da meta?", ["Curto", "Médio", "Longo"])
            effort_type = st.selectbox("Tipo de meta", ["Acadêmica", "Profissional", "Saúde & Bem-estar", "Intrapessoal", "Relacional"])

            # Slider visual invertido: 1 (high priority) à direita.
            display_priorities = [5, 4, 3, 2, 1]
            priority_display = st.select_slider(
                "Nível de prioridade",
                options=display_priorities,
                value=3,
                format_func=lambda x: f"{x}"
            )
            priority_level = 6 - priority_display  # ← inverte visual para valor real.
                
            if feedback_machine == FeedbackStates.GOAL_SENT.value:
                st.success("✅ Meta cadastrada com sucesso!")
                auth_machine.set_variable("feedback", FeedbackStates.NONE.value)

            feedback = st.empty()

            submit = st.form_submit_button("Cadastrar", use_container_width=True)

        # Validação dos campos obrigatórios.
        if submit:
            missing = []
            if not patient_name: missing.append("Patient")
            if not description.strip(): missing.append("Description")
            if not timeframe: missing.append("Timeframe")
            if not effort_type: missing.append("Effort type")
                
            if missing:
                feedback.warning(f"⚠️ Preencha todos os campos corretamente.")

            else:
                    
                # Interface → valor interno
                prazo_map = {
                    "Curto": "curto",
                    "Médio": "medio",
                    "Longo": "longo"
                }

                payload = {
                    "goal": description.strip(),
                    "timeframe": prazo_map[timeframe],
                    "effort_type": effort_type.lower(),
                    "priority_level": priority_level,
                    "link_id": link_map[patient_name]
                }
                success = save_goal(payload)

                if success:
                    auth_machine.set_variable("feedback", FeedbackStates.GOAL_SENT.value)
                    load_goals_by_link_id(payload["link_id"], auth_machine)
                    st.rerun()
                else:
                    feedback.error("❌ Falha ao salvar meta, tente novamente.")


    # ABA DE MONITORAMENTO DE METAS DOS PACIENTES ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    with tabs[1]:
        st.write("Monitoring of patients’ goals will be available here soon.")

        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)


# 📺 FUNÇÃO PARA RENDERIZAR AS TABS DO PACIENTE ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_goals(auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a seção de metas voltada a pacientes com formulário de progresso e histórico diário.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do paciente.

    Returns:
        Tuple[None, str | None]: Resultado da operação.
    """
    
    # Recupera os vínculos do paciente com profissionais responsáveis.
    links = auth_machine.get_variable("links", default=[])

    # Desenha as abas da interface de metas do paciente.
    abas = st.tabs(["Curto", "Médio", "Longo prazo"])

    # Se não houver vínculos, exibir aviso dentro de todas as abas.
    if len(links) == 0:
        for aba in abas:
            with aba:
                st.warning("⚠️ Nenhum profissional vinculado ao seu perfil.")
        return

    # Caso múltiplos vínculos (não implementado ainda)
    if len(links) > 1:
        for aba in abas:
            with aba:
                st.info("ℹ️ Essa funcionalidade será implementada no futuro (vários vínculos detectados).")
        return

    # Vínculo único
    link_id = links[0].get("id")


    # CARREGAMENTO DE METAS E PROGRESSO ────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Carrega metas apenas se necessário
    if not auth_machine.get_variable("goals"):
        load_goals_by_link_id(link_id, auth_machine)
    
    metas = auth_machine.get_variable("goals", default=[])

    # Carrega todo o progresso de uma vez, a cada rerun().
    load_goal_progress(link_id=link_id, auth_machine=auth_machine)

    # Organiza metas por timeframe.
    timeframe_map = {"curto": [], "medio": [], "longo": []}
    
    # Para cada meta em metas...
    for meta in metas:
        tf = meta.get("timeframe", "").lower() # ⬅ Obtém o prazo da meta em minúsculas.
        
        # Se o prazo obtido estiver no mapeamento de prazos...
        if tf in timeframe_map:
            timeframe_map[tf].append(meta) # ⬅ Adiciona a meta à lista correspondente.

    
    # RENDERIZAÇÃO DAS ABAS DINAMICAMENTE ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Define uma lista ordenada de prazos para renderizar metas dinamicamente nas abas corretas.
    prazos = ["curto", "medio", "longo"]

    # Para cada prazo na ordem definida, e seu índice correspondente i...
    for i, prazo in enumerate(prazos):
        
        # Ativa a aba de índice i.
        with abas[i]:
            metas_do_prazo = timeframe_map.get(prazo, [])
            if not metas_do_prazo:
                st.info("Nenhuma meta definida para esse prazo.")
                continue

            for meta in metas_do_prazo:
                goal_id = meta["id"]
                descricao = meta.get("goal", "Meta sem descrição")
                created_at = meta.get("created_at")

                progresso = auth_machine.get_variable(f"goal_progress__{goal_id}", default=[])
                hoje = str(date.today())
                registrado_hoje = any(p["date"] == hoje for p in progresso)

                with st.expander(descricao):
                    st.markdown("<br>", unsafe_allow_html=True)

                    if created_at:
                        try:
                            dt = datetime.fromisoformat(created_at)
                            st.write(f"Criada em: 🗓️ **{dt.strftime('%d/%m/%Y')}**")
                        except:
                            st.write("Data de criação indisponível")
                    else:
                        st.write("Data de criação não informada")

                    effort_type = (meta.get("effort_type") or "—").lower()
                    priority = meta.get("priority_level", "—")
                    st.write(f"**Meta do tipo {effort_type} e nível de prioridade #{priority}**")

                    if registrado_hoje:
                        st.info("Parabéns, você concluiu essa meta hoje!")
                    else:
                        with st.form(f"form_{goal_id}"):
                            mood_labels = {
                                1: "Muito ruim", 2: "Ruim", 3: "Regular", 4: "Bom", 5: "Ótimo"
                            }
                            mood_label = st.selectbox(
                                "Como você se sentiu hoje?",
                                options=list(mood_labels.values()),
                                index=2,
                                key=f"mood_{goal_id}"
                            )
                            mood = next(score for score, label in mood_labels.items() if label == mood_label)

                            duration = st.number_input(
                                "Tempo de dedicação, em minutos",
                                min_value=0, max_value=1440, value=60, step=5,
                                key=f"dur_{goal_id}"
                            )

                            feedback = st.empty()
                            if st.form_submit_button("Concluir", use_container_width=True):
                                payload = {
                                    "goal_id": goal_id,
                                    "link_id": link_id,
                                    "date": hoje,
                                    "completed": True,
                                    "duration_minutes": duration,
                                    "mood_rating": mood
                                }
                                result = save_goal_progress(payload)
                                if result:
                                    st.rerun()
                                else:
                                    feedback.error("Erro ao registrar progresso. Tente novamente.")
                        
                    col1, col2 = st.columns([200, 1])
                    with col1:
                        render_goal_progress_chart(goal_id, auth_machine)
                    estimate_completion_time(goal_id, auth_machine)
                    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

