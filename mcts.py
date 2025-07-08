import random
import math
import copy

""" hard: iterações= 1000, C=1.41
medium: iterações=250, C=1
easy: iterações=50, C=2 """

class MCTS(object):
    def __init__(self, state, iterations=1000, exploration_constant=1.41):
        """
        state: estado atual do tabuleiro, passdo como argumento
        iterations: número de iterações para a simulação.
        exploration_constant: constante C utilizada na fórmula UCT.
        """
        self.state = state
        self.iterations = iterations
        self.exploration_constant = exploration_constant

    @staticmethod
    def get_legal_moves(state):
        """Returns a list of not full columns"""
        moves = []
        for col in range(7):
            for row in range(6):
                if state[row][col] == ' ':
                    moves.append(col)
                    break
        return moves

    @staticmethod
    def make_move(state, col, color):
        """Returns a new state after choosing a column to play"""
        new_state = copy.deepcopy(state)
        for row in range(6):
            if new_state[row][col] == ' ':
                new_state[row][col] = color
                break
        return new_state

    @staticmethod
    def game_result(state):
        """
        Verifies if there is a winner (returns "x" or "o"), if not returns "draw"
        """
        for i in range(6):
            for j in range(7):
                #for each position on the board
                if state[i][j] != ' ':
                    token = state[i][j]
                    # horizontal
                    if j <= 7 - 4 and all(state[i][j+k] == token for k in range(4)):
                        return token
                    # vertical
                    if i <= 6 - 4 and all(state[i+k][j] == token for k in range(4)):
                        return token
                    # diagonal descendente
                    if i <= 6 - 4 and j <= 7 - 4 and all(state[i+k][j+k] == token for k in range(4)):
                        return token
                    # diagonal ascendente
                    if i >= 3 and j <= 7 - 4 and all(state[i-k][j+k] == token for k in range(4)):
                        return token
        #if there's no winner and every position is not empty, then its a draw
        if all(state[i][j] != ' ' for i in range(6) for j in range(7)):
            return 'draw'
        return None

    @staticmethod
    def other_player(player):
        """Returns the opposite player ('x' ou 'o')."""
        return 'o' if player == 'x' else 'x'

    class Node(object):
        def __init__(self, state, move=None, parent=None, player=None):
            """
            state: estado atual do tabuleiro.
            move: jogada (coluna) que levou a este estado (None para a raiz).
            parent: nó pai.
            player: jogador que realizou a jogada que levou a este nó.
                     Na raiz, este valor deve ser o oponente do jogador a mover.
            """
            self.state = state
            self.move = move
            self.parent = parent
            self.children = []
            self.untried_moves = MCTS.get_legal_moves(state)
            #for each node we keep track of visits and wins
            self.visits = 0
            self.wins = 0
            self.player = player  
            
        #returns true if mcts tried every legal column
        def fully_expanded(self):
            return len(self.untried_moves) == 0

        def best_child(self, exploration_constant):
            """Chosing the child to expand using the UCT formula"""
            best_score = -float("inf")
            best_child = None
            for child in self.children:
                win_rate = child.wins / child.visits
                exploration = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
                score = win_rate + exploration
                if score > best_score:
                    best_score = score
                    best_child = child
            return best_child

    def bestMove(self, state, player):
        """
        Executes and chooses the best play
        """
        
        root = self.Node(state, player=self.other_player(player))
        """ Aqui, a raiz representa o estado atual do jogo. 
        O atributo player da raiz é definido como o jogador oposto ao que queremos mover, 
        porque o nó raiz é pensado como tendo sido alcançado após a jogada do adversário. 
        """
        
        for _ in range(self.iterations):
            """ vai realizar iterações porque esse é o valor passado no construtor
             em cada iteração, realiza seleção, expansão, simulação e retropropagação """
            
            node = root
            state_copy = copy.deepcopy(state)
            
            #SELECTION 
            """ só entra no loop se o nó estiver totalmente expandido
            caso entre: seleciona o melhor filho, atualiza o estado
            com a jogada escolhida no filho e "node"""
            while node.fully_expanded() and self.game_result(state_copy) is None:
                node = node.best_child(self.exploration_constant)
                # Determina o jogador que fez a jogada neste nó.
                move_player = self.other_player(node.parent.player) if node.parent else player
                state_copy = self.make_move(state_copy, node.move, move_player)
            
            # EXPANSION
            """ 
            se o estado atual nao for terminal e ainda houver movimentos não explorados
            (node.untried_moves), o algoritmo escolhe aleatoriamente um desses moves
            e cria um novo nó (filho) na árvore.
            -> se já tiver tentado todos os moves, deixa de fazer expansão e vai para o prox passo
            """
            if self.game_result(state_copy) is None and node.untried_moves:
                move = random.choice(node.untried_moves)
                new_state = self.make_move(state_copy, move, self.other_player(node.player))
                child_node = self.Node(new_state, move=move, parent=node, player=self.other_player(node.player))
                node.untried_moves.remove(move)
                node.children.append(child_node)
                node = child_node #a simulação vai começar a partir deste novo nó
            
            # SIMULATION (Rollout)
            """ 
            simula uma sequência de jogadas aleatórias até que o jogo termine
            -> cria uma copia (rollout_state) para preservar o estado original da árvore
            """
            rollout_state = copy.deepcopy(state_copy)
            current_player = self.other_player(node.player) #player that makes the next move
            result = self.game_result(rollout_state)
            while result is None:
                legal_moves = self.get_legal_moves(rollout_state)
                if not legal_moves:
                    result = 'draw'
                    break
                move = random.choice(legal_moves)
                rollout_state = self.make_move(rollout_state, move, current_player)
                current_player = self.other_player(current_player)
                result = self.game_result(rollout_state)
            
            # Define a recompensa do ponto de vista do jogador que queremos mover
            if result == player:
                reward = 1
            elif result == 'draw':
                reward = 0.5
            else:
                reward = 0
            
            #BACKPROPAGATION
            while node is not None:
                node.visits += 1 #increase the number of visits

                if node.player == player: #if it is a node of our player: give the reward calculated before
                    node.wins += reward
                else:
                    node.wins += 1 - reward  #else, give the opposite reward
                node = node.parent

        
        #To choose a move, we select the child of the root node with the most visits
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move
    


