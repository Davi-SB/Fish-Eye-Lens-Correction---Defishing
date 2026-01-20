# Treadmill Speed Tracker - Black Circle Detection

Sistema de visão computacional para estimar a velocidade de uma esteira baseado no movimento de **círculos pretos** desenhados em Post-it notes.

## 🎯 Nova Abordagem: Círculos Pretos

Em vez de detectar a cor do Post-it, o sistema agora detecta **círculos pretos sólidos** desenhados no centro dos Post-its. Esta abordagem oferece:

- ✅ **Alto contraste** - preto é fácil de isolar em qualquer fundo
- ✅ **Centro preciso** - o centroide do círculo é muito preciso para medir cruzamento
- ✅ **Menos sensível à iluminação** - círculos pretos são mais estáveis que cores
- ✅ **Filtragem por forma** - circularidade elimina falsos positivos

## 📁 Estrutura do Projeto

```
Treadmil Speed Tracker/
├── utils.py              # Funções de processamento e detecção de círculos
├── calibrador.py         # GUI para calibração de parâmetros
├── main.py               # Script principal de execução
├── requirements.txt      # Dependências do projeto
├── images/               # Pasta para imagens de calibração
├── calibration_config.json  # Configuração (gerada após calibração)
└── README.md             # Este arquivo
```

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## 📖 Como Usar

### Passo 1: Preparar os Marcadores

1. Pegue Post-it notes (qualquer cor)
2. Desenhe um **círculo preto sólido preenchido** no centro de cada Post-it
3. Use caneta permanente preta para melhor contraste
4. Mantenha os círculos aproximadamente do mesmo tamanho

### Passo 2: Calibração

Tire fotos dos seus Post-its com círculos e coloque na pasta `images/`:

```bash
python calibrador.py
```

**Parâmetros de Calibração:**

| Parâmetro | Descrição |
|-----------|-----------|
| **Black Threshold** | Limite para considerar um pixel como "preto" (0-255, menor = mais escuro) |
| **Min/Max Area** | Faixa de área para filtrar círculos por tamanho |
| **Min Circularity** | Circularidade mínima (0-100%, onde 100% = círculo perfeito) |
| **Use Adaptive** | Usa threshold adaptativo para iluminação variável |
| **Blur/Contrast/Saturation** | Filtros de pré-processamento |
| **Erode/Dilate** | Operações morfológicas para limpar a máscara |

**Controles do Calibrador:**
- **N** / **→** - Próxima imagem
- **P** / **←** - Imagem anterior
- **S** - Salvar configuração
- **R** - Resetar parâmetros
- **Q** / **ESC** - Sair

### Passo 3: Executar o Tracker

```bash
python main.py
```

**Controles do Tracker:**
- **M** - Alternar visualização da máscara
- **R** - Resetar calculador de velocidade
- **Q** / **ESC** - Sair

## ⚙️ Configuração

### Parâmetros no `main.py`

```python
# Distância real entre os marcadores (em metros)
REAL_DISTANCE_BETWEEN_MARKERS = 0.30  # 30 cm

# Fonte de vídeo: 0 para webcam, ou caminho do arquivo
VIDEO_SOURCE = 0

# Posição da linha virtual (0.0 a 1.0, onde 0.5 é o centro)
VIRTUAL_LINE_POSITION = 0.5
```

### Argumentos de Linha de Comando

```bash
# Calibrador
python calibrador.py --images pasta_imagens --config config.json

# Main
python main.py --source 0 --distance 0.25 --line 0.5 --config config.json
```

## 🔬 Lógica de Funcionamento

### Detecção de Círculos Pretos

1. **Pré-processamento**: Ajuste de contraste, saturação e blur
2. **Conversão para Grayscale**: Simplifica a detecção
3. **Threshold**: Isola pixels escuros (pretos)
4. **Operações Morfológicas**: Remove ruído e preenche buracos
5. **Detecção de Contornos**: Encontra formas na máscara
6. **Filtro de Circularidade**: Mantém apenas formas circulares

### Cálculo de Circularidade

$$\text{Circularity} = \frac{4 \pi \times \text{Area}}{\text{Perimeter}^2}$$

- Círculo perfeito = 1.0 (100%)
- Quadrado ≈ 0.785 (78.5%)
- Formas irregulares < 0.6

### Detecção de Velocidade

1. **Círculo A cruza a linha virtual** → Inicia cronômetro (`t_start`)
2. **Círculo B cruza a linha virtual** → Para cronômetro (`t_end`)
3. **Cálculo:** $v = \frac{d}{\Delta t}$
4. O sistema reseta e aguarda o próximo par

## 🎨 Dicas para Melhores Resultados

### Desenho dos Círculos
- Use caneta permanente preta (tipo Sharpie)
- Preencha completamente o círculo (sólido)
- Mantenha círculos de tamanho similar
- Evite borrões ou círculos imperfeitos

### Calibração
- **Black Threshold**: Comece com 80-100, ajuste até o círculo ficar branco na máscara
- **Min Circularity**: 60-70% funciona bem para círculos desenhados à mão
- **Min/Max Area**: Ajuste para o tamanho dos seus círculos

### Iluminação
- Iluminação uniforme é ideal
- Se a luz varia muito, ative o **Adaptive Threshold**
- Evite sombras sobre os marcadores

## 📊 Interface Visual

O sistema exibe em tempo real:
- **Bounding Box** verde ao redor dos círculos detectados
- **Centróide** vermelho no centro exato do círculo
- **Circularidade** (%) de cada círculo detectado
- **Linha Virtual** magenta no centro do frame
- **Velocidade** calculada em m/s e km/h
- **Estado** atual (aguardando Círculo A ou B)

## 🛠️ Estrutura dos Módulos

### `utils.py`
- `BlackCircleParams`: Parâmetros para detecção de círculos pretos
- `calculate_circularity()`: Calcula circularidade de contornos
- `create_black_mask()`: Cria máscara binária para preto
- `detect_black_circles()`: Detecta e filtra círculos
- `process_frame_for_black_circles()`: Pipeline completo

### `calibrador.py`
- GUI com 4 janelas de visualização
- Trackbars para todos os parâmetros
- Salva/carrega configuração JSON

### `main.py`
- `SpeedCalculator`: Máquina de estados para cálculo de velocidade
- `TreadmillSpeedTracker`: Aplicação principal com webcam

## 📝 Licença

Este projeto é para fins educacionais.
