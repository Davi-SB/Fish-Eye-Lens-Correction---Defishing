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
    IMAGE_PATH = "data/data_geral/image_000.jpg"
    img = correct_img(IMAGE_PATH, FOLDER_PARAM)
    
    cv2.imshow("Imagem Corrigida", img)
    cv2.waitKey(0)   # espera uma tecla
    cv2.destroyAllWindows()