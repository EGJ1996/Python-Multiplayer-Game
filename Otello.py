import random, sys,pygame,time,copy
from pygame.locals import *
import math
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
FPS=10
WINDOWWIDTH=640
WINDOWHEIGHT=480
SPACESIZE=50
BOARDWIDTH=8
BOARDHEIGHT=8
WHITE_TILE='WHITE_TILE'
BLACK_TILE='BLACK_TILE'
EMPTY_SPACE='EMPTY_SPACE'
HINT_TILE='HINT_TILE'
ANIMATIONSPEED=25
XMARGIN=int((WINDOWWIDTH-(BOARDWIDTH*SPACESIZE)/2))
YMARGIN=int((WINDOWHEIGHT-(WINDOWHEIGHT*SPACESIZE)/2))
WHITE=(255,255,255)
BLACK=(0,0,0)
GREEN=(0,155,0)
BRIGHTBLUE=(0,50,255)
BROWN=(174,94,0)
TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN

class Otello(ConnectionListener):
    def Network_close(self):
        exit()
    def Network_startGame(self):
        self.running=True
        self.gameid=data['gameid']
        self.num=data['player']
    def Network_yourturn(self,data):
        self.turn=data['torf']
    def Network_gameEnded(self,data):
        s0=data['score0']
        s1=data['score1']
    def Network_close(self,data):
        exit()
    def Network_move(self,data):
        x=data['x']
        y=data['y']
        self.MAINCLOCK.tick(FPS)
        pygame.display.update()
        self.makeMove(self.board, self.Tile, movexy[0], movexy[1], True)
        
    # def main(self):
    #   while True:
    #        if self.runGame()==False:
    #           break
    
    def getScoreOfBoard(self):
        # xscore = 0
        # oscore = 0
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.board[x][y] == self.Tile:
                    self.score+=1
                if self.board[x][y] == self.otherTile:
                    self.otherscore+=1
    def __init__(self):
        print('Constructor invoked')
        self.justplaced=10
        self.board=self.getNewBoard()
        # global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE
        pygame.init()
        self.MAINCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Flippy')
        self.FONT = pygame.font.Font('freesansbold.ttf', 16)
        self.BIGFONT = pygame.font.Font('freesansbold.ttf', 32)
        self.boardImage = pygame.image.load('flippyboard.png')
        self.boardImage = pygame.transform.smoothscale(self.boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
        self.boardImageRect = self.boardImage.get_rect()
        self.boardImageRect.topleft = (XMARGIN, YMARGIN)
        self.BGIMAGE = pygame.image.load('flippybackground.png')
        self.BGIMAGE = pygame.transform.smoothscale(self.BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
        self.BGIMAGE.blit(self.boardImage, self.boardImageRect)
        self.newGameSurf = self.FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR2)
        self.newGameRect = self.newGameSurf.get_rect()
        self.newGameRect.topright = (WINDOWWIDTH - 8, 10)
        self.DISPLAYSURF.blit(self.newGameSurf, self.newGameRect)
        self.turn=True
        self.score=0
        self.otherscore=0
        self.Tile=WHITE_TILE
        self.otherTile=BLACK_TILE
        self.drawBoard(self.board)
        self.drawInfo(self.board, self.Tile, self.otherTile)
        self.running=False
        self.num=0
        print('Middle of the constructor')
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
        print "Otello client started"
        print('Ater connecting to server')
        #while not self.running:
            #self.Pump()
            #connection.Pump()
            #sleep(0.1)
        if self.num==0:
            self.turn=True
            self.Tile=WHITE_TILE
            self.otherTile=BLACK_TILE
        else:
            self.turn=False
            self.Tile=BLACK_TILE
            self.otherTile=WHITE_TILE
        print('After pumping')
        print('Constructing Ended')
    def runGame(self):
        print('Executing Run')
        self.MAINCLOCK.tick(FPS)
        connection.Pump()
        self.Pump()
        self.resetBoard(self.board)
        self.drawBoard(self.board)
        while True:
            if self.turn:
                movexy=None
                if self.getValidMoves(self.board, self.Tile) == []:
                    break
                while movexy == None:
                    self.checkForQuit()
                    for event in pygame.event.get():
                        print('Event processed')
                        if event.type == MOUSEBUTTONUP:
                            mousex, mousey = event.pos
                            if self.newGameRect.collidepoint( (mousex, mousey) ):
                                return True
                            movexy = self.getSpaceClicked(mousex, mousey)
                            if movexy != None and not isValidMove(self.board, self.Tile, movexy[0], movexy[1]):
                                movexy = None

        if(movexy!=None):
                self.Send({'action': 'fill','x': mousex,'y': mousey, 'num':self.num,'gameid':self.gameid})
        
            
        scores = self.getScoreOfBoard()
        if self.score>self.otherscore:
            text = 'You beat your opponent by %s points! Congratulations!' % \
                   (self.score-self.otherscore)
        elif self.otherscore<self.score:
            text = 'You lost. Your opponent beat you by %s points.' % \
                   (self.otherscore-self.score)
        else:
            text = 'The game was a tie!'

        self.textSurf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
        self.textRect = self.textSurf.get_rect()
        self.textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
        self.DISPLAYSURF.blit(textSurf, textRect)

        self.text2Surf = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
        self.text2Rect = self.text2Surf.get_rect()
        self.text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

        self.yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
        self.yesRect = self.yesSurf.get_rect()
        self.yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

        self.noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
        self.noRect = self.noSurf.get_rect()
        self.noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)
        

        while True:
            self.checkForQuit()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    if yesRect.collidepoint( (mousex, mousey) ):
                        return True
                    elif noRect.collidepoint( (mousex, mousey) ):
                        return False
            self.DISPLAYSURF.blit(self.textSurf, self.textRect)
            DISPLAYSURF.blit(self.text2Surf, self.text2Rect)
            DISPLAYSURF.blit(self.yesSurf, self.yesRect)
            DISPLAYSURF.blit(self.noSurf, self.noRect)
            pygame.display.update()
            MAINCLOCK.tick(FPS)                                
            
                        
    def translateBoardToPixelCoord(self,x, y):
        return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)

    def animateTileChange(self,tilesToFlip, tileColor, additionalTile):
        if tileColor == WHITE_TILE:
            additionalTileColor = WHITE
        else:
            additionalTileColor = BLACK
        additionalTileX, additionalTileY =self.translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
        pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
        pygame.display.update()

        for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
            if rgbValues > 255:
                rgbValues = 255
            elif rgbValues < 0:
                rgbValues = 0

            if tileColor == WHITE_TILE:
                color = tuple([rgbValues] * 3)
            elif tileColor == BLACK_TILE:
                color = tuple([255 - rgbValues] * 3)

            for x, y in tilesToFlip:
                centerx, centery = self.translateBoardToPixelCoord(x, y)
                pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
            pygame.display.update()
            MAINCLOCK.tick(FPS)
            self.checkForQuit()

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
                    pygame.draw.circle(self.DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
                if board[x][y] == HINT_TILE:
                    pygame.draw.rect(self.DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))

    def getSpaceClicked(self,mousex, mousey):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if mousex > x * SPACESIZE + XMARGIN and \
                   mousex < (x + 1) * SPACESIZE + XMARGIN and \
                   mousey > y * SPACESIZE + YMARGIN and \
                   mousey < (y + 1) * SPACESIZE + YMARGIN:
                    return (x, y)
        return None


    def drawInfo(self,board, playerTile, computerTile):
        scores = self.getScoreOfBoard()
        scoreSurf = self.FONT.render("Player Score: %s    Opponent Score: %s" % (str(self.score), str(self.otherscore)), True, TEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
        self.DISPLAYSURF.blit(scoreSurf, scoreRect)

    def resetBoard(self,board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                board[x][y] = EMPTY_SPACE

        board[3][3] = WHITE_TILE
        board[3][4] = BLACK_TILE
        board[4][3] = BLACK_TILE
        board[4][4] = WHITE_TILE

    def getNewBoard(self):
        board = []
        for i in range(BOARDWIDTH):
            board.append([EMPTY_SPACE] * BOARDHEIGHT)

        return board

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

    def isOnBoard(self,x, y):
        return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT

    def getBoardWithValidMoves(self,board, tile):
        dupeBoard = copy.deepcopy(board)

        for x, y in self.getValidMoves(dupeBoard, tile):
            dupeBoard[x][y] = HINT_TILE
        return dupeBoard

    def getValidMoves(self,board, tile):
        validMoves = []

        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.isValidMove(board, tile, x, y) != False:
                    validMoves.append((x, y))
        return validMoves

    def makeMove(self,board, tile, xstart, ystart, realMove=False):

        tilesToFlip = self.isValidMove(board, tile, xstart, ystart)

        if tilesToFlip == False:
            return False

        board[xstart][ystart] = tile

        if realMove:
            animateTileChange(tilesToFlip, tile, (xstart, ystart))

        for x, y in tilesToFlip:
            board[x][y] = tile
        return True

    def checkForQuit(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

ot=Otello()
while True:
    ot.runGame()
    sleep(0.1)
