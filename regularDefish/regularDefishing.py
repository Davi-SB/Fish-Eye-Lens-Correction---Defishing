# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os

# --- 1. CONFIGURAÇÕES ---
# Parâmetros que você encontrou com o calibrador manual
FOCAL_LENGTH_FX = 297
K1_TRACKBAR_VALUE = 0
K2_TRACKBAR_VALUE = 159

# Pastas de entrada e saída
INPUT_FOLDER = 'fisheye_dataset'
OUTPUT_FOLDER = 'regularDefish/regular_defished_images'

# --- FIM DAS CONFIGURAÇÕES ---


def main():
    """
    Função principal que processa as imagens.
    """
    print("Iniciando o processo de correção de imagens...")

    # Verifica se a pasta de entrada existe
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Erro: A pasta de entrada '{INPUT_FOLDER}' não foi encontrada.")
        print("Por favor, certifique-se de que a pasta com as imagens existe.")
        return

    # Cria a pasta de saída se ela não existir
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Imagens corrigidas serão salvas em: '{OUTPUT_FOLDER}'")

    # --- 2. CONVERSÃO DOS PARÂMETROS ---
    # Converte os valores inteiros dos sliders para os coeficientes float
    # Mapeamento usado no calibrador: (valor_do_slider - 100) / 100.0
    k1_float = (K1_TRACKBAR_VALUE - 100) / 100.0
    k2_float = (K2_TRACKBAR_VALUE - 100) / 100.0
    
    # Cria o vetor de coeficientes de distorção que o OpenCV espera
    # [k1, k2, p1, p2, k3]
    dist_coeffs = np.array([k1_float, k2_float, 0, 0, 0], dtype=np.float32)

    print("\nParâmetros de correção a serem aplicados:")
    print(f"  Distância Focal (fx): {FOCAL_LENGTH_FX}")
    print(f"  Coeficientes (k1, k2): {k1_float:.2f}, {k2_float:.2f}\n")

    # Lista todos os arquivos na pasta de entrada
    file_list = os.listdir(INPUT_FOLDER)
    image_files = [f for f in file_list if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

    if not image_files:
        print("Nenhuma imagem encontrada na pasta de entrada.")
        return

    # --- 3. PROCESSAMENTO DAS IMAGENS ---
    for filename in image_files:
        # Monta o caminho completo do arquivo de entrada
        input_path = os.path.join(INPUT_FOLDER, filename)
        
        # Lê a imagem original
        original_image = cv2.imread(input_path)
        if original_image is None:
            print(f"  Aviso: Não foi possível ler a imagem {filename}. Pulando...")
            continue
            
        print(f"Processando '{filename}'...")
        
        # Obtém as dimensões da imagem
        h, w = original_image.shape[:2]
        
        # Constrói a matriz da câmera para esta imagem específica
        # Assumimos que o ponto central (cx, cy) é o centro da imagem e fx = fy
        camera_matrix = np.array([
            [FOCAL_LENGTH_FX, 0, w / 2],
            [0, FOCAL_LENGTH_FX, h / 2],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # Aplica a correção de distorção
        corrected_image = cv2.undistort(original_image, camera_matrix, dist_coeffs)
        
        # --- 4. COMBINAÇÃO E SALVAMENTO ---
        # Adiciona legendas às imagens
        cv2.putText(original_image, 'Original', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        cv2.putText(corrected_image, 'Corrigida', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

        # Empilha as imagens lado a lado
        combined_image = np.hstack([original_image, corrected_image])
        
        # Define o nome do arquivo de saída
        output_filename = f"{os.path.splitext(filename)[0]}_corrected.jpg"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Salva a nova imagem
        cv2.imwrite(output_path, combined_image)

    print(f"\nProcesso concluído! {len(image_files)} imagens foram corrigidas e salvas.")


if __name__ == '__main__':
    main()