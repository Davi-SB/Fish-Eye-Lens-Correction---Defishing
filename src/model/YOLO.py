import os
from pathlib import Path
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm

INPUT_PATH = "data/data_geral"
YOLO_MODEL_NAME = 'yolov8x.pt'
TARGET_CLASS = 'backpack'

# para melhor manipulação
input_path = Path(INPUT_PATH)

# Cria o diretorio de saída
output_dir_name = "data_geral"
output_path = Path("resultsYOLO") / output_dir_name

if output_path.exists():
    print(f"--- O diretório de saída '{output_path}' já existe. Os arquivos serão sobrescritos.")
    input("--- Pressione Enter para continuar ou Ctrl+C para cancelar...")

output_path.mkdir(parents=True, exist_ok=True)
print(f"Resultados serão salvos em: {output_path}")

print(f"Carregando modelo {YOLO_MODEL_NAME}...")
model = YOLO(YOLO_MODEL_NAME)
print("Modelo carregado com sucesso.")

# --- PROCESSAMENTO DAS IMAGENS ---
# Lista para armazenar todos os dados de detecção
all_detections_data = []

# Lista para armazenar os nomes dos arquivos onde nenhuma mochila foi detectada
false_negative_files = []

# Lista de extensões de imagem válidas
image_extensions = ['.jpg', '.jpeg', '.png']
image_files = [f for f in input_path.iterdir() if f.suffix.lower() in image_extensions]
total_image_count = len(image_files)

print(f"Encontradas {total_image_count} imagens em '{input_path}'. Iniciando processamento...")

for image_file in tqdm(image_files, desc="Processando Imagens"):
    # Executa a detecção na imagem
    results = model(image_file)
    result  = results[0]  # Pega o resultado da primeira (e única) imagem

    # Salva a imagem com as bouding boxes, labels e confiança com o mesmo nome
    result.save(filename=output_path / image_file.name)

    # Verifica se a classe 'backpack' foi detectada nesta imagem
    backpack_found = False
    
    # Itera sobre todas as detecções na imagem
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        coordinates = box.xyxy[0].tolist() # Converte para lista

        # Adiciona os dados de todas as detecções da imagem
        detection_info = {
            'nome_do_arquivo': image_file.name,
            'classe_detectada': class_name,
            'pontuacao_de_confianca': confidence,
            'coordenadas_caixa': coordinates
        }
        all_detections_data.append(detection_info)
        
        # Se a classe detectada for a mochila
        if class_name == TARGET_CLASS:
            backpack_found = True
            
    # Se após verificar todas as detecções, nenhuma mochila foi encontrada --> é um falso negativo
    if not backpack_found:
        false_negative_files.append(image_file.name)

print("Processamento de imagens concluído.")

# --- RELATÓRIOS ---
# Realtório de todos os resultados
csv_path = output_path / "0 - results.csv"
print(f"Gerando arquivo de resultados em: {csv_path}")

if all_detections_data:
    df = pd.DataFrame(all_detections_data)
    df.to_csv(csv_path, index=False, sep=';', decimal='.')
else:
    # Cria um arquivo vazio com cabeçalhos se nada foi detectado
    pd.DataFrame(columns=['nome_do_arquivo', 'classe_detectada', 'pontuacao_de_confianca', 'coordenadas_caixa']).to_csv(csv_path, index=False, sep=';')

# Relatório de Falsos Negativos
report_path = output_path / "1 - falseNegative.txt"
print(f"Gerando relatório de falsos negativos em: {report_path}")

# --- Cálculo das Métricas de Falsos Negativos (Recall no nível da imagem) ---
# Recall = Verdadeiros Positivos / (Verdadeiros Positivos + Falsos Negativos)
# - Verdadeiro Positivo (TP): Uma imagem onde pelo menos uma mochila foi detectada.
# - Falso Negativo (FN): Uma imagem onde nenhuma mochila foi detectada.
# No caso desse primeiro dataset, todas as imagens contêm mochilas, então:
# Total de imagens = TP + FN
# TP = P (positive)
# Recall = P / Total de imagens

# A lista 'false_negative_files' já foi populada durante o processamento das imagens.
false_negative_count = len(false_negative_files)

# O número de imagens totais já foi calculado como 'total_image_count'
if total_image_count > 0:
    detected_count = total_image_count - false_negative_count
    # A métrica é a "Taxa de Detecção" ou "Recall"
    detection_rate = (detected_count / total_image_count) * 100
else:
    detected_count = 0
    detection_rate = 0.0

# Escreve o relatório no arquivo
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("--- Relatório de Falsos Negativos (Mochilas Não Detectadas) ---\n\n")
    f.write(f"Total de imagens processadas: {total_image_count}\n")
    f.write(f"Total de imagens com mochila detectada (Verdadeiros Positivos): {detected_count}\n")
    f.write(f"Total de imagens onde NENHUMA mochila foi detectada (Falsos Negativos): {false_negative_count}\n\n")
    f.write(f"Taxa de Detecção (Recall no nível da imagem): {detection_rate:.2f}%\n")
    f.write("A Taxa de Detecção representa a porcentagem de imagens do total em que o modelo conseguiu encontrar pelo menos uma mochila.\n\n")
    f.write("------------------------------------------------------------------\n")
    f.write("Lista de arquivos onde nenhuma mochila foi detectada:\n")
    if false_negative_files:
        for file_name in false_negative_files:
            f.write(f"{file_name}\n")
    else:
        f.write("Nenhum falso negativo encontrado. Todas as imagens tiveram ao menos uma mochila detectada.\n")
    f.write("------------------------------------------------------------------\n\n")

print("\nAnálise concluída com sucesso!")