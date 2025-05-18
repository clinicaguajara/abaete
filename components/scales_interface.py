import logging
import streamlit as st

from frameworks.sm import StateMachine
from utils.role import is_professional_user
from services.professional_patient_link import load_links_for_professional, load_links_for_patient
from datetime import date
from utils.design import render_scales_header

logger = logging.getLogger(__name__)


def render_scales_interface(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a interface da aba "Escalas Psicossociais" com abas separadas para profissional e paciente.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do usuário autenticado.

    Calls:
        StateMachine("auth_redirect", True): Inicializa flag de redirecionamento | instanciado por frameworks.sm.StateMachine.
        render_abaete_header(): Renderiza cabeçalho padrão da aplicação | definida em utils.design.
        is_professional_user(): Verifica perfil de usuário | definida em utils.role.
        render_professional_scales(): Abre interface de escalas para profissionais | definida neste módulo.
        render_patient_scales(): Abre interface de escalas para pacientes | definida neste módulo.

    Returns:
        tuple[None, str | None]:
            - None: Se execução for bem-sucedida.
            - str | None: Mensagem de erro em caso de falha.
    """
    
    # ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    redirect = StateMachine("auth_redirect", True)
        
    if redirect.current:
        redirect.to(False, True) # desativa flag.


    # INTERFACE DE AVALIAÇÕES ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Log de entrada na página
    logger.info("Desenhando a interface de avaliações.")
    
    # Cabeçalho
    render_scales_header()
    st.write("As avaliações psicométricas no Abaeté não são apenas instrumentos de medida — são pontos de encontro entre a escuta e a precisão. Compreendemos que cada resposta carrega um ritmo, uma raiz, uma história. Por isso, tratamos cada processo com o cuidado de quem reconhece que crescer também é se reconhecer. Aqui, avaliar é um gesto de atenção: firme na metodologia, suave na presença.")
    
    # Roteamento por perfil de usuário
    if is_professional_user(auth_machine):
        return render_professional_scales(auth_machine)
    else:
        return render_patient_scales(auth_machine)


def render_professional_scales(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a interface de escalas para profissionais.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do usuário profissional.

    Calls:
        st.tabs(): Cria abas de navegação | instanciado por streamlit.
        load_links_for_professional(): Carrega vínculos ativos | definida em services.professional_patient_link.
        load_available_scales(): Carrega definições de escalas disponíveis | definida em services.available_scales.
        save_scale_assignment(): Persiste atribuição de escala | definida em services.scales.
        st.form(): Inicia formulário | instanciado por streamlit.
        st.selectbox(), st.form_submit_button(): Controles de formulário | instanciados por streamlit.
        st.success(), st.error(), st.info(): Feedback visual | instanciados por streamlit.

    Returns:
        tuple[None, str | None]:
            - None: Se execução for bem-sucedida.
            - str | None: Mensagem de erro em caso de falha.
    """
    # Abas dedicadas ao profissional
    tabs = st.tabs(["Avaliações", "Visualizar resultados", "Evolução"])
    with tabs[0]:
        st.subheader("Atribuir instrumentos")

        # Carrega vínculos se ainda não estiverem em memória
        if not auth_machine.get_variable("professional_patient_links"):
            user_id = auth_machine.get_variable("user_id")
            load_links_for_professional(user_id, auth_machine)

        # Carrega definições de escalas
        if not auth_machine.get_variable("available_scales"):
            from services.available_scales import load_available_scales
            load_available_scales(auth_machine)

        # Recupera dados de links e escalas
        links = auth_machine.get_variable("professional_patient_links", default=[])
        escalas = auth_machine.get_variable("available_scales", default=[])

        # Filtra apenas links aceitos
        links_ativos = [l for l in links if l.get("status") == "accepted"]
        if not links_ativos:
            st.info("⚠️ Nenhum paciente vinculado.")
            return None, None

        # Mapas para populamento de controles
        nomes = [l["patient_name"] for l in links_ativos]
        mapa_links = {l["patient_name"]: l["id"] for l in links_ativos}
        nomes_escalas = [e["scale_name"] for e in escalas]
        mapa_escalas = {e["scale_name"]: e["id"] for e in escalas}

        # Formulário de atribuição
        with st.form("form_atribuicao_escala"):
            nome = st.selectbox("Paciente", nomes)
            escala = st.selectbox("Escala", nomes_escalas)
            enviar = st.form_submit_button("Atribuir", use_container_width=True)

        # Ação de submissão
        if enviar:
            from services.scales import save_scale_assignment
            payload = {
                "link_id": mapa_links[nome],
                "scale_id": mapa_escalas[escala],
                "scale_name": escala
            }
            sucesso = save_scale_assignment(payload)
            if sucesso:
                st.success("✅ Escala atribuída com sucesso!")
            else:
                st.error("❌ Não foi possível atribuir a escala.")

    return None, None


def render_patient_scales(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a interface de escalas para pacientes com abas para responder, histórico e resumo.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do paciente.

    Calls:
        load_links_for_patient(): Carrega vínculos do paciente | definida em services.professional_patient_link.
        st.warning(), st.info(): Feedback visual | instanciado por streamlit.
        st.tabs(): Cria abas de navegação | instanciado por streamlit.
        render_scales(): Renderiza perguntas interativas | definida neste módulo.

    Returns:
        tuple[None, str | None]:
            - None: Se execução for bem-sucedida.
            - str | None: Mensagem de erro em caso de falha.
    """
    # Carrega vínculos se necessário
    patient_id = auth_machine.get_variable("user_id")
    if not auth_machine.get_variable("patient_links"):
        load_links_for_patient(patient_id, auth_machine)

    # Valida existência de vínculo
    links = auth_machine.get_variable("patient_links", default=[])

    # Cria abas antes da validação
    tabs = st.tabs(["Responder avaliações", "Histórico", "Resumo"])

    # Nenhum vínculo
    if len(links) == 0:
        for tab in tabs:
            with tab:
                st.warning("⚠️ Nenhum profissional vinculado ao seu perfil.")
        return None, None

    # Múltiplos vínculos (ainda não implementado)
    if len(links) > 1:
        for tab in tabs:
            with tab:
                st.info("ℹ️ Essa funcionalidade será implementada no futuro (vários vínculos detectados).")
        return None, None

    # Apenas um vínculo: segue com renderização normal
    with tabs[0]:
        return render_scales(auth_machine)
    with tabs[1]:
        st.info("📅 Histórico de respostas estará disponível em breve.")
    with tabs[2]:
        st.info("📊 Um resumo dos resultados será exibido futuramente.")

    return None, None



def render_scales(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza as escalas atribuídas ao paciente uma pergunta por vez (modo interativo).

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do paciente.

    Calls:
        load_links_for_patient(): Carrega vínculos caso necessário | services.professional_patient_link.
        load_scales_by_link_id(): Busca escalas atribuídas | services.scales.
        load_available_scales(): Busca definições de escalas | services.available_scales.
        load_scale_progress(): Carrega progresso salvo | services.scales_progress.
        render_scale_item_interactive(): Renderiza cada pergunta | definida neste módulo.
        finalize_scale_response(): Finaliza e salva respostas | definida neste módulo.

    Returns:
        tuple[None, str | None]:
            - None: Se execução for bem-sucedida.
            - str | None: Mensagem de erro em caso de falha.
    """
    # Imports locais para reduzir overhead
    from services.professional_patient_link import load_links_for_patient
    from services.scales import load_scales_by_link_id
    from services.scales_progress import load_scale_progress
    from services.available_scales import load_available_scales

    hoje = str(date.today())  # Data de hoje
    user_id = auth_machine.get_variable("user_id")

    # Garantir vínculos antes de processar escalas
    if not auth_machine.get_variable("patient_links"):
        load_links_for_patient(user_id, auth_machine)
    links = auth_machine.get_variable("patient_links", default=[])
    if len(links) == 0:
        st.warning("⚠️ Nenhum profissional vinculado ao seu perfil.")
        return None, None
    if len(links) > 1:
        st.info("ℹ️ Suporte a múltiplos vínculos será implementado futuramente.")
        return None, None

    link_id = links[0]["id"]  # ID do vínculo único

    # Carrega escalas e progresso
    if auth_machine.get_variable("assigned_scales") in (None, [], {}):
        load_scales_by_link_id(link_id, auth_machine)
    if auth_machine.get_variable("available_scales") in (None, [], {}):
        load_available_scales(auth_machine)
    load_scale_progress(link_id=link_id, auth_machine=auth_machine)

    assigned = auth_machine.get_variable("assigned_scales", default=[])
    definicoes = auth_machine.get_variable("available_scales", default=[])
    mapa_definicoes = {e["id"]: e for e in definicoes}

    st.subheader("Escalas atribuídas para hoje")
    alguma_pendente = False  # Flag para detectar pendências

    for escala in assigned:
        scale_id = escala["scale_id"]
        scale_name = escala.get("scale_name", "Escala sem nome")
        progresso = auth_machine.get_variable(f"scale_progress__{scale_id}", default=[])
        respondida_hoje = any(p["date"] == hoje and p.get("completed") for p in progresso)
        if respondida_hoje:
            continue

        estrutura = mapa_definicoes.get(scale_id)
        if not estrutura:
            st.warning(f"⚠️ Estrutura da escala '{scale_name}' não encontrada ou mal formatada.")
            continue

        itens = parse_scale_items(estrutura.get("items"))
        descricao = estrutura.get("description", "")
        if not isinstance(itens, list) or len(itens) == 0:
            st.warning(f"⚠️ Escala '{scale_name}' sem perguntas válidas.")
            continue

        alguma_pendente = True
        with st.expander(f"{scale_name}"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Instruções:** {descricao}", unsafe_allow_html=True)
            render_scale_item_interactive(scale_id, itens, auth_machine)
            if auth_machine.get_variable(f"scale_progress__{scale_id}__done"):
                finalize_scale_response(scale_id, link_id, auth_machine)

    if not alguma_pendente:
        st.success("🎉 Você já respondeu todas as escalas atribuídas para hoje.")

    return None, None


def parse_scale_items(raw_items: dict | str) -> list[dict]:
    import json
    try:
        if isinstance(raw_items, str):
            raw_items = json.loads(raw_items)
        if isinstance(raw_items, dict):
            itens = raw_items.get("items", [])
        else:
            itens = []
        if isinstance(itens, str):
            itens = json.loads(itens)
        return itens if isinstance(itens, list) else []
    except Exception as e:
        logger.exception(f"Erro ao parsear items da escala: {e}")
        return []


def render_scale_item_interactive(scale_id: str, itens: list[dict], auth_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza interativamente cada pergunta da escala com checkboxes.

    Args:
        scale_id (str): Identificador da escala.
        itens (list[dict]): Lista de dicionários contendo perguntas e opções.
        auth_machine (StateMachine): Máquina de estado para controle de progresso.

    Calls:
        st.checkbox(), st.rerun(): Controles de fluxo e rerun | instanciados por streamlit.
    """
    idx_key = f"scale_progress__{scale_id}__idx"
    resp_key = f"scale_progress__{scale_id}__resp"
    done_key = f"scale_progress__{scale_id}__done"

    idx = auth_machine.get_variable(idx_key, default=0)
    respostas = auth_machine.get_variable(resp_key, default={})

    if idx >= len(itens):
        auth_machine.set_variable(done_key, True)
        return

    pergunta = itens[idx]
    qid = pergunta.get("id")
    qtxt = pergunta.get("question", f"Pergunta {qid}")
    opcoes = pergunta.get("options", [])

    st.markdown(f"**{qid}. {qtxt}**")
    for i, opcao in enumerate(opcoes):
        if st.checkbox(opcao, key=f"{scale_id}_{qid}_{i}"):
            respostas[f"question_{qid}"] = opcao
            auth_machine.set_variable(resp_key, respostas)
            auth_machine.set_variable(idx_key, idx + 1)
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)


def finalize_scale_response(scale_id: str, link_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Finaliza a resposta da escala, salva no backend e notifica o usuário.

    Args:
        scale_id (str): Identificador da escala.
        link_id (str): Identificador do vínculo paciente-profissional.
        auth_machine (StateMachine): Máquina de estado para controle de progresso.

    Calls:
        save_scale_progress(): Persiste progresso da escala | definida em services.scales_progress.
        st.success(), st.error(): Feedback visual | instanciados por streamlit.
    """
    from services.scales_progress import save_scale_progress

    resp_key = f"scale_progress__{scale_id}__resp"
    done_key = f"scale_progress__{scale_id}__done"
    respostas = auth_machine.get_variable(resp_key, default={})
    if not respostas:
        return

    payload = {
        "scale_id": scale_id,
        "link_id": link_id,
        "date": str(date.today()),
        "completed": True,
        "answers": respostas
    }
    sucesso = save_scale_progress(payload)
    if sucesso:
        st.success("✅ Escala enviada com sucesso!")
        auth_machine.set_variable(resp_key, {})
        auth_machine.set_variable(done_key, False)
        auth_machine.set_variable(f"scale_progress__{scale_id}__idx", 0)
        st.rerun()
    else:
        st.error("❌ Erro ao enviar escala.")
