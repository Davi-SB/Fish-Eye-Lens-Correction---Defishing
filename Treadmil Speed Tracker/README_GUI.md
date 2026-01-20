# 🎯 Treadmill Speed Tracker - Modern GUI Version

## 📖 Overview

Versão **user-friendly** do sistema de rastreamento de velocidade em esteira com interface gráfica moderna usando **Tkinter**.

### ✨ Melhorias da Interface

#### **Calibrador (calibrador_gui.py)**
- ✅ Interface intuitiva com painéis organizados
- ✅ 4 janelas de preview em grid 2x2
- ✅ Sliders agrupados por categoria
- ✅ Labels coloridos e informativos
- ✅ Botões grandes e fáceis de usar
- ✅ Navegação entre imagens simplificada
- ✅ Informações em tempo real
- ✅ Tema dark moderno

#### **Rastreador Principal (main_gui.py)**
- ✅ Display grande de velocidade (m/s e km/h)
- ✅ Controles Start/Stop/Reset intuitivos
- ✅ Painel de estatísticas em tempo real
- ✅ Configurações acessíveis por diálogo
- ✅ Status visual claro
- ✅ Thread dedicada para processamento de vídeo
- ✅ Interface responsiva

---

## 🚀 Como Usar

### 1️⃣ **Calibração com Interface Gráfica**

```bash
python calibrador_gui.py
```

**Features:**
- 📸 **4 Previews simultâneos**: Original+Detecção, Filtrado, Grayscale, Máscara
- 🎛️ **Sliders organizados** em seções:
  - 🔍 Black Circle Detection
  - 🌓 Adaptive Threshold  
  - 🎨 Image Filters
  - 🔬 Morphological Operations
- ⌨️ **Navegação**: Botões "Previous" / "Next"
- 💾 **Save**: Salva configuração automaticamente
- 🔄 **Reset**: Volta aos valores padrão
- ❌ **Close**: Fecha aplicação

**Workflow:**
1. Adicione imagens na pasta `images/`
2. Execute o calibrador
3. Ajuste os sliders até detectar os círculos corretamente
4. Clique em "Save Configuration"
5. Feche o calibrador

---

### 2️⃣ **Rastreamento em Tempo Real**

```bash
python main_gui.py
```

**Features:**
- 📹 **Live Feed**: Vídeo ao vivo com detecção
- 📊 **Display grande de velocidade**: 
  - m/s em destaque
  - km/h abaixo
- 📈 **Estatísticas**:
  - Estado atual (aguardando A ou B)
  - Círculos detectados
  - Número de cruzamentos
  - Distância configurada
- ⚙️ **Settings**: Ajuste distância, fonte de vídeo e posição da linha
- 🔄 **Reset**: Limpa estatísticas sem parar o vídeo

**Controles:**
- ▶ **Start**: Inicia captura e rastreamento
- ⏸ **Stop**: Pausa rastreamento
- 🔄 **Reset**: Zera estatísticas
- ⚙️ **Settings**: Abre janela de configurações

---

## 📦 Dependências Adicionais

A interface gráfica requer:

```bash
pip install pillow
```

**Bibliotecas usadas:**
- `tkinter` - GUI nativa do Python (já incluída)
- `PIL/Pillow` - Conversão de imagens para Tkinter
- `threading` - Processamento assíncrono de vídeo

---

## 🎨 Interface Visual

### **Calibrador**
```
┌─────────────────────────────────┬─────────────────┐
│  📷 Original + Detection        │  ⚙️ Parameters  │
│  🎨 Filtered Preview            │                 │
│  ⬛ Grayscale                    │  Sliders:       │
│  🎭 Black Mask                   │  • Threshold    │
│                                  │  • Area         │
│  [◀ Previous]  [Next ▶]         │  • Circularity  │
│  Circles detected: X            │  • Filters      │
└─────────────────────────────────┴─────────────────┘
```

### **Main Tracker**
```
┌──────────────────────────────────────────────────┐
│  🏃 Treadmill Speed Tracker                      │
│  [▶ Start] [⏸ Stop] [🔄 Reset] [⚙️ Settings]    │
├───────────────────────────┬──────────────────────┤
│                           │  📊 Statistics       │
│   📹 Live Feed            │                      │
│   [Video with detection]  │  Current Speed       │
│                           │   2.50 m/s           │
│                           │   9.00 km/h          │
│                           │                      │
│                           │  State: 🔴 A         │
│                           │  Circles: 2          │
│                           │  Crossings: 15       │
│                           │  Distance: 0.30 m    │
└───────────────────────────┴──────────────────────┘
│ ● Tracking active                                │
└──────────────────────────────────────────────────┘
```

---

## ⚙️ Configurações Disponíveis

### **Settings Dialog (Main)**
- **Distance between markers**: Distância real em metros
- **Video source**: 0 para webcam, caminho para arquivo
- **Virtual line position**: 0.0 (esquerda) a 1.0 (direita)

### **Calibration Parameters**
Todos os parâmetros originais estão disponíveis:
- Black threshold (0-255)
- Min/Max area (×100)
- Min circularity (0-100%)
- Adaptive threshold settings
- Blur, contrast, saturation
- Erode/dilate iterations

---

## 🆚 Comparação: OpenCV vs Tkinter GUI

| Feature | OpenCV (Original) | Tkinter (Nova) |
|---------|-------------------|----------------|
| **Usabilidade** | Trackbars simples | Sliders organizados |
| **Visual** | Janelas separadas | Interface integrada |
| **Organização** | Linear | Agrupado por seção |
| **Feedback** | Texto console | Labels coloridos |
| **Navegação** | Teclas | Botões grandes |
| **Settings** | Não disponível | Dialog dedicado |
| **Status** | Console | Barra de status |
| **Tema** | Sistema | Dark moderno |

---

## 🔧 Troubleshooting

### **Erro: "No images found"**
- Adicione imagens JPG/PNG na pasta `images/`

### **Erro: "No Configuration"**
- Execute primeiro `calibrador_gui.py` e salve a configuração

### **Vídeo não abre**
- Verifique se a webcam está disponível
- Tente mudar Video Source em Settings (0, 1, 2...)

### **Interface lenta**
- Reduza a resolução das imagens de calibração
- Use menos imagens na pasta `images/`

---

## 💡 Dicas de Uso

1. **Calibração eficiente**: 
   - Use 3-5 imagens representativas
   - Varie iluminação e ângulos
   - Salve configurações frequentemente

2. **Tracking em tempo real**:
   - Ajuste a posição da linha virtual para o centro do campo de visão
   - Use distância precisa entre marcadores
   - Resete estatísticas ao mudar condições

3. **Performance**:
   - A GUI usa thread separada para vídeo
   - Não trava durante processamento
   - Pode ajustar parâmetros em Settings sem parar

---

## 📝 Arquivos do Projeto

```
Treadmill Speed Tracker/
│
├── calibrador.py          # Versão original OpenCV
├── calibrador_gui.py      # ✨ Nova versão Tkinter
│
├── main.py                # Versão original OpenCV
├── main_gui.py            # ✨ Nova versão Tkinter
│
├── utils.py               # Funções de detecção (compartilhado)
├── calibration_config.json # Configuração salva
│
├── README.md              # Documentação original
└── README_GUI.md          # 📖 Esta documentação
```

---

## 🎯 Próximos Passos

Use a **versão GUI** para maior produtividade:

```bash
# Calibração
python calibrador_gui.py

# Rastreamento
python main_gui.py
```

Ou continue usando as versões originais OpenCV se preferir:

```bash
# Calibração original
python calibrador.py

# Rastreamento original  
python main.py
```

Ambas as versões compartilham o mesmo arquivo de configuração! 🎉
