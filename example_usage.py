#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso da Aplicação Integrada de Correção Fisheye
Demonstra como usar o algoritmo programaticamente
"""

import cv2
import numpy as np
from integrated_defisheye_app import DefisheyeAlgorithm
import os

def example_basic_correction():
    """Exemplo básico de correção fisheye"""
    print("🔧 Exemplo 1: Correção Básica")
    
    # Verifica se existe uma imagem de exemplo
    example_image = "fisheye_samples/example.jpg"
    if not os.path.exists(example_image):
        print(f"❌ Imagem de exemplo não encontrada: {example_image}")
        print("Por favor, coloque uma imagem fisheye na pasta 'fisheye_samples'")
        return
    
    # Parâmetros básicos
    params = {
        "fov": 180,
        "pfov": 140,
        "dtype": "stereographic",
        "format": "fullframe"
    }
    
    try:
        # Aplica correção
        defisheye = DefisheyeAlgorithm(example_image, **params)
        corrected_image = defisheye.convert()
        
        # Salva resultado
        output_path = "example_output_basic.jpg"
        cv2.imwrite(output_path, corrected_image)
        
        print(f"✅ Correção básica concluída! Resultado salvo em: {output_path}")
        
    except Exception as e:
        print(f"❌ Erro na correção básica: {e}")

def example_advanced_correction():
    """Exemplo avançado com diferentes parâmetros"""
    print("\n🔧 Exemplo 2: Correção Avançada")
    
    example_image = "fisheye_samples/example.jpg"
    if not os.path.exists(example_image):
        print(f"❌ Imagem de exemplo não encontrada: {example_image}")
        return
    
    # Diferentes configurações para testar
    configurations = [
        {
            "name": "Linear",
            "params": {"fov": 180, "pfov": 120, "dtype": "linear", "format": "fullframe"}
        },
        {
            "name": "Equal Area",
            "params": {"fov": 180, "pfov": 130, "dtype": "equalarea", "format": "circular"}
        },
        {
            "name": "Orthographic",
            "params": {"fov": 180, "pfov": 110, "dtype": "orthographic", "format": "fullframe"}
        }
    ]
    
    for config in configurations:
        try:
            print(f"Processando configuração: {config['name']}")
            
            defisheye = DefisheyeAlgorithm(example_image, **config['params'])
            corrected_image = defisheye.convert()
            
            output_path = f"example_output_{config['name'].lower().replace(' ', '_')}.jpg"
            cv2.imwrite(output_path, corrected_image)
            
            print(f"✅ {config['name']} salvo em: {output_path}")
            
        except Exception as e:
            print(f"❌ Erro na configuração {config['name']}: {e}")

def example_parameter_sweep():
    """Exemplo de varredura de parâmetros"""
    print("\n🔧 Exemplo 3: Varredura de Parâmetros")
    
    example_image = "fisheye_samples/example.jpg"
    if not os.path.exists(example_image):
        print(f"❌ Imagem de exemplo não encontrada: {example_image}")
        return
    
    # Testa diferentes valores de PFOV
    pfov_values = [90, 110, 130, 150]
    
    for pfov in pfov_values:
        try:
            print(f"Testando PFOV = {pfov}")
            
            params = {
                "fov": 180,
                "pfov": pfov,
                "dtype": "stereographic",
                "format": "fullframe"
            }
            
            defisheye = DefisheyeAlgorithm(example_image, **params)
            corrected_image = defisheye.convert()
            
            output_path = f"example_output_pfov_{pfov}.jpg"
            cv2.imwrite(output_path, corrected_image)
            
            print(f"✅ PFOV {pfov} salvo em: {output_path}")
            
        except Exception as e:
            print(f"❌ Erro com PFOV {pfov}: {e}")

def compare_original_and_corrected():
    """Compara imagem original com corrigida lado a lado"""
    print("\n🔧 Exemplo 4: Comparação Original vs Corrigida")
    
    example_image = "fisheye_samples/example.jpg"
    if not os.path.exists(example_image):
        print(f"❌ Imagem de exemplo não encontrada: {example_image}")
        return
    
    try:
        # Carrega imagem original
        original = cv2.imread(example_image)
        
        # Aplica correção
        params = {
            "fov": 180,
            "pfov": 140,
            "dtype": "stereographic",
            "format": "fullframe"
        }
        
        defisheye = DefisheyeAlgorithm(example_image, **params)
        corrected = defisheye.convert()
        
        # Redimensiona para ter o mesmo tamanho
        height, width = original.shape[:2]
        corrected_resized = cv2.resize(corrected, (width, height))
        
        # Combina as imagens lado a lado
        combined = np.hstack([original, corrected_resized])
        
        # Adiciona legendas
        cv2.putText(combined, 'Original', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        cv2.putText(combined, 'Corrigida', (width + 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        
        # Salva comparação
        output_path = "example_comparison.jpg"
        cv2.imwrite(output_path, combined)
        
        print(f"✅ Comparação salva em: {output_path}")
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")

def main():
    """Função principal com todos os exemplos"""
    print("=" * 60)
    print("🐟 Exemplos de Uso - Aplicação Integrada de Correção Fisheye")
    print("=" * 60)
    
    # Verifica se o arquivo principal existe
    if not os.path.exists("integrated_defisheye_app.py"):
        print("❌ Arquivo 'integrated_defisheye_app.py' não encontrado!")
        print("Certifique-se de executar este script no diretório correto")
        return
    
    # Cria pasta de saída se não existir
    os.makedirs("example_outputs", exist_ok=True)
    
    # Executa exemplos
    example_basic_correction()
    example_advanced_correction()
    example_parameter_sweep()
    compare_original_and_corrected()
    
    print("\n" + "=" * 60)
    print("✅ Todos os exemplos foram executados!")
    print("📁 Verifique a pasta atual para os resultados")
    print("🎯 Para usar a interface gráfica, execute: python integrated_defisheye_app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

