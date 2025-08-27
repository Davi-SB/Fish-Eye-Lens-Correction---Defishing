# Aplicação de Correção Fisheye - Parâmetros Fixos

Esta versão da aplicação utiliza **parâmetros fixos** exatamente como mostrados na imagem de referência, sem possibilidade de alteração.

## 🎯 Características

- **Parâmetros Fixos**: Valores exatos da imagem de referência
- **Sem Ajustes**: Não é possível alterar os parâmetros
- **Processamento Automático**: Correção aplicada automaticamente
- **Interface Simples**: Foco na visualização e salvamento

## ⚙️ Parâmetros Fixos (Exatos da Imagem)

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| **FOV** | 180 | Campo de visão da lente fisheye |
| **PFOV** | 140 | Campo de visão da imagem de saída |
| **X center** | -1 | Centro X (automático) |
| **Y center** | -1 | Centro Y (automático) |
| **Radius** | -1.4 | Raio da área fisheye |
| **Angle** | -1 | Rotação (automático) |
| **Dtype** | stereographic | Tipo de distorção |
| **Format** | fullframe | Formato da imagem |
| **Pad** | 0 | Padding da imagem |

## 🚀 Como Usar

### Instalação
```bash
pip install -r requirements.txt
```

### Execução
```bash
python integrated_defisheye_app.py
```

### Uso da Interface

1. **Abrir Imagem**: Clique em "📁 Abrir Imagem" para selecionar uma imagem fisheye
2. **Visualizar**: A correção é aplicada automaticamente com os parâmetros fixos
3. **Salvar**: Clique em "💾 Salvar Resultado" para salvar a imagem corrigida
4. **Informações**: Clique em "ℹ️ Parâmetros" para ver os parâmetros fixos

## 🎨 Interface

```
┌─────────────────────────────────────────────────────────────┐
│ [📁 Abrir] [💾 Salvar] [ℹ️ Parâmetros]                    │
├─────────────────┬───────────────────────────────────────────┤
│ Parâmetros      │ ┌─────────────┐ ┌─────────────┐          │
│ Fixos:          │ │ Original    │ │ Corrigida   │          │
│ FOV: 180        │ │ Image       │ │ Image       │          │
│ PFOV: 140       │ │             │ │             │          │
│ X center: -1    │ │             │ │             │          │
│ Y center: -1    │ │             │ │             │          │
│ Radius: -1.4    │ │             │ │             │          │
│ Angle: -1       │ │             │ │             │          │
│ Dtype: stereo   │ │             │ │             │          │
│ Format: full    │ │             │ │             │          │
│ Pad: 0          │ └─────────────┘ └─────────────┘          │
│                 │                                          │
│ [🔄 Processar]  │                                          │
└─────────────────┴───────────────────────────────────────────┘
```

## 📋 Funcionalidades

### ✅ Disponíveis
- Carregamento de imagens fisheye
- Correção automática com parâmetros fixos
- Visualização lado a lado (original vs corrigida)
- Salvamento da imagem corrigida
- Informações sobre parâmetros fixos

### ❌ Não Disponíveis
- Alteração de parâmetros
- Sistema de presets
- Validação de entrada
- Ajustes em tempo real

## 🔧 Uso Programático

```python
from integrated_defisheye_app import DefisheyeAlgorithm

# Parâmetros fixos (exatos da imagem)
params = {
    "fov": 180,
    "pfov": 140,
    "xcenter": None,  # -1 se torna None
    "ycenter": None,  # -1 se torna None
    "radius": -1.4,
    "angle": None,    # -1 se torna None
    "dtype": "stereographic",
    "format": "fullframe",
    "pad": 0
}

# Aplicar correção
defisheye = DefisheyeAlgorithm("imagem.jpg", **params)
corrected_image = defisheye.convert()
```

## 🎯 Casos de Uso

### Ideal Para:
- Correção consistente de imagens fisheye
- Processamento em lote com parâmetros padronizados
- Usuários que não precisam de ajustes finos
- Aplicações que requerem resultados reproduzíveis

### Não Ideal Para:
- Ajustes finos de correção
- Experimentação com diferentes parâmetros
- Lentes com características muito específicas
- Usuários que precisam de controle total

## 📊 Comparação com Versão Completa

| Característica | Versão Fixa | Versão Completa |
|----------------|-------------|-----------------|
| **Parâmetros** | Fixos | Ajustáveis |
| **Interface** | Simples | Avançada |
| **Presets** | ❌ | ✅ |
| **Validação** | ❌ | ✅ |
| **Flexibilidade** | Baixa | Alta |
| **Facilidade** | Alta | Média |

## 🔄 Fluxo de Processamento

1. **Carregamento**: Imagem é carregada
2. **Parâmetros Fixos**: Valores exatos da imagem são aplicados
3. **Correção**: Algoritmo defisheye é executado
4. **Exibição**: Resultado é mostrado lado a lado
5. **Salvamento**: Imagem pode ser salva

## 📝 Notas Técnicas

- **Algoritmo**: Baseado no projeto defisheye
- **Processamento**: OpenCV + NumPy
- **Interface**: Tkinter
- **Parâmetros**: Exatamente como na imagem de referência
- **Compatibilidade**: Python 3.6+

## 🎯 Vantagens dos Parâmetros Fixos

1. **Consistência**: Sempre o mesmo resultado
2. **Simplicidade**: Interface mais limpa
3. **Velocidade**: Sem validação de entrada
4. **Confiabilidade**: Menos pontos de falha
5. **Reproduzibilidade**: Resultados idênticos

## 📞 Suporte

Para dúvidas sobre esta versão:
- Verifique os parâmetros fixos na interface
- Use o botão "ℹ️ Parâmetros" para informações
- Consulte a documentação da versão completa se precisar de flexibilidade

---

**Versão com parâmetros fixos - Sempre aplica os valores exatos da imagem de referência**

