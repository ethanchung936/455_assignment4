#!/usr/bin/python3
# Set the path to your python3 above

"""
Cmput 455 sample code
Written by Cmput 455 TA and Martin Mueller
"""
from gtp_connection import GtpConnection, format_point, point_to_coord, move_to_coord
from board_base import DEFAULT_SIZE, GO_POINT, GO_COLOR
from board import GoBoard
from board_util import GoBoardUtil
from engine import GoEngine
from mcts import MCTS, TreeNode
import time
import random
import numpy as np
from board_base import (
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    GO_COLOR, GO_POINT,
    PASS,
    MAXSIZE,
    coord_to_point,
    opponent
)


class A4SubmissionPlayer(GoEngine):
    def __init__(self) -> None:
        """
        Starter code for assignment 4
        """
        GoEngine.__init__(self, "Go0", 1.0)
        self.time_limit = 1
        self.MCTS = MCTS()
        
    def reset(self) -> None:
        self.MCTS = MCTS()
        
    def update(self, board: GoBoard, move: str) -> None:
        self.parent = self.MCTS.root
        coord = move_to_coord(move, board.size)
        point = coord_to_point(coord[0], coord[1], board.size) 
        self.MCTS.update_with_move(point)

    def get_move(self, board: GoBoard, color: GO_COLOR) -> GO_POINT:
        """
        Implement for assignment 4
        """
        exploration = 0.5
        heuristic_weight = 1
        
        point = self.MCTS.get_move(board, color, self.time_limit, exploration, heuristic_weight)
        coord = point_to_coord(point, board.size)
        move = format_point(coord)
        self.MCTS.print_pi(board) # TODO: remove this call when done testing
        return move

    def set_time_limit(self, time_limit):
        self.time_limit = time_limit

def run() -> None:
    """
    start the gtp connection and wait for commands.
    """
    board: GoBoard = GoBoard(DEFAULT_SIZE)
    con: GtpConnection = GtpConnection(A4SubmissionPlayer(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
