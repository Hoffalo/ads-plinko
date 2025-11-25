class Board():
    def __init__(self, board:list):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])

    def GetSlotScore(self, col: int) -> int:
        return self.board[self.rows - 1][col]
    
    def Print(self):
        print(self.board)


boardMap = [
    [0,1,0,1,0,1,0],
    [0,0,1,0,1,0,0],
    [0,1,0,1,0,1,0],
    [0,0,1,0,1,0,0],
    [10,20,50,100,50,20,10]
]

board = Board(boardMap)

board.Print()


