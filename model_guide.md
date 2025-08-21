# 🤖 Guia de Modelos KRAG

##  Comparativo de Modelos

| Modelo | Parâmetros | RAM | Velocidade | Qualidade | Melhor Para |
|--------|------------|-----|------------|-----------|-------------|
| **gemma3:270m** | 270M | ~1.5GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Testes rápidos, prototipagem |
| **qwen3:0.6b** | 600M | ~2GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Análise básica, desenvolvimento ágil |
| **gemma3:1b** | 1B | ~3GB | ⚡⚡⚡ | ⭐⭐⭐ | Uso geral balanceado |
| **deepseek-r1:1.5b** | 1.5B | ~4GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Reasoning, lógica complexa |
| **qwen3:1.7b** | 1.7B | ~4.5GB | ⚡⚡ | ⭐⭐⭐⭐ | Análise de qualidade |
| **qwen2.5:3b** | 3B | ~6GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Análises complexas |
| **gemma3:4b** | 4B | ~8GB | ⚡ | ⭐⭐⭐⭐⭐ | Análise profunda, produção |

##  Recomendações de Uso

### ‍️ **Para Desenvolvimento Rápido**
- **gemma3:270m**: Ideal para iteração rápida, testes de conceito
- **qwen3:0.6b**: Bom equilíbrio entre velocidade e qualidade básica

### ️ **Para Uso Geral**
- **gemma3:1b**: Melhor custo-benefício geral
- **deepseek-r1:1.5b**: Quando precisar de raciocínio mais elaborado

### **Para Análise Profunda**
- **qwen3:1.7b**: Análises mais detalhadas sem consumir muitos recursos
- **qwen2.5:3b**: Para projetos grandes e complexos
- **gemma3:4b**: Máxima qualidade quando recursos não são limitação

## ️ **Configurações Automáticas por Modelo**

Cada modelo tem configurações otimizadas automaticamente:

### **Ultra-Compactos (270M-600M)**
- Context window: 1024-1536 tokens
- Chunk size: 600-700 caracteres
- Documentos recuperados: 3
- Batch size: 25-30

### **Compactos (1B-1.5B)**
- Context window: 2048 tokens
- Chunk size: 800-900 caracteres
- Documentos recuperados: 4
- Batch size: 40-50

### **Médios/Robustos (1.7B+)**
- Context window: 2560-4096 tokens
- Chunk size: 1000-1400 caracteres
- Documentos recuperados: 5
- Batch size: 75-150

## 🔄 **Troca de Modelos em Tempo Real**

Você pode trocar modelos a qualquer momento na interface:
1. Vá na sidebar > "Configuração do Modelo"
2. Selecione o modelo desejado
3. O sistema reconfigura automaticamente todos os parâmetros
4. Continue a conversa com o novo modelo

## 💡 **Dicas de Performance**

### **Hardware Limitado** (< 8GB RAM)
Recomendado: `gemma3:270m`, `qwen3:0.6b`, `gemma3:1b`

### **Hardware Médio** (8-16GB RAM)
Recomendado: `deepseek-r1:1.5b`, `qwen3:1.7b`, `qwen2.5:3b`

### **Hardware Robusto** (16GB+ RAM)
Recomendado: `gemma3:4b`, `qwen2.5:3b`

## 🎨 **Casos de Uso Específicos**

### **Análise de Arquitetura**
- Melhor: `gemma3:4b`, `qwen2.5:3b`
- Alternativa rápida: `qwen3:1.7b`

### **Debugging Rápido**
- Melhor: `gemma3:270m`, `qwen3:0.6b`
- Para problemas complexos: `deepseek-r1:1.5b`

### **Documentação de Código**
- Melhor: `qwen3:1.7b`, `qwen2.5:3b`
- Rápido: `gemma3:1b`

### **Onboarding de Novos Devs**
- Melhor: `qwen2.5:3b`, `gemma3:4b`
- Básico: `gemma3:1b`, `qwen3:1.7b`

---

## 🚀 **Começando**

1. **Primeiro uso**: Comece com `gemma3:1b` (bom equilíbrio)
2. **Se muito lento**: Mude para `qwen3:0.6b` ou `gemma3:270m`
3. **Se qualidade baixa**: Suba para `qwen3:1.7b` ou `qwen2.5:3b`
4. **Para produção**: Use `gemma3:4b` ou `qwen2.5:3b`

**Lembre-se**: Você pode trocar modelos a qualquer momento sem perder o índice de documentos!