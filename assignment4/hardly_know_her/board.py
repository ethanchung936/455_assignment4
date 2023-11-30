"""
board.py
Cmput 455 sample code
Written by Cmput 455 TA and Martin Mueller

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""
#TEST
import numpy as np
from typing import List, Tuple

from board_base import (
    board_array_size,
    coord_to_point,
    is_black_white,
    is_black_white_empty,
    opponent,
    where1d,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    MAXSIZE,
    NO_POINT,
    PASS,
    GO_COLOR,
    GO_POINT,
)


"""
The GoBoard class implements a board and basic functions to play
moves, check the end of the game, and count the acore at the end.
The class also contains basic utility functions for writing a Go player.
For many more utility functions, see the GoBoardUtil class in board_util.py.

The board is stored as a one-dimensional array of GO_POINT in self.board.
See coord_to_point for explanations of the array encoding.
"""
class GoBoard(object):
    def __init__(self, size: int) -> None:
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
        self.reset(size)
        self.black_captures = 0
        self.white_captures = 0
        self.depth = 0
        self.black_capture_history = []
        self.white_capture_history = []
        self.move_history = []

    def add_two_captures(self, color: GO_COLOR) -> None:
        if color == BLACK:
            self.black_captures += 2
        elif color == WHITE:
            self.white_captures += 2
    
    def get_captures(self, color: GO_COLOR) -> None:
        if color == BLACK:
            return self.black_captures
        elif color == WHITE:
            return self.white_captures
    
    def reset(self, size: int) -> None:
        """
        Creates a start state, an empty board with given size.
        """
        self.size: int = size
        self.NS: int = size + 1
        self.WE: int = 1
        self.last_move: GO_POINT = NO_POINT
        self.last2_move: GO_POINT = NO_POINT
        self.current_player: GO_COLOR = BLACK
        self.maxpoint: int = board_array_size(size)
        self.board: np.ndarray[GO_POINT] = np.full(self.maxpoint, BORDER, dtype=GO_POINT)
        self._initialize_empty_points(self.board)
        self.black_captures = 0
        self.white_captures = 0
        self.depth = 0
        self.black_capture_history = []
        self.white_capture_history = []
        self.move_history = []

    def copy(self) -> 'GoBoard':
        b = GoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.last_move = self.last_move
        b.last2_move = self.last2_move
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        b.black_captures = self.black_captures
        b.white_captures = self.white_captures
        b.depth = self.depth
        b.black_capture_history = self.black_capture_history.copy()
        b.white_capture_history = self.white_capture_history.copy()
        b.move_history = self.move_history.copy()
        return b

    def get_color(self, point: GO_POINT) -> GO_COLOR:
        return self.board[point]

    def pt(self, row: int, col: int) -> GO_POINT:
        return coord_to_point(row, col, self.size)

    def is_legal(self, point: GO_POINT, color: GO_COLOR) -> bool:
        """
        Check whether it is legal for color to play on point
        This method tries to play the move on a temporary copy of the board.
        This prevents the board from being modified by the move
        """
        if point == PASS:
            return True
        #board_copy: GoBoard = self.copy()
        #can_play_move = board_copy.play_move(point, color)
        #return can_play_move
        return self.board[point] == EMPTY

    def end_of_game(self) -> bool:
        return self.get_empty_points().size == 0 or (self.last_move == PASS and self.last2_move == PASS)
           
    def get_empty_points(self) -> np.ndarray:
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def row_start(self, row: int) -> int:
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1

    def _initialize_empty_points(self, board_array: np.ndarray) -> None:
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start: int = self.row_start(row)
            board_array[start : start + self.size] = EMPTY

    def play_move(self, point: GO_POINT, color: GO_COLOR) -> bool:
        """
        Tries to play a move of color on the point.
        Returns whether or not the point was empty.
        """
        if self.board[point] != EMPTY:
            return False
        self.board[point] = color
        self.current_player = opponent(color)
        self.last2_move = self.last_move
        self.last_move = point
        O = opponent(color)
        offsets = [1, -1, self.NS, -self.NS, self.NS+1, -(self.NS+1), self.NS-1, -self.NS+1]
        # bcs = []
        # wcs = []
        for offset in offsets:
            if self.board[point+offset] == O and self.board[point+(offset*2)] == O and self.board[point+(offset*3)] == color:
                self.board[point+offset] = EMPTY
                self.board[point+(offset*2)] = EMPTY
                if color == BLACK:
                    self.black_captures += 2
                    # bcs.append(point+offset)
                    # bcs.append(point+(offset*2))
                else:
                    self.white_captures += 2
        #             wcs.append(point+offset)
        #             wcs.append(point+(offset*2))
        # self.depth += 1
        # self.black_capture_history.append(bcs)
        # self.white_capture_history.append(wcs)
        # self.move_history.append(point)
        return True
    
    def undo(self):
        self.board[self.move_history.pop()] = EMPTY
        self.current_player = opponent(self.current_player)
        self.depth -= 1
        bcs = self.black_capture_history.pop()
        for point in bcs:
            self.board[point] = WHITE
            self.black_captures -= 1
        wcs = self.white_capture_history.pop()
        for point in wcs:
            self.board[point] = BLACK
            self.white_captures -= 1
        if len(self.move_history) > 0:
            self.last_move = self.move_history[-1]
        if len(self.move_history) > 1:
            self.last2_move = self.move_history[-2]

    def neighbors_of_color(self, point: GO_POINT, color: GO_COLOR) -> List:
        """ List of neighbors of point of given color """
        nbc: List[GO_POINT] = []
        for nb in self._neighbors(point):
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc

    def _neighbors(self, point: GO_POINT) -> List:
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point: GO_POINT) -> List:
        """ List of all four diagonal neighbors of point """
        return [point - self.NS - 1,
                point + self.NS + 1,
                point - self.NS + 1,
                point + self.NS - 1]

    def last_board_moves(self) -> List:
        """
        Get the list of last_move and second last move.
        Only include moves on the board (not NO_POINT, not PASS).
        """
        board_moves: List[GO_POINT] = []
        if self.last_move != NO_POINT and self.last_move != PASS:
            board_moves.append(self.last_move)
        if self.last2_move != NO_POINT and self.last2_move != PASS:
            board_moves.append(self.last2_move)
        return board_moves

    def full_board_detect_five_in_a_row(self) -> GO_COLOR:
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        Checks the entire board.
        """
        for point in range(self.maxpoint):
            c = self.board[point]
            if c != BLACK and c != WHITE:
                continue
            for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                i = 1
                num_found = 1
                while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
                    i += 1
                    num_found += 1
                i = -1
                while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
                    i -= 1
                    num_found += 1
                if num_found >= 5:
                    return c
        
        return EMPTY
    
    def detect_five_in_a_row(self) -> GO_COLOR:
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        Only checks around the last move for efficiency.
        """
        if self.last_move == NO_POINT or self.last_move == PASS:
            return EMPTY
        c = self.board[self.last_move]
        for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            i = 1
            num_found = 1
            while self.board[self.last_move + i * offset[0] * self.NS + i * offset[1]] == c:
                i += 1
                num_found += 1
            i = -1
            while self.board[self.last_move + i * offset[0] * self.NS + i * offset[1]] == c:
                i -= 1
                num_found += 1
            if num_found >= 5:
                return c
        
        return EMPTY

    def is_terminal(self):
        """
        Returns: is_terminal, winner
        If the result is a draw, winner = EMPTY
        """
        winner = self.detect_five_in_a_row()
        if winner != EMPTY:
            return True, winner
        elif self.get_captures(BLACK) >= 10:
            return True, BLACK
        elif self.get_captures(WHITE) >= 10:
            return True, WHITE
        elif self.end_of_game():
            return True, EMPTY
        else:
            return False, EMPTY

    def heuristic_eval(self):
        """
        Returns: a very basic heuristic value of the board
        Currently only considers captures
        """
        if self.current_player == BLACK:
            return (self.black_captures - self.white_captures) / 10
        else:
            return (self.white_captures - self.black_captures) / 10

    def state_to_str(self):
        state = np.array2string(self.board, separator='')
        state += str(self.current_player)
        state += str(self.black_captures)
        state += str(self.white_captures)
        return state

    def compute_confront_heuristic(self, point, color):
        player_heuristic = self.heuristic_lines(point, color) + self.capture_heuristic(point, color)
        opp_heuristic = self.heuristic_lines(point, opponent(color)) + self.capture_heuristic(point, opponent(color))
        beta = 1/6
        # print(f"player: {player_heuristic} | opp: {opp_heuristic}")
        heuristic =  (beta * player_heuristic) + (((1-beta) * opp_heuristic) / 10) 
        return heuristic

    def heuristic_lines(self, point, color):
        """ point: point on board where we start check from
            color: color whose heuristic we are evaluating for
        """
        heuristic = 0
        count = 1
        opp_color = opponent(color)
        neighbors = self._neighbors(point)
        for i, nb in enumerate(neighbors):
            #Checks neighbors from W-E and N-S
            if i % 2 == 0:
                #Reset count after checking EW and NS
                if count > 1:
                    heuristic += self.compute_line_heuristic(count, decay, closed)
                    # print(self.compute_line_heuristic(count, decay, closed))
                count = 1
                closed = 0
                decay = 1
            neighbor = nb
            while self.board[neighbor] == color:
                count += 1
                if count == 5:
                    break
                neighbor = self._neighbors(neighbor)[i]
            if self.board[neighbor] != EMPTY:
                closed += 1
            elif self.board[neighbor] == EMPTY and count < 4:
                neighbor = self._neighbors(neighbor)[i]
                #Check for decay
                if neighbor == opp_color:
                    decay = 0.9 
                elif self.board[neighbor] == color:
                    decay = 0.9
                    while self.board[neighbor] == color:
                        count += 1
                        neighbor = self._neighbors(neighbor)[i]
                        if count >= 5:
                            count -= 1
                            break
                    if self.board[neighbor] != EMPTY:
                        closed += 1
        
        if count > 1:
            # print(self.compute_line_heuristic(count, decay, closed))
            heuristic += self.compute_line_heuristic(count, decay, closed)

        #Diagonals
        count = 1
        neighbors = self._diag_neighbors(point)
        for i, nb in enumerate(neighbors):
            #Checks neighbors from W-E and N-S
            if i % 2 == 0:
                #Reset count after checking EW and NS
                if count > 1:
                    heuristic += self.compute_line_heuristic(count, decay, closed)
                    # print(self.compute_line_heuristic(count, decay, closed))
                count = 1
                closed = 0
                decay = 1
            neighbor = nb
            while self.board[neighbor] == color:
                count += 1
                if count == 5:
                    break
                neighbor = self._diag_neighbors(neighbor)[i]
            if self.board[neighbor] != EMPTY:
                closed += 1
            elif self.board[neighbor] == EMPTY and count < 4:
                neighbor = self._diag_neighbors(neighbor)[i]
                #Check for decay
                if neighbor == opp_color:
                    decay = 0.9 
                elif self.board[neighbor] == color:
                    decay = 0.9
                    while self.board[neighbor] == color:
                        count += 1
                        neighbor = self._diag_neighbors(neighbor)[i]
                        if count >= 5:
                            count -= 1
                            break
                    if self.board[neighbor] != EMPTY:
                        closed += 1
        
        if count > 1:
            # print(self.compute_line_heuristic(count, decay, closed))
            heuristic += self.compute_line_heuristic(count, decay, closed)
        return heuristic

    def compute_line_heuristic(self, count, decay, closed):
        # print(f"count: {count} | decay: {decay} | closed: {closed}")
        if count >= 5:
            return 10 ** 5
        elif closed == 0:
            return (10 ** count) * decay
        elif closed == 1 and count != 2:
            return (10 ** (count - 1)) * decay
        else:
            return 0
        
    def capture_heuristic(self, point, color):
        heuristic = 0
        captures = 0
        O = opponent(color)
        offsets = [1, -1, self.NS, -self.NS, self.NS+1, -(self.NS+1), self.NS-1, -self.NS+1]
        for offset in offsets:
            if self.board[point+offset] == O and self.board[point+(offset*2)] == O and self.board[point+(offset*3)] == color:
                captures += 2

        if captures > 0:
            heuristic += self.compute_capture_heuristic(color, captures)

        # print(f"capture heuristic:{heuristic}")
        return heuristic

    def compute_capture_heuristic(self, color, new_captures):
        if color == BLACK:
            if new_captures + self.black_captures > 10:
                return 10**5
            else:
                return 10 ** ((self.black_captures + new_captures) / 2)
        else:
            if new_captures + self.white_captures > 10:
                return 10**5
            else:
                return 10 ** ((self.white_captures + new_captures) / 2)
        
        

