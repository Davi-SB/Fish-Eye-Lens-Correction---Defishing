# 📖 Guia de Execução do Projeto

Este guia contém todas as instruções necessárias para rodar a simulação, seja no editor online do p5.js ou localmente em sua máquina.

## 🌐 Opção 1: Executando no Editor Web do p5.js (Recomendado)

Esta é a forma mais simples e rápida de ver o projeto funcionando.

1.  **Copie o código**: Acesse cada arquivo de código (`.js`, `index.html`, `style.css`) neste repositório.
2.  **Acesse o Editor p5.js**: Abra o [Editor Web do p5.js](https://editor.p5js.org/).
3.  **Cole os arquivos**:
    -   Cole o conteúdo de `sketch.js` no arquivo `sketch.js` do editor.
    -   Se houver outros arquivos `.js`, clique no ícone `>` ao lado de "Sketch Files" e selecione "Add File" para criar e colar o conteúdo dos outros arquivos (`agent.js`, `grid.js`, etc.). **Importante**: lembre-se de carregar esses novos arquivos no `index.html`.
    -   Faça o mesmo para `index.html` e `style.css`.
4.  **Execute**: Clique no botão "Play" (▶️) para iniciar a simulação.

## 💻 Opção 2: Executando Localmente com VS Code

Esta opção é ideal para desenvolvimento e modificações. Como você usa Windows 11 e VS Code, estes passos são direcionados para seu ambiente.

### Pré-requisitos

1.  **[Git](https://git-scm.com/downloads)** instalado.
2.  **[VS Code](https://code.visualstudio.com/)** instalado.
3.  Extensão **[Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)** instalada no VS Code. Ela é essencial para rodar projetos p5.js localmente.

### Passos

1.  **Clone o Repositório**
    -   Abra um terminal (pode ser o `cmd`, `PowerShell` ou o terminal do `Git Bash`).
    -   Navegue até a pasta onde deseja salvar o projeto.
    -   Execute o comando abaixo (substitua pela URL do seu repositório):
        ```bash
        git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
        ```

2.  **Abra no VS Code**
    -   Abra o VS Code.
    -   Vá em `File` > `Open Folder...` e selecione a pasta do projeto que você acabou de clonar.

3.  **Baixe a biblioteca p5.js**
    -   Vá para a página de [download do p5.js](https://p5js.org/download/).
    -   Baixe o arquivo `p5.js` (não o `p5.min.js`, para facilitar a depuração).
    -   Crie uma pasta chamada `lib` dentro do seu projeto e coloque o arquivo `p5.js` lá dentro.
    -   Certifique-se que seu `index.html` está apontando para este arquivo, com uma linha como esta dentro do `<head>`:
        ```html
        <script src="lib/p5.js"></script>
        ```

4.  **Inicie o Servidor Local**
    -   No canto inferior direito do VS Code, você verá um botão chamado **`Go Live`**. Clique nele.
    -   Seu navegador padrão abrirá automaticamente com o projeto em execução! 🎉

Toda vez que você salvar uma alteração em um dos arquivos, o Live Server recarregará a página automaticamente.