from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


# ----- Constants for cell types -----
EMPTY = 0
PEG   = 1


@dataclass
class BoardModel:
    """
    Represents the logical Plinko board:
    - A grid of pegs (and empty cells) in the upper rows.
    - A row of slot scores at the bottom.
    """
    grid: List[List[int]]            # rows of 0/1 (EMPTY/PEG)
    slot_scores: List[int]           # one score per column

    # You can derive rows/cols from grid
    rows: int = field(init=False)
    cols: int = field(init=False)

    def __post_init__(self) -> None:
        self.rows = len(self.grid)
        if self.rows == 0:
            raise ValueError("Grid must have at least 1 row.")

        self.cols = len(self.grid[0])
        if any(len(row) != self.cols for row in self.grid):
            raise ValueError("All grid rows must have the same number of columns.")

        if len(self.slot_scores) != self.cols:
            raise ValueError("slot_scores length must match number of columns in grid.")

    # ---------- Class constructors ----------

    @classmethod
    def default(cls) -> "BoardModel":
        """
        Create a default Plinko layout (your current design).
        You can modify this to create different preset boards.
        """
        grid = [
            [0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0],
        ]
        slot_scores = [10, 20, 50, 100, 50, 20, 10]
        return cls(grid=grid, slot_scores=slot_scores)

    # (Optional) you can add from_file/to_file later for load/save.

    # ---------- Basic helpers ----------

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_cell(self, r: int, c: int) -> int:
        """
        Return the value in the grid at (r, c): EMPTY or PEG.
        Raises if out of bounds.
        """
        if not self.in_bounds(r, c):
            raise IndexError(f"Cell ({r}, {c}) is out of bounds.")
        return self.grid[r][c]

    def set_cell(self, r: int, c: int, value: int) -> None:
        """
        Set the cell at (r, c) to EMPTY or PEG.
        """
        if not self.in_bounds(r, c):
            raise IndexError(f"Cell ({r}, {c}) is out of bounds.")
        if value not in (EMPTY, PEG):
            raise ValueError("Cell value must be EMPTY or PEG.")
        self.grid[r][c] = value

    # ---------- Cell type checks ----------

    def is_peg(self, r: int, c: int) -> bool:
        return self.in_bounds(r, c) and self.grid[r][c] == PEG

    def is_empty(self, r: int, c: int) -> bool:
        return self.in_bounds(r, c) and self.grid[r][c] == EMPTY

    def is_slot_row(self, r: int) -> bool:
        """
        True if this row index corresponds to the slot line (conceptually below the grid).
        For the data model, slots are not in grid rows, so the slot 'row index'
        is equal to self.rows.
        """
        return r == self.rows

    # ---------- Modifying pegs ----------

    def add_peg(self, r: int, c: int) -> None:
        """
        Place a peg at (r, c).
        """
        self.set_cell(r, c, PEG)

    def remove_peg(self, r: int, c: int) -> None:
        """
        Remove a peg at (r, c), making it empty.
        """
        self.set_cell(r, c, EMPTY)

    def toggle_peg(self, r: int, c: int) -> None:
        """
        If there's a peg, remove it. If it's empty, add a peg.
        """
        if not self.in_bounds(r, c):
            raise IndexError(f"Cell ({r}, {c}) is out of bounds.")
        self.grid[r][c] = EMPTY if self.grid[r][c] == PEG else PEG

    # Placeholder for "rotating" pegs if you later introduce directional pegs.
    def rotate_peg(self, r: int, c: int) -> None:
        """
        For now, rotation doesn't change anything because pegs are symmetric.
        If you later introduce directional pegs with different probabilities,
        you can store orientation here.
        """
        if not self.is_peg(r, c):
            raise ValueError(f"No peg to rotate at ({r}, {c}).")
        # TODO: implement when you introduce special peg types
        pass

    # ---------- API for other modules ----------

    def get_pegs(self) -> List[Tuple[int, int]]:
        """
        Return a list of (row, col) for all peg positions.
        """
        result: List[Tuple[int, int]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == PEG:
                    result.append((r, c))
        return result

    def get_slot_scores(self) -> List[int]:
        """
        Return the list of slot scores, one per column.
        """
        return list(self.slot_scores)

    def get_slot_score_at_col(self, c: int) -> int:
        """
        Return the score of the slot under column c.
        """
        if not (0 <= c < self.cols):
            raise IndexError(f"Column {c} is out of bounds.")
        return self.slot_scores[c]

    # ----- Children of a peg (for graph builder, Option A behavior) -----

    def get_children_of_peg(self, r: int, c: int) -> Tuple[Optional[Tuple[int, int]], Optional[int]]:
        """
        Given a peg at (r, c), return its children:

        - Left child: either coordinates (row, col) of the next peg encountered
          when going down-left through empty cells, or None if it would fall off
          the board, or an integer 'slot column' if it falls into a slot.

        - Right child: same logic.

        We encode children as:
          (left_child, right_child)

        Each child is either:
          - (row, col) for a peg, OR
          - an integer representing a slot column, OR
          - None if it exits the board.

        NOTE: This function just computes where the ball WOULD go if
        probabilities choose left/right; the graph builder will turn this
        into node ids and edges.
        """
        if not self.is_peg(r, c):
            raise ValueError(f"No peg at ({r}, {c}).")

        left_child = self._trace_child_direction(r, c, direction=-1)
        right_child = self._trace_child_direction(r, c, direction=+1)
        return left_child, right_child

    def _trace_child_direction(
        self,
        r: int,
        c: int,
        direction: int
    ) -> Optional[Tuple[int, int] | int]:
        """
        Helper for get_children_of_peg.

        direction = -1 for left, +1 for right.

        Algorithm (Option A: transparent empties):
        - Move diagonally down in the given direction:
              r' = r + 1, c' = c + direction
        - If c' is out of bounds -> return None (ball leaves board).
        - While r' is within peg rows and cell is EMPTY:
              r' += 1 (same column)
          (we let the ball fall straight down through empties)
        - If r' is within peg rows and cell is PEG:
              return (r', c') => child peg
        - Else, we've passed all peg rows:
              return c' => slot at that column
        """
        next_col = c + direction
        if not (0 <= next_col < self.cols):
            # Ball goes out of bounds in this direction.
            return None

        # Start one row below the current peg.
        next_row = r + 1

        # If there are no more peg rows below, we go straight to slot.
        if next_row >= self.rows:
            return next_col  # slot column

        # Transparent-empty behavior: fall down in this column until we hit a peg or pass the last peg row.
        # First, drop diagonally into (next_row, next_col)
        current_row = next_row

        # While within peg rows and cell is EMPTY, keep moving down.
        while current_row < self.rows and self.grid[current_row][next_col] == EMPTY:
            current_row += 1

        # If we stopped within peg rows and found a PEG:
        if current_row < self.rows and self.grid[current_row][next_col] == PEG:
            return (current_row, next_col)

        # Otherwise, we fell past all peg rows into the slot line.
        return next_col  # slot column

    # ---------- (Optional) save/load for future ----------

    def to_dict(self) -> Dict:
        """
        Serialize the board to a plain dict (for saving as JSON, etc.).
        """
        return {
            "grid": self.grid,
            "slot_scores": self.slot_scores,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BoardModel":
        """
        Construct a BoardModel from a dict (e.g., loaded from JSON).
        """
        return cls(grid=data["grid"], slot_scores=data["slot_scores"])



