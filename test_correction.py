#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a correção fisheye
"""

import cv2
import numpy as np
from integrated_defisheye_app import DefisheyeAlgorithm
import os

def test_correction():
    """Testa a correção com diferentes parâmetros"""
    
    # Verifica se existe uma imagem de teste
    test_image = "fisheye_samples/test.jpg"
    if not os.path.exists(test_image):
        print(f"❌ Imagem de teste não encontrada: {test_image}")
        print("Por favor, coloque uma imagem fisheye na pasta 'fisheye_samples'")
        return
    
    print("🔧 Testando correção fisheye...")
    
    # Testa com os parâmetros exatos da imagem
    params_exact = {
        "fov": 180,
        "pfov": 140,
        "xcenter": None,  # -1 se torna None
        "ycenter": None,  # -1 se torna None
        "radius": -1.4,
        "angle": None,    # -1 se torna None
        "dtype": "stereographic",
        "format": "fullframe",
        "pad": 0
    }
    
    try:
        print("Aplicando correção com parâmetros exatos...")
        defisheye = DefisheyeAlgorithm(test_image, **params_exact)
        corrected = defisheye.convert()
        
        # Salva resultado
        output_path = "test_correction_exact.jpg"
        cv2.imwrite(output_path, corrected)
        print(f"✅ Correção salva em: {output_path}")
        
        # Mostra informações da imagem
        print(f"📊 Dimensões da imagem corrigida: {corrected.shape}")
        print(f"📊 Tipo de dados: {corrected.dtype}")
        print(f"📊 Valor mínimo: {corrected.min()}")
        print(f"📊 Valor máximo: {corrected.max()}")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()

def test_different_params():
    """Testa com diferentes parâmetros para comparação"""
    
    test_image = "fisheye_samples/test.jpg"
    if not os.path.exists(test_image):
        return
    
    print("\n🔧 Testando diferentes parâmetros...")
    
    # Testa diferentes valores de PFOV
    pfov_values = [120, 130, 140, 150, 160]
    
    for pfov in pfov_values:
        try:
            params = {
                "fov": 180,
                "pfov": pfov,
                "xcenter": None,
                "ycenter": None,
                "radius": -1.4,
                "angle": None,
                "dtype": "stereographic",
                "format": "fullframe",
                "pad": 0
            }
            
            defisheye = DefisheyeAlgorithm(test_image, **params)
            corrected = defisheye.convert()
            
            output_path = f"test_pfov_{pfov}.jpg"
            cv2.imwrite(output_path, corrected)
            print(f"✅ PFOV {pfov} salvo em: {output_path}")
            
        except Exception as e:
            print(f"❌ Erro com PFOV {pfov}: {e}")

def test_different_dtypes():
    """Testa diferentes tipos de distorção"""
    
    test_image = "fisheye_samples/test.jpg"
    if not os.path.exists(test_image):
        return
    
    print("\n🔧 Testando diferentes tipos de distorção...")
    
    dtypes = ["linear", "equalarea", "orthographic", "stereographic"]
    
    for dtype in dtypes:
        try:
            params = {
                "fov": 180,
                "pfov": 140,
                "xcenter": None,
                "ycenter": None,
                "radius": -1.4,
                "angle": None,
                "dtype": dtype,
                "format": "fullframe",
                "pad": 0
            }
            
            defisheye = DefisheyeAlgorithm(test_image, **params)
            corrected = defisheye.convert()
            
            output_path = f"test_dtype_{dtype}.jpg"
            cv2.imwrite(output_path, corrected)
            print(f"✅ {dtype} salvo em: {output_path}")
            
        except Exception as e:
            print(f"❌ Erro com {dtype}: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Teste de Correção Fisheye")
    print("=" * 50)
    
    test_correction()
    test_different_params()
    test_different_dtypes()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("📁 Verifique os arquivos gerados para comparar os resultados")
    print("=" * 50)

