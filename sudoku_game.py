import sys
import random
import copy
from PyQt6.QtWidgets import QApplication, QMainWindow,QTableWidget,QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont
from sudoku_ui import Ui_MainWindow


class SudokuGame(QMainWindow):
    # Initializing - Constructor
    def __init__(self):
        # Initializing - The Window
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initializing - Variables
        self.initial_board = [[0]*9 for x in range(9)] # Create a Board of 9x9 for starting position
        self.max_mistakes = 3 # The maximum number of mistakes is referenced to by 3
        self.is_paused = False # The inital pause state is off as the game just started unless was changed by the player
        self.difficulty = None # The initial state of the difficulty is none unless the player changed it to one of the available options
        self.timer = QTimer() # Timer instance from the PyQt Lib.
        self.timer.timeout.connect(self.update_time) # Every time the timer completes a cycle, automatically trigger the chosen function
        self.setup_table() # Call for the function setup_table, it handles the creation of the Soduku Table.
        self.connect_buttons() # Call for the function connect_buttons, it activates the buttons and make it connected to other methods
        self.ui.stackedWidget.setCurrentIndex(1) # setting the page to the main menu page
        self.board = [[0]*9 for x in range(9)] # Create a Board of 9x9 for the game
        self.solution = [[0]*9 for x in range(9)] # Create a Board of 9x9 for the solution
        self.notes = [[set() for x in range(9)] for x in range(9)] # Create a note space for each cell
        self.mistakes = 0 # starting mistakes is referenced to by 0
        self.time_seconds = 0 # The starting time is referenced to by 0
        self.move_history = [] # The last board state before the player press the undo button
        self.selected_cell = None # The selected cell by the user is initially nothing
        self.note_mode = False # The inital note state is off as the game just started unless was changed by the player
        self.is_solving = False # Initial Condition for the auto solve button
        self.ui.Title.setReadOnly(True)
    
    # This will disable all the buttons
    def disable_buttons(self):
        self.ui.SodukuTable_2.setEnabled(False)
        self.ui.N1_button_2.setEnabled(False)
        self.ui.N2_button_2.setEnabled(False)
        self.ui.N3_button_2.setEnabled(False)
        self.ui.N4_button_2.setEnabled(False)
        self.ui.N5_button_2.setEnabled(False)
        self.ui.N6_button_2.setEnabled(False)
        self.ui.N7_button_2.setEnabled(False)
        self.ui.N8_button_2.setEnabled(False)
        self.ui.N9_button_2.setEnabled(False)
        self.ui.Erase_button_2.setEnabled(False)
        self.ui.Note_button_2.setEnabled(False)
        self.ui.Undo_button_2.setEnabled(False)
        self.ui.Solve_button_2.setEnabled(False)
    
    # This will enable all the buttons
    def enable_buttons(self):
        self.ui.SodukuTable_2.setEnabled(True)
        self.ui.N1_button_2.setEnabled(True)
        self.ui.N2_button_2.setEnabled(True)
        self.ui.N3_button_2.setEnabled(True)
        self.ui.N4_button_2.setEnabled(True)
        self.ui.N5_button_2.setEnabled(True)
        self.ui.N6_button_2.setEnabled(True)
        self.ui.N7_button_2.setEnabled(True)
        self.ui.N8_button_2.setEnabled(True)
        self.ui.N9_button_2.setEnabled(True)
        self.ui.Erase_button_2.setEnabled(True)
        self.ui.Note_button_2.setEnabled(True)
        self.ui.Undo_button_2.setEnabled(True)
        self.ui.Solve_button_2.setEnabled(True)
    
    # Configuring the Sudoku Table apperance and behavior
    def setup_table(self):
        table = self.ui.SodukuTable_2
        # Make table cells square
        for i in range(9):
            table.setColumnWidth(i, 50)
            table.setRowHeight(i, 44)
    
        # Enable selection
        table.setEnabled(True)

        # Disable Manual editing
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Connect cell click
        table.cellClicked.connect(self.cell_clicked) # This is connected to the method cell_clicked
    
    # Connecting each button to the desired method    
    def connect_buttons(self):
    
    # Welcome page buttons
        self.ui.Play_button.clicked.connect(self.start_game)
        self.ui.Instruction_button.clicked.connect(self.show_instructions)
        self.ui.contact_button.clicked.connect(self.show_contact)
        self.ui.credit_button.clicked.connect(self.show_credits)
        
    # Number buttons (1-9)
        # lambda args: return_value, and we used lambda ('anonymus function as we just want to return a single number)
        self.ui.N1_button_2.clicked.connect(lambda: self.number_clicked(1)) 
        self.ui.N2_button_2.clicked.connect(lambda: self.number_clicked(2))
        self.ui.N3_button_2.clicked.connect(lambda: self.number_clicked(3))
        self.ui.N4_button_2.clicked.connect(lambda: self.number_clicked(4))
        self.ui.N5_button_2.clicked.connect(lambda: self.number_clicked(5))
        self.ui.N6_button_2.clicked.connect(lambda: self.number_clicked(6))
        self.ui.N7_button_2.clicked.connect(lambda: self.number_clicked(7))
        self.ui.N8_button_2.clicked.connect(lambda: self.number_clicked(8))
        self.ui.N9_button_2.clicked.connect(lambda: self.number_clicked(9))
    
    # Control buttons
        self.ui.NewGame_button_2.clicked.connect(self.new_game)
        self.ui.Pause_button_2.clicked.connect(self.toggle_pause)
        self.ui.Erase_button_2.clicked.connect(self.erase_cell)
        self.ui.Note_button_2.clicked.connect(self.toggle_note_mode)
        self.ui.Solve_button_2.clicked.connect(self.auto_solve)
        self.ui.Undo_button_2.clicked.connect(self.undo_move)
        
        button_style = """
            QPushButton {
                background-color: #000000;
                border: 2px solid #888888;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #000000;
                border-style: inset; 
                padding-left: 7px;   
                padding-top: 7px;    
            }
        """
        self.setStyleSheet(button_style)

    # The Game Start Stage - Switching between the Main Menu and the Game Page
    def start_game(self):
        difficulty = self.ui.Level_selection.currentText() # This variable depends on the user choice, whether it is easy, medium or hard and takes whatever text is currently visible

        if difficulty == "Choose Difficulty": # Error Handling - To prevent the user from not choosing any level
            QMessageBox.warning(self, "No Level", "Please select a difficulty level!")
            return # It stops the function right here if the user did not choose a level to play
        self.difficulty = difficulty # It saves the local choice to the class variable, this allows other functions to know the difficulty level chosen
        self.generate_puzzle(difficulty) # The generation of the puzzle depends on the difficulty level and it calls the generate_puzzle function which will create a solved puzzle and 
                                         # delete some numbers based on the level chosen
        self.ui.stackedWidget.setCurrentIndex(0) # Switching the page from Main Menu to the Game Page
        self.timer.start(1000) # Start the timer - 1000ms = 1s (every second the update_time function will now run making the clock on the screen go up)

    # Puzzle Generation Stage - The Backtracking Algorithm
    def generate_puzzle(self, difficulty): 
        # Difficulty was included as an argument because the generation of the puzzle depends on the difficulty level chosen whether it is easy, medium or hard.

        # Generate a complete valid board
        self.solution = [[0]*9 for x in range(9)]
        self.generate_complete_board(self.solution) # This calls the backtracking algorithm function to fill the self.solution list with a perfectly valid, completed Sudoku grid, it must follows the Sudoku RULES

        # Copy to current board
        self.board = copy.deepcopy(self.solution)  # This creates a PHYISCAL CLONE of the solution and names it self.board, deepcopy ensures that the two objects are totally separated in the memory

        # Remove numbers based on difficulty, this is the difficulty setting, using a dictionary, it maps the name to the number
        cells_to_remove = {
            "Easy":25,
            "Medium":45,
            "Hard":65
        }

        self.remove_numbers(cells_to_remove[difficulty]) # using the remove_numbers function, based on the value of the difficulty, the number of cells to be removed will be determined by the dictionary above

        # Ensure the solve button is usable for the new agme
        self.enable_buttons()
        self.ui.Pause_button_2.setEnabled(True)

        # Resetting Stats
        self.mistakes = 0
        self.time_seconds = 0
        self.move_history = []
        self.selected_cell = None
        self.note_mode = False
        self.notes = [[set() for x in range(9)] for x in range(9)]
        self.ui.Note_button_2.setStyleSheet("background-color: rgb(0,0,0);")
        self.ui.Pause_button_2.setStyleSheet("background-color: rgb(0,0,0);")

        # Sve initial board (the starting one)
        self.initial_board = copy.deepcopy(self.board) # It takes a deepcopy of the board right after the numbers were removed, but before the player makes any moves

        # Update ALL displays after implementing changes
        self.update_display()
        self.update_mistakes_display()
        self.update_time_display()

    # Generate a complete valid Sudoku board using backtracking
    def generate_complete_board(self, board):
        # board was included as an argument since we want to manipulate changes on the game board

        # Fill Diagonal 3x3 boxes first (they don't depend on each other) (Top-left, Middle-center, Bottom-right)
        for box in range(0, 9, 3):
            self.fill_box(board, box, box)

        # Fill remaining cells
        self.solve_board(board) # This will solve the remaining boxes as the process became easier after filling the diagonal 3x3 boxes

    # Fill a 3x3 box with random numbers: The goal is to fill a 1D list into a 2D list (sub-grid)
    def fill_box(self, board, row, col): # row and col represent the coordiantes of the 9x9 grid
        # board, row, and col are included as arguments, so the computer can add numbers to the specific row and column in the board
        numbers = list(range(1, 10)) # This is the trial numbers (from 1 to 9)
        random.shuffle(numbers) # Shuffle it to make it in a completely random order

        for i in range(3): # for rows inside the 3x3 box
            for j in range(3): # for columns inside the 3x3 box
                board[row + i][col + j] = numbers[i * 3 + j] # right-hand-side equation will convert the 2D box coordinates into a 1D list index so we can place all shuffled values into the 3x3 box

    # Solve the board using backtracking algorithm  - THIS PART EXPLAINS VERY WELL THE backtracking ALGO
    def solve_board(self, board): # We can call it recursive method
        # Find empty cell
        empty = self.find_empty_cell(board)
        if not empty:
            return True # The puzzles is completed
        
        row, col = empty # Unpacking the tuple into two variables (row and column)

        # Try numbers from 1 to 9
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for num in numbers: # Try every element in that randomed list
            if self.is_valid(board, row, col, num): # checking whether num isn't already in the row,column, and in the 3x3 box to validate the answer
                board[row][col] = num               # tentaively place an answer that fit the rules for now
                
                if self.solve_board(board): # This is the recursive call, if it is true proceed the solving process and if it is wrong do the backtrack trick (go the previous one)
                    return True
                
                # Backtracking
                board[row][col] = 0
        return False # Assume none of the numbers worked for this cell, this tells the previous recursive call to try something else because the chosen path is unsolvable

    # Find an empty cell with value 0
    def find_empty_cell(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return(i,j)
        return None
    
    # Check if the placed number is valid as it follows the three rules of Sudoku (not repeated in the same row, column or 3x3 box)
    def is_valid(self, board, row, col, num):

        # 1) Check row
        if num in board[row]: # Checking each row in the 9x9 grid regardless the column
            return False
        
        # 2) Check column
        if num in [board[i][col] for i in range(9)]: # We added two coordinates because first index is for the row whereas the second one is for the column
            return False
        
        # 3) Check 3x3 box
        box_row, box_col = 3* (row//3), 3* (col//3) # This equation is responisble to snap the position to the nearset corner of the chosen row and col
        for i in range(box_row, box_row + 3): # as we have 3 row in the box
            for j in range(box_col, box_col + 3): # as we have 3 column in the box
                if board[i][j] == num: # here we check each number in the the box whether it is equal to the placed number
                    return False
        return True
    
    # Remove numbers from the board to create a puzzle
    def remove_numbers(self, count):
        # Count is included as an argument as it decides the number of numbers to be deleted from the board
        cells = [(i,j) for i in range(9) for j in range(9)] # This create a list of every possible coordinate on the board of the 81 numbers, so we can remove it from the board
        random.shuffle(cells) # This is used to randomly remove the set 

        # The Erasing Loop
        for i in range(count):
            row, col = cells[i]
            self.board[row][col] = 0
    
    # Update the table display
    def update_display(self):
        table = self.ui.SodukuTable_2
        font_size = 20
        is_bold = True

        # Preparing the table
        for i in range(9): # Looping through every row
            for j in range(9): # Looping throught every column
                item = table.item(i,j) # Get the current cell's object
                if item is None: # if the cell is empty
                    item = QTableWidgetItem() # create a new cell object that can hold data for a single cell
                    table.setItem(i, j, item) # put that object into the table row (i) and column (j)
        
                 # Filled Cell
                if self.board[i][j] != 0:
                    item.setText(str(self.board[i][j]))
                    font_size = 20
                    is_bold = QFont.Weight.Bold

                # Notes
                elif self.notes[i][j]:
                    display_grid = [" " for x in range(9)] # Representing the 3x3 box
                    for n in self.notes[i][j]:
                        display_grid[n-1] = str(n) # 1 at index 0, 2 at index 1 etc...

                    row1 = f"{display_grid[0]} {display_grid[1]} {display_grid[2]}" # 1 2 3
                    row2 = f"{display_grid[3]} {display_grid[4]} {display_grid[5]}" # 4 5 6
                    row3 = f"{display_grid[6]} {display_grid[7]} {display_grid[8]}" # 7 8 9

                    # Display notes in small font
                    notes_text = f"{row1}\n{row2}\n{row3}"
                    item.setText(notes_text)
                    font_size = 9
                    is_bold = QFont.Weight.Normal

                else:
                    item.setText("")

                font = QFont("Arial", font_size)
                font.setWeight(is_bold)
                item.setFont(font)

                # Colors
                if self.initial_board[i][j] != 0:
                    # Original Numbers - Black & Bold
                    item.setForeground(QColor(0, 0, 0))
                    font_size = 20
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) # To prevent the user from editing it

                elif self.board[i][j] != 0:
                    # Check if the entered number matches the solution
                    if self.board[i][j] == self.solution[i][j]:
                        # Correct Number - Blue
                        item.setForeground(QColor(0, 0, 255))
                    else:
                        # Incorrect Number - Red
                        item.setForeground(QColor(255, 0, 0))                          
                else:
                    item.setForeground(QColor(0, 0, 0))  # Also sets text color

                    # Highlight Selected Cell
                if self.selected_cell == (i, j):
                    item.setBackground(QColor(200, 200, 255)) # light Blue
                else:
                    item.setBackground(QColor(255, 255, 255)) # White 
                
                # Center Alignment
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Disabling Auto-Solve Button
        if self.is_board_complete():
            self.ui.Solve_button_2.setEnabled(False)
        else:
            if not getattr(self, 'is_solving', False):
                self.ui.Solve_button_2.setEnabled(True)
                
    # Update the mistakes display
    def update_mistakes_display(self):
        self.ui.Mistakes_Number_2.setText(f"{self.mistakes}/{self.max_mistakes}")

    # Update the time display
    def update_time_display(self):
        minutes = self.time_seconds // 60 # To get total minutes
        seconds = self.time_seconds % 60 # To get total seconds
        self.ui.Time_passed_2.setText(f"{minutes:02d}:{seconds:02d}")

    # Called every second by timer
    def update_time(self):
        if not self.is_paused: # Logically if the game is paused, so is the timer
            self.time_seconds += 1
            self.update_time_display()

    # Handle cell clicks
    def cell_clicked(self, row, col):
        if self.is_paused: # Clicks are unpremitted in the pause game
            return
        
        # Only allow selection of empty cells
        if self.initial_board[row][col] == 0:
            self.selected_cell = (row, col)
            self.update_display()

    # Handle number clicks    
    def number_clicked(self, num):
        if not self.timer.isActive() or self.is_paused or self.selected_cell is None: # Number is placed only when the cell is empty or the game is not paused
            return
        
        row, col =self.selected_cell

        # Can't Modify initial cells
        if self.initial_board[row][col] != 0:
            return
        
        # Save state for undo
        old_val = self.board[row][col]
        old_notes = copy.deepcopy(self.notes[row][col])

        if self.note_mode:
            # Toggle note
            if num in self.notes[row][col]:
                self.notes[row][col].remove(num)
            else:
                self.notes[row][col].add(num)
        else:
            # Place number
            self.board[row][col] = num
            self.notes[row][col].clear() # Clear notes when place number

            # Check if answer is correct
            if self.solution [row][col] != num:
                self.mistakes += 1 # Increase the mistake when the number placed is incorrect
                self.update_mistakes_display()

                if self.mistakes >= self.max_mistakes: # End the game if the number of max mistakes is reached
                    self.update_display()
                    self.game_over(False) # Player lost
                    return
                
            # check if puzzle is complete
            if self.is_board_complete():
                self.update_display()
                self.game_over(True) # Player won
                return
    
        # Save move for undo
        self.move_history.append((row, col, old_val, old_notes))
        
        self.update_display()

    # Erase the selected cell
    def erase_cell(self):
        if not self.timer.isActive() or self.is_paused or self.selected_cell is None:
            return
        
        row, col = self.selected_cell

        # Can't erase inital cells
        if self.initial_board[row][col] != 0:
            return
        
        # Save for undo
        old_val = self.board[row][col]
        old_notes = copy.deepcopy(self.notes[row][col])
        self.move_history.append((row, col, old_val, old_notes))

        self.board[row][col] = 0
        self.notes[row][col].clear()
        self.update_display()

    # Undo Mechanism
    def undo_move(self):
        if not self.move_history or self.is_paused:
            return
        
        row, col, old_val, old_notes = self.move_history.pop() # pop(): This is a specific Python command for lists. It removes the very last item from the list and hands it to the variable
        self.board[row][col] = old_val
        self.notes[row][col] = old_notes
        self.update_display()
    
    # Toggle Note-taking mode
    def toggle_note_mode(self):
        self.note_mode = not self.note_mode

        if self.note_mode:
            self.ui.Note_button_2.setStyleSheet("background-color: rgb(100, 100, 255);")
        else:
            self.ui.Note_button_2.setStyleSheet("background-color: rgb(0, 0, 0);")
    
    # Toggle pause/resume the game
    def toggle_pause(self): # boolean toggle like the one above
        self.is_paused = not self.is_paused # initially the game is on --> self.is_paused = false but once the user click the button it will activiate this line

        if self.is_paused:
            self.timer.stop()
            self.ui.Pause_button_2.setStyleSheet("background-color: rgb(100, 100, 255);")
            self.disable_buttons()
            # Hide board
            for i in range(9):
                for j in range(9):
                    item = self.ui.SodukuTable_2.item(i, j)
                    if item:
                        item.setText('')
                    if self.selected_cell == (i, j):
                        item.setBackground(QColor(255, 255, 255)) 
                    else:
                        item.setBackground(QColor(255, 255, 255)) 
        else:
            self.timer.start(1000)
            self.ui.Pause_button_2.setStyleSheet("background-color: rgb(0, 0, 0);")
            self.enable_buttons()
            self.update_display()

    def new_game(self):    
        if self.is_board_complete():               
            self.reset_game()
            
        else:
            reply = QMessageBox.question(
                    self,
                    'Exit Game',
                    "Are you sure you want to quit to a new game? Your progress will be lost.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                    )
            if reply == QMessageBox.StandardButton.Yes:
                self.reset_game()

            else:
                return

    # Reset game and return to the front page
    def reset_game(self):
        if hasattr(self, 'solve_timer'):
            self.solve_timer.stop()               

        self.is_solving = False
        self.enable_buttons()
        self.ui.stackedWidget.setCurrentIndex(1) # Go to homescreen
        self.is_paused = False # Reset the pause
        self.timer.stop()  # Stop the timer
        self.ui.Level_selection.setCurrentIndex(0) # Reset the level selection
        
    # The automicatlly solving the puzzle mechanism
    def auto_solve(self):
        if self.is_solving:
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Auto Solve")
        msg_box.setText("How would you like to solve the puzzle?")

        # Add custom buttons
        instant_btn = msg_box.addButton("Instant Solution", QMessageBox.ButtonRole.ActionRole)
        step_btn = msg_box.addButton("Step-by-Step", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg_box.addButton(QMessageBox.StandardButton.Cancel)

        result =msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == instant_btn:
            self.disable_buttons()
            self.ui.Pause_button_2.setEnabled(False)
            self.instant_solve()

        elif clicked == step_btn:
            self.disable_buttons()
            self.ui.Pause_button_2.setEnabled(False)
            self.step_by_step_solve() 
        else:
            self.update_display()

    # Instant Solution
    def instant_solve(self):
        self.board = copy.deepcopy(self.solution)
        self.update_display()
        self.timer.stop()
        QMessageBox.information(self,"Solved!", "The board is solved instantly automatically!")

    # Step-By-Step Solution
    def step_by_step_solve(self):
        self.cells_to_fill = []
        self.is_solving = True
        self.cell_clicked = None
        
        # Find every cell where the board is currently empty
        for i in range(9):
            for j in range(9):
                if self.initial_board[i][j] == 0:
                    self.cells_to_fill.append((i,j)) # A tuple of the row,column

        # Create a timer to fill them one by one
        self.solve_timer = QTimer()
        self.solve_timer.timeout.connect(self.fill_next_cell) # By each second pass, a cell is filled
        self.solve_timer.start(300) # It takes 300ms (0.3s) to fill a square

    # The Filling Logic
    def fill_next_cell(self):
        # The board is already solved
        if not self.cells_to_fill:
            self.solve_timer.stop()
            self.timer.stop()
            QMessageBox.information(self,"Solved!", "The board is solved step by step automatically!")
            return
        
        # Take the first cell from the list
        row, col = self.cells_to_fill.pop(0)

        # Insert the correct number from the solution into the board
        self.board[row][col] = self.solution[row][col]

        # Redraw the board so the player can see the change each time
        self.update_display()
    
    # Check if the board is complete and correctly filled
    def is_board_complete(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return False
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True

    # Handle the game ending
    def game_over(self, won):
        self.timer.stop()
        self.disable_buttons()
        self.ui.Pause_button_2.setEnabled(False)
        if won:
            minutes = self.time_seconds // 60
            seconds = self.time_seconds % 60
            QMessageBox.information(
                self,
                "Congratulations!",
                f"You solved the Sudoku Puzzle!\n\nTime: {minutes:02d}:{seconds:02d}\nMistakes: {self.mistakes}/{self.max_mistakes}"
            )
        else:
            QMessageBox.information(
                self,
                "Game Over.",
                f"Good Game, but you made too many mistakes!\nPlease, try again!"
            )
            self.reset_game()

    # Show game instructions
    def show_instructions(self):
        instructions_text = (
        "Welcome to Sudoku!\n\n"
        "THE GOAL:\n"
        "Fill the 9x9 grid so that every row, every column, and every "
        "3x3 box contains the numbers 1 to 9 without any repeats.\n\n"
        
        "CONTROLS:\n"
        "• SELECT: Click any empty cell to highlight it.\n"
        "• PLACE: Click a number button (1-9) to fill the selected cell.\n"
        "• ERASE: Use the Eraser button to clear a cell's number or notes.\n"
        "• NOTES: Toggle 'Note Mode' to brainstorm possible numbers.\n"
        "• PAUSE: Toggle 'Pause/Resume' to freeze the game and unfreeze it."

        "These won't count as mistakes!\n\n"
        
        "RULES & LIVES:\n"
        f"• You can make up to {self.max_mistakes} mistakes before the game ends.\n"
        "• Numbers provided at the start (Black) cannot be changed.\n"
        "• Correct moves appear in Blue; mistakes appear in Red.\n\n"
        
        "Stuck? Use the 'Auto Solve' button for help!"
    )

        QMessageBox.information(
            self,
            "How to Play",
            instructions_text
        )

    # Show contact info
    def show_contact(self):
        contact_info = (
            "Sudoku Game v1.0\n\n"
            "Developed by: Sudoku Game Co.\n"
            "Support: support@SudokuGame.com\n"
            "GitHub: github.com/SudokuGame\n\n"
            "Thank you for playing! If you enjoyed the game, "
            "feel free to reach out with feedback or suggestions."
        )
        
        QMessageBox.about(
            self,
            "Contact Information",
            contact_info
        )
    
    def show_credits(self):
        QMessageBox.information(
            self,
            "Credits",
            "Sudoku Game v1.0\n\n"
            "Development: Sudoku Game Co.\n"
            "Language: Python 3.14\n"
            "Interface: PyQt6 (Qt Creator)\n"
            "Logic: Backtracking Algorithm"
        )

# This block is to run the program 
def main():
    app = QApplication(sys.argv)
    game = SudokuGame()
    game.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

