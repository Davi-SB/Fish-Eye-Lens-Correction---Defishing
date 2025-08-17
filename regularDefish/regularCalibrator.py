# -*- coding: utf-8 -*-
import cv2
import numpy as np
import glob
import os

class ManualCalibrator:
    """
    Uma ferramenta para correção manual e heurística da distorção de lentes
    usando sliders para ajustar os parâmetros em tempo real.
    """
    def __init__(self, image_folder):
        self.image_folder = image_folder
        self.image_paths = sorted(glob.glob(os.path.join(image_folder, '*.jpg')))
        if not self.image_paths:
            print(f"Nenhuma imagem .jpg encontrada na pasta: {image_folder}")
            exit()
            
        self.current_image_index = 0
        self.img_color = None
        self.img_height, self.img_width = 0, 0

        # Nomes das janelas
        self.window_name_preview = "Preview Corrigido"
        self.window_name_controls = "Controles"

        # Variáveis para armazenar os valores dos sliders
        self.focal_length_val = 1000 # Valor inicial para a distância focal
        self.k1_val = 100 # Valor inicial (mapeado para 0.0)
        self.k2_val = 100 # Valor inicial (mapeado para 0.0)

    def _load_current_image(self):
        """Carrega la imagen actual y la redimensiona si es necesario."""
        path = self.image_paths[self.current_image_index]
        self.img_color = cv2.imread(path)
        
        h, w = self.img_color.shape[:2]
        scale = min(1280/w, 720/h, 1.0)
        if scale < 1.0:
            self.img_color = cv2.resize(self.img_color, (int(w*scale), int(h*scale)))

        self.img_height, self.img_width = self.img_color.shape[:2]
        print(f"Carregada imagem {self.current_image_index + 1}/{len(self.image_paths)}: {os.path.basename(path)}")
        
        # Define um valor inicial razoável para a distância focal baseado na largura da imagem
        self.focal_length_val = self.img_width
        
        # ## CORREÇÃO ##
        # A linha abaixo foi movida para a função run() para garantir que
        # a janela de controles já exista quando esta função for chamada novamente.
        # cv2.setTrackbarPos('Focal (fx)', self.window_name_controls, self.focal_length_val)


    def _create_trackbars(self):
        """Cria a janela de controles com os sliders."""
        cv2.namedWindow(self.window_name_controls, cv2.WINDOW_AUTOSIZE)
        
        def on_trackbar(val):
            pass

        # A função createTrackbar já define o valor inicial
        cv2.createTrackbar('Focal (fx)', self.window_name_controls, self.focal_length_val, self.img_width * 2, on_trackbar)
        cv2.createTrackbar('k1', self.window_name_controls, self.k1_val, 200, on_trackbar)
        cv2.createTrackbar('k2', self.window_name_controls, self.k2_val, 200, on_trackbar)
        
    def run(self):
        """Inicia o loop principal da aplicação."""
        cv2.namedWindow(self.window_name_preview)

        # ## CORREÇÃO ##
        # A ordem das duas linhas abaixo foi invertida.
        # Primeiro carregamos a imagem para saber suas dimensões.
        self._load_current_image()
        # Depois, criamos os sliders, que dependem das dimensões da imagem.
        self._create_trackbars()
        
        while True:
            # Mostra a imagem original para referência
            original_with_text = self.img_color.copy()
            help_text = "N/P: Prox/Ant | Q: Sair"
            cv2.putText(original_with_text, help_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(original_with_text, help_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

            cv2.imshow("Original", original_with_text)

            # 1. Lê os valores atuais dos sliders
            self.focal_length_val = cv2.getTrackbarPos('Focal (fx)', self.window_name_controls)
            self.k1_val = cv2.getTrackbarPos('k1', self.window_name_controls)
            self.k2_val = cv2.getTrackbarPos('k2', self.window_name_controls)

            if self.focal_length_val == 0:
                self.focal_length_val = 1
            
            # 2. Converte os valores dos sliders para float
            k1_float = (self.k1_val - 100) / 100.0
            k2_float = (self.k2_val - 100) / 100.0

            # 3. Constrói a matriz da câmera e os coeficientes de distorção
            cx = self.img_width / 2
            cy = self.img_height / 2
            
            camera_matrix = np.array([
                [self.focal_length_val, 0, cx],
                [0, self.focal_length_val, cy],
                [0, 0, 1]
            ], dtype=np.float32)

            dist_coeffs = np.array([k1_float, k2_float, 0, 0, 0], dtype=np.float32)

            # 4. Aplica a correção de distorção
            undistorted_img = cv2.undistort(self.img_color, camera_matrix, dist_coeffs, None, None)

            # 5. Mostra o resultado
            cv2.imshow(self.window_name_preview, undistorted_img)
            
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\n--- Parâmetros Finais ---")
                print(f"Distancia Focal (fx, fy): {self.focal_length_val}")
                print(f"Coeficientes de Distorcao (k1, k2): {k1_float}, {k2_float}")
                print("-------------------------")
                break
            
            elif key == ord('n'): # Próxima imagem
                self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
                self._load_current_image()
                # ## CORREÇÃO ##
                # Atualiza a posição do slider ao carregar uma nova imagem
                cv2.setTrackbarPos('Focal (fx)', self.window_name_controls, self.focal_length_val)

            elif key == ord('p'): # Imagem anterior
                self.current_image_index = (self.current_image_index - 1 + len(self.image_paths)) % len(self.image_paths)
                self._load_current_image()
                # ## CORREÇÃO ##
                # Atualiza a posição do slider ao carregar uma nova imagem
                cv2.setTrackbarPos('Focal (fx)', self.window_name_controls, self.focal_length_val)

        cv2.destroyAllWindows()

if __name__ == '__main__':
    PASTA_DE_IMAGENS = 'fisheye_samples'

    if not os.path.isdir(PASTA_DE_IMAGENS):
        print(f"Erro: A pasta '{PASTA_DE_IMAGENS}' nao foi encontrada.")
        print("Por favor, crie a pasta e coloque suas imagens de calibracao nela.")
    else:
        calibrator = ManualCalibrator(PASTA_DE_IMAGENS)
        calibrator.run()