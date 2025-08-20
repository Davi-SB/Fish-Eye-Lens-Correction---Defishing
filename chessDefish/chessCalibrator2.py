# -*- coding: utf-8 -*-
import cv2
import numpy as np
import glob
import os
from datetime import datetime

# --- CONFIGURAÇÕES DO GRID ---
CHESSBOARD_SIZE = (17, 11)  # Número de quadrados internos (colunas, linhas)
SQUARE_SIZE_MM = 40

class InteractiveCalibrator:
    """
    Versão modificada do calibrador interativo que:
    1. Dobra o tamanho das imagens para melhor visualização.
    2. Permite salvar os parâmetros de calibração em um arquivo .txt.
    """
    def __init__(self, image_folder, chessboard_size, square_size_mm):
        self.image_folder = image_folder
        self.image_paths = sorted(glob.glob(os.path.join(image_folder, '*.jpg')))
        if not self.image_paths:
            print(f"Nenhuma imagem .jpg encontrada na pasta: {image_folder}")
            exit()

        self.chessboard_size = chessboard_size
        self.points_per_grid = chessboard_size[0] * chessboard_size[1]
        self.square_size_mm = square_size_mm
        
        self.objp = np.zeros((self.points_per_grid, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
        self.objp *= square_size_mm

        self.obj_points = [None] * len(self.image_paths)
        self.img_points = [np.empty((0, 1, 2), dtype=np.float32) for _ in self.image_paths]
        self.processed_images_mask = [False] * len(self.image_paths)

        self.current_image_index = 0
        self.img_gray = None
        self.img_color = None

        self.camera_matrix = np.eye(3)
        self.dist_coeffs = np.zeros(5)
        self.is_calibrated = False

        self.selected_point_index = None
        self.window_name_editor = "Editor de Pontos (Resolucao 2x)"
        self.window_name_preview = "Preview Corrigido (Resolucao 2x)"

    def _load_current_image(self):
        """Carrega e prepara a imagem atual."""
        path = self.image_paths[self.current_image_index]
        self.img_color = cv2.imread(path)
        
        # <-- MUDANÇA: Dobra o tamanho da imagem antes de qualquer outra coisa
        # Usamos INTER_CUBIC para uma melhor qualidade de interpolação ao ampliar
        if self.img_color is not None:
            self.img_color = cv2.resize(self.img_color, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        else:
            print(f"Erro ao carregar a imagem: {path}")
            return

        self.img_gray = cv2.cvtColor(self.img_color, cv2.COLOR_BGR2GRAY)
        print(f"Carregada imagem {self.current_image_index + 1}/{len(self.image_paths)}: {os.path.basename(path)}")


    def _draw_points(self, image):
        """Desenha os pontos na imagem do editor."""
        points = self.img_points[self.current_image_index]
        
        if self.processed_images_mask[self.current_image_index]:
             cv2.drawChessboardCorners(image, self.chessboard_size, points, True)
        
        for i, point in enumerate(points):
            color = (0, 0, 255) if i == self.selected_point_index else (255, 0, 0)
            cv2.circle(image, tuple(point.ravel().astype(int)), 5, color, -1)
        return image

    def _update_windows(self):
        """Atualiza a janela do editor e a de preview."""
        editor_img = self.img_color.copy()
        self._draw_points(editor_img)
        
        # <-- MUDANÇA: Adicionado 'S' para Salvar no texto de ajuda
        help_text = "N/P: Prox/Ant | D: Detectar | C: Calibrar | S: Salvar | R: Resetar | Q: Sair"
        cv2.putText(editor_img, help_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(editor_img, help_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.imshow(self.window_name_editor, editor_img)

        if self.is_calibrated:
            undistorted_img = cv2.undistort(self.img_color, self.camera_matrix, self.dist_coeffs, None, None)
            cv2.imshow(self.window_name_preview, undistorted_img)
        else:
            preview_placeholder = np.zeros_like(self.img_color)
            cv2.putText(preview_placeholder, "Calibre para ver o preview", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(self.window_name_preview, preview_placeholder)
    
    # <-- MUDANÇA: Nova função para salvar os dados de calibração
    def _save_calibration_data(self, filename="calibration_parameters.txt"):
        """Salva a matriz da câmera e os coeficientes de distorção em um arquivo de texto."""
        print(f"Salvando parâmetros de calibração em '{filename}'...")
        with open(filename, 'a') as f:
            f.write(f"# Parâmetros de Calibração da Câmera\n")
            f.write(f"# Salvo em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# ATENCAO: Estes parametros sao validos para imagens com resolucao dobrada (2x).\n\n")
            
            f.write("# Matriz da Câmera (mtx):\n")
            np.savetxt(f, self.camera_matrix, fmt='%.6f')
            
            f.write("\n# Coeficientes de Distorção (dist):\n")
            np.savetxt(f, self.dist_coeffs, fmt='%.6f')
        
        print("Parâmetros salvos com sucesso.")

    def _recalibrate(self):
        """Executa a calibração com os pontos disponíveis."""
        valid_obj_points = [p for p, valid in zip(self.obj_points, self.processed_images_mask) if valid]
        valid_img_points = [p for p, valid in zip(self.img_points, self.processed_images_mask) if valid]

        if len(valid_obj_points) < 3:
            print("Calibracao precisa de pelo menos 3 imagens com pontos validos.")
            self.is_calibrated = False
            return
        
        print(f"Calibrando com {len(valid_obj_points)} imagens...")
        # A forma da imagem (self.img_gray.shape) agora é a da imagem com tamanho dobrado
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            valid_obj_points, valid_img_points, self.img_gray.shape[::-1], None, None
        )
        if ret:
            self.camera_matrix = mtx
            self.dist_coeffs = dist
            self.is_calibrated = True
            print("Calibracao bem-sucedida!")
            print("\nMatriz da Camera (Intrinsecos):")
            print(self.camera_matrix)
            print("\nCoeficientes de Distorcao:")
            print(self.dist_coeffs)
        else:
            print("A calibracao falhou.")
            self.is_calibrated = False

    def _check_and_update_status(self, img_index):
        """Verifica se a imagem atual tem pontos suficientes e atualiza o status."""
        num_points = len(self.img_points[img_index])
        if num_points == self.points_per_grid:
            self.processed_images_mask[img_index] = True
            self.obj_points[img_index] = self.objp
        else:
            self.processed_images_mask[img_index] = False
            self.obj_points[img_index] = None

    def _mouse_callback(self, event, x, y, flags, param):
        """Lida com os eventos do mouse para edição de pontos."""
        # A lógica interna permanece a mesma, operando nas coordenadas da imagem ampliada
        current_points = self.img_points[self.current_image_index]

        if event == cv2.EVENT_LBUTTONDOWN:
            distances = [np.linalg.norm(p.ravel() - np.array([x, y])) for p in current_points]
            if distances and min(distances) < 15:
                self.selected_point_index = np.argmin(distances)
            else:
                if len(current_points) < self.points_per_grid:
                    new_points = np.append(current_points, [[[x, y]]], axis=0).astype(np.float32)
                    self.img_points[self.current_image_index] = new_points
                    self.selected_point_index = len(new_points) - 1
                    self._check_and_update_status(self.current_image_index)
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selected_point_index is not None:
                self.img_points[self.current_image_index][self.selected_point_index] = [x, y]
        
        elif event == cv2.EVENT_LBUTTONUP:
            if self.selected_point_index is not None:
                if self.is_calibrated: self._recalibrate()
                self.selected_point_index = None

        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(current_points) > 0:
                distances = [np.linalg.norm(p.ravel() - np.array([x, y])) for p in current_points]
                if min(distances) < 15:
                    point_to_delete_idx = np.argmin(distances)
                    self.img_points[self.current_image_index] = np.delete(current_points, point_to_delete_idx, axis=0)
                    self._check_and_update_status(self.current_image_index)
                    if self.is_calibrated: self._recalibrate()

    def run(self):
        """Inicia o loop principal da aplicação."""
        cv2.namedWindow(self.window_name_editor)
        cv2.namedWindow(self.window_name_preview)
        cv2.setMouseCallback(self.window_name_editor, self._mouse_callback)
        self._load_current_image()

        while True:
            self._update_windows()
            key = cv2.waitKey(20) & 0xFF

            if key == ord('q'):
                break
            
            elif key == ord('n'): 
                self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
                self._load_current_image()

            elif key == ord('p'):
                self.current_image_index = (self.current_image_index - 1 + len(self.image_paths)) % len(self.image_paths)
                self._load_current_image()

            elif key == ord('d'):
                print("Tentando detectar o grid...")
                ret, corners = cv2.findChessboardCorners(self.img_gray, self.chessboard_size, None)
                if ret:
                    print("Grid encontrado!")
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    corners_refined = cv2.cornerSubPix(self.img_gray, corners, (11, 11), (-1, -1), criteria)
                    self.img_points[self.current_image_index] = corners_refined
                else:
                    print("Nenhum grid encontrado. Adicione os pontos manualmente.")
                    self.img_points[self.current_image_index] = np.empty((0, 1, 2), dtype=np.float32)
                self._check_and_update_status(self.current_image_index)
            
            elif key == ord('c'):
                self._recalibrate()
            
            elif key == ord('s'):
                if self.is_calibrated:
                    self._save_calibration_data()
                else:
                    print("Ação inválida: Você precisa calibrar a câmera primeiro (pressione 'c').")

            elif key == ord('r'):
                print("Resetando pontos da imagem atual.")
                self.img_points[self.current_image_index] = np.empty((0, 1, 2), dtype=np.float32)
                self._check_and_update_status(self.current_image_index)
                if self.is_calibrated: self._recalibrate()

        cv2.destroyAllWindows()


if __name__ == '__main__':
    PASTA_DE_IMAGENS = 'data/largeBoard/B'
    if not os.path.isdir(PASTA_DE_IMAGENS):
        print(f"Erro: A pasta '{PASTA_DE_IMAGENS}' nao foi encontrada.")
        print("Por favor, crie a pasta e coloque suas imagens de calibracao nela.")
    else:
        calibrator = InteractiveCalibrator(PASTA_DE_IMAGENS, CHESSBOARD_SIZE, SQUARE_SIZE_MM)
        calibrator.run()