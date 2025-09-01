import os
from pathlib import Path
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm
import cv2
import numpy as np
from numpy import arange, sqrt, arctan, sin, tan, meshgrid, pi
from numpy import ndarray, hypot

# =================================================================================
# --- 1. CONFIGURAÇÕES E PARÂMETROS ALTERÁVEIS ---
# =================================================================================

# --- TIPO DE CORREÇÃO ---
# Escolha o método de correção de lente que deseja testar.
# Opções disponíveis: "stereographic", "equalarea", "orthographic", "linear"
PROJECTION_TYPE = "stereographic"

# --- PARÂMETROS DO YOLO ---
# Pasta onde suas imagens originais (com olho de peixe) estão localizadas.
INPUT_PATH = "data/mochilaFishEye"

# Modelo do YOLO a ser utilizado. Você pode usar outros, como 'yolov8n.pt' (mais rápido)
# ou 'yolov8x.pt' (mais preciso).
YOLO_MODEL_NAME = 'yolov8x.pt'

# O nome exato da classe que você quer que o script procure e conte nos relatórios.
# O nome deve corresponder a uma das classes que o modelo YOLO conhece.
TARGET_CLASS = 'backpack'

# --- PARÂMETROS ÓPTICOS DA LENTE (ALGORITMO DEFISHEYE) ---
# Dicionário com as configurações para o algoritmo de correção.
# Você pode ajustar 'fov' e 'pfov' para refinar o resultado visual.
DEFISHEYE_PARAMS = {
    # Define a fórmula matemática da projeção. É controlado pela variável PROJECTION_TYPE acima.
    "dtype": PROJECTION_TYPE,

    # Formato da imagem de entrada. 'fullframe' ou 'circular'
    "format": "fullframe",

    # (Field of View) O campo de visão da sua lente olho de peixe original, em graus.
    "fov": 180,

    # (Perspective Field of View) O campo de visão desejado para a imagem de SAÍDA.
    "pfov": 120
}

# =================================================================================
# --- FIM DAS CONFIGURAÇÕES ---
# Nenhuma alteração é necessária abaixo desta linha para rodar os testes.
# =================================================================================


# --- 2. ALGORITMO DE CORREÇÃO (EXTRAÍDO DO SEU SOFTWARE) ---
class DefisheyeAlgorithm:
    """
    Algoritmo de correção fisheye baseado no projeto defisheye
    """
    def __init__(self, infile, **kwargs):
        vkwargs = {"fov": 180, "pfov": 120, "xcenter": None, "ycenter": None,
                   "radius": None, "pad": 0, "angle": 0, "dtype": "equalarea",
                   "format": "fullframe"}
        self._start_att(vkwargs, kwargs)

        if type(infile) == str:
            _image = cv2.imread(infile)
        elif type(infile) == ndarray:
            _image = infile
        else:
            raise Exception("Formato de imagem não reconhecido")

        if self._pad > 0:
            _image = cv2.copyMakeBorder(
                _image, self._pad, self._pad, self._pad, self._pad, cv2.BORDER_CONSTANT)

        width, height = _image.shape[1], _image.shape[0]
        xcenter, ycenter = width // 2, height // 2
        dim = min(width, height)
        x0, xf = xcenter - dim // 2, xcenter + dim // 2
        y0, yf = ycenter - dim // 2, ycenter + dim // 2

        self._image = _image[y0:yf, x0:xf, :]
        self._width, self._height = self._image.shape[1], self._image.shape[0]

        if self._xcenter is None: self._xcenter = (self._width - 1) // 2
        if self._ycenter is None: self._ycenter = (self._height - 1) // 2

    def _map(self, i, j, ofocinv, dim):
        xd, yd = i - self._xcenter, j - self._ycenter
        rd = hypot(xd, yd)
        phiang = arctan(ofocinv * rd)

        if self._dtype == "linear":
            ifoc = dim * 180 / (self._fov * pi)
            rr = ifoc * phiang
        elif self._dtype == "equalarea":
            ifoc = dim / (2.0 * sin(self._fov * pi / 720))
            rr = ifoc * sin(phiang / 2)
        elif self._dtype == "orthographic":
            ifoc = dim / (2.0 * sin(self._fov * pi / 360))
            rr = ifoc * sin(phiang)
        elif self._dtype == "stereographic":
            ifoc = dim / (2.0 * tan(self._fov * pi / 720))
            rr = ifoc * tan(phiang / 2)

        rdmask = rd != 0
        xs, ys = xd.astype(np.float32).copy(), yd.astype(np.float32).copy()
        xs[rdmask] = (rr[rdmask] / rd[rdmask]) * xd[rdmask] + self._xcenter
        ys[rdmask] = (rr[rdmask] / rd[rdmask]) * yd[rdmask] + self._ycenter
        xs[~rdmask], ys[~rdmask] = 0, 0
        return xs, ys

    def convert(self, outfile=None):
        if self._format == "circular":
            dim = min(self._width, self._height)
        elif self._format == "fullframe":
            dim = sqrt(self._width ** 2.0 + self._height ** 2.0)
        if self._radius is not None:
            dim = 2 * self._radius

        ofoc = dim / (2 * tan(self._pfov * pi / 360))
        ofocinv = 1.0 / ofoc
        i, j = arange(self._width), arange(self._height)
        i, j = meshgrid(i, j)
        xs, ys, = self._map(i, j, ofocinv, dim)
        img = cv2.remap(self._image, xs, ys, cv2.INTER_LINEAR)
        if outfile is not None:
            cv2.imwrite(outfile, img)
        return img

    def _start_att(self, vkwargs, kwargs):
        pin = []
        for key, value in kwargs.items():
            if key not in vkwargs: raise NameError(f"Invalid key {key}")
            else:
                pin.append(key)
                setattr(self, f"_{key}", value)
        pin = set(pin)
        rkeys = set(vkwargs.keys()) - pin
        for key in rkeys:
            setattr(self, f"_{key}", vkwargs[key])

def apply_defisheye_correction(image, params):
    defisheye = DefisheyeAlgorithm(image, **params)
    corrected_image = defisheye.convert()
    return corrected_image

# --- 3. SETUP DOS DIRETÓRIOS E MODELO ---
input_path = Path(INPUT_PATH)
output_dir_name = f"{input_path.name}-{YOLO_MODEL_NAME.replace('.pt', '')}-Defisheye{PROJECTION_TYPE.capitalize()}"
output_path = Path("resultsYOLO") / output_dir_name
output_path_detections = output_path / "detections"
output_path_corrected = output_path / "corrected_images"
output_path_detections.mkdir(parents=True, exist_ok=True)
output_path_corrected.mkdir(parents=True, exist_ok=True)
print(f"Resultados para o tipo '{PROJECTION_TYPE}' serão salvos em: {output_path}")

print(f"Carregando modelo {YOLO_MODEL_NAME}...")
model = YOLO(YOLO_MODEL_NAME)
print("Modelo carregado com sucesso.")

# --- 4. PROCESSAMENTO DAS IMAGENS ---
all_detections_data = []
false_negative_files = []
image_extensions = ['.jpg', '.jpeg', '.png']
image_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]
total_image_count = len(image_files)
print(f"Encontradas {total_image_count} imagens. Iniciando processamento com correção 'defisheye {PROJECTION_TYPE}'...")
for image_file in tqdm(image_files, desc=f"Processando ({PROJECTION_TYPE})"):
    original_image = cv2.imread(str(image_file))
    if original_image is None:
        continue
    corrected_image = apply_defisheye_correction(original_image, DEFISHEYE_PARAMS)
    cv2.imwrite(str(output_path_corrected / image_file.name), corrected_image)
    results = model(corrected_image, verbose=False)
    result = results[0]
    img_with_boxes = result.plot()
    cv2.imwrite(str(output_path_detections / image_file.name), img_with_boxes)
    backpack_found = False
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        coordinates = box.xyxy[0].tolist()
        detection_info = {'nome_do_arquivo': image_file.name, 'classe_detectada': class_name, 'pontuacao_de_confianca': confidence, 'coordenadas_caixa': coordinates}
        all_detections_data.append(detection_info)
        if class_name == TARGET_CLASS:
            backpack_found = True
    if not backpack_found:
        false_negative_files.append(image_file.name)
print("Processamento de imagens concluído.")

# --- 5. GERAÇÃO DE RELATÓRIOS ---
csv_path = output_path / "0 - all_detections_report.csv"
if all_detections_data:
    df = pd.DataFrame(all_detections_data)
    df.to_csv(csv_path, index=False, sep=';', decimal='.')
report_path = output_path / "1 - false_negative_report.txt"
false_negative_count = len(false_negative_files)
if total_image_count > 0:
    detected_count = total_image_count - false_negative_count
    detection_rate = (detected_count / total_image_count) * 100
else:
    detected_count = 0
    detection_rate = 0.0
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("--- Relatório de Falsos Negativos (Mochilas Não Detectadas) ---\n")
    f.write(f"--- (Executado com Correção Defisheye {PROJECTION_TYPE.capitalize()}) ---\n\n")
    f.write(f"Total de imagens processadas: {total_image_count}\n")
    f.write(f"Total de imagens com mochila detectada (Verdadeiros Positivos): {detected_count}\n")
    f.write(f"Total de imagens onde NENHUMA mochila foi detectada (Falsos Negativos): {false_negative_count}\n\n")
    f.write(f"Taxa de Detecção (Recall no nível da imagem): {detection_rate:.2f}%\n")
    f.write("------------------------------------------------------------------\n")
    f.write("Lista de arquivos onde nenhuma mochila foi detectada:\n")
    if false_negative_files:
        for file_name in false_negative_files: f.write(f"- {file_name}\n")
    else:
        f.write("Nenhum falso negativo encontrado.\n")
    f.write("------------------------------------------------------------------\n\n")
print("\nAnálise concluída com sucesso!")