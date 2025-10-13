## **Visão Geral da Arquitetura**

### **1. Estrutura de Arquivos e Diretórios**

```
/Saqueador_de_Marmitas
|-- /src
    |
    |-- index.html              // Arquivo HTML principal que carrega o p5.js e os scripts
    |-- sketch.js               // O cérebro do projeto: loop principal, UI, estados e animação
    |
    |-- /modules
    |   |-- terrain.js          // Enum/configuração para os tipos de terreno (custos, cores)
    |   |-- Node.js             // Classe que representa um único "quadrado" ou nó no grid
    |   |-- Grid.js             // Classe que gerencia o mapa (grid), nós e sua clonagem
    |   |-- Agent.js            // Classe que gerencia o agente (posição, movimento)
    |   |-- Food.js             // Classe que gerencia a comida
    |
    |-- /algorithms
    |   |-- search.js           // Arquivo com TODAS as funções de busca (BFS, DFS, A*, etc.)
    |   |-- heuristics.js       // Funções de heurística (Manhattan e Euclidiana)
    |   |-- PriorityQueue.js    // Estrutura de dados auxiliar para buscas de custo
    |
    |-- style.css               // CSS para estilizar a página e a UI (opcional)
```

-----

### **2. Definição das Classes e Interfaces (O "Contrato" da Equipe)**

Esta é a parte mais importante. Todos devem seguir estas definições para garantir a compatibilidade.

#### **`terrain.js` - A Configuração Central dos Terrenos**

Para garantir consistência, usaremos um objeto que funciona como um `enum` para definir todos os tipos de terreno, seus custos e outras propriedades.

```javascript
// /modules/terrain.js

const Terrain = {
    SAND: {
        name: 'sand',
        cost: 1,
        isObstacle: false,
        color: [210, 180, 140]
    },
    SWAMP: {
        name: 'swamp',
        cost: 5,
        isObstacle: false,
        color: [85, 107, 47]
    },
    WATER: {
        name: 'water',
        cost: 10,
        isObstacle: false,
        color: [70, 130, 180]
    },
    OBSTACLE: {
        name: 'obstacle',
        cost: Infinity,
        isObstacle: true,
        color: [128, 128, 128]
    }
};

// Object.freeze() impede que o objeto seja modificado em outras partes do código
Object.freeze(Terrain);
```

#### **`Node.js` - A Unidade Fundamental**

Representa um único quadrado no grid e agora usa o `enum` de terreno.

```javascript
// /modules/Node.js

class Node {
    constructor(x, y, ...) {
        this.x = x; // Coordenada X no grid
        this.y = y; // Coordenada Y no grid
        
        // O terreno é um objeto do nosso enum, contendo custo, cor, etc.
        this.terrain = Terrain.(...);

        // Propriedade para visualização dos algoritmos.
        // Ex: 'default', 'frontier', 'visited', 'path'
        this.state = 'default';

        // Propriedades para os algoritmos de busca
        this.parent = parent;
        this.g = g;
        this.h = h;
        this.f = f;
    }
}
```

#### **`Grid.js` - O Mundo do Agente**

Gerencia o mapa, sua geração, clonagem e visualização.

```javascript
// /modules/Grid.js

class Grid {
    constructor(cols, rows, cellSize) {
        this.cols = cols;
        this.rows = rows;
        this.cellSize = cellSize;
        this.grid = []; // Matriz 2D de objetos Node
        this.generateRealisticMap();
    }

    // Gera o mapa usando Ruído de Perlin e o enum de Terrenos
    generateRealisticMap() { /* ... Lógica usando noise() para atribuir Terrain.SAND, etc. */ }

    /**
     * Desenha o grid, colorindo cada nó de acordo com seu this.state
     * ou, se o estado for 'default', com a cor do seu terreno.
     */
    draw() { /* ... Lógica para ler node.state e node.terrain.color */ }
    
    /**
     * Cria e retorna uma cópia profunda (deep copy) deste grid.
     * Essencial para criar o histórico da busca.
     */
    clone() { /* ... Lógica para criar um novo Grid e copiar cada Node */ }

    getNeighbors(node) { /* ... Retorna vizinhos que não são obstáculos */ }
}
```

#### **`search.js` - O Cérebro dos Algoritmos**

Todas as funções de busca devem retornar um histórico de grids para a animação.

```javascript
// /algorithms/search.js

/**
 * Assinatura para TODAS as buscas.
 * @returns {Object} Um objeto com o caminho final e o histórico de grids.
 * { finalPath: Node[], gridHistory: Grid[] }
 */
function breadthFirstSearch(initialGrid, startNode, goalNode) {
    const gridHistory = [];
    
    // ... setup inicial do algoritmo ...

    while (/* fronteira não vazia */) {
        // 1. Processa um passo da busca
        
        // 2. Cria uma NOVA cópia do grid do passo anterior
        let stepGrid = gridHistory[gridHistory.length - 1].clone();

        // 3. Atualiza o 'state' dos nós NESTA CÓPIA (ex: 'visited', 'frontier')

        // 4. Adiciona a cópia atualizada ao histórico
        gridHistory.push(stepGrid);
    }
    
    // ...
    return { finalPath: [...], gridHistory: gridHistory };
}

// Todas as outras funções (DFS, UCS, Greedy, A*) devem seguir a MESMA lógica.
```

-----

### **3. Divisão de Tarefas para a Equipe (5 Integrantes)**

#### **Integrante 1: O Mundo**

  * **Arquivos Principais:** `terrain.js`, `Node.js`, `Grid.js`
  * **Responsabilidades:**
    1.  **Foco Principal:** Definir e implementar o `enum` de terrenos no arquivo `terrain.js`, centralizando os custos, cores e propriedades de cada tipo.
    2.  Implementar a classe `Node`, garantindo que ela utilize corretamente o `enum` `Terrain`.
    3.  Implementar a classe `Grid`, incluindo a geração de mapa com **Ruído de Perlin** e o crucial método `clone()`.
    4.  Ajustar `Grid.draw()` para renderizar cores com base no `Node.state` e `Node.terrain.color`.

#### **Integrante 2: Animação e Lógica**

  * **Arquivos Principais:** `sketch.js`, `Agent.js`, `Food.js`
  * **Responsabilidades:**
    1.  Configurar o `setup()` e `draw()` e instanciar os objetos principais.
    2.  Receber o `gridHistory` da busca e, no loop `draw()`, exibir um grid do histórico por frame para criar a animação.
    3.  **Foco Principal:** Gerenciar o estado do problema. Ao mudar o algoritmo no menu, a busca deve ser re-executada no **mesmo mapa**, limpando apenas a animação anterior.
    4.  Implementar a classe `Agent` e o movimento final pelo `finalPath`, com velocidade baseada em `currentNode.terrain.cost`.

#### **Integrante 3: O Explorador 1**

  * **Arquivos Principais:** `search.js`, `heuristics.js`
  * **Responsabilidades:**
    1.  Implementar o algoritmo **BFS (Busca em Largura)**, seguindo o formato de retorno `gridHistory`.
    2.  Implementar o algoritmo **DFS (Busca em Profundidade)**, seguindo o mesmo formato.
    3.  **Foco Principal:** Implementar o arquivo `heuristics.js`, contendo as funções `manhattanDistance` e `euclideanDistance`, que recebem o grid e dois nodes dele e retornam o valor da heuristica

#### **Integrante 4: O Explorador 2**
  * **Arquivos Principais:** `search.js`, `PriorityQueue.js`
  * **Responsabilidades:**
    1.  Implementar uma estrutura de dados **Priority Queue** em `PriorityQueue.js`.
    2.  Implementar o algoritmo **Custo Uniforme (UCS)**, seguindo o formato de retorno `gridHistory`.
    3.  Implementar o algoritmo **Gulosa (Greedy Best-First Search)**, que receberá uma função de heurística como parâmetro e também retornará o `gridHistory`.

#### **Integrante 5: O Estrategista com Interface (Strategist & UI Designer)**
  * **Arquivos Principais:** `search.js`, `sketch.js` (parte da UI)
  * **Responsabilidades:**
    1.  Implementar o algoritmo \**A* (A-Star)\*\*, que utilizará a `PriorityQueue` e as heurísticas e retornará o `gridHistory`. Lembrar de usar pesos na função de avaliação \(f(n) = g(n) + h(n)\)\, quando apropriado.
    2.  **Foco Principal:** Implementar o menu de controle da aplicação, que deve conter:
          * Um seletor para o **algoritmo de busca**. Lembrar que mudar o algoritmo deve reiniciar a busca no mesmo mapa e posição inicial de agente/comida.
          * Um seletor para a **heurística**, que deve ficar visível/ativo **apenas** quando "Gulosa" ou "A\*" for selecionado.
          * Opção de "Gerar Novo Mapa".
    3.  Conectar os eventos do menu ao código principal em `sketch.js` para disparar as ações corretas.

-----