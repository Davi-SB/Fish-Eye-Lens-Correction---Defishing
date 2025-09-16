import cv2
import numpy as np
import os
import glob
from newChessProcessing import execute_correction


def load_from_file(FOLDER_PARAM):
    data = np.load(f"{FOLDER_PARAM}camera_calibration_fisheye.npz")
    return data["K"], data["D"], data["dim"]


def correct_img(path, folder_param):
    K, D, dim = load_from_file(folder_param)
    img = cv2.imread(path)

    final_img = execute_correction(img ,K,D,dim)
    return final_img


# Para integrar é necessário duas coisas
# 1. O arquivo .npz que está em parameterMatrix
# 2. A função execute_correction
if __name__ == "__main__":
    # Ajustar caso necessário para o caminho do npz
    FOLDER_PARAM = "parameterMatrix/"
    IMAGE_PATH = "data/data_geral/image_003.jpg"
    img = correct_img(IMAGE_PATH, FOLDER_PARAM)
    cv2.imshow("Imagem Corrigida", img)
    cv2.waitKey(0)   # espera uma tecla
    cv2.destroyAllWindows()

#def process_images_in_directory(input_path: str):
#    # 1. Definir os diretórios de saída com base no nome do diretório de entrada
#    input_folder_name = os.path.basename(os.path.normpath(input_path))
#    base_output_folder = f"resultsYOLO/{input_folder_name}-newChess"
#    
#    correction_output_path = os.path.join(base_output_folder, "corrections")
#    yolo_output_path = os.path.join(base_output_folder, "corrected_images")
#
#    # 2. Criar os diretórios de saída, se eles não existirem
#    os.makedirs(correction_output_path, exist_ok=True)
#    # O diretório do YOLO será criado pela própria função predict, mas podemos garantir o pai
#    os.makedirs(base_output_folder, exist_ok=True)
#
#    print(f"Diretório de entrada: {input_path}")
#    print(f"Salvando imagens corrigidas em: {correction_output_path}")
#    print(f"Salvando resultados do YOLO em: {yolo_output_path}")
#    print("-" * 30)
#
#    # 3. Corrigir todas as imagens no diretório de entrada
#    supported_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
#    image_paths_to_process = []
#    for extension in supported_extensions:
#        image_paths_to_process.extend(glob.glob(os.path.join(input_path, extension)))
#
#    if not image_paths_to_process:
#        print("Nenhuma imagem encontrada no diretório especificado.")
#        return
#
#    print(f"Encontradas {len(image_paths_to_process)} imagens para processar.")
#    
#    # Lista para armazenar os caminhos das novas imagens corrigidas
#    corrected_image_paths = []
#
#    for image_path in image_paths_to_process:
#        try:
#            # Roda a sua função de correção
#            corrected_image = correct_img(image_path, FOLDER_PARAM)
#            
#            # Constrói o caminho para salvar a imagem corrigida
#            file_name = os.path.basename(image_path)
#            save_path_correction = os.path.join(correction_output_path, file_name)
#            
#            # Salva a imagem no disco
#            cv2.imwrite(save_path_correction, corrected_image)
#            corrected_image_paths.append(save_path_correction)
#            print(f"Imagem '{file_name}' corrigida e salva em '{save_path_correction}'")
#
#        except Exception as e:
#            print(f"Erro ao processar a imagem {image_path}: {e}")
#            
#    print("-" * 30)
#
#    # 4. Rodar o YOLO em todas as imagens que foram corrigidas com sucesso
#    if not corrected_image_paths:
#        print("Nenhuma imagem foi corrigida com sucesso. Encerrando o processo.")
#        return
#        
#    print("Iniciando detecção com YOLO nas imagens corrigidas...")
#    
#    # Carrega o modelo YOLO
#    model = YOLO(YOLO_MODEL_NAME)
#    
#    # Executa a predição. O YOLO salvará os resultados automaticamente.
#    # 'project' define a pasta base e 'name' define a subpasta da execução.
#    model.predict(
#        source=corrected_image_paths,
#        save=True,
#        project=base_output_folder,
#        name="corrected_images",
#        exist_ok=True  # Sobrescreve o diretório de resultados se ele já existir
#    )
#    
#    print("\nProcesso concluído com sucesso!")
#    print(f"Resultados do YOLO foram salvos dentro de: {yolo_output_path}")
#
#
#if __name__ == "__main__":
#    # Especifique aqui o diretório que contém as imagens que você quer processar
#    INPUT_IMAGE_DIRECTORY = "data/data_geral"
#    YOLO_MODEL_NAME = 'yolov8x.pt'
#    FOLDER_PARAM = "parameterMatrix/"
#    
#    process_images_in_directory(INPUT_IMAGE_DIRECTORY)