import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
BOARDWIDTH=8
BOARDHEIGHT=8
SPACESIZE = 50
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)
class ClientChannel(PodSixNet.Channel.Channel):
    def getSpaceClicked(self,mousex, mousey):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if mousex > x * SPACESIZE + XMARGIN and \
                   mousex < (x + 1) * SPACESIZE + XMARGIN and \
                   mousey > y * SPACESIZE + YMARGIN and \
                   mousey < (y + 1) * SPACESIZE + YMARGIN:
                    return (x, y)
        return None
    
    def Network(self,data):
        print data
        
    def Network_fill(self,data):
        x=data['x']
        y=data['y']
        num=data['num']
        print("Fill action received on the server side")
        print("x is: ",x)
        print("y is: ",y)
        gameid=data['gameid']
        movexy=self.getSpaceClicked(x,y)
        self._server.fillBoard(movexy[0],movexy[1],num,gameid,data)
        
    def Network_startnew(self,data):
        gid=data['id']
        self._server.newGame(gid,data)
        
    def Network_quit(self,data):
        gid=data['id']
        self._server.quitGame(gid,data)

    def Close(self):
        self._server.Close(self.gameid)
class OtelloServer(PodSixNet.Server.Server):
    channelClass=ClientChannel
    def __init__(self,*args,**kwargs):
        PodSixNet.Server.Server.__init__(self,*args,**kwargs)
        self.games=[]
        self.queue=None
        self.index=0
    def Connected(self,channel,addr):
        print 'New Connection', channel
        if self.queue==None:
            self.index+=1
            channel.gameid=self.index
            self.queue=Game(channel,self.index)
        else:
            channel.gameid=self.index
            self.queue.player1=channel
            print('Sending the start game action')
            self.queue.player0.Send({"action": "startgame","player": 0,"gameid": self.queue.gameid})
            self.queue.player1.Send({"action": "startgame","player": 1,"gameid": self.queue.gameid})
            self.queue.player0.Send({"action": "yourturn","torf": True})
            self.queue.player1.Send({"action": "yourturn","torf": False})
            self.games.append(self.queue)
            self.queue=None
    
    def fillBoard(self,x,y,num,gameid,data):
        game=[a for a in self.games if a.gameid==gameid]
        game[0].fillBoard(x,y,num,gameid,data)

    def newGame(self,gid,data):
        game=[a for a in self.games if a.gameid==gid][0]
        game.player0.Send({"action": "New"})
        game.player1.Send({"action": "New"})
        
    def Close(self,gameid):
        try:
            game=[a for a in self.games if a.gameid==gameid][0]
            game.player0.Send({"action": "close"})
            game.player1.Send({"action": "close"})
        except:
            pass
        
    def quitGame(self,gid):
        game=[a for a in self.games if a.gameid==gid][0]
        game.player0.Send({"action": "quit"})
        game.player1.Send({"action": "quit"})
        
    def tick(self):
        score0=0
        score1=1
        for game in self.games:
            for x in range(BOARDWIDTH):
                for y in range(BOARDHEIGHT):
                    if game.board[x][y]==0:
                        score0+=1
                    elif game.board[x][y]==1:
                        score1+=1

        if score0+score1 == BOARDWIDTH*BOARDHEIGTH:
            if score0>score1:
                game.player0.Send({"action": "end", "res": "win"})
                game.player1.Send({"action": "end", "res": "lose"})
            
            elif score1>score0:
                game.player0.Send({"action": "end", "res": "lose"})
                game.player1.Send({"action": "end", "res": "win"})

            else:
                game.player0.Send({"action": "end", "res": "tie"})
                game.player1.Send({"action": "end", "res": "tie"})
                    
class Game:
        def isOnBoard(self,x, y):
            return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT

        def isValidMove(self,board, tile, xstart, ystart):
            
            if board[xstart][ystart] != -1 or not self.isOnBoard(xstart, ystart):
                return False

            board[xstart][ystart] = tile

            if tile == 0:
                otherTile = 1
            else:
                otherTile = 0

            tilesToFlip = []
            
            for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
                x, y = xstart, ystart
                x += xdirection
                y += ydirection
                if self.isOnBoard(x, y) and board[x][y] == otherTile:
                    x += xdirection
                    y += ydirection
                    if not self.isOnBoard(x, y):
                        continue
                    while board[x][y] == otherTile:
                        x += xdirection
                        y += ydirection
                        if not self.isOnBoard(x, y):
                            break
                    if not self.isOnBoard(x, y):
                        continue
                    if board[x][y] == tile:
                        while True:
                            x -= xdirection
                            y -= ydirection
                            if x == xstart and y == ystart:
                                break
                            tilesToFlip.append([x, y])

            board[xstart][ystart] = -1
            if len(tilesToFlip) == 0:
                return False
            return tilesToFlip
        

        def makeMove(self,board,tile,xstart, ystart):
            tilesToFlip = self.isValidMove(board, tile, xstart, ystart)

            if tilesToFlip == False:
                return False

            board[xstart][ystart] = tile

            for x, y in tilesToFlip:
                board[x][y] = tile
            return True
    
        def getNewBoard(self):
            board = []
            for i in range(BOARDWIDTH):
                board.append([-1] * BOARDHEIGHT)
            return board

        def __init__(self,player0,currentIndex):
            self.turn=0
            self.gameid=currentIndex
            self.player0=player0
            self.player1=None
            self.board=self.getNewBoard()
            self.board[3][3]=0
            self.board[3][4]=1
            self.board[4][3]=1
            self.board[4][4]=0
            self.score0=0
            self.score1=0
            
        def fillBoard(self,x,y,num,gameid,data):
            if num==self.turn:
                self.turn=0 if self.turn else 1
                self.player1.Send({"action": "yourturn","torf": True if self.turn==1 else False})
                self.player0.Send({"action": "yourturn","torf": True if self.turn==0 else False})
                print("Calling the move function")
                self.makeMove(self.board,self.turn,x,y)
                print("About to send the fill action")
                print("Name of the action is: ", data['action'])
                self.player0.Send({"action": "fill","x": x,"y": y,"n": num})
                self.player1.Send({"action": "fill","x": x,"y": y,"n": num})

address=raw_input("Host:Port (localhost:8000): ")
if not address:
    host, port="localhost", 8000
else:
    host,port=address.split(":")
oServ = OtelloServer(localaddr=(host, int(port)))
while True:
    #oServ.Pump()
    oServ.Pump()
    sleep(0.01)
