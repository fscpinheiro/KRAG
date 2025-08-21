import streamlit as st
import os
import pandas as pd
import psutil
import time
from rag_engine import KRAGEngine

# Configuração da página
st.set_page_config(
    page_title="KRAG - Sistema Legado",
    page_icon="🚀",
    layout="wide"
)


# Inicializar RAG (cache)
@st.cache_resource
def init_rag():
    engine = KRAGEngine()
    engine.initialize()
    return engine


def show_download_progress_inline(model_name: str, rag_engine):
    """Mostra progresso de download inline na sidebar"""
    import requests

    status_container = st.empty()

    try:
        with status_container.container():
            st.caption("📦 Baixando...")
            progress = st.progress(0)

            check_response = requests.get(f"{rag_engine.config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if check_response.status_code == 200:
                existing = [m["name"] for m in check_response.json().get("models", [])]
                if model_name in existing:
                    progress.progress(100)
                    time.sleep(0.5)
                    status_container.empty()
                    return True

            progress.progress(30)

            pull_response = requests.post(
                f"{rag_engine.config.OLLAMA_BASE_URL}/api/pull",
                json={"name": model_name},
                timeout=300
            )

            if pull_response.status_code == 200:
                progress.progress(100)
                time.sleep(0.5)
                status_container.empty()
                return True
            else:
                status_container.error("❌ Erro no download")
                time.sleep(1)
                status_container.empty()
                return False

    except Exception as e:
        status_container.error(f"❌ Erro: {e}")
        time.sleep(1)
        status_container.empty()
        return False


def show_folder_selector():
    """Mostra seletor de pasta com navegação"""
    st.markdown("## 📁 Selecionar Pasta de Código")

    # Pasta atual
    current_path = st.session_state.get("custom_source_path", "./data/source_code")

    # Navegação por pastas comuns
    st.markdown("**📂 Pastas Sugeridas:**")

    common_paths = [
        "./data/source_code",
        os.path.expanduser("~/"),
        "/",  # Raiz (Linux/Mac)
        "C:\\",  # Raiz (Windows)
        os.path.expanduser("~/Desktop"),  # Desktop
        os.path.expanduser("~/Documents"),  # Documentos
    ]

    valid_paths = [path for path in common_paths if os.path.exists(path)]

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_base = st.selectbox(
            "Pasta base:",
            valid_paths,
            help="Escolha uma pasta base para navegar"
        )

    with col2:
        if st.button("🔍 Explorar"):
            st.session_state.browsing_path = selected_base
            st.rerun()

    # Se estiver navegando
    if hasattr(st.session_state, 'browsing_path'):
        browse_path = st.session_state.browsing_path

        st.markdown(f"**📂 Navegando: `{browse_path}`**")

        try:
            items = os.listdir(browse_path)
            folders = [item for item in items if os.path.isdir(os.path.join(browse_path, item))]
            folders.sort()

            if browse_path != "/":
                parent = os.path.dirname(browse_path)
                if st.button(f"⬆️ Voltar para {os.path.basename(parent) or parent}"):
                    st.session_state.browsing_path = parent
                    st.rerun()

            # Lista de pastas
            st.markdown("**📁 Subpastas:**")
            for folder in folders[:10]:  # Máximo 10 pastas
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"📁 {folder}")
                with col2:
                    if st.button("📂", key=f"browse_{folder}"):
                        new_path = os.path.join(browse_path, folder)
                        st.session_state.browsing_path = new_path
                        st.rerun()

            # Usar pasta atual
            st.markdown("---")
            if st.button(f"✅ Usar Esta Pasta: {browse_path}", type="primary"):
                st.session_state.selected_new_path = browse_path
                delattr(st.session_state, 'browsing_path')
                st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao ler pasta: {e}")

    # Input manual
    st.markdown("**✏️ Ou digite o caminho:**")
    manual_path = st.text_input(
        "Caminho completo:",
        value=current_path,
        help="Ex: /home/user/projeto ou C:\\Projetos\\Sistema"
    )

    # Preview da pasta
    if manual_path and os.path.exists(manual_path) and manual_path != current_path:
        try:
            files = os.listdir(manual_path)
            code_files = [f for f in files if f.endswith(('.py', '.java', '.js', '.php', '.cpp', '.c', '.h'))]

            st.success(f"✅ Pasta válida")
            st.caption(f"📊 {len(files)} itens | {len(code_files)} arquivos de código")

            if code_files[:5]:
                st.markdown("**👀 Arquivos de código encontrados:**")
                for file in code_files[:5]:
                    st.text(f"📄 {file}")
                if len(code_files) > 5:
                    st.caption(f"... e mais {len(code_files) - 5} arquivos")

        except Exception as e:
            st.error(f"❌ Erro: {e}")

    # Botões finais
    col1, col2, col3 = st.columns(3)

    with col1:
        final_path = st.session_state.get("selected_new_path", manual_path)
        if st.button("✅ Confirmar") and final_path and os.path.exists(final_path):
            st.session_state.custom_source_path = final_path
            # Limpar estados temporários
            for key in ["browsing_path", "selected_new_path", "show_folder_selector"]:
                if key in st.session_state:
                    delattr(st.session_state, key)
            st.success("✅ Pasta alterada!")
            st.rerun()

    with col2:
        if st.button("🔄 Padrão"):
            st.session_state.custom_source_path = "./data/source_code"
            for key in ["browsing_path", "selected_new_path", "show_folder_selector"]:
                if key in st.session_state:
                    delattr(st.session_state, key)
            st.success("✅ Resetado!")
            st.rerun()

    with col3:
        if st.button("❌ Cancelar"):
            for key in ["browsing_path", "selected_new_path", "show_folder_selector"]:
                if key in st.session_state:
                    delattr(st.session_state, key)
            st.rerun()


def show_model_removal_progress(model_name: str, rag_engine):
    """Mostra progresso de remoção do modelo"""
    progress_container = st.empty()

    with progress_container.container():
        st.warning(f"🗑️ **Removendo {model_name}**")

        # Mostrar tamanho do modelo
        size = rag_engine.get_model_disk_usage(model_name)
        st.caption(f"Liberando: {size} de espaço")

        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("🔍 Verificando modelo...")
            progress_bar.progress(20)
            time.sleep(0.5)

            status_text.text("🗑️ Removendo arquivos...")
            progress_bar.progress(50)
            time.sleep(1)

            # Fazer remoção real
            success, message = rag_engine.remove_model(model_name)

            if success:
                progress_bar.progress(100)
                status_text.text("✅ Modelo removido!")
                time.sleep(1)
                progress_container.empty()
                return True
            else:
                status_text.text("❌ Erro na remoção")
                st.error(f"Erro: {message}")
                time.sleep(2)
                progress_container.empty()
                return False

        except Exception as e:
            status_text.text("❌ Erro na remoção")
            st.error(f"Erro: {e}")
            time.sleep(2)
            progress_container.empty()
            return False


def main():
    st.title("🚀 KRAG - Análise de Sistema Legado")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Painel de Controle")

        # Inicializar RAG
        try:
            rag = init_rag()
            st.success("✅ Sistema Online")
        except Exception as e:
            st.error(f"❌ Erro: {e}")
            return

        # === SEÇÃO 1: MODELOS LLM (Retrátil) ===
        with st.expander("🤖 **Modelos LLM**", expanded=True):
            try:
                models_status = rag.get_available_models()
                available = models_status.get("available", [])
                not_available = models_status.get("not_available", [])

                # Modelo atual
                if "selected_model" not in st.session_state:
                    st.session_state.selected_model = available[0] if available else "gemma3:1b"

                current_model = st.session_state.selected_model

                # MODELO ATIVO
                st.markdown("**🟢 ATIVO:**")
                info = rag.get_model_info(current_model)
                st.success(f"🎯 **{current_model}**")
                st.caption(f"💾 {info.get('ram_usage', '?')} | ⚡ {info.get('speed', '?')}")

                # DISPONÍVEIS PARA TROCAR
                others = [m for m in available if m != current_model]
                if others:
                    st.markdown("**✅ DISPONÍVEIS:**")
                    for model in others:
                        # Nome do modelo
                        st.markdown(f"✅ **{model}**")

                        # Botões em sequência horizontal compacta
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Ativar", key=f"activate_{model}", use_container_width=True):
                                with st.spinner(f"Ativando {model}..."):
                                    success, msg = rag.change_model(model)
                                    if success:
                                        st.session_state.selected_model = model
                                        st.rerun()
                                    else:
                                        st.error(msg)
                        with col2:
                            if st.button("🗑️ Remover", key=f"remove_{model}", use_container_width=True):
                                st.session_state.removing_model = model
                                st.rerun()

                # PARA BAIXAR
                if not_available:
                    st.markdown("**⬇️ BAIXAR:**")
                    for model in not_available:
                        # Nome do modelo
                        st.markdown(f'<span style="color: #666; opacity: 0.6;">⬇️ **{model}**</span>',
                                    unsafe_allow_html=True)

                        # Botão de download
                        if st.button("📥 Baixar", key=f"download_{model}", use_container_width=True):
                            st.session_state.downloading_model = model
                            st.rerun()

                        # Status de download
                        if st.session_state.get("downloading_model") == model:
                            with st.container():
                                if show_download_progress_inline(model, rag):
                                    st.success(f"✅ {model} baixado!")
                                    if "downloading_model" in st.session_state:
                                        del st.session_state.downloading_model
                                    st.cache_resource.clear()
                                    st.rerun()
                                else:
                                    if "downloading_model" in st.session_state:
                                        del st.session_state.downloading_model

                # Status de remoção
                if st.session_state.get("removing_model"):
                    model = st.session_state.removing_model

                    with st.container():
                        st.markdown("---")
                        st.warning(f"⚠️ **Confirmar remoção de {model}?**")

                        # Mostrar informações do modelo
                        size = rag.get_model_disk_usage(model)
                        st.caption(f"📊 Liberará: {size} de espaço em disco")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirmar Remoção", type="primary"):
                                if show_model_removal_progress(model, rag):
                                    st.success(f"🎉 {model} removido com sucesso!")
                                    # Limpar estado e forçar refresh
                                    del st.session_state.removing_model
                                    st.cache_resource.clear()
                                    st.rerun()
                                else:
                                    # Manter o estado para mostrar erro
                                    pass

                        with col2:
                            if st.button("❌ Cancelar"):
                                del st.session_state.removing_model
                                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro: {e}")

        # === SEÇÃO 2: PASTA RAG (Retrátil) ===
        with st.expander("📁 **Pasta RAG**", expanded=False):
            current_path = st.session_state.get("custom_source_path", "./data/source_code")

            st.info(f"📂 **Atual:**")
            st.code(current_path)

            # File uploader para selecionar pasta (workaround)
            st.markdown("**📁 Nova Pasta:**")
            new_path = st.text_input(
                "Caminho:",
                value=current_path,
                help="Ex: /home/user/projeto ou C:\\Projetos\\Sistema",
                key="new_path_input"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📁 Alterar"):
                    if new_path != current_path:
                        if os.path.exists(new_path):
                            success = rag.set_custom_source_path(new_path)
                            if success:
                                st.session_state.custom_source_path = new_path
                                st.success("✅ Alterado!")
                                st.rerun()
                            else:
                                st.error("❌ Erro")
                        else:
                            st.error("❌ Pasta não existe")

            with col2:
                if st.button("🔄 Padrão"):
                    if rag.set_custom_source_path("./data/source_code"):
                        st.session_state.custom_source_path = "./data/source_code"
                        st.success("✅ Resetado!")
                        st.rerun()

            # Auto-sync
            st.markdown("**🔄 Auto-Sync:**")
            auto_enabled = st.session_state.get("auto_reindex_enabled", False)

            if st.checkbox("🤖 Monitorar mudanças", value=auto_enabled):
                if not auto_enabled:
                    st.session_state.auto_reindex_enabled = True
                    try:
                        rag.start_auto_reindex(current_path)
                        st.success("👁️ Monitorando!")
                    except:
                        st.error("❌ Erro no monitor")
                        st.session_state.auto_reindex_enabled = False
            else:
                if auto_enabled:
                    st.session_state.auto_reindex_enabled = False
                    rag.stop_auto_reindex()
                    st.info("ℹ️ Parado")

        # === SEÇÃO 3: INDEXAÇÃO (Retrátil) ===
        with st.expander("📚 **Indexação**", expanded=False):
            stats = rag.get_stats()
            total_docs = stats.get("total_documents", 0)

            if total_docs == 0:
                st.warning("📭 Nenhum documento indexado")
                action_text = "📊 Indexar Agora"
                help_text = "Primeira indexação"
            else:
                st.info(f"📚 {total_docs} documentos indexados")
                action_text = "🔄 Reindexar"
                help_text = "Força nova indexação"

            # Botão único inteligente
            if st.button(action_text, help=help_text, use_container_width=True):
                force_reindex = total_docs > 0  # Se já tem docs, força reindex

                with st.spinner("🔄 Processando..."):
                    try:
                        rag.index_documents(force_reindex=force_reindex)
                        st.success("✅ Concluído!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")

            # Botão para limpar
            if total_docs > 0:
                if st.button("🗑️ Limpar Índice", help="Remove todos os documentos"):
                    with st.spinner("🗑️ Limpando..."):
                        try:
                            rag.clear_index()
                            st.success("✅ Índice limpo!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")

        # === SEÇÃO 4: SISTEMA (Retrátil) ===
        with st.expander("📊 **Sistema**", expanded=False):
            # Métricas do sistema
            try:
                # CPU e Memória
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("CPU", f"{cpu_percent:.1f}%")
                    st.metric("Documentos", stats.get("total_documents", 0))
                with col2:
                    st.metric("RAM", f"{memory.percent:.1f}%")
                    st.metric("Tokens ~", f"{stats.get('total_documents', 0) * 200:,}")

                # Informações do modelo atual
                model_info = stats.get("model_info", {})
                if model_info:
                    st.markdown("**🤖 Modelo Ativo:**")
                    st.caption(f"RAM Necessária: {model_info.get('ram_usage', '?')}")
                    st.caption(f"Velocidade: {model_info.get('speed', '?')}")

                # Tokens consumidos (simulado)
                if "total_tokens_used" not in st.session_state:
                    st.session_state.total_tokens_used = 0

                st.metric("Tokens Consumidos", f"{st.session_state.total_tokens_used:,}")

            except Exception as e:
                st.error(f"❌ Erro nas métricas: {e}")

        # === AÇÕES RÁPIDAS ===
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Modelos", use_container_width=True):
                st.session_state.show_models_modal = True
                st.rerun()

        with col2:
            if st.button("💡 Ajuda", use_container_width=True):
                st.session_state.show_help_modal = True
                st.rerun()

    # === MODALS NA ÁREA PRINCIPAL ===

    # MODAL: Seletor de Pasta
    if st.session_state.get("show_folder_selector", False):
        show_folder_selector()
        return

    # MODAL: Todos os Modelos
    if st.session_state.get("show_models_modal", False):
        st.markdown("## 📊 Todos os Modelos Ollama")

        try:
            import requests
            response = requests.get(f"{rag.config.OLLAMA_BASE_URL}/api/tags", timeout=5)

            if response.status_code == 200:
                models = response.json().get("models", [])

                if models:
                    # Criar tabela com ações
                    data = []
                    for model in models:
                        size_gb = model.get('size', 0) / (1024 ** 3)
                        name = model['name']

                        # Status
                        our_models = ["gemma3:270m", "qwen3:0.6b", "gemma3:1b", "deepseek-r1:1.5b",
                                      "qwen3:1.7b", "qwen2.5:3b", "gemma3:4b"]
                        status = "🎯 KRAG" if name in our_models else "📦 Outro"

                        # Verificar se é o modelo ativo
                        current_model = rag.get_current_model()
                        if name == current_model:
                            status += " (ATIVO)"

                        data.append({
                            "Status": status,
                            "Modelo": name,
                            "Tamanho": f"{size_gb:.1f}GB",
                            "Família": name.split(':')[0]
                        })

                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)

                    # Ações rápidas
                    st.markdown("### 🎛️ Ações Rápidas")

                    # Seletor de modelo para remoção
                    non_active_models = [row["Modelo"] for row in data
                                         if "(ATIVO)" not in row["Status"]]

                    if non_active_models:
                        col1, col2 = st.columns(2)

                        with col1:
                            selected_for_removal = st.selectbox(
                                "Remover modelo:",
                                [""] + non_active_models,
                                help="Selecione um modelo para remover"
                            )

                        with col2:
                            if selected_for_removal and st.button("🗑️ Remover Selecionado"):
                                with st.spinner(f"Removendo {selected_for_removal}..."):
                                    success, msg = rag.remove_model(selected_for_removal)
                                    if success:
                                        st.success(f"✅ {selected_for_removal} removido!")
                                        st.cache_resource.clear()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")

                    # Métricas atualizadas
                    total_size = sum([float(row["Tamanho"].replace("GB", "")) for row in data])
                    krag_count = len([row for row in data if "KRAG" in row["Status"]])

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total", len(models))
                    col2.metric("KRAG", krag_count)
                    col3.metric("Espaço", f"{total_size:.1f}GB")

                else:
                    st.warning("Nenhum modelo encontrado")
            else:
                st.error("Erro de conexão com Ollama")

        except Exception as e:
            st.error(f"Erro: {e}")

        if st.button("❌ Fechar"):
            del st.session_state.show_models_modal
            st.rerun()

        st.markdown("---")
        return

    # MODAL: Ajuda
    if st.session_state.get("show_help_modal", False):
        st.markdown("## 💡 Guia de Uso")

        tab1, tab2, tab3 = st.tabs(["🤖 Modelos", "📁 Pastas", "🔧 Comandos"])

        with tab1:
            st.markdown("""
            ### 🎯 Escolha do Modelo por Hardware

            **💻 Hardware Básico (< 8GB RAM):**
            - `gemma3:270m` - Ultra-rápido (300MB)
            - `qwen3:0.6b` - Eficiente (600MB) 
            - `gemma3:1b` - Balanceado ⭐ (1GB)

            **🖥️ Hardware Médio (8-16GB RAM):**
            - `deepseek-r1:1.5b` - Reasoning (1.5GB)
            - `qwen3:1.7b` - Qualidade (1.7GB)

            **🚀 Hardware Premium (16GB+ RAM):**
            - `qwen2.5:3b` - Análise profunda (3GB)
            - `gemma3:4b` - Máxima qualidade (4GB)
            """)

        with tab2:
            st.markdown("""
            ### 📁 Configuração de Pastas

            **Exemplos de caminhos:**
            ```
            # Windows
            C:\\Projetos\\MeuSistema
            D:\\Repositorios\\projeto-legado

            # Linux/Mac  
            /home/usuario/projetos/sistema
            /Users/nome/repositorio-git
            ```

            **Vantagens pasta customizada:**
            - ✅ Acesso direto ao repositório Git
            - ✅ Auto-sync com mudanças
            - ✅ Sem copiar arquivos
            """)

        with tab3:
            st.markdown("""
            ### 🔧 Comandos Úteis

            **Baixar modelos:**
            ```bash
            # Encontrar container
            docker ps | grep ollama

            # Baixar modelo
            docker exec -it <container> ollama pull <modelo>

            # Listar modelos
            docker exec -it <container> ollama list
            ```

            **Troubleshooting:**
            ```bash
            # Reiniciar serviços
            docker-compose restart

            # Ver logs
            docker-compose logs krag
            docker-compose logs ollama
            ```
            """)

        if st.button("❌ Fechar Ajuda"):
            del st.session_state.show_help_modal
            st.rerun()

        st.markdown("---")
        return

    # === CHAT PRINCIPAL ===
    st.header("💬 Chat com o Sistema Legado")

    # Verificar documentos
    stats = rag.get_stats()
    if stats.get("total_documents", 0) == 0:
        st.warning("⚠️ Sistema sem documentos indexados!")

        col1, col2 = st.columns(2)
        with col1:
            st.info("📁 Coloque arquivos em `data/source_code/`")
        with col2:
            if st.button("📊 Indexar Agora", type="primary"):
                with st.spinner("🔄 Indexando..."):
                    try:
                        rag.index_documents(force_reindex=False)
                        st.success("✅ Indexado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
        return

    # Chat
    if "messages" not in st.session_state:
        current_model = st.session_state.get("selected_model", "gemma3:1b")
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"👋 KRAG pronto! {stats.get('total_documents', 0)} documentos | Modelo: {current_model}",
                "sources": [],
                "response_time": 0
            }
        ]

    # Histórico (com suporte a mensagens do sistema)
    for message in st.session_state.messages:
        # Mensagens do sistema com estilo diferente
        if message["role"] == "system":
            # Mensagem do sistema destacada
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6; 
                border-left: 4px solid #4CAF50; 
                padding: 10px; 
                margin: 10px 0; 
                border-radius: 5px;
                ">
                <strong>{message['content']}</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.chat_message(message["role"]):
                st.write(message["content"])

                # Tempo de resposta com cores
                if message["role"] == "assistant" and message.get("response_time", 0) > 0:
                    time_val = message["response_time"]
                    color = "🟢" if time_val < 5 else "🟡" if time_val < 15 else "🔴"
                    st.caption(f"{color} {time_val}s")

                # Fontes
                if message.get("sources"):
                    with st.expander("📋 Fontes"):
                        for source in message["sources"]:
                            filename = source.split("/")[-1] if "/" in source else source
                            st.text(f"📄 {filename}")

    # Input do chat
    if prompt := st.chat_input("Pergunte sobre o sistema..."):
        # Adicionar pergunta
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Mostrar pergunta
        with st.chat_message("user"):
            st.write(prompt)

        # Resposta
        with st.chat_message("assistant"):
            current_model = st.session_state.get("selected_model", "gemma3:1b")

            with st.spinner(f"🤔 {current_model} analisando..."):
                try:
                    result = rag.query(prompt)

                    st.write(result["answer"])

                    # Tempo e estatísticas
                    response_time = result.get("response_time", 0)
                    if response_time > 0:
                        color = "🟢" if response_time < 5 else "🟡" if response_time < 15 else "🔴"
                        st.caption(f"{color} {response_time}s")

                        # Atualizar tokens consumidos (estimativa)
                        estimated_tokens = len(prompt) + len(result["answer"])
                        st.session_state.total_tokens_used += estimated_tokens

                    # Histórico
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result.get("sources", []),
                        "response_time": response_time
                    })

                    # Fontes
                    if result.get("sources"):
                        with st.expander("📋 Fontes"):
                            for source in result["sources"]:
                                filename = source.split("/")[-1] if "/" in source else source
                                st.text(f"📄 {filename}")

                except Exception as e:
                    error_msg = f"❌ Erro: {str(e)}"
                    st.error(error_msg)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": [],
                        "response_time": 0
                    })

    # Sugestões rápidas
    if len(st.session_state.messages) <= 1:
        st.markdown("---")
        st.subheader("💡 Perguntas Sugeridas")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🏗️ Arquitetura do Sistema"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Descreva a arquitetura geral do sistema baseado nos arquivos"
                })
                st.rerun()

        with col2:
            if st.button("🔐 Sistema de Autenticação"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Como funciona o sistema de autenticação e autorização?"
                })
                st.rerun()

        with col3:
            if st.button("📊 Classes e Módulos"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Quais são as principais classes, módulos e suas responsabilidades?"
                })
                st.rerun()

    # Limpar chat
    if len(st.session_state.messages) > 1:
        st.markdown("---")
        if st.button("🗑️ Limpar Histórico"):
            current_model = st.session_state.get("selected_model", "gemma3:1b")
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"🔄 Chat limpo! {stats.get('total_documents', 0)} documentos | {current_model} ativo.",
                    "sources": [],
                    "response_time": 0
                }
            ]
            st.rerun()


if __name__ == "__main__":
    main()