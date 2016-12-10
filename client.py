import random, sys, pygame, time, copy
from pygame.locals import *
from pygame import gfxdraw
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
SPACESIZE = 50
BOARDWIDTH = 8
BOARDHEIGHT = 8
WHITE_TILE = 'WHITE_TILE'
BLACK_TILE = 'BLACK_TILE'
EMPTY_SPACE = 'EMPTY_SPACE'
HINT_TILE = 'HINT_TILE'
ANIMATIONSPEED = 25
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN

class ClientGame(ConnectionListener):
    def Network_close(self):
        exit()
    def Network_startgame(self,data):
        print('Startgame called')
        self.running=True
        self.gameid=data['gameid']
        self.num=data['player']
        print(self.num)
        if(self.num==0):
            self.Tile=WHITE_TILE
            self.otherTile=BLACK_TILE
        else:
            self.Tile=BLACK_TILE
            self.otherTile=WHITE_TILE
    def Network_yourturn(self,data):
        self.turn=data['torf']
    def Network_gameEnded(self,data):
        s0=data['score0']
        s1=data['score1']
    def Network_close(self,data):
        exit()

    def Network_quit(self,data):
        exit()
    
    def Network_New(self,data):
        self.resetBoard(self.mainBoard)
        self.drawBoard(self.mainBoard)
    def Network_fill(self,data):
        print("Received fill action on the client side")
        x=data['x']
        y=data['y']
        n=data['n']
        if(self.num==n):
            self.makeMove(self.mainBoard,self.Tile,x,y)
        else:
            self.makeMove(self.mainBoard,self.otherTile,x,y)
        self.MAINCLOCK.tick(FPS)
        pygame.display.update()

        
    def main(self):
        print("Main function called")
        pygame.init()
        self.MAINCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Flippy')
        self.FONT = pygame.font.Font('freesansbold.ttf', 16)
        self.BIGFONT = pygame.font.Font('freesansbold.ttf', 32)
        self.turn=True
        self.Tile=WHITE_TILE
        self.otherTile=BLACK_TILE
        self.num=0
        self.Score=0
        self.otherScore=0
        self.gameid=0
        self.boardImage = pygame.image.load('flippyboard.png')
        self.boardImage = pygame.transform.smoothscale(self.boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
        self.boardImageRect = self.boardImage.get_rect()
        self.boardImageRect.topleft = (XMARGIN, YMARGIN)
        self.BGIMAGE = pygame.image.load('flippybackground.png')
        self.BGIMAGE = pygame.transform.smoothscale(self.BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
        self.BGIMAGE.blit(self.boardImage, self.boardImageRect)
        address=raw_input("Address of Server: ")
        try:
            if not address:
                host, port="localhost", 8000
            else:
                host,port=address.split(":")
            self.Connect((host, int(port)))
        except:
            print "Error Connecting to Server"
            print "Usage:", "host:port"
            print "e.g.", "localhost:31425"
            exit()

        while True:
            if self.runGame() == False:
                break
    
    def getScoreOfBoard(self,board):
        s=0
        os=0
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == self.Tile:
                    s += 1
                if board[x][y] == self.otherTile:
                    os += 1
        return (s,os)
                
    def drawInfo(self,board):
        scores = self.getScoreOfBoard(board)
        scoreSurf = self.FONT.render("Your Score: %s    Opponent Score: %s" % (str(scores[0]), str(scores[1])),True, TEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
        self.DISPLAYSURF.blit(scoreSurf, scoreRect)
                
    def translateBoardToPixelCoord(self,x, y):
        return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)
    def getNewBoard(self):
        board = []
        for i in range(BOARDWIDTH):
            board.append([EMPTY_SPACE] * BOARDHEIGHT)

        return board
    
    
    def resetBoard(self,board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                board[x][y] = EMPTY_SPACE
                
        board[3][3] = WHITE_TILE
        board[3][4] = BLACK_TILE
        board[4][3] = BLACK_TILE
        board[4][4] = WHITE_TILE

    def isOnBoard(self,x, y):
        return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT
    
    def isValidMove(self,board, tile, xstart, ystart):
        if board[xstart][ystart] != EMPTY_SPACE or not self.isOnBoard(xstart, ystart):
            return False

        board[xstart][ystart] = tile

        if tile == WHITE_TILE:
            otherTile = BLACK_TILE
        else:
            otherTile = WHITE_TILE

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

        board[xstart][ystart] = EMPTY_SPACE
        if len(tilesToFlip) == 0:
            return False
        return tilesToFlip
    
    def getValidMoves(self,board, tile):
        validMoves = []

        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.isValidMove(board, tile, x, y) != False:
                    validMoves.append((x, y))
        return validMoves
    
    def checkForQuit(self):
        for event in pygame.event.get((QUIT, KEYUP)):
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
    def getSpaceClicked(self,mousex, mousey):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if mousex > x * SPACESIZE + XMARGIN and \
                   mousex < (x + 1) * SPACESIZE + XMARGIN and \
                   mousey > y * SPACESIZE + YMARGIN and \
                   mousey < (y + 1) * SPACESIZE + YMARGIN:
                    return (x, y)
        return None
    
    def makeMove(self,board, tile, xstart, ystart):
        print(xstart,ystart)
        tilesToFlip = self.isValidMove(board, tile, xstart, ystart)

        if tilesToFlip == False:
            return False

        board[xstart][ystart] = tile

        #if realMove:
            #animateTileChange(tilesToFlip, tile, (xstart, ystart))

        for x, y in tilesToFlip:
            board[x][y] = tile
        return True
    
    def runGame(self):
        self.mainBoard = self.getNewBoard()
        self.resetBoard(self.mainBoard)
        self.drawBoard(self.mainBoard)
        
        self.newGameSurf = self.FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR2)
        self.newGameRect = self.newGameSurf.get_rect()
        self.newGameRect.topright = (WINDOWWIDTH - 8, 10)

        while True:
            if self.getValidMoves(self.mainBoard, self.Tile) == []:
                break
            movexy = None
            while movexy == None:
                self.checkForQuit()
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONUP:
                        mousex, mousey = event.pos
                        if self.newGameRect.collidepoint( (mousex, mousey) ):
                            self.Send({"action": "startnew","id": self.gameid})
                            return True
                        movexy = self.getSpaceClicked(mousex, mousey)
                        if movexy != None and not self.isValidMove(self.mainBoard, self.Tile, movexy[0], movexy[1]):
                            movexy = None

                self.drawBoard(self.mainBoard)
                self.drawInfo(self.mainBoard)
                self.DISPLAYSURF.blit(self.newGameSurf, self.newGameRect)
                self.MAINCLOCK.tick(FPS)
                connection.Pump()
                self.Pump()
                pygame.display.update()

            print(movexy)
            if(movexy!=None):
                self.Send({"action": "fill","x": mousex,"y": mousey,"num": self.num,"gameid": self.gameid})
        
    def displayNewGameMenu(self,text):
        textSurf = self.FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect = textSurf.get_rect()
        textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
        self.DISPLAYSURF.blit(textSurf, textRect)

        text2Surf = self.BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
        text2Rect = text2Surf.get_rect()
        text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

        yesSurf = self.BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
        yesRect = yesSurf.get_rect()
        yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

        noSurf = self.BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
        noRect = noSurf.get_rect()
        noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)

        while True:
            self.checkForQuit()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    if yesRect.collidepoint( (mousex, mousey) ):
                        self.Send({"action": "startnew", "id": self.gameid})
                        return True
                    elif noRect.collidepoint( (mousex, mousey) ):
                        self.Send({"action": "quit", "id": self.gameid})
                        return False
                    
            self.DISPLAYSURF.blit(textSurf, textRect)
            self.DISPLAYSURF.blit(text2Surf, text2Rect)
            self.DISPLAYSURF.blit(yesSurf, yesRect)
            self.DISPLAYSURF.blit(noSurf, noRect)
            pygame.display.update()
            self.MAINCLOCK.tick(FPS)

    def drawBoard(self,board):
        self.DISPLAYSURF.blit(self.BGIMAGE, self.BGIMAGE.get_rect())
        for x in range(BOARDWIDTH + 1):
            startx = (x * SPACESIZE) + XMARGIN
            starty = YMARGIN
            endx = (x * SPACESIZE) + XMARGIN
            endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
            pygame.draw.line(self.DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
        for y in range(BOARDHEIGHT + 1):
            startx = XMARGIN
            starty = (y * SPACESIZE) + YMARGIN
            endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
            endy = (y * SPACESIZE) + YMARGIN
            pygame.draw.line(self.DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                centerx, centery = self.translateBoardToPixelCoord(x, y)
                if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                    if board[x][y] == WHITE_TILE:
                        tileColor = WHITE
                    else:
                        tileColor = BLACK
                    #pygame.draw.circle(self.DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
                    pygame.gfxdraw.filled_circle(self.DISPLAYSURF,centerx, centery,int(SPACESIZE / 2) - 4,tileColor)
                if board[x][y] == HINT_TILE:
                    pygame.draw.rect(self.DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))

ot=ClientGame()
if __name__=="__main__":
    ot.main()
