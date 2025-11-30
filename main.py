from board import BoardModel, EMPTY, PEG
import graph_dp
import simulation


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
    #add pegs
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
    board_model = BoardModel(grid, slot_scores)
    return board_model

def ask_human_column(board_model):
    while True:
        text = input("Choose a column from 0 to " + str(board_model.number_of_columns - 1) + ": ")
        try:
            column = int(text)
        except ValueError:
            print("Please type a number.")
            continue
        if 0 <= column < board_model.number_of_columns:
            return column
        print("Column is out of range.")

#main game loop
def play_game():
    board_model = create_default_board_model()
    human_score = 0
    ai_score = 0
    number_of_rounds = 5
    current_round = 1

    while current_round <= number_of_rounds:
        print("Round ", current_round,)
        human_column = ask_human_column(board_model)
        #calling simulation code  
        human_path, human_slot, human_round_score = simulation.simulate_fall_and_score(board_model, human_column)
        print("Player one's path:", human_path)
        print("Player one's final slot column:", human_slot)
        print("Player one's round score:", human_round_score)
        human_score = human_score + human_round_score

        ai_column, ai_expected_value = graph_dp.choose_best_column(board_model)
        print("AI chooses column", ai_column)
        ai_path, ai_slot, ai_round_score = simulation.simulate_fall_and_score(board_model, ai_column)
        print("AI path:", ai_path)
        print("AI final slot column:", ai_slot)
        print("AI round score:", ai_round_score)
        ai_score = ai_score + ai_round_score

        print("Total player one's score:", human_score)
        print("Total AI score:", ai_score)
        current_round = current_round + 1

    print("GAME OVER!!!!")
    print("Final player one's score:", human_score)
    print("Final AI score:", ai_score)
    if human_score > ai_score:
        print("Player one wins!")
    elif ai_score > human_score:
        print("AI wins!")
    else:
        print("It is a tie.")

def main():
    play_game()

if __name__ == "__main__":
    main()