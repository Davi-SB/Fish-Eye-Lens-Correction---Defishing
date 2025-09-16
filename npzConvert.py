# Salve este código como: npz_to_py_converter.py
import numpy as np
import argparse
import os

def convert_npz_to_py(input_file_path: str, output_file_path: str):
    """
    Lê um arquivo .npz e gera um script Python (.py) que recria os arrays contidos.

    Args:
        input_file_path (str): O caminho para o arquivo de entrada .npz.
        output_file_path (str): O caminho para o arquivo de saída .py.
    """
    try:
        # Carrega o arquivo .npz. O 'with' garante que o arquivo seja fechado.
        with np.load(input_file_path) as data:
            # Lista para armazenar as linhas de código que serão geradas
            code_lines = [
                "# Arquivo Python gerado automaticamente a partir de:",
                f"# {os.path.basename(input_file_path)}",
                "#",
                "# Este script contém os arrays NumPy que estavam armazenados no arquivo .npz.",
                "import numpy as np",
                ""
            ]

            print(f"Lendo o arquivo '{input_file_path}'...")
            print(f"Arrays encontrados: {', '.join(data.files)}")

            # Itera sobre cada array dentro do arquivo .npz
            for key in data.files:
                array = data[key]
                
                # A função repr() do NumPy cria uma representação de string do array
                # que é um código Python válido para recriá-lo.
                # Ex: repr(np.array([1, 2])) -> "array([1, 2])"
                # Nós apenas adicionamos "np." no início.
                array_representation = f"np.{repr(array)}"
                
                # Adiciona a linha de código formatada (ex: "camera_matrix = np.array(...)")
                code_lines.append(f"{key} = {array_representation}")
                code_lines.append("") # Adiciona uma linha em branco para legibilidade

            # Junta todas as linhas de código em uma única string
            output_code = "\n".join(code_lines)

            # Escreve a string no arquivo de saída .py
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(output_code)
            
            print("-" * 30)
            print(f"Sucesso! O código foi salvo em: '{output_file_path}'")

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{input_file_path}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Converte os arrays de um arquivo .npz para um script Python (.py).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Caminho para o arquivo .npz de entrada."
    )
    parser.add_argument(
        "-o", "--output_file",
        type=str,
        default=None,
        help="Caminho para o arquivo .py de saída (opcional).\n"
             "Se não for fornecido, o nome será baseado no arquivo de entrada (ex: dados.npz -> dados_data.py)."
    )
    
    args = parser.parse_args()
    
    input_path = args.input_file
    output_path = args.output_file

    # Se nenhum nome de arquivo de saída foi dado, cria um baseado no de entrada
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_data.py"
        
    convert_npz_to_py(input_path, output_path)

if __name__ == "__main__":
    main()