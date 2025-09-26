# Guia de Integração: Defisheye + Fish-Eye-Lens-Correction

Este documento explica como foi realizada a integração entre o algoritmo do projeto **defisheye** e a interface do projeto **Fish-Eye-Lens-Correction**.

## 🎯 Objetivo da Integração

Criar uma aplicação unificada que combine:
- **Algoritmo robusto** do projeto defisheye para correção de distorção fisheye
- **Interface intuitiva** similar à mostrada na imagem de referência
- **Controles em tempo real** para ajuste de parâmetros
- **Visualização lado a lado** da imagem original e corrigida

## 📁 Estrutura dos Arquivos Criados

```
Fish-Eye-Lens-Correction---Defishing-main/
├── integrated_defisheye_app.py      # Aplicação principal integrada
├── config.py                        # Configurações e presets
├── requirements.txt                 # Dependências do projeto
├── install_and_run.py              # Script de instalação automática
├── example_usage.py                # Exemplos de uso programático
├── README_INTEGRATED.md            # Documentação da aplicação
└── INTEGRATION_GUIDE.md            # Este arquivo
```

## 🔧 Componentes da Integração

### 1. **DefisheyeAlgorithm** (integrated_defisheye_app.py)
```python
class DefisheyeAlgorithm:
    """
    Algoritmo de correção fisheye baseado no projeto defisheye
    """
```

**Características:**
- Implementação completa do algoritmo do projeto defisheye
- Suporte a múltiplos tipos de distorção (linear, equalarea, orthographic, stereographic)
- Parâmetros configuráveis (FOV, PFOV, centro, raio, ângulo, etc.)
- Processamento eficiente usando OpenCV

### 2. **IntegratedDefisheyeApp** (integrated_defisheye_app.py)
```python
class IntegratedDefisheyeApp:
    """
    Aplicação integrada com interface gráfica para correção de lente fisheye
    """
```

**Características:**
- Interface gráfica moderna usando Tkinter
- Controles em tempo real para todos os parâmetros
- Visualização lado a lado (original vs corrigida)
- Sistema de presets para diferentes tipos de lente
- Validação de parâmetros em tempo real

### 3. **Sistema de Presets** (config.py)
```python
FISHEYE_PRESETS = {
    "stereographic": { ... },
    "linear": { ... },
    "equalarea": { ... },
    "orthographic": { ... },
    "ultra_wide": { ... },
    "circular": { ... }
}
```

**Características:**
- Presets pré-configurados para diferentes tipos de lente
- Validação automática de parâmetros
- Informações descritivas para cada preset

## 🎨 Interface do Usuário

### Layout da Interface
```
┌─────────────────────────────────────────────────────────────┐
│ [📁 Abrir] [💾 Salvar] [Presets: ▼] [ℹ️ Info]              │
├─────────────────┬───────────────────────────────────────────┤
│ Parâmetros:     │ ┌─────────────┐ ┌─────────────┐          │
│ FOV: [180]      │ │ Original    │ │ Corrigida   │          │
│ PFOV: [140]     │ │ Image       │ │ Image       │          │
│ X center: [-1]  │ │             │ │             │          │
│ Y center: [-1]  │ │             │ │             │          │
│ Radius: [-1.4]  │ │             │ │             │          │
│ Angle: [-1]     │ │             │ │             │          │
│ Dtype: [▼]      │ │             │ │             │          │
│ Format: [▼]     │ │             │ │             │          │
│ Pad: [0]        │ └─────────────┘ └─────────────┘          │
│                 │                                          │
│ [🔄 Processar]  │                                          │
└─────────────────┴───────────────────────────────────────────┘
```

### Controles Disponíveis
- **📁 Abrir Imagem**: Seleciona imagem fisheye para correção
- **💾 Salvar Resultado**: Salva a imagem corrigida
- **Presets**: Seleção rápida de configurações pré-definidas
- **ℹ️ Info**: Informações sobre o preset selecionado
- **Parâmetros**: Controles individuais para ajuste fino
- **🔄 Processar**: Aplica a correção (automático em tempo real)

## ⚙️ Parâmetros de Correção

### Parâmetros Principais
1. **FOV (Field of View)**: Campo de visão da lente fisheye (0-180°)
2. **PFOV (Perspective FOV)**: Campo de visão da imagem de saída (0-180°)
3. **X center / Y center**: Centro da área fisheye (-1 = automático)
4. **Radius**: Raio da área fisheye (-1 = automático)
5. **Angle**: Rotação da imagem em graus (-1 = sem rotação)

### Tipos de Distorção (Dtype)
- **linear**: Lente equidistante
- **equalarea**: Lente equisólida
- **orthographic**: Lente ortográfica
- **stereographic**: Lente estereográfica (padrão)

### Formatos (Format)
- **fullframe**: Imagem preenche toda a diagonal
- **circular**: Imagem preenche um círculo

## 🚀 Como Usar

### Instalação Rápida
```bash
# 1. Navegue para o diretório do projeto
cd Fish-Eye-Lens-Correction---Defishing-main

# 2. Execute o script de instalação
python install_and_run.py
```

### Uso Manual
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar aplicação
python integrated_defisheye_app.py
```

### Uso Programático
```python
from integrated_defisheye_app import DefisheyeAlgorithm

# Aplicar correção
defisheye = DefisheyeAlgorithm("imagem.jpg", fov=180, pfov=140, dtype="stereographic")
corrected_image = defisheye.convert()
```

## 📊 Presets Disponíveis

| Preset | FOV | PFOV | Dtype | Format | Uso Recomendado |
|--------|-----|------|-------|--------|-----------------|
| **stereographic** | 180 | 140 | stereographic | fullframe | Lentes fisheye comuns |
| **linear** | 180 | 120 | linear | fullframe | Lentes equidistantes |
| **equalarea** | 180 | 130 | equalarea | circular | Lentes equisólidas |
| **orthographic** | 180 | 110 | orthographic | fullframe | Lentes ortográficas |
| **ultra_wide** | 140 | 90 | stereographic | fullframe | Lentes ultra wide |
| **circular** | 180 | 140 | stereographic | circular | Imagens circulares |

## 🔍 Validação e Tratamento de Erros

### Validação de Parâmetros
- **FOV**: 0-180 graus
- **PFOV**: 0-180 graus
- **Angle**: 0-360 graus
- **Radius**: > 0
- **Pad**: 0-1000

### Tratamento de Erros
- Verificação de formato de imagem
- Validação de parâmetros antes do processamento
- Mensagens de erro informativas
- Recuperação automática de erros

## 🎯 Benefícios da Integração

### Para o Usuário
- **Interface intuitiva**: Controles fáceis de usar
- **Feedback visual**: Resultado em tempo real
- **Presets úteis**: Configurações pré-definidas
- **Flexibilidade**: Ajuste fino de parâmetros

### Para o Desenvolvedor
- **Código modular**: Fácil manutenção e extensão
- **Reutilização**: Algoritmo pode ser usado programaticamente
- **Configurabilidade**: Sistema de presets extensível
- **Validação**: Controle de qualidade integrado

## 🔄 Fluxo de Processamento

1. **Carregamento**: Imagem é carregada e redimensionada para exibição
2. **Parâmetros**: Valores são obtidos dos controles da interface
3. **Validação**: Parâmetros são validados antes do processamento
4. **Correção**: Algoritmo defisheye é aplicado com os parâmetros
5. **Exibição**: Resultado é convertido e exibido na interface
6. **Salvamento**: Imagem pode ser salva em diferentes formatos

## 📈 Melhorias Implementadas

### Sobre o Projeto Original defisheye
- ✅ Interface gráfica moderna
- ✅ Controles em tempo real
- ✅ Sistema de presets
- ✅ Validação de parâmetros
- ✅ Visualização lado a lado

### Sobre o Projeto Original Fish-Eye-Lens-Correction
- ✅ Algoritmo mais robusto
- ✅ Múltiplos tipos de distorção
- ✅ Parâmetros mais flexíveis
- ✅ Interface mais intuitiva

## 🛠️ Tecnologias Utilizadas

- **Python 3.6+**: Linguagem principal
- **OpenCV**: Processamento de imagem
- **NumPy**: Computação numérica
- **Tkinter**: Interface gráfica
- **PIL/Pillow**: Manipulação de imagem

## 📝 Licenças

Este projeto integra código de projetos open source:
- **defisheye**: Apache License 2.0
- **Fish-Eye-Lens-Correction**: Licença original do projeto

## 🤝 Contribuição

Para contribuir com melhorias:
1. Fork do repositório
2. Criação de branch para feature
3. Implementação das melhorias
4. Testes e validação
5. Pull request com documentação

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique a documentação em `README_INTEGRATED.md`
- Execute os exemplos em `example_usage.py`
- Consulte os presets em `config.py`

---

**Desenvolvido com ❤️ integrando as melhores características dos projetos defisheye e Fish-Eye-Lens-Correction**

