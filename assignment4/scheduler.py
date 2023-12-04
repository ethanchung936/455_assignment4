import pexpect

#Change the paths here to test different players

player1='hardly_know_her/Ninuki.py'

player2='hardly_know_her/Ninuki.py'

#Change the timeout to test different time limits
#We will use a 60 second timeout for testing your submission
timeout= 1

#Change the number of games played by the script
numGames = 10

explorations = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
heuristics = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
best_e = 0
best_h = 0


win1=0
win2=0
numTimeout=0
draw=0

def getMove(p,color):
    p.sendline('genmove '+color)
    p.expect([pexpect.TIMEOUT,'= [a-z][0-9]','= resign','= pass'])
    if p.after==pexpect.TIMEOUT:
        return 'timeout'
    return p.after.decode("utf-8")[2:]

def playMove(p,color,move):
    p.sendline('play '+color+' '+move)

def setupPlayer(p, best):
    p.sendline('boardsize 7')
    p.sendline('clear_board')
    p.sendline('timelimit {}'.format(timeout))
    if best:
        e = best_e
        h = best_h
    else:
        e = explorations[i]
        h = heuristics[j]
    p.sendline('e_val {}'.format(e))
    p.sendline('h_val {}'.format(h))
    
def setupBasePlayer(p):
    p.sendline('boardsize 7')
    p.sendline('clear_board')
    p.sendline('timelimit {}'.format(timeout))

def playSingleGame(alternative=False):
    if not alternative:
        p1=pexpect.spawn('python3 '+player1,timeout=timeout+1)
        p2=pexpect.spawn('python3 '+player2,timeout=timeout+1)
    else:
        p1=pexpect.spawn('python3 '+player2,timeout=timeout+1)
        p2=pexpect.spawn('python3 '+player1,timeout=timeout+1)
    ob=pexpect.spawn('python3 random_player/Ninuki-random.py')
    setupPlayer(p1, True)
    setupPlayer(p2, False)
    setupBasePlayer(ob)
    result=None
    numTimeout=0
    sw=0
    while 1:
        if sw==0:
            move=getMove(p1,'b')
            if move=='resign':
                result=2
                break
            elif move=='timeout':
                result=2
                break
            playMove(p2,'b',move)
            playMove(ob,'b',move)
        else:
            move=getMove(p2,'w')
            if move=='resign':
                result=1
                break
            elif move=='timeout':
                result=1
                break
            playMove(p1,'w',move)
            playMove(ob,'w',move)
        sw=1-sw
        print(move)
        ob.sendline('gogui-rules_final_result')
        ob.expect(['= black','= white','= draw','= unknown'])
        status=ob.after.decode("utf-8")[2:]
        if status=='black':
            result=1
            break
        elif status=='white':
            result=2
            break
        elif status=='draw':
            result=0
            break
        #else:
        #    assert(status=='unknown')
        
    return result,numTimeout

def playGames(numGames):
    global win1,win2,draw,numTimeout,explorations,heuristics,best_e,best_h
    print("player1:",player1)
    print("player2:",player2)
    for i in range(0,numGames):
        print("Game: ",i+1)
        if(i<numGames/2):
            alter=False
        else:
            alter=True
        result,timeout=playSingleGame(alternative=alter)
        if timeout>0:
            numTimeout+=1
        else:
            if result==0:
                print("draw")
                draw+=1
            else:
                if result==1 and alter==False or result==2 and alter==True:
                    print("player1 wins")
                    win1+=1
                else:
                    assert(result==1 and alter==True or result==2 and alter==False)
                    win2+=1
                    print("player2 wins")

def outputResult():
    print('player1 win {} player2 win {} draw {} (e = {}, h = {}) vs (e = {}, h = {})'.format(win1, win2, draw, best_e, best_h, explorations[i], heuristics[j]))

def saveResult():
    f = open("compare_results.txt", "a")
    f.write("player 1: {} (e = {}, h = {})\n".format(player1, best_e, best_h))
    f.write("player 2: {} (e = {}, h = {})\n".format(player2, explorations[i], heuristics[j]))
    f.write("player 1 wins {}\n".format(win1))
    f.write("player 2 wins {}\n".format(win2))
    f.write("draw {}\n".format(draw))
    f.write("=====================\n")
    f.close()
    
def saveOverall():
    f = open("compare_results.txt", "a")
    f.write("Overall winner: e = {}, h = {}".format(best_e, best_h))
    f.close

f = open("compare_results.txt", "w")
f.close()

global i,j
for i in range(len(explorations)):
    for j in range(len(heuristics)):
        playGames(numGames)
        outputResult()
        saveResult()
        if win2 > win1:
            best_e = explorations[i]
            best_h = heuristics[j]
        win1=0
        win2=0
        numTimeout=0
        draw=0
saveOverall()


