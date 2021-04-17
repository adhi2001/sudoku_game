Project Description:
> This project creates a GUI for sudoku game using 'pygame' library.
All the interface is created using 'pygame' library gui functionalities.

> It uses backtracking algorithm to check every move is valid or not made by the user.
The 'solver.py' file contains all the functions related to solving the puzzle by backtracking

> The puzzle for each game is extracted using web-scrapping of a sudoku website using 'requests' library,
which allows us to send HTTP requests to the website to download information as string data.

> We will parse the information received from the website using 'beautifulsoup4' library,
which allows us to access information related to the sudoku puzzle easily using various ids.
Ids of various data elements can be extracted by Inspect element of the browser to see front end of the page.
And thus all the data related to 9 grids of the puzzle is extracted and stored in a list.

Libraries to be installed:
> numpy
> pygame
> requests
> beautifulsoup4

Steps to install:

# Installing all libraries requirement file as argument
> pip install -r requirements.txt

# OR installing every library individually
> pip install numpy
> pip install pygame
> pip install requests
> pip install beautifulsoup4

Execution of file:
# Only one file needs to be executed
> python3 GUI.py

Input:
# No input from terminal or command line, only using the GUI interface to communicate with the program

Output:
# No important output on the terminal or command line, only displaying coordinates of the selected cell for reference.
# Only major output is the GUI interface on the pygame window to interact with the user

Important Notes:
> Border rendering function of text is not provided in the library and is very difficult to replicate yourself,
thus a code has been referred from the internet that solves this issue by rendering many texts behind the main text with little offsets.
This gives the illusion of the border on texts.
(Source: https://stackoverflow.com/questions/54363047/how-to-draw-outline-on-the-fontpygame#:~:text=Pygame%20doesn't%20support%20this,color%20on%20top%20of%20it.)

> The get_puzzle function is also referred from the internet which uses 'requests' library to send http request to certain sudoku website,
and then extract front end information as string of data.
'beautifulsoup4' library has been used to parsed the string data and extract data using various ids which can be viewed by using Inspect element on the webiste.
(Source: https://github.com/a-plus-coding/sudoku-with-python/blob/master/app_class.py)

> Puzzle is not immediately finished if auto solved is used,
we have to select any cell and press the Return/Enter button on keyboard to finish the game.
This is done so that the user can see the solution of the puzzle after the auto solve without having the game finished in 2 seconds.

Creator:
> Adhiraj Deshmukh
> adhirajdeshmukh2001@gmail.com
> https://github.com/adhi2001







