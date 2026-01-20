# 📹 Guia de Configuração de Câmera do Celular

## 🎯 Por que usar a câmera do celular?

- **Alta taxa de FPS**: 60-120 FPS (vs 30 FPS de webcams comuns)
- **Melhor qualidade**: Sensores superiores e maior resolução
- **Menor motion blur**: Obturador mais rápido para objetos em movimento
- **Flexibilidade**: Posicionamento livre e ajustes manuais

---

## 📱 Apps Recomendados

### 1️⃣ **IP Webcam** (Android) - ⭐ RECOMENDADO

**Grátis | Melhor custo-benefício**

#### Instalação:
1. [Baixe na Play Store](https://play.google.com/store/apps/details?id=com.pas.webcam)
2. Abra o app e role até o final
3. Clique em **"Start Server"**

#### Configuração para Alta Performance:

**Settings → Video Preferences:**
- **Resolution**: `1280x720` ou `1920x1080`
- **Quality**: `80-90%`
- **FPS limit**: `60 FPS` (ou máximo do seu celular)
- **Video encoder**: `H264` (melhor compressão)

**Settings → Camera Settings:**
- **Focus mode**: `Fixed` ou `Continuous Video`
- **Exposure compensation**: `-1` ou `-2` (menos motion blur)
- **Scene mode**: `Sports` (prioriza velocidade)

**Settings → Network:**
- Anote o endereço IP exibido (ex: `192.168.1.100:8080`)

#### URLs de Streaming:

```
RTSP (Melhor qualidade):
rtsp://192.168.1.100:8080/h264_ulaw.sdp

HTTP/MJPEG (Mais compatível):
http://192.168.1.100:8080/video

MJPEG (Alternativo):
http://192.168.1.100:8080/video?action=stream
```

---

### 2️⃣ **DroidCam** (Android/iOS)

**Grátis | Funciona como webcam USB ou WiFi**

#### Instalação:
1. [Baixe na Play Store](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam) ou App Store
2. Instale o [cliente Windows](https://www.dev47apps.com/droidcam/windows/)
3. Abra o app no celular e no PC

#### Configuração:
- **No app móvel**: Anote o WiFi IP
- **No cliente PC**: Insira o IP e conecte
- **FPS**: 60 FPS (versão paga) ou 30 FPS (grátis)

**URL WiFi:**
```
http://192.168.1.100:4747/video
```

**No Treadmill Speed Tracker:**
- Source: Cole a URL acima
- Type: HTTP/MJPEG Stream

---

### 3️⃣ **iVCam** (Android/iOS)

**Grátis com limitações | Baixa latência**

#### Instalação:
1. Baixe na [Play Store](https://play.google.com/store/apps/details?id=com.e2esoft.ivcam) ou App Store
2. Instale o [cliente Windows](https://www.e2esoft.com/ivcam/)
3. Conecte via WiFi ou USB

#### Vantagens:
- Auto-conecta ao abrir
- Funciona como webcam virtual (aparece como device 0, 1, etc)
- Suporta até 4K (versão paga)

---

## ⚙️ Configuração no Treadmill Speed Tracker

### 1. **Abra o Camera Setup**

No app principal, clique no botão **"📹 Camera Setup"**

### 2. **Configure a fonte**

#### Para Webcam USB/Built-in:
- **Camera Source**: Selecione "💻 Webcam"
- **Source**: `0` (primeira webcam) ou `1` (segunda)

#### Para RTSP (IP Webcam):
- **Camera Source**: Selecione "📱 RTSP Stream"
- **Source**: Cole a URL RTSP
  ```
  rtsp://192.168.1.100:8080/h264_ulaw.sdp
  ```

#### Para HTTP/MJPEG:
- **Camera Source**: Selecione "🌐 HTTP/MJPEG Stream"
- **Source**: Cole a URL HTTP
  ```
  http://192.168.1.100:8080/video
  ```

### 3. **Configure Alta Performance**

**FPS (frames/sec):**
- Mínimo: `60 FPS`
- Recomendado: `120 FPS` (se seu celular suportar)
- ⚠️ Valores muito altos podem causar lag na rede WiFi

**Resolution:**
- **720p (1280x720)**: Balanço ideal velocidade/qualidade
- **1080p (1920x1080)**: Máxima qualidade (requer boa conexão)
- **480p (640x480)**: Mínima latência

**Exposure (Exposição):**
- `-6` a `-10`: Menos motion blur (recomendado)
- `-11` a `-13`: Mínimo absoluto (pode escurecer)
- ⚡ Menor exposure = menos rastro de movimento

### 4. **Salve e Teste**

1. Clique em **"💾 Save Settings"**
2. Clique em **"▶ Start"** para iniciar
3. Observe os logs no terminal para confirmar FPS

---

## 🔧 Troubleshooting

### ❌ "Cannot open video source"

**Causa**: URL incorreta ou celular não alcançável

**Soluções:**
1. ✅ Verifique se PC e celular estão na **mesma rede WiFi**
2. ✅ Teste a URL no navegador (deve mostrar o vídeo)
3. ✅ Desabilite firewall temporariamente
4. ✅ Reinicie o app no celular

### 📉 FPS baixo / Lag

**Causas**: Rede WiFi lenta ou resolução muito alta

**Soluções:**
1. ✅ Use WiFi 5GHz se disponível (menor latência)
2. ✅ Reduza resolução para 720p
3. ✅ Reduza qualidade no app (70-80%)
4. ✅ Aproxime o celular do roteador
5. ✅ Use USB tethering (DroidCam/iVCam)

### 🌫️ Motion blur / Imagem borrada

**Causa**: Exposição (shutter speed) muito alta

**Soluções:**
1. ✅ Reduza Exposure no Camera Setup (`-8` a `-10`)
2. ✅ Configure Scene Mode para "Sports" no app
3. ✅ Aumente iluminação ambiente
4. ✅ Ajuste ISO manualmente (se app permitir)

### 🔌 Conexão instável

**Soluções:**
1. ✅ Use cabo USB em vez de WiFi (DroidCam/iVCam)
2. ✅ Ative "Keep screen on" no celular
3. ✅ Desative economia de energia
4. ✅ Use carregador para evitar bateria baixa

---

## 🏆 Configuração Ideal Recomendada

### Para Máxima Precisão:

```
App: IP Webcam (Android)
Protocol: RTSP
Resolution: 1280x720 (720p)
FPS: 60 FPS
Quality: 85%
Scene Mode: Sports
Exposure: -2
Focus: Fixed

No Tracker:
- FPS: 60
- Exposure: -8
- Width: 1280
- Height: 720
```

### Para Mínima Latência:

```
App: iVCam (USB)
Resolution: 640x480 (480p)
FPS: 120 FPS
Connection: USB Cable

No Tracker:
- FPS: 120
- Exposure: -10
- Width: 640
- Height: 480
```

---

## 📊 Comparação de Performance

| Método | FPS | Latência | Qualidade | Dificuldade |
|--------|-----|----------|-----------|-------------|
| **Webcam USB** | 30 | Baixa | Média | ⭐ Fácil |
| **IP Webcam RTSP** | 60 | Média | Alta | ⭐⭐ Moderada |
| **DroidCam WiFi** | 30-60 | Média | Alta | ⭐⭐ Moderada |
| **iVCam USB** | 120 | Muito Baixa | Muito Alta | ⭐ Fácil |

---

## 🎥 Como Posicionar a Câmera

### Montagem Recomendada:

1. **Altura**: Nível da esteira (visão lateral)
2. **Distância**: 30-50cm dos marcadores
3. **Ângulo**: 90° perpendicular ao movimento
4. **Fixação**: Use tripé ou suporte estável
5. **Foco**: Ajuste para a área dos marcadores

### Iluminação:

- ✅ **Luz uniforme** sem sombras fortes
- ✅ **Sem reflexos** diretos na câmera
- ✅ **Contraste alto** entre Post-it e fundo
- ✅ **Evite contra-luz**

---

## 📝 Checklist Pré-Teste

- [ ] Celular e PC na mesma rede WiFi
- [ ] App de câmera instalado e iniciado
- [ ] URL testada no navegador
- [ ] FPS configurado para 60+
- [ ] Exposure reduzido (-6 a -10)
- [ ] Câmera posicionada e focada
- [ ] Iluminação adequada
- [ ] Calibração feita (calibrador_gui.py)
- [ ] Distância entre marcadores medida

---

## 🚀 Fluxo Completo

```
1. Configure o celular (IP Webcam)
   └─> Ajuste FPS, resolução, exposure

2. Anote a URL RTSP/HTTP
   └─> Teste no navegador

3. Abra main_gui.py
   └─> Clique "📹 Camera Setup"

4. Cole a URL e configure performance
   └─> Save Settings

5. Clique "▶ Start"
   └─> Verifique logs de FPS no terminal

6. Calibre se necessário
   └─> Ajuste Exposure se houver motion blur

7. Teste com esteira em movimento
   └─> Monitore velocidade detectada
```

---

## 💡 Dicas Avançadas

### Para Desenvolvedores:

O código automaticamente:
- ✅ Configura buffer size = 1 (mínima latência)
- ✅ Desabilita auto-focus
- ✅ Define exposure manual
- ✅ Força resolução e FPS desejados

### Logs Úteis:

Ao iniciar, o terminal mostra:
```
[INFO] Camera configured:
  Resolution: 1280x720
  FPS: 60
  Exposure: -8.0
```

Se os valores não batem, o hardware pode não suportar.

### Testing FPS Real:

Execute o tracker e observe o terminal - o OpenCV reporta o FPS atual.

---

## ✅ Pronto!

Agora você tem uma configuração profissional com:
- 📹 Alta taxa de FPS (60-120)
- ⚡ Baixo motion blur
- 🎯 Máxima precisão na detecção
- 📱 Qualidade superior ao webcam

**Boa sorte com seus testes!** 🏃‍♂️💨
