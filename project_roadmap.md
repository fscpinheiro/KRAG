# KRAG - Roadmap de Desenvolvimento

## Visão Geral
Este documento detalha as próximas implementações planejadas para o KRAG, focando em melhorar a experiência do usuário, arquitetura do código e funcionalidades essenciais.

## TAREFA 1: Contexto Compartilhado Entre Modelos
**Prioridade: ALTA**

### Objetivo
Permitir que diferentes modelos LLM mantenham continuidade da conversa quando o usuário troca entre eles.

### Funcionalidades
- Sistema de resumo automático da conversa anterior
- Injeção inteligente de contexto no novo modelo
- Toggle para escolher entre "Continuar conversa" ou "Começar do zero"
- Indicador visual quando há contexto transferido

### Implementação Técnica
- Função `generate_conversation_summary()` para criar resumos
- Modificação no `change_model()` para incluir contexto
- Sistema de mensagens do tipo "system" para contexto
- Interface na sidebar para controlar comportamento

### Impacto Esperado
- Usuário não perde contexto ao trocar modelos
- Permite usar modelo rápido para exploração e robusto para análise
- Fluxo natural de trabalho entre diferentes especialidades de modelo

---

## TAREFA 2: Sistema de Persistência de Conversas
**Prioridade: ALTA**

### Objetivo
Implementar sistema completo de salvamento, carregamento e gestão de conversas históricas.

### Funcionalidades
- Banco SQLite local para armazenar conversas
- Interface para listar, carregar e deletar conversas salvas
- Títulos automáticos baseados no conteúdo das conversas
- Sistema de busca em conversas anteriores
- Gestão automática de espaço com cleanup inteligente

### Implementação Técnica
- Classe `ConversationManager` para gerenciar persistência
- Schema SQLite com tabelas: sessions, messages, metadata
- Sistema de limites configurable (200 mensagens/sessão, 90 dias retenção)
- Auto-cleanup baseado em idade e importância das conversas
- Interface na sidebar para gestão de conversas

### Estrutura de Dados
```sql
CREATE TABLE conversation_sessions (
    id INTEGER PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP,
    last_updated TIMESTAMP,
    project_path TEXT,
    total_messages INTEGER,
    status TEXT DEFAULT 'active'
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    model_name TEXT,
    role TEXT,
    content TEXT,
    sources JSON,
    response_time REAL,
    created_at TIMESTAMP
);
```

### Impacto Esperado
- Histórico completo de análises por projeto
- Continuidade entre sessões de trabalho
- Base de conhecimento acumulado sobre projetos

---

## TAREFA 3: Seletor de Pasta Externa + Arquitetura SOLID
**Prioridade: ALTA**

### Objetivo Principal: Seletor de Pasta
Permitir análise de qualquer projeto/repositório através de seleção de pasta externa.

#### Funcionalidades
- Dialog nativo do Windows para seleção de pastas
- Preview automático da pasta selecionada
- Validação e contagem de arquivos suportados
- Histórico de pastas analisadas recentemente
- Bookmarks para projetos frequentes

#### Implementação
- Integração com tkinter `filedialog.askdirectory()`
- Função `preview_folder()` para estatísticas da pasta
- Sistema de configuração dinâmica de caminhos
- Interface híbrida: dialog + input manual

### Objetivo Secundário: Refatoração Arquitetural (SOLID)

#### Melhorias na Interface
- Footer com estatísticas do sistema
- Nome do projeto/KRAG no cabeçalho da sidebar
- Layout mais fluido e responsivo
- Separação clara entre seções funcionais

#### Refatoração do Código
- **Single Responsibility**: Separar `main.py` em módulos específicos
  - `ui_components.py`: Componentes de interface
  - `session_manager.py`: Gerenciamento de sessão
  - `model_manager.py`: Operações com modelos
- **Open/Closed**: Interfaces abstratas para extensibilidade
- **Dependency Inversion**: Injeção de dependências no RAG engine
- **Interface Segregation**: Separar interfaces específicas por funcionalidade

#### Estrutura Proposta
```
app/
├── main.py                 # Orquestração principal
├── components/
│   ├── ui_sidebar.py      # Sidebar components  
│   ├── ui_chat.py         # Chat interface
│   ├── ui_modals.py       # Modals e dialogs
│   └── ui_footer.py       # Footer com stats
├── managers/
│   ├── conversation_manager.py
│   ├── model_manager.py
│   ├── folder_manager.py
│   └── session_manager.py
├── core/
│   ├── rag_engine.py      # Core RAG (refatorado)
│   ├── config_manager.py  # Configurações dinâmicas
│   └── interfaces.py      # Interfaces abstratas
└── utils/
    ├── file_utils.py
    ├── ui_utils.py
    └── validation.py
```

### Impacto Esperado
- Análise de qualquer projeto sem mover arquivos
- Código mais maintível e testável
- Interface mais profissional e intuitiva
- Base sólida para futuras funcionalidades

---

## TAREFA 4: Auto-Descoberta de Modelos + Documentação
**Prioridade: MÉDIA**


### Objetivo Principal: Auto-Descoberta
Detectar automaticamente novos modelos instalados no Ollama, mesmo que não estejam na lista hardcoded.

#### Funcionalidades
- Scan automático da API Ollama para descobrir modelos
- Classificação inteligente de modelos por família/tamanho
- Configuração automática de parâmetros baseada em heurísticas
- Lista dinâmica de modelos disponíveis

#### Implementação
- Função `discover_available_models()` que consulta `/api/tags`
- Sistema de classificação baseado em nome e tamanho
- Configuração de fallback para modelos desconhecidos
- Cache de descoberta com refresh periódico

### Objetivo Secundário: Documentação Completa
Criar documentação abrangente do projeto atual.

#### Conteúdo da Documentação
- Descrição do propósito e casos de uso do KRAG
- Lista completa de modelos suportados e suas características
- Guia de instalação e configuração Docker
- Instruções de uso passo-a-passo
- Exemplos práticos de análise de código
- Troubleshooting comum
- Arquitetura técnica e decisões de design

#### Estrutura dos Documentos
```
docs/
├── README.md              # Overview e quick start
├── INSTALLATION.md        # Setup detalhado
├── USER_GUIDE.md         # Manual do usuário
├── MODELS.md             # Guia de modelos
├── ARCHITECTURE.md       # Documentação técnica
└── TROUBLESHOOTING.md    # Resolução de problemas
```

### Modelos Documentados
- gemma3:270m - Ultra-rápido para prototipagem
- qwen3:0.6b - Eficiente para desenvolvimento ágil  
- gemma3:1b - Balanceado para uso geral
- deepseek-r1:1.5b - Especializado em reasoning complexo
- qwen3:1.7b - Foco em análise de qualidade
- qwen2.5:3b - Robusto para análises complexas
- gemma3:4b - Máxima qualidade para produção

### Docker Guide
- Pré-requisitos e instalação do Docker
- Comandos básicos do docker-compose
- Gerenciamento de modelos via container
- Backup e restore de dados
- Configuração de recursos (RAM, CPU)
- Logs e debugging

### Impacto Esperado
- Suporte automático para novos modelos lançados
- Documentação profissional para adoção
- Facilita onboarding de novos usuários
- Base para contribuições da comunidade

---


## Critérios de Sucesso

### Funcionalidade
- Contexto mantido entre trocas de modelo
- Conversas salvas e recuperáveis
- Análise de projetos externos sem configuração
- Interface fluida e profissional

### Qualidade de Código
- Cobertura de testes > 80%
- Arquitetura SOLID aplicada
- Documentação completa e atualizada
- Performance mantida ou melhorada

### Experiência do Usuário
- Setup em menos de 5 minutos
- Curva de aprendizado suave
- Feedback visual adequado
- Funcionalidades intuitivas