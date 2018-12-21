import numpy as np

class Game():
    def __init__(self, player_is_white=True):
        self.colors = ['white', 'black']
        self.pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
        # dicts to translate chess pieces to values and back etc.
        self.to_piece = {k: v for k, v in zip(range(len(self.pieces)), 
                         self.pieces)}
        self.from_piece = {v: k for k, v in self.to_piece.items()}  
        # one state for each grid position, see to_state for details. For RL this will likely be reshaped to vector, and extra states tacked on the end for win, loss, draw.
        self.state = np.ones((8, 8), dtype=np.uint8)*2*len(self.pieces) # unoccupied
        # set up players
        self.P1 = Player(True, player_is_white)
        self.P2 = Player(False, not player_is_white)
        # set up states
        for piece in self.P1.pieces:
            self.state[tuple(piece.pos)] = self.to_state(piece)
        for piece in self.P2.pieces:
            self.state[tuple(piece.pos)] = self.to_state(piece)

    # player 1 pieces = [0,5], player two pieces = [6, 11], unoccupied = 12
    def to_state(self, piece):
        return len(self.pieces) - len(self.pieces)*piece.is_p1 + \
               self.from_piece[piece.__class__.__name__.lower()]

    # returns board notation of given position, exists in ([1,8]x[a,h])
    def to_board_notation(self, pos):
        return (8 - pos[0], chr(ord('a') + pos[1]))

    # gets unicode chesspiece icon for display
    def to_unicode(self, piece):
        return chr(ord('\u2654') + piece.is_white*6 \
                   + from_piece[piece.__class__.__name__.lower()])

    # gets letter for corresponding chesspiece for display
    def to_letter(self, piece):
        if piece.__class__.__name__ == 'Knight':
            icon = 'n'
        else:
            icon = piece.__class__.__name__[0].lower()
        if piece.is_white:
            return icon.upper()
        return icon

    def display_board(self, piece=None, rot=False):
        self.board = np.empty((8, 8), dtype='str')
        self.board[:] = '.'
        for piece in self.P1.pieces:
          # using to_unicode(piece, self.P1.is_white) gives spacing issues in terminal
            self.board[tuple(piece.pos)] = self.to_letter(piece)
        for piece in self.P2.pieces:
            self.board[tuple(piece.pos)] = self.to_letter(piece)

        print('   | {} {} {} {} {} {} {} {}'.
              format(*[chr(ord('a')+i) for i in range(8)]))
        print('-----------------------')
        for i in range(8):
            print('{}  | {} {} {} {} {} {} {} {} |'
                  .format(8 - i, *self.board[i,:]))
        print('-----------------------')


class Player():
    def __init__(self, is_p1, is_white):
        self.is_p1 = is_p1
        self.is_white = is_white
        self.pieces = []
        for i in range(8):
            self.pieces.append(Pawn([1 + 5*self.is_p1, i]))
        self.pieces.append(Rook([0 + 7*self.is_p1, 0]))
        self.pieces.append(Rook([0 + 7*self.is_p1, 7]))
        self.pieces.append(Knight([0 + 7*self.is_p1, 1]))
        self.pieces.append(Knight([0 + 7*self.is_p1, 6]))
        self.pieces.append(Bishop([0 + 7*self.is_p1, 2]))
        self.pieces.append(Bishop([0 + 7*self.is_p1, 5]))
        self.pieces.append(Queen([0 + 7*self.is_p1, 
                                  3 + (self.is_white ^ self.is_p1)]))
        self.pieces.append(King([0 + 7*self.is_p1, 
                                 4 - (self.is_white ^ self.is_p1)]))
        for piece in self.pieces:
            piece.is_p1 = self.is_p1
            piece.is_white = self.is_white

    # returns list of positions of player's pieces
    def get_positions(self):
        return [piece.pos for piece in self.pieces]

    ''' 
    with_king ensures that when we search the kings available actions, since it must know if an action results in possible attack from another piece, it does not search the opposing kings actions resulting in an infinite loop
    '''
    def get_actions(self, P1, P2, with_king=True):
        actions = []
        for piece in self.pieces:
            if piece.__class__name__.lower() == 'king':
                if with_king:
                    actions+= piece.get_actions(P1,P2)
                else:
                    pass
            else:
                actions+= piece.get_actions(P1,P2)
        return actions
  
class Piece():
    def __init__(self, pos):
        self.is_p1 = True
        self.is_white = True
        self.pos = pos
        self.directions = []

        # mask for available actions based on board position. This is to give unified action space between different pieces. [True, False] for every grid position
        self.action_state = np.zeros((8, 8), dtype=np.uint8)

    # is coordinate on the chessboard
    def is_valid(self, pos):
        return True if 0 <= pos[0] <= 7 and 0 <= pos[1] <= 7 else False

    # generic function that gets actions by moving in the piece direction and adding  positions up to a friendly piece and up to and including an enemy piece. Works for queen, rook, Bishop
    def get_actions(self, P1, P2):
        if self.is_p1:
            player, enemy = P1, P2
        else:
            player, enemy = P2, P1

        actions = []
        player_positions = player.get_positions()
        enemy_positions = enemy.get_positions()

        for direction in self.directions:
            for i in range(1,8):
                new_pos = [self.pos[0] + i*direction[0], 
                          self.pos[1] + i*direction[1]]
                if self.is_valid(new_pos):
                    if new_pos in player_positions:
                        break
                    elif new_pos in enemy_positions:
                        actions.append(tuple(new_pos))
                        break
                    else:
                        actions.append(tuple(new_pos))
        return actions


class King(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), 
                           (1,0), (1,1)]
        self.has_moved = False

    def get_actions(self, P1, P2):
        for (i,j) in self.directions:
            new_pos = (self.pos[0] + i, self.pos[1] + j)
            if self.is_valid(new_pos):
                #todo: if not own piece position
                #todo: if not in enemy positions list, add as available action
                pass 


class Queen(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), 
                           (1,0), (1,1)]


class Rook(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [(-1,0), (0,-1), (0,1), (1,0)]
        self.has_moved = False


class Bishop(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [(-1,-1), (-1,1), (1,-1), (1,1)]


class Knight(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), 
                           (2,-1), (2,1)]
  
    def get_actions(self, P1, P2):
        if self.is_p1:
            player, enemy = P1, P2
        else:
            player, enemy = P2, P1

        actions = []
        for (i, j) in self.directions:
            new_pos = [self.pos[0] + i, self.pos[1] + j]
            if self.is_valid(new_pos):
                if new_pos not in player.get_positions():
                    actions.append(tuple(new_pos))
        return actions

class Pawn(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = (-2*self.is_p1+1, 0)
        self.has_2spaced = False

    def get_actions(self, P1, P2):
        if self.is_p1:
            player, enemy = P1, P2
        else:
            player, enemy = P2, P1
        
        actions = []
        # new forward and diagonal positions
        [new_pos, new_diag_l, new_diag_r] = 
            [[self.pos[0] + self.direction, self.pos[1] + i]
             for i in [0, -1, 1]]

        # moving forward one space
        if self.is_valid(new_pos) and \
           new_pos not in player.get_positions() and \
           new_pos not in enemy.get_positions():
            actions+= new_pos
        
        # taking diagonally
        for new_diag in [new_diag_l, new_diag_r]:
            if self.is_valid(new_pos) and \
               new_diag in enemy.get_positions():
                actions+= new_pos

        # moving 2 spaces on first go
        if self.pos[0] == 1 + 5*self.is_p1:
            #2space logic here
            pass
        elif self.pos[0] == 4 -1*self.is_p1:
            #enpassant logic here
            pass

        
G1 = Game()
G1.P1.pieces.append(Rook([2,2]))
G1.P1.pieces.append(Queen([3,3]))

G1.P2.pieces.append(Rook([3,1]))
G1.P2.pieces[-1].is_p1 = False
G1.P2.pieces[-1].is_white = False
G1.display_board()

print(G1.to_board_notation(G1.P1.pieces[-1].pos),'\n')
actions = G1.P1.pieces[-1].get_actions(G1.P1, G1.P2)
for a in actions:
  print(G1.to_board_notation(a))