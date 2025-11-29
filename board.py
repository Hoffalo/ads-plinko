EMPTY = 0
PEG = 1

class BoardModel:
    def __init__(self, grid, slot_scores):
        self.grid = grid
        self.slot_scores = slot_scores
        self.number_of_rows = len(grid)
        self.number_of_columns = len(grid[0])

    def in_bounds(self, row, column):
        return 0 <= row < self.number_of_rows and 0 <= column < self.number_of_columns

    def get_cell(self, row, column):
        if not self.in_bounds(row, column):
            raise Exception("Out of bounds")
        return self.grid[row][column]

    def set_cell(self, row, column, value):
        if not self.in_bounds(row, column):
            raise Exception("Out of bounds")
        if value != EMPTY and value != PEG:
            raise Exception("Invalid value")
        self.grid[row][column] = value

    def is_peg(self, row, column):
        return self.in_bounds(row, column) and self.grid[row][column] == PEG

    def is_empty(self, row, column):
        return self.in_bounds(row, column) and self.grid[row][column] == EMPTY

    def get_pegs(self):
        result = []
        for row in range(self.number_of_rows):
            for column in range(self.number_of_columns):
                if self.grid[row][column] == PEG:
                    result.append((row, column))
        return result

    def get_slot_scores(self):
        return self.slot_scores[:]

    def get_slot_score_at_column(self, column):
        if not (0 <= column < self.number_of_columns):
            raise Exception("Invalid column")
        return self.slot_scores[column]

    def get_children_of_peg(self, row, column):
        if not self.is_peg(row, column):
            raise Exception("There is no peg at this position")
        left_child = self.child_direction(row, column, -1)
        right_child = self.child_direction(row, column, 1)
        return left_child, right_child

    def child_direction(self, row, column, direction):
        new_column = column + direction
        new_row = row + 1

        if new_column < 0 or new_column >= self.number_of_columns:
            return None

        if new_row >= self.number_of_rows:
            return new_column

        if self.grid[new_row][new_column] == PEG:
            return (new_row, new_column)

        current_row = new_row
        while current_row < self.number_of_rows and self.grid[current_row][new_column] == EMPTY:
            current_row += 1

        if current_row < self.number_of_rows:
            return (current_row, new_column)

        return new_column




