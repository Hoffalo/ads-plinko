
board = [
    [0,1,0,1,0,1,0],
    [0,0,1,0,1,0,0],
    [0,1,0,1,0,1,0],
    [0,0,1,0,1,0,0],
    [10,20,50,100,50,20,10]
]

rows, cols = len(board), len(board[0])

def GetSlotScore(col: int) -> int:
    return board[rows-1][col]