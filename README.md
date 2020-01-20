# Sudoku
Solves a given n^2xn^2 sudoku puzzle using backtracking and the tensor method.
The tensor method is as follows:
    create an n^2xn^2xn^2 tensor of booleans.
        The first two dimensions represent the position on the board.
        The last dimension represents whether a number, corresponding to the index, can go at the corresponding position on the board.
        e.g. if the value at [1,2,3] was true, the value 4 (recall that 0 is an empty space) can be at position [1,2] without direct conflicts.
    The tensor is then summed across each of its dimensions to fill the board.
