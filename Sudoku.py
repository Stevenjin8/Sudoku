import numpy as np
from turtle import Turtle, Screen

#notes that [y,x] is used instead of [x,y] because the first dimension indicates height

n = 4
n2 = n**2

#turtle setup
board_turtle = Turtle()
board_turtle.ht()
#make a 9x9 matrix of turtles each to draw at their corresponding position
#so it is easier to clear
turtles = [[Turtle() for _ in range(n2)] for _ in range(n2)]
screen = Screen()

for x in range(n2):
    for y in range(n2):
        turtles[y][x].hideturtle()

screen.tracer(False)
height = screen.window_height()-40
width = screen.window_width()-40

def render(t):
    #draws the board
    t.up()
    t.goto(-width//2, -height//2)
    t.down()
    for i in range(n2):
        if i%n == 0: #so each third line is thicker
            t.pensize(5)
        t.forward(width)
        t.backward(width)
        t.pensize(2)
        t.left(90)
        t.forward(height//n2)
        t.right(90)
    t.pensize(5)
    t.forward(width)
    t.backward(width)
    t.pensize(2)
    
    t.right(90)
    for i in range(n2):
        if i%n == 0:
            t.pensize(5)
        t.forward(height)
        t.backward(height)
        t.pensize(2)
        t.left(90)
        t.forward(width//n2)
        t.right(90)
    t.pensize(5)
    t.forward(height)
    t.backward(height)
    t.pensize(2)

    
def draw_digit(digit, x, y):
    #clears and draws digit digit at position x,y on the board
    turtles[y][x].clear()
    
    if digit!= 0:
        t = turtles[y][x]
        
        t.up()
        t.goto(x*width//n2 - width//2 + width//30, -y*height//n2 + height//2 - height//9)
        
        t.write(str(hex(digit)[2:]), True, align="left", font=("Arial", 25, "normal"))
        t.down()
    
def draw_nums(board):
    #draws all the numbers
    for x in range(n2):
        for y in range(n2):
            draw_digit(board[y,x], x, y)
            

def clear(board):
    #clears digits that are now zero
    for x in range(n2):
        for y in range(n2):
            if board[y,x] == 0:
                turtles[y][x].clear()


def get_quad(board,x,y):
    #returns an 1x9 ndarray of a quadrant
    return board[n*y:n*y+n,n*x:n*x+n]

def check(line):
    #checks if a line has only one of each digit
    checked = []
    for x in line:
        if x != 0 and x in checked:
            return False
        else:
            checked.append(x)
    return True

def check_rows(board):
    #checks all thre rows in a board
    lines = [board[line_num,:] for line_num in range(9)]
    checks = [check(line) for line in lines]
    return not False in checks

def check_cols(board):
    #checks all the columns in a board
    lines = [board[:,col_num].reshape(board[:,col_num].size) for col_num in range(9)]
    checks = [check(line) for line in lines]
    return not False in checks

def check_quads(board):
    #checks all the quadrants in a board
    lines = []
    for x in range(n):
        for y in range(n):
            lines.append(get_quad(board,x,y).reshape(n2))
    checks = [check(line) for line in lines]
    return not False in checks

def check_all(board):
    #checks the whole board
    return check_quads(board) and check_rows(board) and check_cols(board)

def stuck(board):
    #checks if the board is stuck ie the first blank cannot hold 1-9
    first_zero = (np.where(board == 0)[0][0], np.where(board == 0)[1][0])
    for i in range(1,n2+1):
        board[first_zero[0],first_zero[1]] = i
        if check_all(board):
            return False
    return True

def can_go(num, x, y, board):
    #checks if a number can go in a spot
    if board[x,y] != 0:
        return False
    else:
        board[x,y] = num
        #replace to make faster?
        return check_all(board)

def can_go_tensor(board):
    #returns an 9x9x9 (y,x,n) tensor of booleans where position (y,x,n) indicates whether
    #value n can go in position (y,x) in the board
    out = np.zeros([n2,n2,n2])
    for x in range(0,n2):
        for y in range(0,n2):
            #note that the array position correspond to numerical value -1
            out[x,y,:] = np.array([can_go(num,x,y, board.copy()) for num in range(1,n2+1)])
    return out

def solved(board):
    #cehcks if the board has been solved
    return not 0 in board and check_all(board)
    
def fill_once(board):
    #fills in the board like one normally solves a sudoku puzzle
    
    #makes the tensor
    cgt = can_go_tensor(board.copy())
    
    #checks if there are blocks where only one number can go
    for x in range(n2):
        for y in range(n2):
            if np.sum(cgt[x,y,:]) == 1:
                board[x,y] = np.where(cgt[x,y,:])[0][0] + 1 #plus one beucase index 0 corresponds to value 1
                draw_digit(np.where(cgt[x,y,:])[0][0] + 1,y,x)
                
    #checks if a value num can only be in one position in a column
    for x in range(n2):
        for num in range(n2):
            if np.sum(cgt[:,x,num]) == 1:
                board[np.where(cgt[:,x,num]),x] = num+ 1 #plus one beucase index 0 corresponds to value 1
                draw_digit(num+1,x,np.where(cgt[:,x,num])[0][0])
                
    #checks if value num can only be in one postion in a column
    for y in range(n2):
        for num in range(n2):
            if np.sum(cgt[y,:,num]) == 1:
                board[y,np.where(cgt[y,:,num])] = num+1 #plus one beucase index 0 corresponds to value 1
                draw_digit(num+1,np.where(cgt[y,:,num])[0][0],y)

    return board
        
def fill(board):
    #fills the tradition way until backtracking is needed
    new_board = fill_once(board.copy())
    while not np.array_equal(new_board, board):
        board = new_board.copy()
        new_board = fill_once(board.copy())
    return board

def solve(board):
    #sovles using only backtracking
    if not (solved(board) or stuck(board.copy())):
        first_zero = (np.where(board == 0)[0][0], np.where(board == 0)[1][0])
        
        for i in range(1,n2+1):
            board[first_zero[0],first_zero[1]] = i
            if check_all(board):
                draw_digit(i,first_zero[1],first_zero[0])
                new_board = solve(board.copy())
                clear(board)
                if solved(new_board):
                    return new_board
                
    return board


def solve2(board):
    #solves using a hybrid method
    if not (solved(board) or stuck(board.copy())):
        first_zero = (np.where(board == 0)[0][0], np.where(board == 0)[1][0])
        for i in range(1,n2+1):
            board[first_zero[0],first_zero[1]] = i
            draw_digit(i,first_zero[1],first_zero[0])
            clear(board)
            if check_all(board):
                new_board = solve2(fill(board.copy())) #fill is used here
                if solved(new_board):
                    return new_board
                
    return board


"""sdk = np.array([ #zeros represent blank spaces
       [1, 0, 0, 0, 0, 0, 0, 9, 5],
       [0, 9, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 7, 0, 0, 0, 0, 0, 8],
       [7, 0, 6, 0, 0, 3, 0, 0, 0],
       [0, 3, 0, 0, 0, 0, 0, 2, 0],
       [0, 0, 0, 5, 6, 0, 7, 0, 3],
       [9, 2, 0, 0, 3, 0, 6, 0, 0],
       [0, 0, 0, 8, 0, 2, 0, 5, 0],
       [4, 0, 0, 0, 0, 1, 0, 0, 7]
       ])"""
"""#other possible puzzles
sdk = np.array([
    [1,0,0,0,0,0,0,0,0],
    [0,0,3,6,0,0,0,0,0],
    [0,7,0,5,9,0,2,0,0],
    [0,0,0,0,0,7,1,0,0],
    [0,0,0,0,0,5,7,0,0],
    [0,0,0,1,0,6,0,3,0],
    [0,0,1,0,0,0,0,6,8],
    [0,0,8,5,0,0,0,0,0],
    [0,9,0,0,0,0,4,0,0]])
"""
sdk = np.zeros((16,16))


#so the ones that can't be changed say orange
for x in range(n2):
    for y in range(n2):
        if sdk[y,x] != 0:
            turtles[y][x].pencolor('orange')

#draws the board and starting numbers
render(board_turtle)
draw_nums(sdk)

#solves
print(solve2(sdk))