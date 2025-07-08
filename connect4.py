import random
import os
import time
from mcts import MCTS
from decision_tree_model import train_tree, predict_from_tree


class Game(object):
    """ Game object that holds state of Connect 4 board and game values
    """
    
    board = None
    round = None
    finished = None
    winner = None
    turn = None
    players = [None, None]
    game_name = "Connect Four"
    colors = ["x", "o"]
    
    def __init__(self, silent):
        self.round = 1
        self.finished = False
        self.winner = None
        
        # do cross-platform clear screen
        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
        if not silent:
            print(u"Welcome to {0}!".format(self.game_name))
            self.configure_player(0)
            self.configure_player(1)


        #se for silent, tem na mesma que haver configuração do board
        self.board = []
        for i in range(6):
            self.board.append([])
            for j in range(7):
                self.board[i].append(' ')


    def configure_player(self, index):
        """ configuração dos jogadores, human/computer -> DT ou MCTS """

        print(f"\nShould Player {index + 1} be a Human or a Computer?")
        
        while self.players[index] is None:
            choice = input("Type 'H' for Human or 'C' for Computer: ").strip().lower()

            if choice in ['h', 'human']:
                name = input(f"What is Player {index + 1}'s name? ").strip()
                self.players[index] = Player(name, self.colors[index])

            elif choice in ['c', 'computer']:
                print("Choose the AI type:")
                print("1. MCTS")
                print("2. Decision Tree (DT)")
                ai_choice = input("Enter 1 or 2: ").strip()

                if ai_choice == '1':
                    print("Choose difficulty:\n1. Easy\n2. Medium\n3. Hard")
                    diff = input("Enter 1, 2 or 3: ").strip()
                    name = f"MCTS_{['Easy', 'Medium', 'Hard'][int(diff)-1]}"
                    iterations = [50, 250, 1000][int(diff)-1]
                    c_value = [2, 1, 1.41][int(diff)-1]
                    self.players[index] = AIPlayer_MCTS(name, self.colors[index], iterations, c_value)

                elif ai_choice == '2':
                    print("Choose difficulty:\n1. Easy\n2. Medium\n3. Hard")
                    diff = input("Enter 1, 2 or 3: ").strip()
                    name = f"DT_{['Easy', 'Medium', 'Hard'][int(diff)-1]}"
                    difficulty = ['easy', 'medium', 'hard'][int(diff)-1]
                    self.players[index] = AIPlayer_DT(name, self.colors[index], difficulty)


                else:
                    print("Invalid choice for AI type. Please select 1 or 2.")

            else:
                print("Invalid input. Please type 'H' or 'C'.")

        print(f"{self.players[index].name} will be {self.colors[index]}")
                    
                
        self.turn = self.players[0]
        
        #write the board
        self.board = []
        for i in range(6):
            self.board.append([])
            for j in range(7):
                self.board[i].append(' ')
    
    def newGame(self):
        """ Function to reset the game, but not the names or colors """
        self.round = 1
        self.finished = False
        self.winner = None

        # Atualizar o turno para o primeiro jogador da lista
        self.turn = self.players[0]

        self.board = [[' ' for _ in range(7)] for _ in range(6)]


    def switchTurn(self):
        if self.turn == self.players[0]:
            self.turn = self.players[1]
        else:
            self.turn = self.players[0]

        # increment the round
        self.round += 1

    def nextMove(self,silent = False):
        player = self.turn

        # there are only 42 legal places for pieces on the board
        # exactly one piece is added to the board each turn
        if self.round > 42:
            self.finished = True
            #this is a tie
            return
        
        # store the board before the play
        state_before_play = self.board 
        
        # move is the column that player want's to play
        move = player.move(self.board, silent)
            

        #verify if the column has space
        for i in range(6):
            if self.board[i][move] == ' ':
                self.board[i][move] = player.color
                self.switchTurn()
                self.checkForFours()
                if not silent:
                    self.printState()
                    print("{0} played in column {1}.".format(player.name, (move+1)))
                    
                    
                return

        if not silent:
            # if we get here, then the column is full
            print("Invalid move (column is full)")
            return
    
    def checkForFours(self):
        #a function that calls other functions to verify if the game ended
        #if any returns true, the game ends
        #this only checks, it doesnt return where the 4 in a row is, for that we have the "findFours"
        # for each piece in the board
        for i in range(6):
            for j in range(7):
                if self.board[i][j] != ' ':
                    # check if a vertical four-in-a-row starts at (i, j)
                    if self.verticalCheck(i, j):
                        self.finished = True
                        return
                    
                    # check if a horizontal four-in-a-row starts at (i, j)
                    if self.horizontalCheck(i, j):
                        self.finished = True
                        return
                    
                    # check if a diagonal (either way) four-in-a-row starts at (i, j)
                    # also, get the slope of the four if there is one
                    diag_fours, slope = self.diagonalCheck(i, j)
                    if diag_fours:
                        print(slope)
                        self.finished = True
                        return
        
    def verticalCheck(self, row, col):
        
        fourInARow = False
        consecutiveCount = 0
    
        for i in range(row, 6):
            if self.board[i][col].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break
    
        if consecutiveCount >= 4:
            fourInARow = True
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]
    
        return fourInARow
    
    def horizontalCheck(self, row, col):
        fourInARow = False
        consecutiveCount = 0
        
        for j in range(col, 7):
            if self.board[row][j].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break

        if consecutiveCount >= 4:
            fourInARow = True
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]

        return fourInARow
    
    def diagonalCheck(self, row, col):
        fourInARow = False
        count = 0
        slope = None

        # check for diagonals with positive slope
        consecutiveCount = 0
        j = col
        for i in range(row, 6):
            if j > 6:
                break
            elif self.board[i][j].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break
            j += 1 # increment column when row is incremented
            
        if consecutiveCount >= 4:
            count += 1
            slope = 'positive'
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]

        # check for diagonals with negative slope
        consecutiveCount = 0
        j = col
        for i in range(row, -1, -1):
            if j > 6:
                break
            elif self.board[i][j].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break
            j += 1 # increment column when row is decremented

        if consecutiveCount >= 4:
            count += 1
            slope = 'negative'
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]

        if count > 0:
            fourInARow = True
        if count == 2:
            slope = 'both'
        return fourInARow, slope
    
    def findFours(self):
        """ Finds start i,j of four-in-a-row
            Calls highlightFours
        """
    
        for i in range(6):
            for j in range(7):
                if self.board[i][j] != ' ':
                    # check if a vertical four-in-a-row starts at (i, j)
                    if self.verticalCheck(i, j):
                        self.highlightFour(i, j, 'vertical')
                    
                    # check if a horizontal four-in-a-row starts at (i, j)
                    if self.horizontalCheck(i, j):
                        self.highlightFour(i, j, 'horizontal')
                    
                    # check if a diagonal (either way) four-in-a-row starts at (i, j)
                    # also, get the slope of the four if there is one
                    diag_fours, slope = self.diagonalCheck(i, j)
                    if diag_fours:
                        self.highlightFour(i, j, 'diagonal', slope)
    
    def highlightFour(self, row, col, direction, slope=None):
        """ Realça os quatro em linha vencedores com negrito utilizando códigos ANSI """
        bold_start = "\033[1m"
        bold_end = "\033[0m"
        
        if direction == 'vertical':
            for i in range(4):
                self.board[row+i][col] = bold_start + self.board[row+i][col].upper() + bold_end
        
        elif direction == 'horizontal':
            for i in range(4):
                self.board[row][col+i] = bold_start + self.board[row][col+i].upper() + bold_end
        
        elif direction == 'diagonal':
            if slope == 'positive' or slope == 'both':
                for i in range(4):
                    self.board[row+i][col+i] = bold_start + self.board[row+i][col+i].upper() + bold_end
            elif slope == 'negative' or slope == 'both':
                for i in range(4):
                    self.board[row-i][col+i] = bold_start + self.board[row-i][col+i].upper() + bold_end
        else:
            print("Error - Cannot enunciate four-of-a-kind")

    
    def printState(self):
        # cross-platform clear screen
        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
        print(u"{0}!".format(self.game_name))
        print("Round: " + str(self.round))

        print("\t  1   2   3   4   5   6   7 ")
        for i in range(5, -1, -1):
            print("\t", end="")
            for j in range(7):
                print("| " + str(self.board[i][j]), end=" ")
            print("|")
        print("\t ――― ――― ――― ――― ――― ――― ―――")

        if self.finished:
            print("Game Over!")
            if self.winner != None:
                print(str(self.winner.name) + " is the winner")
            else:
                print("Game was a draw")
                
    def autoPlay(self, silent=True):
        while not self.finished:
            self.nextMove(silent=silent)

class Player(object):
    """ Player object.  This class is for human players.
    """
    
    type = None # possible types are "Human" and "AI"
    name = None
    color = None
    def __init__(self, name, color):
        self.type = "Human"
        self.name = name
        self.color = color
    
    def move(self, state, silent):
        if not silent:
            print("{0}'s turn.  {0} is {1}".format(self.name, self.color))
        column = None
        while column == None:
            try:
                choice = int(input("Enter a move (by column number): ")) - 1
            except ValueError:
                choice = None
            if 0 <= choice <= 6:
                column = choice
            else:
                print("Invalid choice, try again")
        return column




class AIPlayer_MCTS(Player):
    """ AIPlayer object that extends Player
        The AI algorithm is Monte Carlo Tree Search """
    

    def __init__(self, name, color,iterations, c):
        self.type = "AI"
        self.name = name
        self.color = color
        self.iterations = iterations
        self.c = c
        

    def move(self, state, silent):
            if not silent:
                print("{0}'s turn.  {0} is {1}".format(self.name, self.color))

            mc = MCTS(state, self.iterations, self.c)
            best_move = mc.bestMove(state, self.color)
            return best_move

    
    
class AIPlayer_DT(Player):
    def __init__(self, name, color, difficulty):
        self.type = "AI"
        self.name = name
        self.color = color
        self.difficulty = difficulty
        self.tree = train_tree(difficulty)

    def move(self, state, silent):
        if not silent:
            print(f"{self.name}'s turn. {self.name} is {self.color}")
        
        move = int(predict_from_tree(self.tree, state))

        # Corrigir se a coluna estiver cheia
        valid_columns = [c for c in range(7) if state[5][c] == ' ']
        if move not in valid_columns:
            move = random.choice(valid_columns)

        return move

    







