# game.py
import math
import copy
import pyautogui

rows = 4
cols = 4

def get_max_cell(board):
    max_cell = 1
    for row in board:
        for cell in row:
            max_cell = max(max_cell, cell)
    return max_cell

def right(board):
    rows = len(board)
    cols = len(board[0])
    board_copy = copy.deepcopy(board)
    for idx, row in enumerate(board_copy):
        new_row = [x for x in row if x!=1]
        new_row = [1]*(len(row)-len(new_row)) + new_row
        board_copy[idx] = new_row
                
    # print(board_copy)
    for idx in range(rows):
        for i in range(cols-1, 0, -1):        
            if board_copy[idx][i]==board_copy[idx][i-1] and board_copy[idx][i] != 1:
                board_copy[idx][i] = board_copy[idx][i]*2
                if i==1:
                    board_copy[idx][0] = 1
                else:
                    board_copy[idx] = [1] + board_copy[idx][:i-1] + board_copy[idx][i:]
    return board_copy


def left(board):
    rows = len(board)
    cols = len(board[0])
    board_copy = copy.deepcopy(board)
    for idx, row in enumerate(board_copy):
        new_row = [x for x in row if x!=1]
        new_row = new_row + [1]*(len(row)-len(new_row))
        board_copy[idx] = new_row

    for idx in range(rows):
        for i in range(cols-1):
            if board_copy[idx][i]==board_copy[idx][i+1] and board_copy[idx][i] != 1:
                board_copy[idx][i] = board_copy[idx][i]*2
                if i==len(board_copy[idx])-2:
                    board_copy[idx][-1] = 1
                else:
                    board_copy[idx] = board_copy[idx][:i+1] + board_copy[idx][i+2:] + [1]
    return board_copy



import copy
from typing import List

def down(board: List[List[int]]) -> List[List[int]]:
    """
    Executes a downward move on the 2048 game board.

    Parameters:
        board (List[List[int]]): The current game board represented as a 2D list.
                                 Empty cells are denoted by 1.

    Returns:
        List[List[int]]: The updated game board after performing the downward move.
    """
    if not board or not board[0]:
        raise ValueError("Board must be a non-empty 2D list.")
    
    rows = len(board)
    cols = len(board[0])
    
    # Verify all rows have the same number of columns
    for row in board:
        if len(row) != cols:
            raise ValueError("All rows must have the same number of columns.")
    
    board_copy = copy.deepcopy(board)
    down_board = [[1 for _ in range(cols)] for _ in range(rows)]
    
    for col in range(cols):
        rowc = rows - 1
        rowd = rows - 1
        while rowc >= 0:
            if board_copy[rowc][col] != 1:
                down_board[rowd][col] = board_copy[rowc][col]
                rowd -= 1
            rowc -= 1
        
        # Merge tiles
        for row in range(rows - 1, 0, -1):
            if down_board[row][col] == down_board[row - 1][col] and down_board[row][col] != 1:
                down_board[row][col] *= 2
                down_board[row - 1][col] = 1
        
        # Push tiles down again after merging
        rowc = rows - 1
        rowd = rows - 1
        while rowc >= 0:
            if down_board[rowc][col] != 1:
                down_board[rowd][col] = down_board[rowc][col]
                rowd -= 1
            rowc -= 1
        
        # Fill the remaining cells with 1
        while rowd >= 0:
            down_board[rowd][col] = 1
            rowd -= 1
    
    return down_board

def find_longest_path(board):
    board_copy = copy.deepcopy(board)
    board_copy[0].reverse()
    board_copy[2].reverse()
    # print(board_copy)
    board_list = [x for row in board_copy for x in row]
    board_list.reverse() 
    # print(board_list)
    longest_seq = []
    last = board_list[0]
    ind = 0
    while ind<len(board_list) and board_list[ind] <= last:
        longest_seq.append(board_list[ind])
        last = board_list[ind]
        ind += 1
    return longest_seq


def score(board):
    score = 0
    seq = find_longest_path(board)
    # print("seq", seq)
    for i in seq:
        score += pow(4,math.log2(i))
    for row in board:
        for cell in row:
            score += pow(3,math.log2(cell))
    return score


def check_pivots(board):

    priority_move = None
    board_copy = copy.deepcopy(board)
    board_list = [x for row in board for x in row]
    board_list.sort(reverse=True)

    for row in range(rows-1, -1, -1):
        bl_idx = (rows-row-1)*cols 
        if board_list[bl_idx] <= 64:
            return None
        if ((rows-row-1)%2==0 and board_list[bl_idx] != board_copy[row][cols-1]) and (bl_idx==0 or (board_copy[row+1][cols-1] == board_list[bl_idx-1])):
            for i in range(cols-1, -1, -1):
                if board_copy[row][i] == 1:
                    continue
                if board_copy[row][i] == board_list[bl_idx]:
                    return "right"
                else:
                    return "undo"
        if ((rows-row-1)%2==1 and board_list[bl_idx] != board_copy[row][0]) and board_copy[row+1][0] == board_list[bl_idx-1 ]:
            for i in range(cols):
                if board_copy[row][i] == 1:
                    continue
                if board_copy[row][i] == board_list[bl_idx]:
                    return "left"
                else:
                    return "undo"
    return None


def next_move(board):
    
    # check if pivots can be at their place if not then undo

    priority_move = check_pivots(board)
    if priority_move:
        return priority_move

    # lookahead 2 moves
    # downdown, downleft, downright, rightright, rightdown, rightleft, leftleft, leftdown, leftright
    # print("board", board)
    possible_boards = [(board, None)]
    lookahead = 3
    max_element = get_max_cell(board)
    for _ in range(lookahead):
        current_boards = possible_boards
        next_boards = []
        for (b, move) in current_boards:
            next_down = down(b)
            next_left = left(b)
            next_right = right(b)
            # print("down",next_down)
            # print("left",next_left)
            # print("right",next_right)
            if move:
                next_boards.append((next_down,move))
                next_boards.append((next_left,move))
                next_boards.append((next_right,move))
            if not move:
                next_boards.append((next_down, "down"))
                next_boards.append((next_left, "left"))
                next_boards.append((next_right, "right")) 
        possible_boards = next_boards
    
    scored_boards = []
    for (b,move) in possible_boards:
        s = score(b)
        # print(s)
        # column_width = max(len(str(item)) for row in b for item in row)

        # Display the matrix
        # for row in b:
            # print(" ".join(f"{item:{column_width}}" for item in row))
        # for row in b:
        #     print(row)
        scored_boards.append((s, move))
    scored_boards.sort(key=lambda x: x[0], reverse=True)
    # print(scored_boards)
    if(len(scored_boards) == 0):
        return "undo"
    return scored_boards[0][1]

    


def press_key(move):
    """
    Presses the corresponding key on the keyboard to swipe or undo.
    
    Args:
        move (str): 'up', 'down', 'left', 'right', or 'undo'.
    """
    key_map = {
        'up':    'up',
        'down':  'down',
        'left':  'left',
        'right': 'right',
        'undo':  u'u'
    }
    print(move)
    key_to_press = key_map.get(move, None)
    if key_to_press:
        pyautogui.press(key_to_press)




def next_board(board):
    move = next_move(board)
    upcoming_board = []

    if move == "undo":
        press_key(move)
        return [[1 for _ in range(cols)] for _ in range(rows)]
    if move == "down":
        upcoming_board = down(board)
    if move == "left":
        upcoming_board = left(board)
    if move == "right":
        upcoming_board = right(board)


    while board == upcoming_board:
        if move == "down":
            move = "left"
            upcoming_board = left(board)
        elif move == "left":
            move = "right"
            upcoming_board = right(board)
        else:
            move = "down"
            upcoming_board = down(board)
        


    press_key(move)
    
    return upcoming_board
    

if __name__ == "__main__":
    # board = [[1, 2, 8, 16], [2, 8, 16, 32], [512, 256, 128, 64], [1024, 2048, 4096, 8192]]
    board = [
        [2,  2,   2,   1], 
        [4,  16,  2,   2], 
        [8,  64,  32,  8], 
        [32, 128, 512, 16384]]
    print(board)
    print(find_longest_path(board))
    # board = [
    #     [2, 1, 1, 2], 
    #     [8, 4, 4, 1], 
    #     [2, 4, 8, 4], 
    #     [4, 8, 128, 16384]]
    # rows = len(board)
    # cols = len(board[0])
    # print(board)
    # print("left:")
    # print(left(board))
    # print("right:")
    # print(right(board))
    # print("up:")
    # print(up(board))
    # print("down:")
    # print(down(board))

    # # find_longest_path(board)
    # print(score(board))
    # print(score(left(board)))
    # print(score(down(board)))
    # print(score(down(left(board))))
    # press_key(next_move(board))
    # print(left(board))



