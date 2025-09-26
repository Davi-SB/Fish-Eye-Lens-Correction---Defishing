#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalação e execução da Aplicação Integrada de Correção Fisheye
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências necessárias"""
    print("🔧 Instalando dependências...")
    
    requirements = [
        "opencv-python>=4.5.0",
        "numpy>=1.19.0", 
        "Pillow>=8.0.0"
    ]
    
    for requirement in requirements:
        try:
            print(f"Instalando {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✅ {requirement} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {requirement}: {e}")
            return False
    
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import cv2
        print("✅ OpenCV instalado")
    except ImportError:
        print("❌ OpenCV não encontrado")
        return False
    
    try:
        import numpy
        print("✅ NumPy instalado")
    except ImportError:
        print("❌ NumPy não encontrado")
        return False
    
    try:
        import PIL
        print("✅ Pillow instalado")
    except ImportError:
        print("❌ Pillow não encontrado")
        return False
    
    try:
        import tkinter
        print("✅ Tkinter disponível")
    except ImportError:
        print("❌ Tkinter não encontrado")
        return False
    
    return True

def run_application():
    """Executa a aplicação integrada"""
    print("🚀 Iniciando aplicação...")
    
    try:
        # Importa e executa a aplicação
        from integrated_defisheye_app import IntegratedDefisheyeApp
        
        app = IntegratedDefisheyeApp()
        print("✅ Aplicação iniciada com sucesso!")
        print("📖 Use a interface para abrir uma imagem e ajustar os parâmetros")
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro ao importar a aplicação: {e}")
        print("Certifique-se de que o arquivo 'integrated_defisheye_app.py' está no diretório atual")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar a aplicação: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("=" * 50)
    print("🐟 Aplicação Integrada de Correção Fisheye")
    print("=" * 50)
    
    # Verifica se estamos no diretório correto
    if not os.path.exists("integrated_defisheye_app.py"):
        print("❌ Arquivo 'integrated_defisheye_app.py' não encontrado!")
        print("Certifique-se de executar este script no diretório correto")
        return
    
    # Verifica dependências
    if not check_dependencies():
        print("\n📦 Instalando dependências ausentes...")
        if not install_requirements():
            print("❌ Falha na instalação das dependências")
            return
        
        # Verifica novamente após instalação
        if not check_dependencies():
            print("❌ Ainda há dependências ausentes após instalação")
            return
    
    print("\n✅ Todas as dependências estão instaladas!")
    
    # Executa a aplicação
    run_application()

if __name__ == "__main__":
    main()

