# KRAG - Sistema de Análise Inteligente

KRAG é um assistente de IA especializado em análise e compreensão de sistemas legados, utilizando tecnologia RAG (Retrieval-Augmented Generation) para transformar bases de código complexas em conhecimento acessível através de conversas em linguagem natural.

## Propósito

O KRAG foi desenvolvido para resolver problemas críticos no desenvolvimento de software:

**Para Desenvolvedores:**
- Reduzir tempo perdido explorando código desconhecido
- Acelerar onboarding em projetos complexos
- Facilitar compreensão de arquiteturas legadas
- Identificar dependências e impactos de mudanças
- Localizar funcionalidades específicas rapidamente

**Para Empresas:**
- Diminuir custos de manutenção de sistemas legados
- Reduzir dependência de desenvolvedores seniores específicos
- Acelerar desenvolvimento de novas features
- Preservar conhecimento técnico institucional
- Mitigar riscos em mudanças de código crítico

## Casos de Uso

### Análise de Código Legado
- "Como funciona o sistema de autenticação neste projeto?"
- "Onde está implementada a validação de CPF?"
- "Quais arquivos serão impactados se eu mudar a API de pagamentos?"
- "Explique a arquitetura geral deste sistema"

### Onboarding de Desenvolvedores
- "Quais são as principais classes e suas responsabilidades?"
- "Como adicionar um novo tipo de usuário?"
- "Onde estão os pontos de integração com serviços externos?"
- "Qual é o fluxo de dados principal da aplicação?"

### Due Diligence Técnica
- "Identifique possíveis vulnerabilidades de segurança"
- "Avalie a qualidade geral do código"
- "Quais são os principais riscos técnicos?"
- "Estime a complexidade de implementar funcionalidade X"

## Modelos LLM Suportados

O KRAG suporta múltiplos modelos Ollama otimizados para diferentes cenários de uso:

### Modelos Ultra-Compactos
**gemma3:270m**
- Tamanho: ~300MB
- RAM necessária: ~1.5GB
- Velocidade: Ultra-rápida
- Ideal para: Prototipagem rápida, testes de conceito
- Contexto: 1024 tokens

**qwen3:0.6b** 
- Tamanho: ~600MB
- RAM necessária: ~2GB
- Velocidade: Muito rápida
- Ideal para: Desenvolvimento ágil, análise básica
- Contexto: 1536 tokens

### Modelos Balanceados
**gemma3:1b**
- Tamanho: ~1GB
- RAM necessária: ~3GB
- Velocidade: Rápida
- Ideal para: Uso geral, melhor custo-benefício
- Contexto: 2048 tokens

**deepseek-r1:1.5b**
- Tamanho: ~1.5GB
- RAM necessária: ~4GB
- Velocidade: Rápida
- Ideal para: Reasoning complexo, análise lógica
- Contexto: 2048 tokens

### Modelos Robustos
**qwen3:1.7b**
- Tamanho: ~1.7GB
- RAM necessária: ~4.5GB
- Velocidade: Média
- Ideal para: Análises detalhadas de qualidade
- Contexto: 2560 tokens

**qwen2.5:3b**
- Tamanho: ~3GB
- RAM necessária: ~6GB
- Velocidade: Média
- Ideal para: Projetos grandes, análises complexas
- Contexto: 3072 tokens

**gemma3:4b**
- Tamanho: ~4GB
- RAM necessária: ~8GB
- Velocidade: Mais lenta
- Ideal para: Análises profundas, ambiente de produção
- Contexto: 4096 tokens

## Linguagens de Programação Suportadas

O sistema analisa automaticamente arquivos nas seguintes linguagens:

**Backend:** Python, Java, PHP, Ruby, Go, C++, C, C#, Kotlin, Swift, Rust
**Frontend:** JavaScript, TypeScript, JSX, TSX, Vue, HTML, CSS, SCSS
**Configuração:** JSON, XML, YAML, SQL, Properties, ENV, INI
**Documentação:** Markdown, TXT, RST

## Instalação e Uso com Docker

### Pré-requisitos
- Docker Desktop instalado e rodando
- Pelo menos 8GB de RAM disponível
- 10GB de espaço livre em disco

### Instalação Rápida

1. **Clone o repositório:**
```bash
git clone git@github.com:fscpinheiro/KRAG.git
cd krag
```

2. **Execute o setup automático (Windows):**
```bash
setup.bat
```

3. **Ou inicie manualmente:**
```bash
# Criar estrutura de diretórios
mkdir -p data/source_code data/docs chroma_db

# Iniciar todos os serviços
docker-compose up -d --build
```

4. **Aguarde a inicialização:**
O sistema baixará automaticamente os modelos essenciais (gemma3:1b e nomic-embed-text).

5. **Acesse a interface:**
Abra http://localhost:8501 no navegador

### Estrutura de Diretórios
```
KRAG/
├── data/
│   ├── source_code/    # Coloque seu código aqui
│   └── docs/           # Documentação adicional
├── chroma_db/          # Base vetorial (criada automaticamente)
├── app/                # Aplicação Streamlit
├── docker-compose.yml  # Orquestração dos serviços
└── requirements.txt    # Dependências Python
```

### Comandos Docker Úteis

**Verificar status dos serviços:**
```bash
docker-compose ps
```

**Ver logs da aplicação:**
```bash
docker-compose logs krag
```

**Ver logs do Ollama:**
```bash
docker-compose logs ollama
```

**Reiniciar serviços:**
```bash
docker-compose restart
```

**Parar tudo:**
```bash
docker-compose down
```

**Atualizar e reiniciar:**
```bash
docker-compose down
docker-compose up -d --build
```

### Gerenciamento de Modelos

**Baixar modelo específico:**
```bash
# Encontrar container do Ollama
docker ps | grep ollama

# Baixar modelo
docker exec -it <container_id> ollama pull qwen2.5:3b
```

**Listar modelos instalados:**
```bash
docker exec -it <container_id> ollama list
```

**Remover modelo:**
```bash
docker exec -it <container_id> ollama rm <nome_do_modelo>
```

## Como Usar

### Primeira Configuração

1. **Adicione seu código:**
   - Copie arquivos para `data/source_code/`
   - Ou use a interface para selecionar pasta externa

2. **Indexe os documentos:**
   - Clique em "Indexar Primeira Vez" na sidebar
   - Aguarde o processamento completo

3. **Escolha o modelo:**
   - Selecione o modelo mais adequado ao seu hardware
   - Para hardware limitado: gemma3:1b
   - Para análises profundas: qwen2.5:3b ou gemma3:4b

### Exemplos de Perguntas

**Arquitetura Geral:**
- "Descreva a arquitetura geral deste sistema"
- "Quais são os principais módulos e suas responsabilidades?"
- "Como os componentes se comunicam entre si?"

**Funcionalidades Específicas:**
- "Como funciona o sistema de login?"
- "Onde está implementada a validação de dados?"
- "Como são processados os pagamentos?"

**Análise de Impacto:**
- "Se eu mudar a API de usuários, quais arquivos serão afetados?"
- "Quais são as dependências do módulo de relatórios?"
- "Como adicionar uma nova funcionalidade de notificações?"

**Segurança e Qualidade:**
- "Identifique possíveis vulnerabilidades de segurança"
- "Há problemas de performance evidentes?"
- "O código segue boas práticas?"

## Configuração Avançada

### Variáveis de Ambiente (.env)
```bash
# Modelo LLM padrão
DEFAULT_MODEL=gemma3:1b

# Modelo de embedding
EMBEDDING_MODEL=nomic-embed-text

# Configurações RAG
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RESULTS=5

# Debug
DEBUG=False
```

### Otimização por Hardware

**Hardware Básico (< 8GB RAM):**
- Use: gemma3:270m, qwen3:0.6b, gemma3:1b
- Chunk size: 600-800 caracteres
- Max results: 3-4

**Hardware Médio (8-16GB RAM):**
- Use: deepseek-r1:1.5b, qwen3:1.7b, qwen2.5:3b
- Chunk size: 900-1200 caracteres
- Max results: 4-5

**Hardware Premium (16GB+ RAM):**
- Use: qwen2.5:3b, gemma3:4b
- Chunk size: 1200-1400 caracteres
- Max results: 5+

## Troubleshooting

### Problemas Comuns

**Container não inicia:**
```bash
# Verificar se Docker está rodando
docker info

# Verificar portas em uso
netstat -an | findstr 8501
netstat -an | findstr 11434
```

**Modelo não baixa:**
```bash
# Verificar conectividade
docker exec -it <ollama_container> curl -I https://ollama.ai

# Tentar download manual
docker exec -it <ollama_container> ollama pull gemma3:1b
```

**Performance baixa:**
- Verifique uso de RAM: `docker stats`
- Reduza chunk_size se necessário
- Use modelo menor (gemma3:270m)
- Aumente recursos do Docker Desktop

**Erro de indexação:**
- Verifique arquivos na pasta `data/source_code/`
- Confirme que há arquivos de código suportados
- Check logs: `docker-compose logs krag`

## Arquitetura Técnica

### Stack Tecnológica
- **LLM Backend:** Ollama (local)
- **Embeddings:** nomic-embed-text
- **Vector Database:** ChromaDB
- **Framework RAG:** LangChain
- **Interface:** Streamlit
- **Containerização:** Docker Compose

### Fluxo de Dados
1. **Ingestão:** Código é carregado e fragmentado otimamente
2. **Embedding:** Fragmentos são convertidos em vetores semânticos
3. **Indexação:** Vetores são armazenados no ChromaDB
4. **Consulta:** Pergunta do usuário é convertida em embedding
5. **Retrieval:** Fragmentos mais relevantes são recuperados
6. **Generation:** LLM gera resposta baseada no contexto recuperado

### Segurança e Privacidade
- **Execução 100% local** - nenhum dado sai da máquina
- **Sem dependências cloud** - funciona offline
- **Dados criptografados** em repouso no ChromaDB
- **Logs auditáveis** de todas as consultas

## Contribuição

Contribuições são bem-vindas! Áreas de interesse:
- Suporte a novas linguagens de programação
- Otimizações de performance
- Novos modelos LLM
- Melhorias na interface
- Documentação e exemplos

## Suporte

Para problemas, sugestões ou discussões:
- Abra uma issue no GitHub
- Consulte a documentação completa na pasta `docs/`
- Verifique o troubleshooting acima