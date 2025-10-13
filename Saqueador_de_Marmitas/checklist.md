# Checklist de Tarefas do Projeto

## Integrante 1: Davi Brilhante

**Foco:** Construir a fundação do mundo do agente: a estrutura de dados do grid, dos nós e dos terrenos.

-   `[ ]` **Módulo `terrain.js`**
    -   `[ ]` Criar o arquivo `terrain.js`.
    -   `[ ]` Definir e exportar o `enum` **Terrain**, contendo as propriedades `name`, `cost`, `color` e `isObstacle` para cada tipo de terreno (SAND, SWAMP, WATER, OBSTACLE).

-   `[ ]` **Módulo `Node.js`**
    -   `[ ]` Criar a classe `Node`.
    -   `[ ]` Implementar o construtor com as propriedades básicas (`x`, `y`).
    -   `[ ]` Adicionar a propriedade `terrain` que recebe um valor do `enum` **Terrain**.
    -   `[ ]` Adicionar a propriedade `state` para controle visual (iniciando como `'default'`).
    -   `[ ]` Adicionar as propriedades para os algoritmos de busca (`parent`, `g`, `h`, `f`).

-   `[ ]` **Módulo `Grid.js`**
    -   `[ ]` Criar a estrutura básica da classe `Grid` em `Grid.js`.
    -   `[ ]` Implementar o método `generateRealisticMap()` utilizando **Ruído de Perlin (noise())** para distribuir os terrenos definidos no `enum`.
    -   `[ ]` Implementar o método `getNeighbors(node)` que retorna um array de nós vizinhos válidos (não-obstáculos).
    -   `[ ]` Implementar o método `clone()` que realiza uma cópia profunda (deep copy) de toda a estrutura do grid e de seus nós.
    -   `[ ]` Implementar o método `draw()` que lê o `node.state` e o `node.terrain.color` para desenhar cada célula do grid.

## Integrante 2: Gabriel Monteiro

**Foco:** Orquestrar o fluxo do programa, gerenciar o estado e dar vida à animação e ao agente.

-   `[ ]` **Configuração do `sketch.js`**
    -   `[ ]` Criar as variáveis globais para `grid`, `agent`, `food`, e estado da aplicação (ex: `currentGameState`).
    -   `[ ]` Implementar a função `setup()`, instanciando os objetos principais.
    -   `[ ]` Estruturar a função `draw()` para chamar os métodos de desenho e atualização corretos com base no estado do jogo.

-   `[ ]` **Lógica de Animação da Busca**
    -   `[ ]` Implementar a lógica que recebe o `gridHistory` de uma função de busca.
    -   `[ ]` No `draw()`, iterar sobre o `gridHistory` (um grid por frame) para exibir a animação passo a passo da busca.

-   `[ ]` **Módulo `Agent.js` e `Food.js`**
    -   `[ ]` Implementar a classe `Agent` com posição e método `draw()`.
    -   `[ ]` Implementar a classe `Food` com posição e método `draw()`.
    -   `[ ]` No `Agent`, implementar o método `setPath(path)` para receber o caminho final.
    -   `[ ]` Implementar a lógica de movimento do agente ao longo do caminho, com velocidade variável baseada em `currentNode.terrain.cost`.
    -   `[ ]` Implementar a detecção de colisão entre o agente e a comida.

-   `[ ]` **Gerenciamento de Estado**
    -   `[ ]` Garantir que, ao selecionar um novo algoritmo no menu, a busca seja re-executada no **mesmo mapa**, limpando apenas o resultado da busca anterior.
    -   `[ ]` Implementar o reaparecimento da comida após a coleta.

## Integrante 3: João Pedro

**Foco:** Implementar os algoritmos de busca não-informada e as funções de heurística que servirão de base para os outros algoritmos.

-   `[ ]` **Módulo `heuristics.js`**
    -   `[ ]` Criar o arquivo `heuristics.js`.
    -   `[ ]` Implementar e exportar a função `manhattanDistance(nodeA, nodeB)`.
    -   `[ ]` Implementar e exportar a função `euclideanDistance(nodeA, nodeB)`.

-   `[ ]` **Módulo `search.js` (Buscas Não-Informadas)**
    -   `[ ]` Implementar o algoritmo **BFS (Busca em Largura)**.
        -   `[ ]` Garantir que a função siga o "contrato" e retorne `{ finalPath, gridHistory }`.
    -   `[ ]` Implementar o algoritmo **DFS (Busca em Profundidade)**.
        -   `[ ]` Garantir que a função também retorne `{ finalPath, gridHistory }`.

## Integrante 4: ???

**Foco:** Implementar a estrutura de dados `PriorityQueue` e os algoritmos de busca informada baseados em custo.

-   `[ ]` **Módulo `PriorityQueue.js`**
    -   `[ ]` Criar e implementar a classe `PriorityQueue`.
    -   `[ ]` A fila deve ser capaz de ordenar os nós com base em uma prioridade (como custo `g` ou `f`).

-   `[ ]` **Módulo `search.js` (Buscas de Custo)**
    -   `[ ]` Implementar o algoritmo **Custo Uniforme (UCS)**.
        -   `[ ]` Utilizar a `PriorityQueue` para ordenar os nós pelo menor custo `g`.
        -   `[ ]` Garantir que a função retorne `{ finalPath, gridHistory }`.
    -   `[ ]` Implementar o algoritmo **Gulosa (Greedy Best-First Search)**.
        -   `[ ]` Utilizar a `PriorityQueue` para ordenar os nós pelo menor valor da heurística `h`.
        -   `[ ]` A função deve aceitar uma função de heurística como parâmetro.
        -   `[ ]` Garantir que a função retorne `{ finalPath, gridHistory }`.

## Integrante 5: ???

**Foco:** Implementar o algoritmo de busca mais complexo (A*) e criar toda a interface de usuário para controlar a aplicação.

-   `[ ]` **Módulo `search.js` (Busca A*)**
    -   `[ ]` Implementar o algoritmo **A* (A-Star)**.
        -   `[ ]` Utilizar a `PriorityQueue` para ordenar os nós pelo menor custo `f (g + h)`.
        -   `[ ]` A função deve aceitar uma função de heurística como parâmetro.
        -   `[ ]` Garantir que a função retorne `{ finalPath, gridHistory }`.

-   `[ ]` **Interface do Usuário (UI) em `sketch.js`**
    -   `[ ]` Criar os elementos HTML/DOM para o menu de controle.
    -   `[ ]` Implementar o seletor (dropdown ou botões) para escolher o **algoritmo de busca**.
    -   `[ ]` Implementar o seletor para a **heurística** (Manhattan/Euclidiana).
    -   `[ ]` Implementar a lógica para habilitar/desabilitar o seletor de heurística (deve estar ativo apenas para Gulosa e A*).
    -   `[ ]` Implementar o botão **"Gerar Novo Mapa"**.

-   `[ ]` **Integração da UI**
    -   `[ ]` Conectar os eventos do menu (ex: `onChange`, `onClick`) para chamar as funções correspondentes no `sketch.js`.
    -   `[ ]` Coordenar com o Integrante 2 para garantir que os eventos da UI disparem a re-execução da busca ou a geração de um novo mapa corretamente.