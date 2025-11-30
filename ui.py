from game2dboard import Board
from board import BoardModel, EMPTY, PEG
import graph_dp
import simulation

board_model = None
board_gui = None
human_score = 0
ai_score = 0
last_human_round_score = 0
last_ai_round_score = 0
round_number = 1
max_rounds = 5
is_busy = False
game_over = False

def create_default_board_model():
    number_of_rows = 30
    number_of_columns = 7

    grid = []
    row_index = 0
    while row_index < number_of_rows:
        row = []
        column_index = 0
        while column_index < number_of_columns:
            row.append(EMPTY)
            column_index = column_index + 1
        grid.append(row)
        row_index = row_index + 1

    row_index = 0
    while row_index < number_of_rows:
        if row_index % 2 == 0:
            grid[row_index][1] = PEG
            grid[row_index][3] = PEG
            grid[row_index][5] = PEG
        else:
            grid[row_index][2] = PEG
            grid[row_index][4] = PEG
        row_index = row_index + 1

    row_index = 0
    while row_index < number_of_rows:
        grid[row_index][0] = PEG
        grid[row_index][number_of_columns - 1] = PEG
        row_index = row_index + 1

    slot_scores = [25, 50, 75, 200, 75, 50, 25]
    board_model_local = BoardModel(grid, slot_scores)
    return board_model_local

def clear_board_gui():
    row = 0
    while row < board_gui.rows:
        column = 0
        while column < board_gui.cols:
            board_gui[row][column] = ""
            column = column + 1
        row = row + 1

def update_scoreboard_row():
    scoreboard_row = 0
    column = 0
    while column < board_model.number_of_columns:
        board_gui[scoreboard_row][column] = ""
        column = column + 1
    board_gui[scoreboard_row][0] = "H:" + str(human_score)
    board_gui[scoreboard_row][3] = "R:" + str(round_number)
    board_gui[scoreboard_row][6] = "AI:" + str(ai_score)

def update_round_info_row(text):
    info_row = 1
    column = 0
    while column < board_model.number_of_columns:
        board_gui[info_row][column] = ""
        column = column + 1
    board_gui[info_row][0] = text

def draw_static_board():
    clear_board_gui()
    update_scoreboard_row()
    update_round_info_row("Click a column to drop your ball")

    offset = 2
    row = 0
    while row < board_model.number_of_rows:
        column = 0
        while column < board_model.number_of_columns:
            if board_model.is_peg(row, column):
                board_gui[row + offset][column] = "●"
            column = column + 1
        row = row + 1

    slot_row_gui = board_model.number_of_rows + offset
    column = 0
    while column < board_model.number_of_columns:
        score_value = board_model.get_slot_score_at_column(column)
        board_gui[slot_row_gui][column] = str(score_value)
        column = column + 1

def update_title():
    text = "Plinko – Human " + str(human_score) + " vs AI " + str(ai_score)
    board_gui.title = text

def animate_path(path_list, final_slot_column, score_value, player_symbol):
    offset = 2
    index = 0
    while index < len(path_list):
        row, column = path_list[index]
        gui_row = row + offset
        old_value = board_gui[gui_row][column]
        board_gui[gui_row][column] = player_symbol
        board_gui.pause(100)
        board_gui[gui_row][column] = old_value
        index = index + 1

    if final_slot_column is not None:
        slot_row_gui = board_model.number_of_rows + offset
        old_value = board_gui[slot_row_gui][final_slot_column]
        board_gui[slot_row_gui][final_slot_column] = player_symbol + " " + str(score_value)
        board_gui.pause(800)
        board_gui[slot_row_gui][final_slot_column] = old_value

def play_round(human_column):
    global human_score
    global ai_score
    global round_number
    global last_human_round_score
    global last_ai_round_score
    global game_over

    if game_over:
        return

    update_round_info_row("Human plays column " + str(human_column))
    path_list, final_slot_column, score_value = simulation.simulate_fall_and_score(board_model, human_column)
    animate_path(path_list, final_slot_column, score_value, "🔵")
    last_human_round_score = score_value
    human_score = human_score + score_value
    update_scoreboard_row()
    update_title()

    ai_column, ai_expected_value = graph_dp.choose_best_column(board_model)
    update_round_info_row("AI plays column " + str(ai_column))
    path_list_ai, final_slot_column_ai, score_value_ai = simulation.simulate_fall_and_score(board_model, ai_column)
    animate_path(path_list_ai, final_slot_column_ai, score_value_ai, "🔴")
    last_ai_round_score = score_value_ai
    ai_score = ai_score + score_value_ai
    update_scoreboard_row()
    update_title()

    text = "Last round H:+"
    text = text + str(last_human_round_score)
    text = text + "  AI:+"
    text = text + str(last_ai_round_score)
    update_round_info_row(text)

    round_number = round_number + 1
    if round_number > max_rounds:
        game_over = True
        if human_score > ai_score:
            final_text = "GAME OVER – Human wins!"
        elif ai_score > human_score:
            final_text = "GAME OVER – AI wins!"
        else:
            final_text = "GAME OVER – It is a tie!"
        update_round_info_row(final_text)
        update_title()

def handle_click(mouse_button, row, column):
    global is_busy
    if is_busy:
        return
    if game_over:
        return
    is_busy = True
    play_round(column)
    is_busy = False

def start_game():
    draw_static_board()
    update_title()

def main():
    global board_model
    global board_gui

    board_model = create_default_board_model()
    total_rows_gui = board_model.number_of_rows + 3

    board_gui = Board(total_rows_gui, board_model.number_of_columns)
    board_gui.cell_size = 28
    board_gui.font_size = 14
    board_gui.cell_color = "#fdf2ff"
    board_gui.grid_color = "#ff66b3"
    board_gui.margin = 20
    board_gui.cell_spacing = 1

    board_gui.on_start = start_game
    board_gui.on_mouse_click = handle_click

    board_gui.show()

if __name__ == "__main__":
    main()
