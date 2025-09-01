import os
from pathlib import Path
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm
import cv2
import numpy as np

# --- 1. CONFIGURAÇÕES ---
# Parâmetros de detecção
INPUT_PATH = "data/mochilaFishEye"
YOLO_MODEL_NAME = 'yolov8x.pt'
TARGET_CLASS = 'backpack'

# Parâmetros de calibração manual (do seu script 'regularDefishing.py')
FOCAL_LENGTH_FX = 297
K1_TRACKBAR_VALUE = 0
K2_TRACKBAR_VALUE = 159

# --- FIM DAS CONFIGURAÇÕES ---

def apply_simple_defish(image, camera_matrix, dist_coeffs):
    """Aplica a correção de distorção padrão do OpenCV."""
    return cv2.undistort(image, camera_matrix, dist_coeffs)

# --- SETUP DOS DIRETÓRIOS ---
input_path = Path(INPUT_PATH)
output_dir_name = f"{input_path.name}-{YOLO_MODEL_NAME.replace('.pt', '')}-SimpleDefish"
output_path = Path("resultsYOLO") / output_dir_name
output_path_detections = output_path / "detections"
output_path_corrected = output_path / "corrected_images"

if output_path.exists():
    print(f"--- O diretório de saída '{output_path}' já existe. Os arquivos serão sobrescritos.")
    input("--- Pressione Enter para continuar ou Ctrl+C para cancelar...")

output_path_detections.mkdir(parents=True, exist_ok=True)
output_path_corrected.mkdir(parents=True, exist_ok=True)
print(f"Resultados serão salvos em: {output_path}")

# --- CARREGAMENTO DO MODELO YOLO ---
print(f"Carregando modelo {YOLO_MODEL_NAME}...")
model = YOLO(YOLO_MODEL_NAME)
print("Modelo carregado com sucesso.")

# --- CONVERSÃO DOS PARÂMETROS DE CALIBRAÇÃO ---
k1_float = (K1_TRACKBAR_VALUE - 100) / 100.0
k2_float = (K2_TRACKBAR_VALUE - 100) / 100.0
dist_coeffs = np.array([k1_float, k2_float, 0, 0, 0], dtype=np.float32)

print("\nParâmetros de correção a serem aplicados:")
print(f"  Distância Focal (fx): {FOCAL_LENGTH_FX}")
print(f"  Coeficientes (k1, k2): {k1_float:.2f}, {k2_float:.2f}\n")

# --- PROCESSAMENTO DAS IMAGENS ---
all_detections_data = []
false_negative_files = []
image_extensions = ['.jpg', '.jpeg', '.png']
image_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]
total_image_count = len(image_files)

print(f"Encontradas {total_image_count} imagens. Iniciando processamento com correção simples...")

for image_file in tqdm(image_files, desc="Processando Imagens com Correção Simples"):
    original_image = cv2.imread(str(image_file))
    if original_image is None:
        print(f"Aviso: Não foi possível ler a imagem {image_file.name}. Pulando.")
        continue

    # --- LÓGICA DE CORREÇÃO (DO SEU SCRIPT) ---
    # 1. Obtém as dimensões da imagem
    h, w = original_image.shape[:2]
    
    # 2. Constrói a matriz da câmera para esta imagem específica
    camera_matrix = np.array([
        [FOCAL_LENGTH_FX, 0, w / 2],
        [0, FOCAL_LENGTH_FX, h / 2],
        [0, 0, 1]
    ], dtype=np.float32)
    
    # 3. Aplica a correção de distorção
    corrected_image = apply_simple_defish(original_image, camera_matrix, dist_coeffs)
    
    # Salva a imagem corrigida para verificação
    cv2.imwrite(str(output_path_corrected / image_file.name), corrected_image)

    # --- DETECÇÃO COM YOLO ---
    # 4. Envia a imagem CORRIGIDA para o modelo YOLO
    results = model(corrected_image, verbose=False)
    result = results[0]

    # 5. Salva a imagem com as caixas de detecção
    img_with_boxes = result.plot()
    cv2.imwrite(str(output_path_detections / image_file.name), img_with_boxes)

    # --- COLETA DE DADOS PARA RELATÓRIO ---
    backpack_found = False
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        coordinates = box.xyxy[0].tolist()

        detection_info = {
            'nome_do_arquivo': image_file.name,
            'classe_detectada': class_name,
            'pontuacao_de_confianca': confidence,
            'coordenadas_caixa': coordinates
        }
        all_detections_data.append(detection_info)
        
        if class_name == TARGET_CLASS:
            backpack_found = True
            
    if not backpack_found:
        false_negative_files.append(image_file.name)

print("Processamento de imagens concluído.")

# --- GERAÇÃO DE RELATÓRIOS ---
csv_path = output_path / "0 - all_detections_report.csv"
print(f"Gerando arquivo de resultados em: {csv_path}")
if all_detections_data:
    df = pd.DataFrame(all_detections_data)
    df.to_csv(csv_path, index=False, sep=';', decimal='.')
else:
    pd.DataFrame(columns=['nome_do_arquivo', 'classe_detectada', 'pontuacao_de_confianca', 'coordenadas_caixa']).to_csv(csv_path, index=False, sep=';')

report_path = output_path / "1 - false_negative_report.txt"
print(f"Gerando relatório de falsos negativos em: {report_path}")

false_negative_count = len(false_negative_files)
if total_image_count > 0:
    detected_count = total_image_count - false_negative_count
    detection_rate = (detected_count / total_image_count) * 100
else:
    detected_count = 0
    detection_rate = 0.0

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("--- Relatório de Falsos Negativos (Mochilas Não Detectadas) ---\n")
    f.write("--- (Executado em imagens com Correção Simples) ---\n\n")
    f.write(f"Total de imagens processadas: {total_image_count}\n")
    f.write(f"Total de imagens com mochila detectada (Verdadeiros Positivos): {detected_count}\n")
    f.write(f"Total de imagens onde NENHUMA mochila foi detectada (Falsos Negativos): {false_negative_count}\n\n")
    f.write(f"Taxa de Detecção (Recall no nível da imagem): {detection_rate:.2f}%\n")
    f.write("A Taxa de Detecção representa a porcentagem de imagens do total em que o modelo conseguiu encontrar pelo menos uma mochila.\n\n")
    f.write("------------------------------------------------------------------\n")
    f.write("Lista de arquivos onde nenhuma mochila foi detectada:\n")
    if false_negative_files:
        for file_name in false_negative_files:
            f.write(f"- {file_name}\n")
    else:
        f.write("Nenhum falso negativo encontrado. Todas as imagens tiveram ao menos uma mochila detectada.\n")
    f.write("------------------------------------------------------------------\n\n")

print("\nAnálise concluída com sucesso!")