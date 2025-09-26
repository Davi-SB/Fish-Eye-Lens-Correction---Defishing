import os
import json
from ultralytics import YOLO
from pathlib import Path

# --- CONFIGURAÇÕES ---

# 1. Especifique o caminho para o diretório com as imagens de entrada.
#    Exemplo: '/home/user/minhas_fotos' ou 'C:/Users/User/Desktop/Imagens'
INPUT_DIR = Path('data/chess_correction_new')

# 2. Especifique o caminho para o diretório onde os resultados serão salvos.
#    Este diretório será criado se não existir.
OUTPUT_DIR = Path('confidence/CorrectedImages - YOLO11x')

# 3. Escolha o modelo YOLO que deseja usar.
#    'yolov8n.pt' -> nano (mais rápido, menos preciso)
#    'yolov8s.pt' -> small
#    'yolov8m.pt' -> medium
#    'yolov8l.pt' -> large
#    'yolov8x.pt' -> extra-large (mais lento, mais preciso)
MODEL_NAME = 'yolo11x.pt'

# 4. Defina as classes de objetos que você quer incluir no relatório.
#    Os nomes devem estar em inglês, pois são os nomes padrão do modelo COCO.
TARGET_CLASSES = {"handbag", "suitcase", "backpack"}

# --- FIM DAS CONFIGURAÇÕES ---


def run_yolo_on_directory(input_path: Path, output_path: Path, model_name: str, target_classes: set):
    """
    Roda um modelo YOLO em todas as imagens de um diretório, salva as imagens
    anotadas e gera um relatório JSON com as confianças das classes-alvo.

    Args:
        input_path (Path): Caminho para o diretório com as imagens de origem.
        output_path (Path): Caminho para o diretório de destino dos resultados.
        model_name (str): Nome do arquivo do modelo YOLO (ex: 'yolov8n.pt').
        target_classes (set): Um conjunto de strings com os nomes das classes de interesse.
    """
    # Garante que o diretório de saída exista
    print(f"Criando diretório de saída em: {output_path.resolve()}")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # --- Carregamento do Modelo ---
    print(f"Carregando o modelo YOLO: {model_name}...")
    try:
        model = YOLO(model_name)
    except Exception as e:
        print(f"Erro ao carregar o modelo. Verifique se o nome '{model_name}' está correto.")
        print(f"Detalhes do erro: {e}")
        return

    # Dicionário para armazenar os nomes das classes do modelo (ex: {0: 'person', 1: 'bicycle', ...})
    class_names = model.names
    print("Modelo carregado com sucesso. Classes disponíveis:", list(class_names.values()))

    # Encontrar os índices numéricos das nossas classes-alvo
    target_class_indices = {
        idx for idx, name in class_names.items() if name in target_classes
    }
    
    if not target_class_indices:
        print("Aviso: Nenhuma das classes-alvo foi encontrada no modelo. O relatório ficará vazio.")
        print(f"Classes-alvo especificadas: {target_classes}")

    # --- Processamento das Imagens ---
    report_data = {}
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    
    # Lista todas as imagens no diretório de entrada
    image_files = [p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() in image_extensions]

    if not image_files:
        print(f"Nenhuma imagem encontrada no diretório: {input_path.resolve()}")
        return

    print(f"\nIniciando o processamento de {len(image_files)} imagens...")

    for image_path in image_files:
        print(f"  -> Processando: {image_path.name}")
        
        # Realiza a predição na imagem
        # O argumento 'save=True' salva a imagem com as bounding boxes
        # 'project' e 'name' controlam o diretório de saída para evitar a criação de subpastas como 'predict', 'predict2', etc.
        results = model.predict(
            source=image_path,
            save=True,
            project=output_path,
            name='imagens_anotadas', # Salva todas as imagens numa única subpasta
            exist_ok=True, # Não cria novas pastas (ex: 'imagens_anotadas2') se já existir
            verbose=False # Reduz a quantidade de logs no console
        )
        
        # Estrutura para guardar as confianças da imagem atual
        image_confidences = []
        
        # O resultado é uma lista (geralmente com um item para uma imagem)
        result = results[0]
        
        # Itera sobre cada bounding box detectada
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            # Verifica se a classe detectada é uma das que nos interessam
            if class_id in target_class_indices:
                image_confidences.append(round(confidence, 2)) # Adiciona a confiança arredondada
                
        # Adiciona os dados ao relatório principal
        report_data[image_path.name] = image_confidences

    # --- Salvando o Relatório ---
    report_file_path = output_path / 'report.json'
    print(f"\nProcessamento concluído. Salvando relatório em: {report_file_path.resolve()}")
    
    with open(report_file_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)
        
    print("Operação finalizada com sucesso!")


if __name__ == '__main__':
    # Verifica se o diretório de entrada existe antes de rodar
    if not INPUT_DIR.is_dir():
        print(f"ERRO: O diretório de entrada especificado não existe: {INPUT_DIR.resolve()}")
        print("Por favor, crie o diretório e adicione imagens a ele ou corrija o caminho na variável 'INPUT_DIR'.")
    else:
        run_yolo_on_directory(
            input_path=INPUT_DIR,
            output_path=OUTPUT_DIR,
            model_name=MODEL_NAME,
            target_classes=TARGET_CLASSES
        )