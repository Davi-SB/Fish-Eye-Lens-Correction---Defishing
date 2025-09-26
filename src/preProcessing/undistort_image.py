import cv2
import numpy as np

def undistort_image(img: np.ndarray) -> np.ndarray | None:
    """
    Corrige a distorção de uma imagem (tipo fisheye) usando parâmetros de calibração pré-definidos.

    Esta função encapsula toda a lógica de correção, incluindo o redimensionamento
    necessário para a aplicação dos parâmetros e o retorno ao tamanho original.

    Args:
        img (np.ndarray): A imagem de entrada como um array NumPy (no formato BGR).

    Returns:
        np.ndarray | None: A imagem corrigida como um array NumPy, ou None se a correção falhar.
    """
    # Estes valores foram extraídos arquivo .npz
    K = np.array([[138.13556794,0., 228.67979535],[0., 142.46798892, 210.19526817],[0.,0.,1.]])
    D = np.array([[ 0.15522498],[-0.1554219 ],[ 0.10805718],[-0.04531632]])
    # Dimensões usadas durante a calibração original [width, height]
    DIM = np.array([464, 400])
    
    # Assegura que a imagem de entrada é válida
    if img is None or img.size == 0:
        print("Erro: Imagem de entrada é inválida.")
        return None

    # Dimensões da imagem original e da calibração
    original_dimensions = (img.shape[1], img.shape[0]) # (width, height)
    calibration_dimensions = tuple(DIM)

    # Redimensionar para as dimensões de calibração
    img_resized = cv2.resize(img, calibration_dimensions)
    
    undistorted_image = None
    
    # Aplicar a correção de distorção fisheye
    try:
        # A função de correção da OpenCV é chamada aqui
        temp_undistorted = cv2.fisheye.undistortImage(img_resized, K, D, None, K)
        
        # Garante que a imagem resultante não é preta/inválida
        if temp_undistorted is not None and np.mean(temp_undistorted) > 5:
            undistorted_image = temp_undistorted
    except Exception as e:
        print(f"Uma exceção ocorreu durante a correção da imagem: {e}")
        pass # Falha silenciosamente e retorna None
    
    if undistorted_image is None:
        print("A correção da imagem falhou ou resultou em uma imagem vazia.")
        return None # Retorna falha se a correção não funcionou

    # Redimensionar a imagem corrigida de volta para o tamanho original
    final_image = cv2.resize(undistorted_image, original_dimensions)
    
    # print("Imagem corrigida com sucesso.")
    return final_image


# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    # Coloque o caminho para uma imagem de teste aqui
    IMAGE_PATH = "data/data_geral/image_003.jpg"

    # Carrega a imagem original do disco
    original_img = cv2.imread(IMAGE_PATH)

    if original_img is None:
        print(f"Erro: não foi possível carregar a imagem de '{IMAGE_PATH}'")
        print("Por favor, verifique se o caminho para a imagem está correto.")
    else:
        # Simula o fluxo de uso que você descreveu
        # (Neste caso, a imagem já está em BGR, então não precisamos do cvtColor)
        print("Aplicando a função undistort_image...")
        corrected_img = undistort_image(original_img)
        print(type(original_img))
        print(type(corrected_img))
        
        # Verifica se a correção foi bem-sucedida
        if corrected_img is not None:
            # Mostra a imagem original e a corrigida lado a lado para comparação
            comparison_image = np.hstack([original_img, corrected_img])
            
            # Redimensiona a imagem de comparação se for muito grande para a tela
            max_width = 1280
            if comparison_image.shape[1] > max_width:
                scale = max_width / comparison_image.shape[1]
                new_height = int(comparison_image.shape[0] * scale)
                comparison_image = cv2.resize(comparison_image, (max_width, new_height))

            cv2.imshow("Original vs. Corrigida", comparison_image)
            print("\nPressione qualquer tecla para fechar as janelas.")
            cv2.waitKey(0)
            cv2.destroyAllWindows()