import cv2
import numpy as np
import os
import glob

# ===================================================================================
# FUNÇÕES DE CALIBRAÇÃO E DIAGNÓSTICO (INTOCADAS)
# ===================================================================================
FOLDER_PARAM = "parameterMatrix/"

def calibrar_camera_olho_de_peixe(
    imagens_calibracao_path: str,
    largura_tabuleiro: int,
    altura_tabuleiro: int,
    tamanho_quadrado_mm: float
):
    """
    Realiza a calibração de uma câmera olho de peixe usando imagens de um tabuleiro de xadrez.
    """
    # ... (código exatamente como o seu, sem alterações)
    # Critérios para o refinamento dos cantos
    subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    
    # Dimensões do tabuleiro
    CHECKERBOARD = (largura_tabuleiro, altura_tabuleiro)

    # Preparar pontos do objeto no mundo real
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp *= tamanho_quadrado_mm

    # Arrays para armazenar pontos
    objpoints = []
    imgpoints = []

    # Encontrar arquivos de imagem
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(imagens_calibracao_path, ext)))
        images.extend(glob.glob(os.path.join(imagens_calibracao_path, ext.upper())))
    
    if not images:
        print(f"Nenhuma imagem encontrada em '{imagens_calibracao_path}'")
        return None, None, None, None, None

    print(f"Encontradas {len(images)} imagens para calibração.")
    gray_shape = None

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if gray_shape is None:
            gray_shape = gray.shape[::-1]

        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, 
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), subpix_criteria)
            imgpoints.append(corners2)
            print(f"✓ Cantos encontrados: {os.path.basename(fname)}")
        else:
            print(f"✗ Cantos não encontrados: {os.path.basename(fname)}")

    if len(objpoints) < 3:
        print(f"Erro: Apenas {len(objpoints)} imagens válidas. Mínimo: 3")
        return None, None, None, None, None
        
    N_OK = len(objpoints)
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for _ in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for _ in range(N_OK)]

    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC | cv2.fisheye.CALIB_CHECK_COND | cv2.fisheye.CALIB_FIX_SKEW

    print(f"Calibrando com {N_OK} imagens...")
    
    try:
        rms, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
            objpoints, imgpoints, gray_shape, K, D, rvecs, tvecs,
            calibration_flags, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
        )

        print(f"✓ Calibração concluída! RMS: {rms:.4f}")
        return K, D, rvecs, tvecs, gray_shape
        
    except cv2.error as e:
        print(f"Erro na calibração: {e}")
        return None, None, None, None, None

def diagnosticar_parametros(K, D, dimensoes):
    """Diagnóstica os parâmetros de calibração"""
    # ... (código exatamente como o seu, sem alterações)
    print("\n" + "="*60)
    print("DIAGNÓSTICO DOS PARÂMETROS DE CALIBRAÇÃO")
    print("="*60)
    
    fx, fy = K[0,0], K[1,1]
    cx, cy = K[0,2], K[1,2]
    width, height = dimensoes
    
    print(f"Dimensões: {width}x{height}")
    print(f"Distância focal: fx={fx:.1f}, fy={fy:.1f}")
    print(f"Centro óptico: cx={cx:.1f}, cy={cy:.1f}")
    print(f"Coeficientes distorção: {D.flatten()}")
    
    # Análise de problemas
    problemas = []
    
    if abs(fx - fy) > min(fx, fy) * 0.15:
        problemas.append(f"Diferença grande entre fx/fy: {abs(fx-fy):.1f}")
    
    if not (width * 0.2 < cx < width * 0.8):
        problemas.append(f"Centro óptico cx fora do esperado: {cx:.1f} vs {width/2:.1f}")
    
    if not (height * 0.2 < cy < height * 0.8):
        problemas.append(f"Centro óptico cy fora do esperado: {cy:.1f} vs {height/2:.1f}")
    
    k1, k2 = D[0,0], D[1,0]
    if abs(k1) < 0.01:
        problemas.append("Distorção k1 muito baixa - pode não ser fisheye")
    
    if abs(k1) > 2.0 or abs(k2) > 2.0:
        problemas.append("Coeficientes de distorção muito altos")
    
    if problemas:
        print("⚠️  PROBLEMAS DETECTADOS:")
        for p in problemas:
            print(f"   - {p}")
    else:
        print("✓ Parâmetros parecem válidos")
    
    print("="*60)

# ===================================================================================
# MUDANÇA ESTRUTURAL: LÓGICA DE CORREÇÃO SEPARADA DA EXIBIÇÃO
# ===================================================================================

def execute_correction(img, K, D, calib_dim):
    """
    Esta função contém a LÓGICA DE CORREÇÃO da sua função original.
    Ela é o "motor" que tanto o modo interativo quanto o modo em lote irão usar.
    """
    # PASSO 1: Redimensionar para dimensões de calibração
    img_resized = cv2.resize(img, calib_dim)
    
    undistorted = None
    
    try:
        temp_undistorted = cv2.fisheye.undistortImage(img_resized, K, D, None, K)
        if temp_undistorted is not None and np.mean(temp_undistorted) > 5:
            undistorted = temp_undistorted
    except Exception:
        pass
    
    if undistorted is None:
        return None # Retorna falha se nada funcionou

    # Redimensiona de volta para o tamanho original
    undistorted_final = cv2.resize(undistorted, (img.shape[1], img.shape[0]))
    
    print(f"✓ Lógica de correção robusta aplicada com sucesso")
    return undistorted_final


def corrigir_imagem_fisheye_robusto(img_path, K, D, calib_dim):
    """
    SUA FUNÇÃO ORIGINAL, agora ela cuida apenas da parte INTERATIVA (carregar e exibir).
    A lógica de correção foi movida para 'executar_correcao_robusta'.
    """
    img = cv2.imread(img_path)
    if img is None:
        print(f"Erro: Não foi possível carregar {img_path}")
        return
    
    print(f"\nProcessando interativamente: {os.path.basename(img_path)}")
    
    # Chama o "motor" de correção
    undistorted_final = execute_correction(img, K, D, calib_dim)

    if undistorted_final is None:
        print("❌ FALHA: Todos os métodos de correção falharam!")
        cv2.imshow("ERRO - Apenas Original", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # A partir daqui, é apenas a lógica de exibição que você já tinha
    original_display = img
    undistorted_display = undistorted_final
    
    max_width = 800
    if original_display.shape[1] > max_width:
        scale = max_width / original_display.shape[1]
        new_w = int(original_display.shape[1] * scale)
        new_h = int(original_display.shape[0] * scale)
        original_display = cv2.resize(original_display, (new_w, new_h))
        undistorted_display = cv2.resize(undistorted_final, (new_w, new_h))
    
    comparison = np.hstack([original_display, undistorted_display])
    
    cv2.putText(comparison, "ORIGINAL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(comparison, f"CORRIGIDA", (original_display.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imshow("Comparacao: Original vs Corrigida", comparison)
    print("Pressione 'q' para fechar, 's' para salvar")
    
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q') or key == 27: break
        elif key == ord('s'):
            output_path = img_path.replace('.jpg', '_undistorted.jpg').replace('.png', '_undistorted.png')
            cv2.imwrite(output_path, undistorted_final)
            print(f"Salvo em: {output_path}")
            break
    
    cv2.destroyAllWindows()


def processar_pasta_em_lote(pasta_entrada, pasta_saida, K, D, calib_dim):
    """
    Processa uma pasta inteira de imagens, chamando o mesmo "motor" de correção robusta.
    """
    os.makedirs(pasta_saida, exist_ok=True)
    print("\n" + "="*60)
    print("MODO DE PROCESSAMENTO EM LOTE ATIVADO")
    print(f"Pasta de Entrada: '{pasta_entrada}'")
    print(f"Pasta de Saída:   '{pasta_saida}'")
    print("="*60)

    extensions = ['*.jpg', '*.jpeg', '*.png']
    imagens_para_corrigir = []
    for ext in extensions:
        imagens_para_corrigir.extend(glob.glob(os.path.join(pasta_entrada, ext)))

    if not imagens_para_corrigir:
        print(f"❌ Nenhuma imagem encontrada em '{pasta_entrada}'")
        return

    print(f"Encontradas {len(imagens_para_corrigir)} imagens. Iniciando...")

    for i, img_path in enumerate(imagens_para_corrigir):
        nome_arquivo = os.path.basename(img_path)
        print(f"  [{i+1}/{len(imagens_para_corrigir)}] Processando: {nome_arquivo}...")
        
        img = cv2.imread(img_path)
        if img is None:
            print(f"    ✗ Erro ao ler a imagem, pulando.")
            continue
        
        # CHAMA O MESMO MOTOR DE CORREÇÃO QUE O MODO INTERATIVO USA
        imagem_corrigida = execute_correction(img, K, D, calib_dim)
        
        if imagem_corrigida is not None:
            caminho_saida = os.path.join(pasta_saida, nome_arquivo)
            cv2.imwrite(caminho_saida, imagem_corrigida)
        else:
            print(f"    ✗ Correção falhou para {nome_arquivo}, imagem pulada.")

    print("\n✓ Processamento em lote concluído!")
    print("="*60)


if __name__ == '__main__':
    # ===================================================================================
    # CONFIGURAÇÃO PRINCIPAL - AJUSTE AQUI
    # ===================================================================================
    # --- MODO DE OPERAÇÃO ---
    MODO_LOTE = False

    # --- CONFIGURAÇÕES DE CALIBRAÇÃO ---
    pasta_calibracao = 'data/largeBoard/B'
    largura_tabuleiro = 17
    altura_tabuleiro = 11
    tamanho_quadrado_mm = 25.0

    # --- CONFIGURAÇÕES PARA O MODO LOTE ---
    if MODO_LOTE:
        pasta_de_entrada_lote = 'data/data_geral'
        pasta_de_saida_lote = 'imagens_corrigidas'

    # ===================================================================================
    # EXECUÇÃO DO SCRIPT
    # ===================================================================================
    K, D, rvecs, tvecs, dimensoes_calibracao = calibrar_camera_olho_de_peixe(
        pasta_calibracao, largura_tabuleiro, altura_tabuleiro, tamanho_quadrado_mm
    )

    if K is not None and D is not None:
        diagnosticar_parametros(K, D, dimensoes_calibracao)
        np.savez(f'{FOLDER_PARAM}camera_calibration_fisheye.npz', K=K, D=D, dim=dimensoes_calibracao)
        print(f"\n✓ Parâmetros salvos em 'camera_calibration_fisheye.npz'")
        
        if MODO_LOTE:
            processar_pasta_em_lote(
                pasta_entrada=pasta_de_entrada_lote,
                pasta_saida=pasta_de_saida_lote,
                K=K, D=D, calib_dim=dimensoes_calibracao
            )
        else:
            print("\nMODO DE TESTE INTERATIVO ATIVADO")
            path_img_teste = os.path.join(pasta_calibracao, 'image_089.jpg')
            
            if os.path.exists(path_img_teste):
                corrigir_imagem_fisheye_robusto(
                    img_path=path_img_teste,
                    K=K, D=D, calib_dim=dimensoes_calibracao
                )
            else:
                print(f"Imagem de teste não encontrada em: {path_img_teste}")
    
    else:
        print("❌ Calibração falhou!")