
# 📦 IMPORTAÇÕES NECESSÁRIAS ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import json 
import logging
import streamlit as st
import pandas    as pd

from typing                             import List, Dict
from datetime                           import date
from frameworks.sm                      import StateMachine
from utils.variables.session            import EvaluationStates, RedirectStates
from utils.load.context                 import is_professional_user
from services.links                     import load_links_for_professional
from services.scales                    import update_scale_status, load_assigned_scales, save_scale_assignment
from services.scales_progress           import load_scale_progress, save_scale_progress
from services.available_scales          import load_available_scales
from components.sidebar                 import render_sidebar


# 👨‍💻 LOGGER ESPECÍFICO PARA O MÓDULO ATUAL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# 🔌 FUNÇÃO PARA RENDERIZAR A INTERFACE DE AVALIAÇÕES (ENTRY POINT) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def scales_interface_entrypoint(auth_machine: StateMachine) -> tuple[None, str | None]:
    """
    <docstrings> Renderiza a interface da page "3_Avaliações" com abas distintas para profissionais e pacientes.
    
    Args:
        auth_machine (StateMachine): Máquina de estados com dados do usuário autenticado.

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
    
    # 🛰️ ESTABILIZAÇÃO PROATIVA DA INTERFACE ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Cria uma instância da máquina de redirecionamento (default: True).
    redirect_machine = StateMachine("scales_redirect_state", RedirectStates.REDIRECT.value, enable_logging = True)
    
    # Se a máquina de redirecionamento estiver ligada...
    if redirect_machine.current:
        redirect_machine.to(RedirectStates.REDIRECTED.value, True) # ⬅ Desativa a flag e força rerun().
    
    # ⚙️ MÁQUINA DE ESCALAS ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    # Define ou recupera a máquina de escalas (default: "start").
    scales_machine = StateMachine("scales_state", EvaluationStates.START.value)

    # 📶 ROTEAMENTO CONFORME PAPEL DO USUÁRIO ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Se o usuário possuir um perfil profissional registrado na máquina de autenticação...
    if is_professional_user(auth_machine):
        _render_professional_scales(auth_machine, scales_machine) # ⬅ Desenha a interface do profissional.
    
    # Caso contrário...
    else:
        _render_patient_scales(auth_machine, scales_machine) # ⬅ Desenha a interface do paciente.
    
    # Desenha a sidebar do aplicativo.
    render_sidebar(auth_machine)


# 📺 FUNÇÃO PARA RENDERIZAR A INTERFACE DO PROFISSIONAL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_professional_scales(auth_machine: StateMachine, scales_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a interface de escalas para profissionais.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados do usuário profissional.
        state_machine (StateMachine): Máquina de estado com dados da escalas.

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

    # Desenha as abas do profissional.
    tabs = st.tabs(["Avaliações", "Visualizar resultados", "Evolução"])

    # Dentro da primeira aba...
    with tabs[0]:

        # Desenha o cabeçalho da aba.
        st.markdown("<h4>Atribuir instrumentos</h4>", unsafe_allow_html=True)

        # Se não houver vínculos registrados na máquina de autenticação...
        if not auth_machine.get_variable("professional_patient_links"):
            user_id = auth_machine.get_variable("user_id")       # ⬅ Recupera o UUID do profissional.
            load_links_for_professional(user_id, auth_machine)   # ⬅ Carrega os vínculos via professional_id

        # Se não houver escalas disponíveis na máquina de escalas...
        if not scales_machine.get_variable("available_scales"):
            load_available_scales(scales_machine) # ⬅ Corrigido: carregar na máquina correta

        # Recupera dados de links e escalas.
        links = auth_machine.get_variable("professional_patient_links", default=[])
        scales = scales_machine.get_variable("available_scales", default=[])

        # Filtra apenas links aceitos.
        active_links = [l for l in links if l.get("status") == "accepted"]
        if not active_links:
            st.info("⚠️ Nenhum paciente vinculado.")
            return None, None

        # Mapas para populamento de controles.
        names = [l["patient_name"] for l in active_links]
        links_map = {l["patient_name"]: l["id"] for l in active_links}
        scales_names = [e["scale_name"] for e in scales]
        scales_map = {e["scale_name"]: e["id"] for e in scales}

        # Formulário de atribuição.
        with st.form("form_atribuicao_escala"):
            nome = st.selectbox("Paciente", names)
            scale = st.selectbox("Escala", scales_names)
            feedback = st.empty()
            click = st.form_submit_button("Atribuir", use_container_width=True)

        # Ação de submissão.
        if click:

            if scale not in scales_map:
                feedback.error("❌ Erro interno: escala selecionada não foi encontrada.")
                return None, None

            payload = {
                "link_id": links_map[nome],
                "available_scale_id": scales_map[scale],
                "scale_name": scale,
                "status": "active"
            }
            done = save_scale_assignment(payload)

            if done == "created":
                feedback.success("✅ Escala atribuída com sucesso!")
            elif done == "duplicate_today":
                feedback.warning("⚠️ Esta escala já foi atribuída ao paciente hoje.")
            else:
                feedback.error("❌ Não foi possível atribuir a escala.")

    with tabs[1]:
        # Recupera o ID do vínculo único.
        link_id = links[0]["id"]
        render_scale_progress_table(link_id, auth_machine)

    return None, None


# 📺 FUNÇÃO PARA RENDERIZAR A INTERFACE DO PACIENTE ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_patient_scales(auth_machine: StateMachine, scales_machine: StateMachine) -> None:
    """
    <docstrings> Renderiza a interface de escalas para pacientes com abas para responder, histórico e resumo.

    Args:
        auth_machine (StateMachine): Máquina de estados com os dados do usuário autenticado.
        state_machine (StateMachine): Máquina de estados dedicada a dados de escalas.

    Calls:
        auth_machine.get_variable(): Recupera variáveis de estado do usuário | instanciado por StateMachine.
        load_links_for_patient(): Carrega vínculos do paciente | definida em services.professional_patient_link.py.
        st.tabs(): Cria conjunto de abas de navegação | definida em streamlit.
        st.warning(): Exibe aviso de ausência de vínculo | definida em streamlit.
        st.info(): Exibe mensagens informativas | definida em streamlit.
        render_scales(): Renderiza escalas pendentes para o paciente | definida em components.scales_interface.py.
        render_scale_progress_table(): Exibe tabela de progresso das escalas | definida em components.scales_interface.py.
        auth_machine.list_variables_with_prefix(): Filtra variáveis relacionadas a progresso | instanciado por StateMachine.
        st.write(): Exibe informações brutas no frontend | definida em streamlit.

    Returns:
        None.

    """

    # Recupera a lista de vínculos do paciente.
    links = auth_machine.get_variable("links", default=[])

    # Se não houver vínculos, exibe mensagem informativa em todas as abas.
    if len(links) == 0:
        for tab in st.tabs(["Responder avaliações", "Histórico", "Resumo"]):
            with tab:
                st.warning("⚠️ Nenhum profissional vinculado ao seu perfil.")
        return

    # Se houver múltiplos vínculos, exibe mensagem informativa em todas as abas.
    if len(links) > 1:
        for tab in st.tabs(["Responder avaliações", "Histórico", "Resumo"]):
            with tab:
                st.info("ℹ️ Essa funcionalidade será implementada no futuro (vários vínculos detectados).")
        return

    # Recupera o primeiro item da lista de vínculos.
    link_id = links[0]["id"]

    # Desenha as abas da sessão de avaliações do paciente.
    tabs = st.tabs(["Responder avaliações", "Histórico", "Resumo"])


    # ✒️ ABA DE AVALIAÇÕES ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Ativa a aba de avaliações.
    with tabs[0]:
        _scales_loader(scales_machine, link_id)


    # 🧮 ABA DE RESULTADOS ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Ativa a aba de resultados.
    with tabs[1]:
        st.info("O histório de respostas será implementado em breve.")


    # 🧩 ABA DE RELATÓRIOS E SÍNTESES ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    # Ativa a aba de relatórios e sínteses.
    with tabs[2]:
        st.info("Um resumo dos resultados será implementado em breve.")


# ✒️ FUNÇÃO PARA CARREGAR E SELECIONAR ESCALAS ATRIBUÍDAS AO PACIENTE ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _scales_loader(scales_machine: StateMachine, link_id: str) -> None:
    """
    <docstrings> Orquestra o fluxo de carregamento, renderização e finalização de escalas.

    Args:
        auth_machine (StateMachine): Máquina de estado com dados de usuário.
        scales_machine (StateMachine): Mátquina de estado com dados de escalas psicométricas.
        links (list[dict]): Lista de vínculos ativos do paciente. 

    Calls:
        load_links_for_patient(): Garantir vínculo paciente | definida em services.professional_patient_link.
        load_available_scales(): Carrega metadados das escalas | definida em services.available_scales.
        load_scale_progress(): Busca histórico de progresso | definida em services.scales_progress.
        load_assigned_scales(): Busca escalas ativas | definida acima.
        render_pending_scales(): Renderiza formulários e trata submissões | definida acima.
        st.warning(), st.success(): Feedback visual | definidos em streamlit.

    Returns:
        tuple[None, str | None]: (None, mensagem de erro) ou (None, None) em sucesso.

    """

    # Carrega os dados psicométricos das escalas disponíveis na máquina de escalas.
    load_available_scales(scales_machine) 

    # Carrega as respostas das escalas atribuídas ao paciente (histórico).
    load_scale_progress(link_id, scales_machine)

    # Recupera as escalas atribuídas via UUID do vínculo.
    assigned = load_assigned_scales(link_id, scales_machine) 

    # Recupera os dados psicométricos das escalas disponíveis no sistema.
    psych_data = scales_machine.get_variable("available_scales", default=[])

    # Se nenhuma escala foi atribuída...
    if not assigned:
        st.info("Você ainda não tem avaliações atribuídas.")
        return # ⬅ Retorna para o fluxo principal.

    # Recupera as escalas pendentes...
    pending_scales = _render_pending_scales(assigned, psych_data, link_id, scales_machine) 
    
    # Se não houver escalas pendentes...
    if not pending_scales:
        st.success("✅ Você já respondeu todas as avaliações que lhe foram atribuídas.")

    # Retorna para o fluxo principal.
    return


# ✒️ FUNÇÃO PARA RENDERIZAR APENAS ESCALAS PENDENTES ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _render_pending_scales(
    assigned: list[dict],
    psych_data: list[dict],
    link_id: str,
    scales_machine: StateMachine
) -> bool:
    """
    <docstrings> Renderiza escalas pendentes em sequência com controle de progresso.

    Args:
        assigned (list[dict]): Escalas ativas atribuídas ao paciente (tabela `scales`).
        psych_data (list[dict]): Estruturas completas das escalas disponíveis (tabela `available_scales`).
        link_id (str): UUID do vínculo profissional-paciente.
        scales_machine (StateMachine): Máquina de estado responsável por armazenar progresso, respostas e estados da interface.

    Calls:
        parse_scale_items(): Converte definição bruta em itens | definida neste módulo.
        check_if_scale_completed_today(): Verifica se escala já foi respondida hoje | definida neste módulo.
        _render_scale_item_full_with_checkboxes(): Renderiza formulário de resposta | definida neste módulo.
        finalize_scale_response(): Persiste respostas e atualiza progresso no backend | definida neste módulo.
        scales_machine.set_variable(): Armazena estados e respostas da interface | instanciado por StateMachine.
        st.subheader(): Exibe subtítulo com o nome da escala | instanciado por streamlit.
        st.markdown(): Renderiza instruções da escala no frontend | instanciado por streamlit.
        st.warning(): Exibe alertas de estrutura inválida | instanciado por streamlit.

    Returns:
        bool: 
            - True se pelo menos uma escala pendente foi identificada e renderizada.
            - False se todas as escalas já foram respondidas no dia atual.
    """
    
    # Flag de controle usada para indicar se ao menos uma escala pendente foi processada.
    pending = False

    # Mapeia os metadados das escalas disponíveis por seu UUID (available_scale_id).
    mapa = {d["id"]: d for d in psych_data}

    # Para cada escala atribuída ao paciente...
    for scale in assigned:
        scale_id = scale["id"] # ⬅ UUID da escala atribuída (scales datafrane).

        # Verifica se a escala já foi respondida hoje; se sim, ignora.
        if check_if_scale_completed_today(scale_id, link_id, scales_machine):
            continue # ⬅ Pula para a próxima escala.

        # Recupera a estrutura psicométrica da escala a partir do UUID das escalas disponívies.
        structure = mapa.get(scale["available_scale_id"])
        
        # Se não houver uma estrutura psicométrica confiramda...
        if not structure:
            st.warning(f"⚠️ Estrutura não encontrada para {scale.get('scale_name')}") # ⬅ Falha de integridade: escala atribuída sem definição.
            continue # ⬅ Pula para a próxima escala.

        # Converte a estrutura bruta de itens (JSON ou dict) em lista uma lista de itens.
        itens = parse_scale_items(structure.get("items"))
        
        # Se não houver itens definidos...
        if not itens:
            st.warning(f"⚠️ Sem itens válidos para {scale.get('scale_name')}")  # ⬅ Falha crítica: escala sem conteúdo aplicável.
            continue # ⬅ Pula para a próxima escala.

        # Se chegou até aqui, a escala está pronta para ser exibida.
        pending = True

        # Ativa um container persistente para adicionar elementos.
        with st.container():
            
            # Renderiza o nome da escala como subtítulo.
            st.subheader(scale.get("scale_name", "Escala"))

            # Renderiza instruções da escala, se disponíveis.
            st.markdown(f"**Instruções:** {structure.get('description', '')}", unsafe_allow_html=True)

            # Define o estado da escala atual como FORM → usado para controle reativo da interface.
            scales_machine.set_variable(f"{scale_id}__state", EvaluationStates.FORM.value)

            # Chama o renderer do formulário da escala, que controla UI, submissão e validação.
            _render_scale_item_full_with_checkboxes(
                scale_id=scale_id,
                itens=itens,
                link_id=link_id,
                scales_machine=scales_machine
            )

            # Verificação extra: garante que escalas finalizadas durante a submissão não sejam duplicadas.
            if check_if_scale_completed_today(scale_id, link_id, scales_machine):
                continue # ⬅ Pula para a próxima escala.

    # Retorna True se alguma escala pendente foi encontrada e exibida; caso contrário, False.
    return pending


# ✒️ FUNÇÃO PARA RENDERIZAR CHECKBOXES DINAMICAMENTE ────────────────────────────────────────────────────────────

def _render_scale_item_full_with_checkboxes(
    scale_id: str,
    itens: list[dict],
    link_id: str,
    scales_machine: StateMachine
) -> None:
    """
    <docstrings> Renderiza um formulário completo da escala com opções do tipo checkbox.

    Esta função é responsável por exibir os itens da escala em um formulário interativo. Após o envio,
    realiza a validação das respostas, exibe feedback visual ao usuário e persiste temporariamente os dados
    na máquina de estados. Se todas as respostas forem válidas, também aciona o encerramento e salvamento da escala.

    Args:
        scale_id (str): ID da escala atribuída (registro da tabela `scales`).
        itens (list[dict]): Lista de perguntas com alternativas (tipo Likert, múltipla escolha etc.).
        link_id (str): UUID do vínculo profissional-paciente.
        scales_machine (StateMachine): Máquina responsável por armazenar respostas, estado da UI e progresso local.

    Calls:
        render_scale_item_ui(): Cria os checkboxes e retorna um dicionário com as alternativas marcadas | definida neste módulo.
        validate_scale_responses(): Valida a estrutura das respostas para garantir que cada item tenha apenas uma alternativa marcada | definida neste módulo.
        handle_scale_submission(): Armazena as respostas válidas e exibe feedback visual condicional (erro ou sucesso) | definida neste módulo.
        finalize_scale_response(): Persiste as respostas no backend e atualiza o status da escala como concluída | definida neste módulo.
        scales_machine.set_variable(): Atualiza o estado interno da escala na máquina de estados | instanciado por StateMachine.
        st.form_submit_button(): Cria botão de envio associado ao formulário | instanciado por streamlit.

    Returns:
        None: A função não retorna valor; sua função é puramente reativa e visual.
    """

    # Cria um formulário isolado para a escala atual.
    with st.form(key=f"form_{scale_id}"):

        # Renderiza os itens da escala como checkboxes, agrupados por questão.
        # Retorna um dicionário bruto com as respostas selecionadas por item.
        raw_answers = render_scale_item_ui(scale_id, itens)

        # Cria o botão de envio do formulário.
        sent = st.form_submit_button("Salvar", use_container_width=True)

        # Se o formulário for enviado...
        if sent:
            # Loga que a submissão do formulário foi iniciada.
            logger.debug(f"[SCALE] Formulário {scale_id} enviado. Iniciando validação.")

            # Valida o conjunto de respostas: separa respostas válidas e itens com erro (ex: não respondidos).
            valid_answers, error_ids = validate_scale_responses(raw_answers)

            # Exibe feedback e persiste as respostas válidas localmente (em memória).
            success = handle_scale_submission(scale_id, valid_answers, error_ids, scales_machine)

            # Se a submissão for considerada válida...
            if success:
                # Armazena respostas e status local de conclusão na máquina de escalas.
                scales_machine.set_variable(f"scale_progress__{scale_id}__resp", valid_answers)
                scales_machine.set_variable(f"scale_progress__{scale_id}__done", True)

                # Persiste no backend e atualiza o estado geral da escala como finalizada.
                finalize_scale_response(scale_id, link_id, scales_machine)


# ✒️ FUNÇÃO AUXILIAR PARA RENDERIZAR A UI DE CHECKBOXES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def render_scale_item_ui(scale_id: str, itens: List[Dict]) -> Dict[str, List[str]]:
    """
    <docstrings> Renderiza os checkboxes da escala e retorna as respostas marcadas.

    Args:
        scale_id (str): ID da escala atribuída.
        itens (list[dict]): Lista de perguntas.

    Returns:
        dict: Dicionário com respostas por pergunta. Ex: {'1': ['A'], '2': []}
    """
    respostas = {}

    for item in itens:
        qid = str(item.get("id"))
        qtxt = item.get("question", f"Pergunta {qid}")
        options = item.get("options", [])

        st.markdown(f"**{qid}. {qtxt}**")
        selecionadas = []

        for i, option in enumerate(options):
            key = f"{scale_id}_{qid}_{i}"
            if st.checkbox(option, key=key):
                selecionadas.append(option)

        respostas[qid] = selecionadas
        st.markdown("---")

    return respostas


# ✒️ FUNÇÃO AUXILIAR PARA VALIDAR AS RESPOSTAS ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def validate_scale_responses(raw_answers: dict) -> tuple[dict, list[str]]:
    """
    <docstrings> Valida as respostas brutas da escala.

    Args:
        raw_answers (dict): Dicionário com respostas por item (possivelmente múltiplas).

    Returns:
        Tuple[dict, list[str]]: Respostas válidas e lista de IDs com erro.
    """
    valid = {}
    erros = []

    for qid, respostas in raw_answers.items():
        if respostas:
            valid[f"question_{qid}"] = respostas[0]
        else:
            valid[f"question_{qid}"] = None
            erros.append(qid)

    return valid, erros


# ✒️ FUNÇÃO AUXILIAR PARA FEEDBACK E CONTROLE ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def handle_scale_submission(
    scale_id: str,
    valid_answers: dict,
    error_ids: list[str],
    scales_machine: StateMachine
) -> bool:
    """
    <docstrings> Gerencia estado, feedback visual e armazena respostas temporárias.

    Args:
        scale_id (str): ID da escala.
        valid_answers (dict): Respostas válidas.
        error_ids (list[str]): Lista de IDs com erro.
        state_machine (StateMachine): Máquina para persistir estado temporário.

    Returns:
        bool: True se pronto para submissão final; False se houver erro.
    """
    feedback = st.empty()

    scales_machine.set_variable(f"{scale_id}__answers", valid_answers)
    scales_machine.set_variable(f"{scale_id}__error_ids", error_ids)

    if error_ids:
        if len(error_ids) == 1:
            feedback.error(f"❌ Verifique o item {error_ids[0]}.")
        else:
            joined = ", ".join(error_ids[:-1]) + " e " + error_ids[-1]
            feedback.error(f"❌ Verifique os itens {joined}.")
        return False

    return True


# 🗃️ FUNÇÃO AUXILIAR PARA CONVERTER ESTRUTURAS DE ITENS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def parse_scale_items(raw_items: dict | str) -> list[dict]:
    """
    <docstrings> Converte diferentes formatos brutos de itens de escala (dict ou string JSON) em uma lista de dicionários.
    
    Essa função é utilizada para garantir que os itens da escala estejam em formato manipulável (`list[dict]`),
    independentemente de como eles foram armazenados ou recebidos do banco (como string JSON ou dict aninhado).

    Args:
        raw_items (dict | str): Estrutura crua contendo os itens da escala, geralmente retornada do Supabase.

    Returns:
        list[dict]: Lista de dicionários representando os itens válidos da escala.
                    Retorna lista vazia em caso de erro de parsing ou tipo inesperado.

    Calls:
        isinstance(): Verifica o tipo de uma variável | built-in.
        json.loads(): Converte string JSON em objeto Python | importada do módulo json.
        dict.get(): Acessa chave 'items' de um dicionário | instanciado por dict.
        logger.exception(): Registra erro com traceback | instanciado por logger.
    """

    # Tenta executar a ação principal...
    try:

        # Se a entrada for uma string JSON...
        if isinstance(raw_items, str):
            raw_items = json.loads(raw_items) # ⬅ Tenta decodificar para Python.

        # Se já for um dicionário...
        if isinstance(raw_items, dict):
            itens = raw_items.get("items", []) # ⬅ Tenta extrair a chave 'items'.
        
        # Caso contrário...
        else:
            itens = []  # ⬅ Cria uma lista vazia como fallback.

        # Se ainda assim os itens forem string JSON...
        if isinstance(itens, str):
            itens = json.loads(itens) # ⬅ Faz novo parsing.

        # Garante que a saída seja uma lista de dicionários.
        return itens if isinstance(itens, list) else []

    # Na exceção...
    except Exception as e:

        # Loga qualquer erro no parsing com stacktrace automático.
        logger.exception(f"Erro ao parsear items da escala: {e}")
        return []  # ⬅ Retorna uma lista vazia como fallback de execução.


# 📞 FUNÇÃO AUXILIAR PARA REGISTAR RESPOSTAS DE ESCALAS  ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def finalize_scale_response(scale_id: str, link_id: str, scales_machine: StateMachine) -> None:
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

    resp_key = f"scale_progress__{scale_id}__resp"
    done_key = f"scale_progress__{scale_id}__done"
    respostas = scales_machine.get_variable(resp_key, default={})
    
    if not respostas:
        return

    payload = {
        "scale_id": scale_id,
        "link_id": link_id,
        "date": str(date.today()),
        "completed": True,
        "answers": respostas
    }

    logger.debug(f"[SCALE] finalize_scale_response: Iniciando envio da escala {scale_id}")
    logger.debug(f"[SCALE] finalize_scale_response: Payload → {payload}")

    sucesso = save_scale_progress(payload)
    if sucesso:
        scales_machine.set_variable(resp_key, {})
        scales_machine.set_variable(done_key, False)
        scales_machine.set_variable(f"scale_progress__{scale_id}__idx", 0)
        update_scale_status(scale_id, "done")
        scales_machine.to(EvaluationStates.START.value, rerun=True)


# 📞 FUNÇÃO AUXILIAR PARA VERIFICAR SE UMA ESCALA JÁ FOI RESPONDIDA HOJE  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def check_if_scale_completed_today(scale_id: str, link_id: str, machine: StateMachine) -> bool:
    """
    <docstrings> Verifica se uma escala foi respondida hoje, com ou sem referência ao vínculo.

    Args:
        scale_id (str): ID da escala atribuída.
        link_id (str): ID do vínculo paciente-profissional.
        machine (StateMachine): Máquina contendo o progresso local da escala.

    Returns:
        bool: True se a escala foi respondida hoje; False caso contrário.
    """
    progresso = machine.get_variable(f"scale_progress__{scale_id}", default=[])
    hoje = str(date.today())

    for p in progresso:
        # Suporte futuro: se link_id estiver registrado no progresso, usa filtro estrito
        if "link_id" in p:
            if p["link_id"] == link_id and p.get("date") == hoje and p.get("completed"):
                return True
        # Suporte atual: assume estrutura simples sem link_id
        elif p.get("date") == hoje and p.get("completed"):
            return True

    return False


# 📞 FUNÇÃO PARA RENDERIZAR PROGRESSOS EM ESCALAS  ────────────────────────────────────────────────────────────

def render_scale_progress_table(link_id: str, auth_machine: StateMachine) -> None:
    """
    <docstrings> Exibe uma tabela com o histórico de respostas do paciente para cada escala.

    Args:
        link_id (str): UUID do vínculo paciente-profissional.
        auth_machine (StateMachine): Máquina de estado com os dados carregados.

    Calls:
        load_scale_progress(): Carrega dados da tabela `scale_progress` | definida em services.scales_progress.
        st.dataframe(): Exibe tabela no frontend | definida em streamlit.
    """

    # Força recarregamento dos dados (caso não estejam carregados ainda)
    load_scale_progress(link_id=link_id, auth_machine=auth_machine)

    raw_vars = auth_machine.list_variables_with_prefix("scale_progress__")

    # Coleta todas as chaves com progresso
    progresso = []
    for v in raw_vars.values():
        if isinstance(v, list):
            progresso.extend(v)
    
    if not progresso:
        st.info("⚠️ Nenhum progresso registrado até o momento.")
        return

    # Converte para dataframe
    df = pd.DataFrame(progresso)

    # Reordena colunas, se possível
    cols_prioritarias = ["scale_id", "date", "completed"]
    cols_ordenadas = cols_prioritarias + [c for c in df.columns if c not in cols_prioritarias]
    df = df[cols_ordenadas]

    # Renderiza
    st.subheader("📊 Histórico de Respostas")
    st.dataframe(df, use_container_width=True)