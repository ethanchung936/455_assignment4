import cProfile
from board import GoBoard
from gtp_connection import GtpConnection
from Ninuki import A4SubmissionPlayer
import os


#Change the number of games played by the script
def play_game():
    board_size = 7
    time_limit = 10 # Change this value to change the amount of time per move
    num_moves = 10 # Change this value to change the number of moves that are played total
    board: GoBoard = GoBoard(board_size)
    con: GtpConnection = GtpConnection(A4SubmissionPlayer(), board)
    con.timelimit_cmd([time_limit])
    colors = ["b", "w"]
    for i in range(num_moves):
        
        con.genmove_cmd(args=[colors[i%2]])


cProfile.run("play_game()")