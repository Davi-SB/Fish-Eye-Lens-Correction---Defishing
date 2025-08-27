# Aplicação Integrada de Correção de Lente Fisheye

Esta aplicação integra o algoritmo do projeto [defisheye](https://github.com/duducosmos/defisheye) com uma interface gráfica moderna e intuitiva, permitindo correção de distorção fisheye em tempo real.

## Características

- **Interface Gráfica Intuitiva**: Interface moderna com controles em tempo real
- **Visualização Lado a Lado**: Comparação simultânea entre imagem original e corrigida
- **Parâmetros Ajustáveis**: Controle completo sobre todos os parâmetros de correção
- **Processamento em Tempo Real**: Atualização automática conforme os parâmetros são alterados
- **Múltiplos Formatos**: Suporte para diversos tipos de lente fisheye

## Instalação

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Executar a aplicação**:
```bash
python integrated_defisheye_app.py
```

## Como Usar

### 1. Abrir Imagem
- Clique em "📁 Abrir Imagem" para selecionar uma imagem com distorção fisheye
- Formatos suportados: JPG, PNG, BMP, TIFF

### 2. Ajustar Parâmetros
A aplicação oferece controle sobre os seguintes parâmetros:

#### **FOV (Field of View)**
- **Descrição**: Campo de visão da lente fisheye em graus
- **Valor padrão**: 180
- **Faixa**: 0-180 graus

#### **PFOV (Perspective Field of View)**
- **Descrição**: Campo de visão da imagem de saída em graus
- **Valor padrão**: 140
- **Faixa**: 0-180 graus

#### **X center / Y center**
- **Descrição**: Centro da área fisheye (use -1 para automático)
- **Valor padrão**: -1 (automático)

#### **Radius**
- **Descrição**: Raio da área fisheye
- **Valor padrão**: -1.4
- **Faixa**: Valores positivos ou -1 para automático

#### **Angle**
- **Descrição**: Rotação da imagem em graus
- **Valor padrão**: -1 (sem rotação)

#### **Dtype (Distortion Type)**
- **linear**: Lente equidistante
- **equalarea**: Lente equisólida
- **orthographic**: Lente ortográfica
- **stereographic**: Lente estereográfica (padrão)

#### **Format**
- **fullframe**: Imagem preenche toda a diagonal
- **circular**: Imagem preenche um círculo

#### **Pad**
- **Descrição**: Expansão da imagem original (padding)
- **Valor padrão**: 0

### 3. Visualizar Resultado
- A imagem corrigida é exibida automaticamente no painel direito
- Os parâmetros são aplicados em tempo real conforme você os ajusta

### 4. Salvar Resultado
- Clique em "💾 Salvar Resultado" para salvar a imagem corrigida
- Escolha o formato de saída (JPG, PNG)

## Configurações Recomendadas

### Para Lentes Fisheye Comuns:
- **FOV**: 180 (padrão para lentes fisheye completas)
- **PFOV**: 120-140 (para perspectiva natural)
- **Dtype**: stereographic (funciona bem para a maioria das lentes)
- **Format**: fullframe (para imagens que preenchem toda a área)

### Para Lentes Ultra Wide:
- **FOV**: 140-160
- **PFOV**: 90-110
- **Dtype**: equalarea ou linear

## Exemplos de Uso

### Exemplo 1: Correção Básica
1. Abra uma imagem fisheye
2. Mantenha os valores padrão
3. Ajuste apenas o PFOV para 120-140
4. Salve o resultado

### Exemplo 2: Correção Avançada
1. Abra uma imagem fisheye
2. Experimente diferentes tipos de distorção (Dtype)
3. Ajuste o centro (X center, Y center) se necessário
4. Use o radius para controlar a área de correção
5. Ajuste o ângulo se a imagem estiver rotacionada

## Solução de Problemas

### Erro: "Image format not recognized"
- Certifique-se de que o arquivo é uma imagem válida
- Verifique se o formato é suportado

### Erro: "Erro ao processar imagem"
- Verifique se os parâmetros estão dentro das faixas válidas
- Tente valores diferentes para FOV e PFOV

### Imagem não aparece corrigida
- Verifique se o FOV está correto para sua lente
- Experimente diferentes tipos de distorção (Dtype)
- Ajuste o PFOV para valores menores

## Baseado nos Projetos

- **defisheye**: Algoritmo de correção fisheye por Eduardo dos Santos Pereira
- **Fish-Eye-Lens-Correction**: Interface e conceitos de calibração

## Licença

Este projeto integra código de projetos open source. Consulte as licenças originais dos projetos base.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novos recursos
- Melhorar a documentação

