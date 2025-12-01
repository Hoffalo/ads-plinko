# Time Complexity Analysis

This document explains the asymptotic time complexity of every algorithmic function in the
project.  Let **R** denote the number of rows in a board, **C** the number of columns, and
**P** the number of pegs (`P ≤ R·C`). When random paths are involved, **k** represents the
number of pegs visited by a single simulated fall (bounded by **R**).

## `board.py`

- `BoardModel.__init__`: Initializes and stores the grid and slot scores in O(1) time given
  pre-built inputs. 【F:board.py†L5-L9】
- `in_bounds`, `get_cell`, `set_cell`, `is_peg`, `is_empty`, `get_slot_score_at_column`:
  perform constant-time bounds checks and value lookups, so O(1). 【F:board.py†L11-L49】
- `get_pegs`: Scans every cell to collect peg locations → O(R·C). 【F:board.py†L51-L58】
- `get_slot_scores`: Returns a shallow copy of the slot scores list → O(C). 【F:board.py†L59-L61】
- `get_children_of_peg`: Calls `child_direction` for left and right so it is two passes of
  that procedure, giving O(Tchild). 【F:board.py†L65-L72】
- `child_direction`: After basic bounds checks, it may walk downward through empty cells in
  the chosen column until it finds a peg or exits the board. In the worst case it inspects
  each remaining row below the current peg, so O(R). 【F:board.py†L74-L92】

## `graph_dp.py`

- `node_for_peg`, `node_for_slot`: Create tuple identifiers in O(1). 【F:graph_dp.py†L5-L9】
- `build_graph`:
  - Collects all pegs using `get_pegs` (O(R·C)).
  - For each peg, `get_children_of_peg` is invoked once and internally calls
    `child_direction` twice, costing O(P·R) in the worst case when many empty rows are
    scanned downward per peg.
  - Initializes start nodes by calling `first_node_for_column` for every column, which can
    scan up to R rows each (O(R·C)).
  - Overall worst-case complexity: O(R·C + P·R + R·C) = O(P·R + R·C).
    When the board is dense (P ≈ R·C), this simplifies to O(R²·C). 【F:graph_dp.py†L11-L46】
- `first_node_for_column`: Walks downward until encountering a peg or the bottom, so O(R).
  【F:graph_dp.py†L48-L57】
- `compute_expected_values`:
  - Builds the graph as above.
  - Uses memoized recursion to evaluate each graph node once. The number of nodes is
    P pegs plus C slots, and each peg contributes up to two edges. Traversal therefore runs
    in O(P + C) after the graph is built.
  - The final list of expected values iterates over all columns in O(C).
    Total complexity: O(P·R + R·C + P + C). 【F:graph_dp.py†L59-L91】
- `choose_best_column`: Scans the expected value list once to find the maximum, so O(C).
  【F:graph_dp.py†L93-L102】

## `simulation.py`

- `first_peg_position_for_column`: Moves downward until a peg is found or the bottom is
  reached → O(R). 【F:simulation.py†L3-L13】
- `simulate_fall`:
  - Finds the first peg in O(R).
  - Each bounce queries `get_children_of_peg`, which may scan downwards through empty cells
    (O(R) per bounce). A path can visit at most k pegs (k ≤ R), so the worst case is
    O(R + k·R) = O(R²). 【F:simulation.py†L15-L46】
- `simulate_fall_and_score`: Delegates to `simulate_fall` and adds constant-time scoring,
  keeping the overall time O(R²). 【F:simulation.py†L48-L53】

## `main.py`

- `create_default_board_model`: Builds a 30×7 grid, fills it, and places pegs using nested
  loops over all cells → O(R·C). Slot score initialization is O(C). 【F:main.py†L1-L38】
- `ask_human_column`: Performs constant-time input validation per attempt → O(1) per try.
  【F:main.py†L40-L54】
- `play_game`: Runs a fixed number of rounds (5). Each round performs one simulation for
  the human and one for the AI and scans expected values via `choose_best_column`.
  With the round count constant, the loop contributes O(1)·(simulation + choice) =
  O(R² + C). 【F:main.py†L56-L93】
- `main`: Invokes `play_game` once → O(R² + C). 【F:main.py†L95-L99】

## `plinko_pygame.py`

- `create_default_board_model`: Builds a larger grid (35×25) and populates pegs; work is
  proportional to the number of cells and columns → O(R·C). 【F:plinko_pygame.py†L8-L67】
- `compute_layout`: Computes layout values with a fixed set of arithmetic operations → O(1).
  【F:plinko_pygame.py†L69-L88】
- `grid_to_pixel`: Constant-time coordinate mapping → O(1). 【F:plinko_pygame.py†L90-L93】
- `build_path_points`: Converts a simulated path of length k into pixel coordinates,
  performing O(k) work. 【F:plinko_pygame.py†L95-L113】
- `handle_human_click`: Validates the click position and, when valid, runs one simulation
  and path conversion. Validation is O(1); the dominant cost is `simulate_fall_and_score`
  (O(R²)) plus `build_path_points` (O(k)). 【F:plinko_pygame.py†L115-L150】
- `start_ai_turn`: Mirrors the human turn logic; overall complexity O(R² + k). 【F:plinko_pygame.py†L152-L173】
- `update_animation`: Advances the ball one step per frame. Each call performs constant work
  regardless of board size, so O(1) per invocation. 【F:plinko_pygame.py†L175-L206】
- `draw_board`: Draws the grid, pegs, and slots by iterating over all rows and columns
  several times, leading to O(R·C) drawing operations per frame. 【F:plinko_pygame.py†L226-L313】
- `draw_ball`: Constant-time drawing for the current ball position → O(1). 【F:plinko_pygame.py†L315-L325】
- `draw_hud`: Performs fixed-size text updates → O(1). 【F:plinko_pygame.py†L327-L371】
- `main`: Runs an event loop that processes user input, triggers simulations as needed, and
  redraws every frame. Per frame cost is dominated by `update_animation` (O(1)) and
  `draw_board` (O(R·C)). 【F:plinko_pygame.py†L373-L438】

## `ui.py`

- `create_default_board_model`: Builds and fills a 31×7 grid and assigns pegs → O(R·C).
  【F:ui.py†L1-L36】
- `clear_board_gui`, `draw_static_board`: Iterate across all board cells once (or a few
  times) to reset and render pegs/slots, costing O(R·C). 【F:ui.py†L38-L61】
- `update_title`, `update_output`: Perform constant-time GUI updates → O(1).
  【F:ui.py†L63-L73】
- `animate_path`: Steps through a simulated path of length k, updating the GUI per step, so
  O(k). 【F:ui.py†L75-L89】
- `play_round`: Executes one human simulation and one AI simulation plus animation. Each
  simulation is O(R²) and each animation O(k), yielding O(R² + k). 【F:ui.py†L91-L132】
- `handle_click`: Simple guard checks and delegation to `play_round` → O(R² + k).
  【F:ui.py†L134-L143】
- `start_game`: Clears the board and sets initial text, dominated by `draw_static_board`
  at O(R·C). 【F:ui.py†L145-L150】
- `main`: Sets up the model and GUI (O(R·C)) and enters the event loop controlled by
  `game2dboard`, whose per-click cost defers to `handle_click`. 【F:ui.py†L152-L186】
