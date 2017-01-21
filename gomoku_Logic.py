import random

#> This class is instantiated in gomoku_Control.py to run the critical operations
#  related to the progression and intialization of the game. 
#> Most game variables are stored as instance variables with this class, 
#  aside from those which are directly related to graphics, which 
#  are stored along with graphical methods in gomoku_GUI.py
class Logic:   
    BLANK = "X"
    NOPATS = []
    EASYPATS = ["XCCCC","CXCCC","CCXCC","XPPPP","PXPPP","PPXPP","XCCCX","XPPPX","XCCC"]
    HARDPATS = ["XCCCC","CCXCC","CXCCC","XPPPP","PXPPP","PPXPP","XPXPP","XCXCC",\
                "XCCCX","XPPPX","XCCC","CXCXC","XPPP","PXPXP"]
                
    #> Initializes instance variables required for the progression of the game.
    #> Randomly selects dimension, scales cellSize to match, assigns player colours.
    #> Converts generalized patterns to game-specific patterns
    def __init__(self):
        self.dimension = random.randrange(10,20)
        self.state = self.stateConstructor()
        self.player = None
        self.human = None
        self.comp = None

        self.welcomeVisible = None # Initialized to "None" for toggleWelcome() logic.
        self.helpVisible = False
        self.diffSetVisible = False
        self.diffWarnVisible = False

        self.diff = 1 # Default difficulty is "easy".
        self.move = 0
        self.winState = False

        self.playerSelector() # Selects the player assignments & who plays first.
        self.playPatterns = self.patternConverter()


    #> Called at the beginning of a (new or loaded) game to prepare for play.
    def initializeNewGame(self, load=False):
        self.graphics.lineman.clear()
        self.graphics.stamper.clear()
        self.graphics.winMan.clear()
        self.graphics.messenger.clear()
        self.graphics.resultMan.clear()

        if not load:
            self.dimension = random.randrange(10,20)
            self.cellSize = int(self.graphics.BOARDSIZE/self.dimension)
            self.playerSelector()
            self.move = 0
            self.graphics.displayMessage(" A  new  game\n has  started!\n")

        if self.welcomeVisible:
            self.graphics.toggleWelcome()
        if self.helpVisible:
            self.graphics.toggleHelp()

        self.winState = False
        self.playPatterns = self.patternConverter()
        
        self.state = self.stateConstructor()
        self.graphics.drawBoard()
        self.graphics.displayTurn()
        self.graphics.displayDiff()

        #> If the first player is the computer, then initiate that move
        if self.player == self.comp:
            self.computerMove()


    #> Creates a 2-D list populated with the str "X" of size dimension.
    #> If the instance was initialized with a preexisting state (i.e. loaded)
    #  this function will simply return that state.
    def stateConstructor(self):
        newState = [""] * self.dimension
        for elem in range(len(newState)):
            newState[elem] = [self.BLANK] * self.dimension
        return newState


    #> Randomly selects the number 0 or 1. If 1, then the human plays first.
    #>> Since black always plays first, this means they are also black.
    #> Sets player, human and comp globals
    def playerSelector(self):
        if random.randrange(2) == 1:
            self.human = "B"
            self.comp = "W"
            self.player = self.human
        else:
            self.human = "W"
            self.comp = "B"
            self.player = self.comp
        #Prints the player assignment to terminal. Primarily for debugging.
        #print("P1:", self.human, "P2:", self.comp) 


    #> Takes the generalized pattern strings and converts them to correspond to
    #  the colour assignments for that game.
    #  Looks up the class variable "HARDPATS", but does not alter it.
    #> Will include difficulty logic for final release
    def patternConverter(self):
        if self.diff == 0:
            selectedPats = self.NOPATS
        elif self.diff <= 2:
            selectedPats = self.EASYPATS
        else:
            selectedPats = self.HARDPATS

        procPatterns = []
        for pattern in selectedPats:
            newPattern = ""
            for letter in pattern:
                if letter == "P":
                    newPattern = newPattern + self.human
                elif letter == "C":
                    newPattern = newPattern + self.comp
                else:
                    newPattern = newPattern + self.BLANK
            procPatterns.append(newPattern)

            # Checks if it is a palindrome; if it isn't, it appends the reversed.
            revPattern = newPattern[::-1] # Clones the string, but in reverse
            if newPattern != revPattern:
                procPatterns.append(revPattern)
        #print(procPatterns) ###DEBUGGING###
        return procPatterns


    #> Checks that the given col and row are within the bounds of the 
    #  boardsize and space they represent is empty. 
    #> Returns True if so, else False
    def isValidInput(self, col, row):
        for inst in [col, row]:
            if inst < 0 or inst > self.dimension-1:
                return False
        if self.state[col][row] != self.BLANK: # Checks that the space is empty
            return False
        else:
            return True

            
    #> Used by checkWin to check if there is a series of 5 pieces in a line.
    #> The line is extrapolated from the col / row of the player piece,
    #  along with the dY and dX (difCol, difRow).
    #> If there is a series of 5, returns a list of form 
    #  [True,start tuple, end tuple]; else, returns a single element list [False].
    def checkLine(self, col, row, difCol,difRow):
        series = 1
        seqStart = "" # Endpoint position placeholders
        seqEnd = ""
        for dir in [-1, 1]: # This negation factor is used to checks both directions
            for next in range (1,self.dimension):
                # Sets the col/row for the next piece to be checked
                nextCol = (col + dir*next*difCol)
                nextRow = (row + dir*next*difRow)

                # If the edge of the board is met, that direction of the series ends
                if nextCol > self.dimension-1 or nextCol < 0\
                or nextRow > self.dimension-1 or nextRow < 0:
                    if dir == -1: # Used for consistent endpoint selection
                        # Assigns a 2-tuple to the col and row of the endpoint
                        seqEnd = (nextCol+difCol, nextRow+difRow)
                    else:
                        seqStart = (nextCol-difCol, nextRow-difRow)
                    break

                # If the next piece doesn't match, that direction of the series ends
                elif self.state[nextCol][nextRow] != self.player:
                    if dir == -1:
                        seqEnd = (nextCol+difCol, nextRow+difRow)
                    else:
                        seqStart = (nextCol-difCol, nextRow-difRow)
                    break

                # If the sequence hasn't ended from either condition, they match.
                else:
                    series = series + 1
                    
        # If the series is exactly 5, then the game is won.
        if series == 5:
            return [True, seqStart, seqEnd]
        else:
            return [False]


    #> Checks to see if the winning condition has been met by the last play by checking
    #  if any of the adjacent 8 spots match the piece just played. If so, check
    #  that line for a series of exactly 5. If the winning condition is met, calls 
    #  setWin() with the coordinates of the winning sequence endpoints.
    def checkWin(self, col, row):
        for checkCol in range(col-1,col+2):
            if checkCol < 0 or checkCol > self.dimension-1:
                continue
                
            for checkRow in range(row-1,row+2):
                # Avoids checking out of bound indices
                if checkRow < 0 or checkRow > self.dimension-1:
                    continue
                # Avoids checking the spot corresponding to the played piece
                elif checkCol == col and checkRow == row:
                    continue
                # Moves on if the pieces don't match.
                elif self.state[checkCol][checkRow] != self.player:
                    continue
                    
                else: # If this runs, the pieces being compared match.
                    # Col/row difference between the pieces; used to traverse the line
                    difCol = checkCol - col
                    difRow = checkRow - row
                    result = self.checkLine(col, row, difCol, difRow)
                    if result[0]:
                        return [result[1], result[2]]


    #> Runs each time the computer needs to make a move. Makes the decision,
    #  checks if the input is valid, places the piece and updates the game state variable.
    def computerMove(self):
        if self.diff == 0: # If AI is off, don't play at all.
            self.player = self.human
            return

        compEle = self.decisionMaker()
        compCol = compEle[0]
        compRow = compEle[1]
        colPos = compCol * self.cellSize # Converts indices to coordinates
        rowPos = compRow * self.cellSize
        
        self.graphics.stampPiece(colPos,rowPos)
        self.state[compCol][compRow] = self.player
        winResult = self.checkWin(compCol, compRow)
        if winResult != None:
            self.graphics.setWin(winResult[0], winResult[1])
        self.player = self.human


    #> Converts the x or y position of a click to the index of a col/row list.
    #> Finds the "base" col / row of the click using integer division,
    #  then checks if the click is greater than half way between nodes.
    #> If so, the variable will be set to that "next" value.
    def clickPosToIndex(self, pxVal):
        indxVal = int(pxVal // self.cellSize)
        if pxVal % self.cellSize >= self.cellSize/2:
            indxVal += 1
        return indxVal


    #> Checks if the user's choice is valid,
    #  updates the game state variable and initiates the computer's move.
    def moveAlternator(self,xPos,yPos):
        humanCol = self.clickPosToIndex(xPos)
        humanRow = self.clickPosToIndex(yPos)

        if not self.isValidInput(humanCol,humanRow):
            self.graphics.displayMessage("   You  cannot\n    place  your\n   piece there")
            return

        humanXPos = humanCol * self.cellSize
        humanYPos = humanRow * self.cellSize


        self.move = self.move + 1
        self.graphics.displayTurn() #Redraws the turn counter
        self.graphics.stampPiece(humanXPos, humanYPos)
        self.state[humanCol][humanRow] = self.player

        winResult = self.checkWin(humanCol, humanRow)
        if winResult != None:
            self.graphics.setWin(winResult[0], winResult[1])

        if not self.winState: # If the player just won, the computer shouldn't play
            self.player = self.comp
            self.computerMove()


    #Traverses the 2D state list and returns a list containing strings which
    #represent all horizontal lines. It also returns a list with the col/row indices
    #of every element in each string. The indices for both lists are related.
    #e.g. The position of ele 3 in line 1 can be obtained by: horiPosList[0][2]
    def horiLines(self):
        horiList = []
        horiPosList = []

        for row in range(len(self.state)):
            horiString = ""
            horiPosList.append([])
            for col in range(len(self.state[0])):
                horiString = horiString + self.state[col][row]
                horiPosList[row].append([col,row])
            horiList.append(horiString)

        return horiList, horiPosList


    #Traverses the 2D state list and returns a list containing strings which
    #represent all vertical lines. It also returns a list with the col/row indices
    #of every element in each string. The indices for both lists are related.
    #e.g. The position of ele 3 in line 1 can be obtained by: vertPosList[0][2]
    def vertLines(self):
        vertList = []
        vertPosList = []

        for col in range(len(self.state[0])):
            vertString = ""
            vertPosList.append([])
            for row in range(len(self.state)):
                vertString = vertString + self.state[col][row]
                vertPosList[col].append([col,row])
            vertList.append(vertString)

        return vertList, vertPosList


    #This function is NOT pure. It appends to both diagList and diagPosList
    #This is intentional since the "old" lists are never used again.
    #It improves readability and enables easier updating of diagPosList.
    #It also minimizes the logic required to avoid strings of len < 5.
    #Returns: None
    #Parameters:
    # 3 ints: col & row of starting position, diag direction (-1 or 1)
    # 2 lists: diagList: contains state strings
    #          diagPosList: contains the positions of each element in those strings
    def diagWalker(self, col, row, diag, diagList, diagPosList):
        valid = True
        diagString = ""
        tempPosList = []
        while valid:
            diagString = diagString + self.state[col][row]
            tempPosList.append([col,row])

            col = col + 1
            row = row + diag
            if col not in range(self.dimension) or row not in range(self.dimension):
                valid = False

        if len(diagString) >= 5:
                diagList.append(diagString)
                diagPosList.append(tempPosList)


    #Traverses the 2D state list and returns a list containing strings which
    #represent all diagonal lines longer than 4. Returns a list with the col/row indices
    #of every element in each string. The indices for both lists are related.
    #e.g. The position of ele 3 in line 1 can be obtained by: vertPosList[0][2]
    def diagLines(self):
        diagList = []
        diagPosList = []
        for diag in [-1,1]: # Checks both diagonals
            # Aligns the starting point of the walker to the correct row
            if diag == -1: # If subtracting rows, run along the top; else, bottom.
                baseRow = self.dimension - 1
            else:
                baseRow = 0

            for vert in range(self.dimension):
                self.diagWalker(0, vert, diag, diagList, diagPosList)

            for hori in range(1,self.dimension):
                self.diagWalker(hori, baseRow, diag, diagList, diagPosList)

        return diagList, diagPosList

        
    #> Checks if either of the two spots on either side of the choice
    #  are filled.
    #> If at least one is, then that is the element which will be chosen.
    #> This avoids placing something at the "wrong place" in the pattern.
    def isAdjFilled(self, eleIndx, line):
        for adjIndx in range(eleIndx-1,eleIndx+2, 2):
            if 0 > adjIndx <= len(line): 
                continue
        
            adjString = line[eleIndx] + line[adjIndx]
            if adjString == self.BLANK*2:
                continue
        
            return True
            
            
    #> This function will return the index of the playable spot in the line where
    #  a pattern was found. If multiples are found, it selects the first one.
    #> If the pattern which is passed is not found in "line", or if the pattern 
    #  does not have an adjacent blaknk/player,a ValueError will be thrown 
    #  by lookUpPatterns.
    def elementChoice(self, pattern, line):
        firstIndx = line.index(pattern) # Looks for the index of the start of the pattern
        lastIndx = firstIndx + len(pattern) # Calculates the first index after the pattern
        
        initEleChoices = []
        for eleIndx in range(firstIndx, lastIndx):
            if line[eleIndx] == self.BLANK:
                if self.isAdjFilled(eleIndx, line):
                    return eleIndx
        

    #> The entire board is deconstructed into strings which represent a complete
    #  vertical, horizontal or diagonal line. These strings are iterated through,
    #> looking for linear patterns on the board to find the playable moves.
    #> Patterns are ranked and so a single col/row pair is returned as a list.    
    def lookUpPatterns(self):
        vertList, vertPosList = self.vertLines()
        horiList, horiPosList = self.horiLines()
        diagList, diagPosList = self.diagLines()

        stringList = vertList + horiList + diagList
        posList = vertPosList + horiPosList + diagPosList

        # Looks for each pattern in each line. If found, calls elementChoice
        # with the matched strings to find the index of a playable (blank) spot.
        # Appends the coordinates, along with the pattern index (rank), to a list.
        choices = []
        for lineIndx in range(len(stringList)):
            lineStr = stringList[lineIndx]
            for patternIndx in range(len(self.playPatterns)):
                patternStr = self.playPatterns[patternIndx]
                if patternStr in lineStr:
                    selIndx = self.elementChoice(patternStr, lineStr)
                    selElem = posList[lineIndx][selIndx] # Returns col/row list.
                    choices.append([patternIndx, selElem])

        choices.sort() # Sorted so the "best" (lowest pattern index) is first.
        # Chooses the coordinates for the first entry in choice
        choice = []
        if len(choices) != 0:
            # Chooses randomly if on "easy", otherwise chooses the "best".
            if self.diff == 1:
                selChoice = random.randrange(len(choices))
            else:
                selChoice = 0
            choice = choices[selChoice][1] # Sets choice to the col/row list
        return choice # Returns the lowest (i.e. best) choice


    #> Parameter; two 2D lists containing the col/row of player/computer pieces.
    #  The selected element to play near is the first in the list,
    #  therefore, the list compPieces should have the "best" piece first.
    def pseudoRandomPlay(self, playerPieces, compPieces):
        if len(compPieces) == 0:
            if len(playerPieces) != 0:
                startCol = playerPieces[0][0]
                startRow = playerPieces[0][1]
            else:
                startCol = self.dimension//2
                startRow = self.dimension//2
                return startCol, startRow
        else:
            startCol, startRow = self.minDistanceFromPlayer(playerPieces, compPieces)

        for check in range(30): # Gets 30 attempts to find a solution, else random
            pseudoRandRow = startRow + random.randrange(-1,2) # rand in [-1,0,1]
            pseudoRandCol = startCol + random.randrange(-1,2,2) # rand in [-1,1]
            if self.isValidInput(pseudoRandCol, pseudoRandRow):
                return [pseudoRandCol, pseudoRandRow]
            if check >= 20: # If that seed isn't working, try another.
                startCol = compPieces[0][0]
                startRow = compPieces[0][1]

        # This block only runs if no viable solution is found in 20 tries.
        randCol = random.randrange(self.dimension)
        randRow = random.randrange(self.dimension)
        return [randCol, randRow]


    #> Different function to determine the position of the computer piece
    #  which is closest to any player piece. Does not consider relative orientation
    #  since it just takes the sum of the col/row differences.
    def minDistanceFromPlayer(self, playerPieces, compPieces):
        distances = []
        for pPiece in range(len(playerPieces)):
            distances.append([])
            for cPiece in range(len(compPieces)):
                dCol = abs(playerPieces[pPiece][0] - compPieces[cPiece][0])
                dRow = abs(playerPieces[pPiece][1] - compPieces[cPiece][1])
                dSum = dCol + dRow
                distances[pPiece].append(dSum)

        lowVal = 100
        lowPos = [0,0]
        for i in range(len(playerPieces)):
            for j in range(len(compPieces)):
                if distances[i][j] < lowVal:
                    lowVal = distances[i][j]
                    lowPos = compPieces[j]
        return lowPos[0], lowPos[1]


    #> Iterates through self.state to find all of the positions which hold
    #  either a computer or human piece. It appends the coordinates into a list
    #  for either player.
    #> Returns: Two 2D lists where each top element is a list with the row/col
    #           of either the computer or human pieces.
    def findPieces(self):
        humanList = []
        compList = []
        for col in range(self.dimension):
            for row in range(self.dimension):
                if self.state[col][row] == self.human:
                    humanList.append([col, row])
                elif self.state[col][row] == self.comp:
                    compList.append([col, row])
        return humanList, compList


    #> Checks if there are any patterns to play off of; if not, uses the
    #  pseudoRandomPlay function to find a spot to play.
    def decisionMaker(self):
        result = self.lookUpPatterns()
        humanPieces, compPieces = self.findPieces()

        if result == []:
            result = self.pseudoRandomPlay(humanPieces, compPieces)
        return result


    #> Saves a file called "Gomokusave.gmk" in the working directory.
    #> The first line stores config variables: winState, move, dimension and human
    #>> Every line after that stores the elements of the 2D array "state".
    #>> No delimiters between elements.
    def saveGame(self):
        if self.winState:
            self.graphics.displayMessage("clear")
            self.graphics.displayMessage("  You  cannot\n     save  this\n ended  game")
            return
            
        saved = open("gomoku_Save.gmk","w")
        configSave = "move,"+str(self.move)+";dimension,"+str(self.dimension)+\
                     ";human,"+str(self.human)+";diff,"+str(self.diff)+"\n"
        saved.write(configSave)

        # Iterates through each row of the state list, accumulates the elements
        # in each col into a string, then writes that string to the file.
        for row in range(self.dimension):
            printedLine = ""
            for col in range(self.dimension):
                printedLine = printedLine + self.state[col][row]
            saved.write(printedLine+"\n")
        saved.close()
        self.graphics.displayMessage("  Game  Saved\n")


    #> Interprets the config line passed by loadGame() and clears previous game info.
    def loadConfig(self,config):
        if self.welcomeVisible: # First closes the welcome screen if it is open.
            self.graphics.toggleWelcome()

        config = config[:len(config)-1] # Removes the newline characters.
        pairs = config.split(";") #> Puts the var/value pairs in a list.
        for entry in range(len(pairs)):
            # Separates the var/values and places them in a nested list
            pairs[entry] = pairs[entry].split(",")
            var = pairs[entry][0]
            val = pairs[entry][1]

            # Checks which var it is and executes the appropriate code.
            if var == "dimension":
                self.dimension = int(val)
                self.cellSize = self.graphics.BOARDSIZE/self.dimension
            elif var == "move":
                self.move = int(val)
                self.graphics.displayTurn()
            elif var == "diff":
                self.diff = int(val)
                self.graphics.displayDiff()
            elif var == "human":
                if val == "B":
                    self.human = "B"
                    self.comp = "W"
                else:
                    self.human = "W"
                    self.comp = "B"
                # Human will always have be first since the comp is "instant".
                self.player = self.human

                
    #> Looks for the file "Gomokusave.gmk" and tries to load a previous save.
    #> If the file is not found, an error message displays in the Turtle window.
    def loadGame(self):
        try:
            loaded = open("gomoku_Save.gmk","r")

            config = loaded.readline() # Reads the config line.
            self.loadConfig(config) # Parses the config line and performs setup.
            self.initializeNewGame("load")

            row = 0 # Sets up an accumulator to count the row the file line represents.
            for line in loaded:
                line = line[:len(line)-1] # Removes the newline characters.
                for col in range(len(line)):
                    ele = line[col]
                    # Places the value of the line entry into the state list.
                    self.state[col][row] = ele
                    if ele != self.BLANK: # If it is blank it must be a player's.
                        # Sets the player var so the correct piece is stamped.
                        self.player = ele
                        colPos = col * self.cellSize
                        rowPos = row * self.cellSize
                        self.graphics.stampPiece(colPos, rowPos)
                row += 1

            loaded.close()
            self.player = self.human # Since the computer takes almost no time to move.
            self.graphics.displayMessage("Game  Loaded\n")

        except IOError:
            self.graphics.displayMessage("  No  save  file\n   was  found!\n")

            
    #> Uses the y value of the click to determine which button is being pressed.
    #> Executes the code corresponding to each button.
    def buttonSelector(self, x, y):
        # Absolute reference for relative bounds.
        boxExit = [585,635]
        boxNew = [boxExit[0]-60,boxExit[1]-60]
        boxLoad = [boxNew[0]-60,boxNew[1]-60]
        boxSave = [boxLoad[0]-60,boxLoad[1]-60]
        boxEasy = [boxSave[0]-145, boxSave[1]-170]
        boxMed = [boxEasy[0]-35, boxEasy[1]-35]
        boxHard = [boxMed[0]-35, boxMed[1]-35]
        boxWarn = [boxHard[0]-45,boxHard[1]-35]
        boxDiff = [boxWarn[0]-60,boxWarn[1]-45]
        boxHelp = [boxDiff[0]-60,boxDiff[1]-60]

        # Creates a 2D list containing all the buttons' y-bounds
        buttons = [boxExit, boxNew, boxLoad, boxSave, boxEasy, boxMed,\
                    boxHard, boxWarn, boxDiff, boxHelp]

        for box in buttons:
            if box[0] < y < box[1]: # If the click is in the given y-bounds.
                if box is boxExit:
                    exit()
                elif box is boxNew:
                    self.initializeNewGame()
                elif box is boxLoad:
                    self.loadGame()
                elif box is boxSave:
                    self.saveGame()
                elif box is boxEasy and self.diffSetVisible:
                    self.newDiff = 1
                    self.graphics.toggleDiffWarning()
                elif box is boxMed and self.diffSetVisible:
                    self.newDiff = 2
                    self.graphics.toggleDiffWarning()
                elif box is boxHard and self.diffSetVisible:
                    self.newDiff = 3
                    self.graphics.toggleDiffWarning()
                elif box is boxWarn and self.diffWarnVisible:
                    self.graphics.diffConfirmation(x)
                elif box is boxDiff:
                    self.graphics.toggleDiffSettings()
                elif box is boxHelp:
                    self.graphics.toggleHelp()


    #> Accepts click coordinates, determines which area of the board it's in
    #  (i.e. sidebar or gameboard) and passes the input to the correct function.
    def sectionSelector(self, x,y):
        x -= self.graphics.OFFSETX
        y -= self.graphics.OFFSETY
        
        if x > -50 and not self.winState: # If the click is on the game board
            self.graphics.displayMessage("clear") # Avoids message board mess.
            
            if self.welcomeVisible: # If the welcome screen is open
                self.graphics.toggleWelcome()
            elif self.helpVisible: # If the help screen is open
                self.graphics.toggleHelp()
            elif self.player == self.human: # Avoids playing during comp turn.
                self.moveAlternator(x,y)

        elif x <= -70: # If the click is in info sidebar area
            self.buttonSelector(x, y)