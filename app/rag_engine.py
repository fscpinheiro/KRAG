import os
from typing import List, Optional
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from config import Config


class KRAGEngine:
    def __init__(self):
        self.config = Config()
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.file_watcher = None
        self.last_index_time = None

    def initialize(self):
        """Inicializa todos os componentes do RAG"""
        print("🚀 Inicializando KRAG...")

        self.embeddings = OllamaEmbeddings(
            base_url=self.config.OLLAMA_BASE_URL,
            model=self.config.EMBEDDING_MODEL
        )

        self.llm = self._create_optimized_llm(self.config.DEFAULT_MODEL)

        self.vectorstore = Chroma(
            persist_directory=self.config.CHROMA_DB_PATH,
            embedding_function=self.embeddings
        )

        template = self._get_optimized_template(self.config.DEFAULT_MODEL)
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": self.config.MAX_RESULTS}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        print("KRAG inicializado com sucesso!")

    def _create_optimized_llm(self, model_name: str):
        """Cria LLM com parâmetros otimizados"""
        model_configs = {
            "gemma3:270m": {
                "temperature": 0.2,
                "top_k": 20,
                "top_p": 0.8,
                "repeat_penalty": 1.2,
                "num_ctx": 1024,
            },
            "qwen3:0.6b": {
                "temperature": 0.15,
                "top_k": 25,
                "top_p": 0.85,
                "repeat_penalty": 1.15,
                "num_ctx": 1536,
            },
            "gemma3:1b": {
                "temperature": 0.1,
                "top_k": 30,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_ctx": 2048,
            },
            "deepseek-r1:1.5b": {
                "temperature": 0.05,
                "top_k": 35,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_ctx": 2048,
            },
            "qwen3:1.7b": {
                "temperature": 0.1,
                "top_k": 35,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_ctx": 2560,
            },
            "qwen2.5:3b": {
                "temperature": 0.1,
                "top_k": 40,
                "top_p": 0.9,
                "repeat_penalty": 1.05,
                "num_ctx": 3072,
            },
            "gemma3:4b": {
                "temperature": 0.1,
                "top_k": 40,
                "top_p": 0.95,
                "repeat_penalty": 1.05,
                "num_ctx": 4096,
            }
        }

        config = model_configs.get(model_name, {
            "temperature": 0.1,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_ctx": 2048,
        })

        return Ollama(
            base_url=self.config.OLLAMA_BASE_URL,
            model=model_name,
            **config
        )

    def _get_optimized_template(self, model_name: str) -> str:
        """Retorna template otimizado para cada modelo"""
        if model_name in ["gemma3:270m", "qwen3:0.6b"]:
            return """Você é um assistente especializado em análise de código legado.

CONTEXTO DO CÓDIGO:
{context}

PERGUNTA: {question}

Se a pergunta for sobre apresentação ou funcionalidades gerais do sistema, responda sobre suas capacidades como assistente de análise de código. Se for técnica, use o código fornecido.

RESPOSTA:"""

        elif model_name in ["gemma3:1b", "deepseek-r1:1.5b"]:
            return """Você é um assistente especializado em análise de sistemas legados.

CÓDIGO/DOCUMENTAÇÃO DISPONÍVEL:
{context}

PERGUNTA DO USUÁRIO: {question}

INSTRUÇÕES:
- Se perguntarem sobre você: explique que é um assistente de análise de código com acesso aos documentos indexados
- Se for pergunta técnica: use o código fornecido como referência
- Se for sobre funcionalidades: explique com base nos arquivos disponíveis
- Seja claro e objetivo

RESPOSTA:"""

        else:
            return """Você é um assistente inteligente especializado em análise de código legado e sistemas complexos.

CONTEXTO DOS DOCUMENTOS:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Se perguntarem sobre sua apresentação: explique suas capacidades como assistente de análise de código, quantos documentos tem acesso, e como pode ajudar
- Se for pergunta técnica sobre código: analise o contexto fornecido e responda com precisão
- Se for sobre arquitetura: explique com base nos arquivos indexados
- Sempre seja útil e técnico quando apropriado
- Cite arquivos específicos quando relevante

RESPOSTA:"""

    def _get_optimal_k_for_model(self, model_name: str) -> int:
        """Retorna número ótimo de documentos para cada modelo"""
        if model_name in ["gemma3:270m", "qwen3:0.6b"]:
            return 3
        elif model_name in ["gemma3:1b", "deepseek-r1:1.5b"]:
            return 4
        else:
            return 5

    def get_model_info(self, model_name: str) -> dict:
        """Retorna informações sobre um modelo"""
        model_specs = {
            "gemma3:270m": {
                "params": "270M",
                "ram_usage": "~1.5GB",
                "speed": "Ultra-rápido",
                "best_for": "Prototipagem rápida",
                "quality": "Básica"
            },
            "qwen3:0.6b": {
                "params": "600M",
                "ram_usage": "~2GB",
                "speed": "Muito rápido",
                "best_for": "Análise básica",
                "quality": "Boa"
            },
            "gemma3:1b": {
                "params": "1B",
                "ram_usage": "~3GB",
                "speed": "Rápido",
                "best_for": "Uso geral",
                "quality": "Boa"
            },
            "deepseek-r1:1.5b": {
                "params": "1.5B",
                "ram_usage": "~4GB",
                "speed": "Rápido",
                "best_for": "Reasoning complexo",
                "quality": "Muito boa"
            },
            "qwen3:1.7b": {
                "params": "1.7B",
                "ram_usage": "~4.5GB",
                "speed": "Médio",
                "best_for": "Análise qualidade",
                "quality": "Muito boa"
            },
            "qwen2.5:3b": {
                "params": "3B",
                "ram_usage": "~6GB",
                "speed": "Médio",
                "best_for": "Análises complexas",
                "quality": "Excelente"
            },
            "gemma3:4b": {
                "params": "4B",
                "ram_usage": "~8GB",
                "speed": "Mais lento",
                "best_for": "Análises profundas",
                "quality": "Excelente"
            }
        }

        return model_specs.get(model_name, {
            "params": "Unknown",
            "ram_usage": "Unknown",
            "speed": "Unknown",
            "best_for": "Uso geral",
            "quality": "Unknown"
        })

    def load_documents(self) -> List[Document]:
        """Carrega documentos da pasta configurada"""
        documents = []

        patterns = [
            "**/*.py", "**/*.java", "**/*.php", "**/*.rb",
            "**/*.go", "**/*.cpp", "**/*.c", "**/*.h",
            "**/*.cs", "**/*.kt", "**/*.swift", "**/*.rs",
            "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx",
            "**/*.vue", "**/*.html", "**/*.css", "**/*.scss",
            "**/*.json", "**/*.xml", "**/*.yaml", "**/*.yml",
            "**/*.sql", "**/*.properties", "**/*.conf",
            "**/*.env", "**/*.ini", "**/*.md", "**/*.txt", "**/*.rst"
        ]

        ignore_patterns = [
            "**/node_modules/**", "**/venv/**", "**/env/**",
            "**/.git/**", "**/build/**", "**/dist/**",
            "**/*.log", "**/*.tmp", "**/target/**", "**/.pytest_cache/**"
        ]

        source_path = self.config.SOURCE_CODE_PATH
        if os.path.exists(source_path):
            print(f"Carregando de: {source_path}")

            for pattern in patterns:
                try:
                    loader = DirectoryLoader(
                        source_path,
                        glob=pattern,
                        loader_cls=TextLoader,
                        loader_kwargs={"encoding": "utf-8"},
                        silent_errors=True,
                        exclude=ignore_patterns
                    )
                    docs = loader.load()

                    max_sizes = {
                        "gemma3:270m": 15000, "qwen3:0.6b": 20000,
                        "gemma3:1b": 25000, "deepseek-r1:1.5b": 30000,
                        "qwen3:1.7b": 40000, "qwen2.5:3b": 50000, "gemma3:4b": 60000
                    }

                    current_model = self.get_current_model()
                    max_size = max_sizes.get(current_model, 30000)

                    filtered_docs = [doc for doc in docs if len(doc.page_content) < max_size]
                    documents.extend(filtered_docs)

                except Exception as e:
                    print(f"⚠️ Erro em {pattern}: {e}")
                    continue

        docs_path = self.config.DOCS_PATH
        if os.path.exists(docs_path):
            print(f"📚 Carregando docs de: {docs_path}")
            for pattern in ["**/*.md", "**/*.txt", "**/*.rst"]:
                try:
                    loader = DirectoryLoader(
                        docs_path,
                        glob=pattern,
                        loader_cls=TextLoader,
                        loader_kwargs={"encoding": "utf-8"},
                        silent_errors=True
                    )
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"⚠️ Erro em docs {pattern}: {e}")
                    continue

        print(f"📄 Total carregado: {len(documents)}")
        return documents

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Processa e fragmenta documentos"""
        print("Fragmentando documentos...")

        current_model = self.get_current_model()
        chunk_configs = {
            "gemma3:270m": {"size": 600, "overlap": 100},
            "qwen3:0.6b": {"size": 700, "overlap": 120},
            "gemma3:1b": {"size": 800, "overlap": 150},
            "deepseek-r1:1.5b": {"size": 900, "overlap": 180},
            "qwen3:1.7b": {"size": 1000, "overlap": 200},
            "qwen2.5:3b": {"size": 1200, "overlap": 240},
            "gemma3:4b": {"size": 1400, "overlap": 280}
        }

        config = chunk_configs.get(current_model, {"size": 1000, "overlap": 200})

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["size"],
            chunk_overlap=config["overlap"],
            separators=["\n\nclass ", "\n\ndef ", "\n\nfunction ", "\n\npublic ", "\n\nimport ", "\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)

        for chunk in chunks:
            source_path = chunk.metadata.get("source", "")

            if source_path.endswith(('.py', '.java', '.js', '.php', '.cpp', '.c', '.h')):
                chunk.metadata["type"] = "source_code"
            elif source_path.endswith(('.md', '.txt', '.rst')):
                chunk.metadata["type"] = "documentation"
            elif source_path.endswith(('.json', '.yaml', '.yml', '.xml')):
                chunk.metadata["type"] = "configuration"
            else:
                chunk.metadata["type"] = "other"

            filename = os.path.basename(source_path)
            chunk.metadata["filename"] = filename

            ext = filename.split('.')[-1] if '.' in filename else ''
            language_map = {
                'py': 'python', 'java': 'java', 'js': 'javascript',
                'ts': 'typescript', 'php': 'php', 'rb': 'ruby',
                'go': 'go', 'cpp': 'cpp', 'c': 'c', 'h': 'c',
                'cs': 'csharp', 'kt': 'kotlin', 'swift': 'swift',
                'rs': 'rust', 'html': 'html', 'css': 'css'
            }
            chunk.metadata["language"] = language_map.get(ext, 'unknown')

        print(f"Chunks criados: {len(chunks)}")
        return chunks

    def index_documents(self, force_reindex: bool = False):
        """Indexa documentos no ChromaDB"""
        try:
            existing_count = 0
            try:
                existing_count = self.vectorstore._collection.count()
            except:
                existing_count = 0

            if not force_reindex and existing_count > 0:
                print("📚 Índice já existe.")
                return

            print("📄 Indexando documentos...")

            if force_reindex or existing_count == 0:
                print("🗑️ Recriando índice...")
                try:
                    self.vectorstore.delete_collection()
                except:
                    pass

                self.vectorstore = Chroma(
                    persist_directory=self.config.CHROMA_DB_PATH,
                    embedding_function=self.embeddings
                )

            documents = self.load_documents()
            if not documents:
                print("⚠️ Nenhum documento encontrado!")
                return

            chunks = self.process_documents(documents)
            if not chunks:
                print("⚠️ Nenhum chunk criado!")
                return

            batch_sizes = {
                "gemma3:270m": 25, "qwen3:0.6b": 30, "gemma3:1b": 40,
                "deepseek-r1:1.5b": 50, "qwen3:1.7b": 75, "qwen2.5:3b": 100, "gemma3:4b": 150
            }

            current_model = self.get_current_model()
            batch_size = batch_sizes.get(current_model, 50)

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                print(f"Lote {i // batch_size + 1}/{(len(chunks) // batch_size) + 1}")
                try:
                    self.vectorstore.add_documents(batch)
                except Exception as e:
                    print(f"⚠️ Erro no lote: {e}")
                    continue

            try:
                self.vectorstore.persist()
            except:
                pass

            print("Indexação concluída!")

        except Exception as e:
            print(f"Erro na indexação: {e}")
            raise e

    def clear_index(self):
        """Limpa o índice"""
        try:
            print("Limpando índice...")
            self.vectorstore.delete_collection()

            self.vectorstore = Chroma(
                persist_directory=self.config.CHROMA_DB_PATH,
                embedding_function=self.embeddings
            )

            template = self._get_optimized_template(self.get_current_model())
            prompt = PromptTemplate(input_variables=["context", "question"], template=template)

            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": self.config.MAX_RESULTS}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )

            print("Índice limpo!")
            return True

        except Exception as e:
            print(f"Erro ao limpar: {e}")
            return False

    def query(self, question: str) -> dict:
        """Faz consulta no RAG"""
        if not self.qa_chain:
            raise Exception("RAG não inicializado")

        # Verificar documentos
        try:
            doc_count = self.vectorstore._collection.count()
            if doc_count == 0:
                return {
                    "answer": "Nenhum documento indexado. Use a sidebar para indexar.",
                    "sources": [],
                    "response_time": 0
                }
        except Exception as e:
            return {
                "answer": f"Erro na base: {str(e)}",
                "sources": [],
                "response_time": 0
            }

        print(f"Pergunta: {question}")

        import time
        start_time = time.time()

        optimized_question = self._optimize_question_for_model(question)

        try:
            result = self.qa_chain({"query": optimized_question})
            response_time = time.time() - start_time

            cleaned_answer = self._clean_thinking_tags(result["result"])

            return {
                "answer": cleaned_answer,
                "sources": [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]],
                "response_time": round(response_time, 2)
            }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "answer": f"Erro: {str(e)}",
                "sources": [],
                "response_time": round(response_time, 2)
            }

    def _clean_thinking_tags(self, text: str) -> str:
        """Remove tags de pensamento"""
        import re

        patterns = [
            r'<think>.*?</think>',
            r'<thinking>.*?</thinking>',
            r'<thought>.*?</thought>',
        ]

        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.IGNORECASE)

        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
        return cleaned_text.strip()

    def _optimize_question_for_model(self, question: str) -> str:
        """Otimiza pergunta por modelo"""
        current_model = self.get_current_model()
        question_lower = question.lower()

        presentation_keywords = ["apresentar", "quem é", "você é", "suas capacidades", "o que faz"]
        is_presentation = any(keyword in question_lower for keyword in presentation_keywords)

        if is_presentation:
            if current_model in ["gemma3:270m", "qwen3:0.6b"]:
                return "Quem é você e como pode ajudar?"
            else:
                return "Apresente-se como assistente de análise de código e suas capacidades"

        if current_model in ["gemma3:270m", "qwen3:0.6b"]:
            if "como funciona" in question_lower:
                return f"Explique: {question}"
            elif "onde está" in question_lower:
                return f"Localizar: {question}"

        return question

    def get_available_models(self) -> dict:
        """Lista modelos disponíveis"""
        try:
            import requests

            all_models = [
                "gemma3:270m", "qwen3:0.6b", "gemma3:1b",
                "deepseek-r1:1.5b", "qwen3:1.7b", "qwen2.5:3b", "gemma3:4b"
            ]

            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=5)

            if response.status_code == 200:
                existing_models = [model["name"] for model in response.json().get("models", [])]

                available = [model for model in all_models if model in existing_models]
                not_available = [model for model in all_models if model not in existing_models]

                return {
                    "available": available,
                    "not_available": not_available,
                    "total_models": len(existing_models),
                    "error": None
                }
            else:
                return {
                    "available": [],
                    "not_available": all_models,
                    "total_models": 0,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "available": [],
                "not_available": all_models,
                "total_models": 0,
                "error": str(e)
            }

    def change_model(self, new_model: str) -> tuple[bool, str]:
        """Troca modelo"""
        try:
            print(f"Trocando para: {new_model}")

            models_status = self.get_available_models()
            if new_model not in models_status.get("available", []):
                return False, f"Modelo {new_model} não está baixado"

            old_llm = self.llm
            old_chain = self.qa_chain

            try:
                self.llm = self._create_optimized_llm(new_model)
                if self.vectorstore:
                    doc_count = self.vectorstore._collection.count()
                    if doc_count > 0:
                        template = self._get_optimized_template(new_model)
                        prompt = PromptTemplate(input_variables=["context", "question"], template=template)
                        max_results = self._get_optimal_k_for_model(new_model)

                        self.qa_chain = RetrievalQA.from_chain_type(
                            llm=self.llm,
                            chain_type="stuff",
                            retriever=self.vectorstore.as_retriever(search_kwargs={"k": max_results}),
                            return_source_documents=True,
                            chain_type_kwargs={"prompt": prompt}
                        )

                        test_stats = self.debug_vectorstore()
                        if not test_stats.get("search_working", False):
                            raise Exception("Chain não funciona")

                    else:
                        return False, "Nenhum documento indexado"

                print(f"Modelo {new_model} ativo!")
                return True, f"Modelo {new_model} ativo"

            except Exception as chain_error:
                # Rollback
                self.llm = old_llm
                self.qa_chain = old_chain
                return False, f"Erro na configuração: {str(chain_error)}"

        except Exception as e:
            return False, f"Erro: {str(e)}"

    def debug_vectorstore(self) -> dict:
        """Debug da vectorstore"""
        try:
            if not self.vectorstore:
                return {"error": "Vectorstore não existe"}

            collection = self.vectorstore._collection
            count = collection.count()

            info = {
                "collection_exists": True,
                "document_count": count,
                "collection_id": str(collection.id) if hasattr(collection, 'id') else "unknown"
            }

            if count > 0:
                try:
                    test_results = self.vectorstore.similarity_search("test", k=1)
                    info["search_working"] = True
                    info["test_results"] = len(test_results)
                except Exception as search_error:
                    info["search_working"] = False
                    info["search_error"] = str(search_error)

            return info

        except Exception as e:
            return {"error": f"Erro: {str(e)}", "collection_exists": False}

    def get_current_model(self) -> str:
        """Modelo atual"""
        if hasattr(self.llm, 'model'):
            return self.llm.model
        return self.config.DEFAULT_MODEL

    def get_stats(self) -> dict:
        """Estatísticas do sistema"""
        if not self.vectorstore:
            return {"error": "Vectorstore não inicializado", "total_documents": 0}

        debug_info = self.debug_vectorstore()

        if debug_info.get("error"):
            return {"error": debug_info["error"], "total_documents": 0}

        count = debug_info.get("document_count", 0)
        current_model = self.get_current_model()
        model_info = self.get_model_info(current_model)

        return {
            "total_documents": count,
            "models": {
                "llm": current_model,
                "embedding": self.config.EMBEDDING_MODEL
            },
            "model_info": model_info,
            "debug": debug_info
        }

    def set_custom_source_path(self, new_path: str) -> bool:
        """Define nova pasta de código fonte"""
        try:
            if not os.path.exists(new_path):
                print(f"Pasta não existe: {new_path}")
                return False

            if not os.path.isdir(new_path):
                print(f"Não é uma pasta: {new_path}")
                return False

            old_path = self.config.SOURCE_CODE_PATH
            self.config.SOURCE_CODE_PATH = new_path

            # Reiniciar monitoramento se ativo
            if hasattr(self, 'file_watcher') and self.file_watcher:
                print("🔄 Reiniciando monitoramento...")
                self.stop_auto_reindex()
                self.start_auto_reindex(new_path)

            print(f"Pasta: {old_path} → {new_path}")
            return True

        except Exception as e:
            print(f"Erro: {e}")
            return False

    def start_auto_reindex(self, source_path: str = None):
        """Inicia monitoramento automático"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            import time

            if not source_path:
                source_path = self.config.SOURCE_CODE_PATH

            class ChangeHandler(FileSystemEventHandler):
                def __init__(self, rag_engine):
                    self.rag_engine = rag_engine
                    self.last_modified = time.time()

                def on_modified(self, event):
                    if event.is_directory:
                        return

                    current_time = time.time()
                    if current_time - self.last_modified > 30:
                        print(f"📝 Modificado: {event.src_path}")
                        try:
                            self.rag_engine.index_documents(force_reindex=True)
                            self.last_modified = current_time
                            print("Reindexação automática OK!")
                        except Exception as e:
                            print(f"Erro auto-reindex: {e}")

            self.file_watcher = Observer()
            self.file_watcher.schedule(ChangeHandler(self), source_path, recursive=True)
            self.file_watcher.start()

            print(f"Monitoramento ativo: {source_path}")
            return True

        except Exception as e:
            print(f"Erro monitoramento: {e}")
            return False

    def stop_auto_reindex(self):
        """Para monitoramento"""
        if hasattr(self, 'file_watcher') and self.file_watcher:
            try:
                self.file_watcher.stop()
                self.file_watcher.join()
                self.file_watcher = None
                print("Monitoramento parado")
            except Exception as e:
                print(f"⚠️ Erro ao parar: {e}")

    def get_current_source_path(self) -> str:
        """Pasta atual"""
        return self.config.SOURCE_CODE_PATH

    def remove_model(self, model_name: str) -> tuple[bool, str]:
        """Remove um modelo do Ollama"""
        try:
            import requests

            print(f"🗑️ Removendo modelo: {model_name}")

            models_status = self.get_available_models()
            if model_name not in models_status.get("available", []):
                return False, f"Modelo {model_name} não está instalado"

            current_model = self.get_current_model()
            if model_name == current_model:
                return False, f"Não é possível remover o modelo ativo ({model_name}). Troque para outro modelo primeiro."

            response = requests.delete(
                f"{self.config.OLLAMA_BASE_URL}/api/delete",
                json={"name": model_name},
                timeout=30
            )

            if response.status_code == 200:
                print(f"Modelo {model_name} removido com sucesso!")
                return True, f"Modelo {model_name} removido"
            else:
                error_msg = f"Erro HTTP {response.status_code}"
                try:
                    error_detail = response.json().get("error", "")
                    if error_detail:
                        error_msg += f": {error_detail}"
                except:
                    pass

                return False, error_msg

        except Exception as e:
            error_msg = f"Erro ao remover modelo: {str(e)}"
            print(f"{error_msg}")
            return False, error_msg

    def get_model_disk_usage(self, model_name: str) -> str:
        """Retorna o uso de disco estimado de um modelo"""
        try:
            import requests

            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"] == model_name:
                        size_bytes = model.get("size", 0)
                        size_gb = size_bytes / (1024 ** 3)
                        return f"{size_gb:.1f}GB"

            # Fallback para estimativas conhecidas
            size_estimates = {
                "gemma3:270m": "0.3GB",
                "qwen3:0.6b": "0.6GB",
                "gemma3:1b": "1.0GB",
                "deepseek-r1:1.5b": "1.5GB",
                "qwen3:1.7b": "1.7GB",
                "qwen2.5:3b": "3.0GB",
                "gemma3:4b": "4.0GB"
            }

            return size_estimates.get(model_name, "?GB")

        except Exception:
            return "?GB"