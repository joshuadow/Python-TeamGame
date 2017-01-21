###
###          ######    #######  ##     ##  #######  ##    ## ##     ##
###         ##    ##  ##     ## ###   ### ##     ## ##   ##  ##     ##
###         ##        ##     ## #### #### ##     ## ##  ##   ##     ##
###         ##   #### ##     ## ## ### ## ##     ## #####    ##     ##
###         ##    ##  ##     ## ##     ## ##     ## ##  ##   ##     ##
###         ##    ##  ##     ## ##     ## ##     ## ##   ##  ##     ##
###          ######    #######  ##     ##  #######  ##    ##  #######
###
###       Team 21: Josh Dow, Liam Schoepp, Sukhjot Sekhon, Thomas Coderre
###                      CPSC 231 Fall 2015 Group Project
###
### This program generates a Gomoku board in Turtle graphics and allows
### the human to play against a rudimentary AI until the game is won.
###
###     Features:
###         > Saving/loading across sessions using files
###         > Click input for all actions
###         > Keyboard shortcuts for common non-positional actions
###         > Difficulty selection
###
###
###     Game modules required:
###         > gomoku_GUI.py
###         > gomoku_Logic.py
###
###     Images required:
###         > background.gif
###         > welcomeScreen.gif and helpScreen.gif
###         > winMessage.gif and loseMessage.gif
###         > easyDiffDisplay.gif, medDiffDisplay.gif,
###         > hardDiffDisplay.gif and noDiffDisplay.gif
###         > diffSettings.gif and diffWarning.gif
###
###     Creates / uses files:
###         > gomoku_Save.gmk
###

import os
from gomoku_GUI import Visuals
from gomoku_Logic import Logic


#> Initiates game setup and enters mainloop(), which does not end until game close.
def main():
    os.system('cls' if os.name == 'nt' else 'clear') #Clears the terminal window

    #> Initializes the Visuals and Logic instances which will be used throughout.
    graphics = Visuals()
    game = Logic()

    #> Places a reference to the instance of the other class in each instance.
    game.graphics = graphics
    graphics.game = game

    graphics.setupBindings()

    #> First game prep. Must be outside of __init__ in Visuals since it depends
    #  on variables set during __init__ in Logic.
    game.cellSize = graphics.BOARDSIZE / game.dimension
    graphics.drawBoard()
    if game.player == game.comp: #>If the first player is the computer.
            game.computerMove()  # then play that before looping.
    graphics.toggleWelcome()
    graphics.displayTurn()

    graphics.win.mainloop() #> Loops indefinitely, waiting for click or key input


main()