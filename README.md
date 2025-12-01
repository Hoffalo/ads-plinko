# Plinko: Human vs AI (Algorithms & Data Structures Project)

## 1. Overview

This project implements a Plinko-style board game where:

- Player 1 is a human.

- Player 2 is an AI.

Both drop balls from the top of a peg board.

The ball bounces left/right off pegs and lands in a slot with a score.

After several rounds, the scores are compared and a winner is announced.

The main question we explore is:

#*Is Plinko really just luck, or can an algorithm find a better strategy?*#

### The project uses the following Algorithms and Data Structures:

#### Multidimensional arrays (2D lists) to represent the board.

#### 1D arrays (lists) for slot scores and paths.

#### Hash tables / dictionaries for graph and dynamic programming.

#### A graph model of the board (pegs + slots, with probabilistic edges).

#### Recursion & Dynamic Programming to compute expected scores.

#### A greedy algorithm to choose the best column for the AI.

#### Randomized simulation for the actual ball paths.

Two different UIs:

A matrix-based GUI using game2dboard.

A more visual Pygame neon Plinko.

## 2. Features

Human vs AI Plinko game with multiple rounds.

AI computes which column has the highest expected score and plays that.

Separate simulation module for random ball paths.

### Two front-ends:

ui.py: grid-based interface with game2dboard.

plinko_pygame.py: full-screen neon Plinko with visible pegs and animated balls.

### Board layout uses:

- Staggered pegs.

- Side walls made of pegs (ragged edges).

- Extra empty row at the top so balls don’t immediately hit a peg.

- Slot scores assigned per column:

- Symmetric pattern in the smaller boards.

- Automatically computed values (high in the center, lower at edges) in the large Pygame board.

- Separate text-mode version (main.py) for quick testing.

## 3. Project Structure

├── board.py            # BoardModel: grid + slot scores + peg physics
├
├── graph_dp.py         # AI logic: graph construction + DP for expected values
├
├── simulation.py       # Random ball path simulation and scoring
├
├── main.py             # Console version of the game (human vs AI, text-based)
├
├── ui.py               # game2dboard-based GUI version (matrix-style interface)
├
├── plinko_pygame.py    # Pygame-based neon Plinko UI (full-screen)
├
├── time_complexity.txt # Time complexity analysis document
├
├── game2dbaord         # Folder containing the necessary requirements for ui.py
├
└── README.md           # This file

### 3.1 board.py

Defines the core data model:

EMPTY = 0, PEG = 1

class BoardModel with:

grid: 2D list (number_of_rows × number_of_columns) containing EMPTY or PEG.

slot_scores: 1D list of length number_of_columns.

number_of_rows, number_of_columns: derived from grid.

#### Main methods:

Bounds and cell access

in_bounds(row, column) → checks if coordinates are inside the grid.

get_cell(row, column) → returns the cell value (with bounds check).

set_cell(row, column, value) → sets a cell to EMPTY or PEG.

#### Helpers

is_peg(row, column) / is_empty(row, column) → convenience checks.

get_pegs() → returns a list of all (row, column) positions that contain a PEG.

get_slot_scores() → returns a copy of the slot scores.

get_slot_score_at_column(column) → returns the score for a particular column.

#### Plinko physics

get_children_of_peg(row, column)
For a peg at (row, column), returns two “children”:

where the ball would go if it bounced left,

and where it would go if it bounced right.
Children can be:

another peg (row, column),

an integer column index (if the ball falls into a slot),

or None (if it falls off the board).

child_direction(row, column, direction)

#### Helper function for left/right:

moves diagonally down-left or down-right one step,

then falls straight down through empty cells until hitting a peg or passing the last row,

returns a child peg, a slot column, or None.

This file is where we represent the board as a 2D array and implement the physics that all other modules rely on.

### 3.2 graph_dp.py

Implements the AI brain using a graph + dynamic programming.

#### Node representation:

node_for_peg(row, column) → ("peg", row, column)

node_for_slot(column) → ("slot", column)

#### Graph data structures:

neighbors (dictionary):
neighbors[node] = [(child_node, probability), ...]
This is an adjacency list for a directed, weighted graph.

start_nodes (dictionary):
start_nodes[column] = node where a ball first enters when dropped in this column.

#### Main functions:

build_graph(board_model)

Gets all pegs from the board (get_pegs).

For each peg:

Uses get_children_of_peg to find left and right children.

Adds edges from this peg node to:

child peg nodes, or

slot nodes,

each with probability 0.5.

For each column:

Calls first_node_for_column(board_model, column) to find the first node a ball hits when dropped there.

Stores that node in start_nodes[column].

first_node_for_column(board_model, column)

Scans down the column from the top until it finds a peg or reaches the bottom.

If it finds a peg, returns ("peg", row, column).

If not, returns ("slot", column) (ball falls straight into slot).

compute_expected_values(board_model)

Builds the graph (neighbors, start_nodes).

Defines a memo table: expected_value = {}.

Uses a recursive function expected_value_for_node(node):

If node is a slot: expected value = that slot’s score.

If node is a peg: expected value = sum over children of probability × child_expected_value.

Results are cached in expected_value to avoid recomputation (top-down DP).

For each column:

Starts from start_nodes[column].

Calls expected_value_for_node to compute the expected score for dropping a ball in that column.

Returns a list of expected values, one per column.

choose_best_column(board_model)

Calls compute_expected_values to get expected scores for all columns.

Linearly scans that list to find the index (column) with the maximum expected value.

Returns (best_column, best_value).

### 3.3 simulation.py

Implements the random simulation of a ball falling through the board.

first_peg_position_for_column(board_model, column)

Scans down one column until it finds a peg or reaches the bottom.

Returns (row, column) of the first peg, or None if there is no peg.

simulate_fall(board_model, start_column)

Finds the first peg position in that column.

Maintains a path_list of peg positions the ball touches.

In a loop:

For the current peg, calls get_children_of_peg to get left and right children.

Uses random.random() to choose left or right with probability ~0.5.

If one side is None, it falls back to the other side.

If the chosen child is:

None → ball leaves the board (no score).

an int → that is the slot column, so the simulation ends.

a (row, column) tuple → another peg; append to path_list and continue.

Returns the list of visited pegs and the final slot column (or None if off-board).

simulate_fall_and_score(board_model, start_column)

Uses simulate_fall to get (path_list, final_slot_column).

If final_slot_column is not None, gets the score from get_slot_score_at_column.

Returns (path_list, final_slot_column, score).

This module is our “random experiment” counterpart to the theoretical expected values from graph_dp.py. The AI’s decision uses the DP; the actual ball outcome uses simulation.py.

### 3.4 main.py (text-mode game)

Provides a simple console version of the game.

create_default_board_model()

Creates a 30×7 grid filled with EMPTY.

Sets staggered pegs in the interior:

One pattern for even rows.

Another pattern for odd rows.

Adds vertical walls of pegs at the leftmost and rightmost columns.

Defines fixed slot scores, e.g. [25, 50, 75, 200, 75, 50, 25].

Returns the BoardModel.

ask_human_column(board_model)

Prompts the user to enter a column index.

Repeats until a valid integer in the allowed range is provided.

play_game()

Creates the board using create_default_board_model.

Initializes human and AI scores.

Plays a fixed number of rounds (e.g., 5):

Human:

Asks for a column.

Simulates a fall using simulate_fall_and_score.

Updates the human score.

AI:

Calls graph_dp.choose_best_column to choose a column.

Simulates that column and updates the AI score.

Prints the path, final slot, round score, and total scores.

At the end, prints final scores and announces who wins or if it’s a tie.

main()

Simply calls play_game() when main.py is run as __main__.

### 3.5 ui.py (game2dboard GUI)

Implements a grid-based GUI using the game2dboard library.

create_default_board_model()

Builds a 31×7 grid:

Row 0 is left empty so balls can start above the first peg.

Rows 1..R−1 have staggered inner pegs (alternating pattern).

Vertical edge pegs on column 0 and column C−1.

Uses fixed slot scores, e.g. [25, 50, 75, 200, 75, 50, 25].

Returns a BoardModel.

clear_board_gui()

Sets every cell in the Board GUI to an empty string.

draw_static_board()

Clears the GUI.

For every peg in board_model, writes "●" in the corresponding GUI cell.

Computes a slot row below the peg rows (with a small gap), and writes each slot score as text there.

update_title()

Sets the window title to something like "Plinko – H <human_score> vs AI <ai_score>".

update_output(message_text)

Updates the output bar (bottom text) with:

Human total score.

Round number.

AI total score.

A short message (like “Click a column to start”).

animate_path(path_list, final_slot_column, score_value, player_symbol)

Animates a ball moving along path_list:

For each peg position in the path, temporarily puts player_symbol (e.g., 🔵 or 🔴) in that cell, pauses, and restores the original value.

At the end, briefly shows the ball + score in the slot row, then restores the slot score text.

play_round(human_column)

Checks if the game is over; if not:

Human move:

Simulates the fall and score.

Animates the path with a blue ball.

Updates the human total score and window title.

AI move:

Chooses best column via graph_dp.choose_best_column.

Simulates the fall and score.

Animates the path with a red ball.

Updates AI score and title.

Updates the output bar with round scores.

Increments the round number and checks for game over:

If finished, prints a final message and updates the title accordingly.

handle_click(mouse_button, row, column)

Called when the user clicks on the board.

If the game is not busy and not over, interprets the clicked column and calls play_round(column).

start_game()

Draws the static board (pegs + slots).

Updates the title and tells the player to click a column to start.

main()

Creates the BoardModel.

Configures the Board GUI:

number of rows and columns,

cell size, fonts, colors, spacing, margins,

output bar.

Registers start_game as on_start and handle_click as on_mouse_click.

Calls board_gui.show() to start the main GUI loop.

### 3.6 plinko_pygame.py (Pygame neon Plinko)

Implements a full-screen neon-style Plinko game using Pygame.

Key elements:

A larger board (e.g., 35 rows × 25 columns) with:

Staggered inner pegs (checkerboard-like pattern).

Ragged edge walls of pegs on left and right.

Top row empty so balls start above the first peg.

Slot scores computed programmatically:

Center column has highest score.

Scores decrease as we move toward the edges.

A minimum score is enforced at the far edges.

A layout system:

compute_layout(screen_width, screen_height)
Calculates:

cell size,

board width/height,

top/left margins,

number of gap rows between pegs and slots.

grid_to_pixel(layout, row, column)
Converts a (row, column) pair to screen (x, y) coordinates.

A path builder:

build_path_points(layout, start_column, path_list, final_slot_column)
Converts the logical path (list of peg coordinates) to a list of screen points:

start point above the board,

each peg location,

final slot coordinates.

Input handling:

handle_human_click(layout, mouse_x, mouse_y)

Checks if the click is inside the board.

Computes the corresponding column index.

Runs a simulation for the human and builds the path points.

Sets game state to animate the human ball.

AI turn:

start_ai_turn(layout)

Uses graph_dp.choose_best_column to pick a column.

Simulates the AI’s fall, builds path points, and sets state for AI animation.

Animation:

update_animation()

Moves the ball smoothly along the list of points.

When the human ball finishes, updates human score and triggers the AI turn.

When the AI ball finishes, updates AI score and either:

moves to the next round, or

marks the game as over after the last round.

Rendering:

draw_neon_frame(surface, layout)

Draws a glowing frame and panel for the Plinko board.

draw_board(surface, layout, font_small)

Draws grid lines.

Draws pegs as glowing circles.

Draws slot bars at the bottom using different colors per column and overlays the slot scores.

draw_ball(surface)

Draws the ball:

human: one color (e.g., pink),

AI: another color (e.g., yellow),

with a lighter highlight trail.

draw_hud(surface, layout, font_small, font_big, font_huge)

Draws a bottom panel with:

human score, round number, AI score,

a message depending on the game state (e.g., “Click to drop your ball”),

a large “HUMAN WINS” / “AI WINS” / “TIE” text at the top when the game is over.

Main loop:

main()

Initializes Pygame and the window (full-screen or near-full-screen).

Creates the large BoardModel.

Computes the layout.

Creates fonts.

Enters the main loop:

Processes events (quit, ESC, mouse clicks).

Updates the animation.

Starts AI turns when needed.

Redraws the board, ball, and HUD each frame.

Uses a fixed frame rate (e.g., 60 FPS).

## 4. How to Run the Project
### 4.1 Requirements

Python 3

game2dboard library:

pip install game2dboard


pygame library:

pip install pygame

### 4.2 Run the text-mode version
python main.py


Plays a 5-round human vs AI game in the terminal.

Human chooses columns by typing numbers.

### 4.3 Run the game2dboard UI
python ui.py


Opens a window showing the board as a grid:

pegs as dots,

slot scores at the bottom,

blue ball for the human,

red ball for the AI.

Click a column to drop your ball and watch both paths animate.

### 4.4 Run the Pygame Plinko 
python plinko_pygame.py


Opens a large neon Plinko board.

The board is wider and taller with many more pegs.

Click anywhere on the board area to drop the human ball.

The AI plays automatically after each human turn.

Scores and winner are displayed on screen.

## 5. Algorithms & Data Structures (Summary)

### Data Structures:

2D arrays (multidimensional arrays)

The board grid BoardModel.grid is a list of lists, representing cells as EMPTY or PEG.

1D arrays (lists)

Slot scores (slot_scores), paths (path_list), expected values per column.

Hash tables (dictionaries)

neighbors (adjacency list of the graph), start_nodes, and expected_value (DP memo table).

Graph representation

Nodes = pegs and slots.

Edges = possible transitions (left/right) with probabilities.

### Algorithms:

Array traversal & sequential search

Scanning the grid to find all pegs.

Scanning a column to find the first peg.

Scanning a list of expected values to find the maximum.

Graph construction

Building neighbors and start_nodes in build_graph.

Recursion + Dynamic Programming

compute_expected_values and expected_value_for_node compute expected scores on a graph (DAG) using memoization.

Greedy algorithm

choose_best_column picks the column with the maximum expected value, based on the DP results.

Randomized simulation

simulate_fall uses random choices (left/right) to simulate a single ball drop.

## 6. Time Complexity

A detailed complexity document is provided separately. 

Here is a brief summary of the most important results:

Building the board (create_default_board_model): O(R·C).

Finding all pegs (get_pegs): O(R·C).

Building the graph (build_graph): up to O(P·R + R·C) in the worst case.

Computing expected values (compute_expected_values):

Graph building plus O(P + C) for the DP traversal.

Simulating one ball (simulate_fall): worst-case O(R²).

Choosing the best column (choose_best_column): O(C).

Drawing the board in the UIs: O(R·C) per full redraw.

## 7. How to Play

Choose which version to run:

main.py for a quick terminal game.

ui.py for a simple grid GUI.

plinko_pygame.py for the full neon Plinko experience.

### Game rules:

The game has a fixed number of rounds (5).

Each round:

Human chooses a column (click or input).

Human ball falls and scores points depending on the slot reached.

AI chooses a column using expected values and plays.

At the end, the total scores are compared and the winner is shown.

## 8. Possible Extensions

Some ideas that could be added in the future:

Let the user configure the board: size, peg pattern, slot scores.

Add a “Monte Carlo mode” where the AI estimates expected values by repeated simulation instead of DP.

Allow multiple balls per round or an entire “match” of many balls.

Add sound effects for peg hits and slot landings.

## 9. Development Challenges

Designing the peg physics

It took several attempts to find a get_children_of_peg / child_direction logic that:

Handled diagonal movement correctly.

Allowed a ball to fall straight down through empty cells.

Worked correctly at the bottom row and near the edges.

We also realized we needed an extra top row of empty cells so the ball could start above the first peg and not immediately collide.

Handling the edges (ragged walls)

At first, when the ball moved near the sides, it could slide straight down without meaningful interactions, which didn’t look like real Plinko.

We introduced vertical walls of pegs on the leftmost and rightmost columns to create a “ragged” boundary, so balls bounce off the edges instead of falling straight down.

Choosing the board size and pattern

Different requirements appeared during development:

Simple 30×7 board for the console version.

31×7 board for the game2dboard UI, with an extra empty row at the top.

Larger 35×25 board for the Pygame UI to make the game visually impressive.

We had to ensure that all of these boards still worked with the same BoardModel, graph_dp, and simulation logic.
It was also our way of testing that the code runs for all test cases (different board sizes)

Graph construction and dynamic programming

We had to carefully define how to represent pegs and slots as nodes and decide what the edges and probabilities should be.

Then we needed a recursive DP function that:

1. Correctly handled slot nodes and peg nodes.

2. Used memoization to avoid recomputing values for the same node.

3. Worked on a directed acyclic graph built from the board.

Debugging this required checking that neighbors, start_nodes, and expected_value were all correctly populated.

Linking modules and imports

We had to organize the code so main.py, ui.py, and plinko_pygame.py all import board, graph_dp, and simulation correctly.

This involved paying attention to file names, relative imports, and making sure we always used the same BoardModel interface.

Game2dboard UI layout issues

In the ui.py version, we initially ran into:

A very small board window where everything was cramped.

Outputs overlapping with the grid.

Slot scores not clearly visible.

We solved these by:

Adjusting cell_size, fonts, margin, and cell_spacing.

Adding gap rows between the last peg row and the slot row.

Tweaking colors to make pegs, text, and background more readable.

Ensuring the ball path is visible

In the grid UI, we wanted the human ball (blue) and AI ball (red) to be clearly visible:

We experimented with different symbols (●, emojis like 🔵 and 🔴).

We added pauses in animate_path to slow down the animation so players could follow the path.

Building the Pygame neon Plinko

Switching to Pygame introduced new challenges:

Computing a layout so the board is centered and scaled properly to the window.

Keeping the code readable while drawing circles, rectangles, and text.

We also had to map grid coordinates to pixel coordinates consistently so that the simulation path and the drawn board lined up correctly.

Animating the ball smoothly in Pygame

Instead of jumping from peg to peg, we wanted the ball to move smoothly along the path.

We implemented:

build_path_points to convert peg positions to a list of screen points.

update_animation to move a little bit toward the next point each frame.

We had to carefully handle when the ball reaches a point and when to advance to the next one, and ensure it doesn’t overshoot.

Game states and synchronization between human and AI turns

In the Pygame version, we needed to manage different states:

Waiting for human click.

Animating human ball.

Animating AI ball.

After round, before next click.

Game over.

We used variables like game_state, round_number, human_score, ai_score, and others to control the flow.

Getting the timing right (for example, starting the AI turn only after the human animation finishes) required some iteration.

Balancing aesthetics and readability

We adjusted colors, fonts, and board sizes multiple times until both readability and aesthetics felt right.