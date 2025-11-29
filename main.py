from board import BoardModel, EMPTY, PEG
import graph_dp
import simulation

def create_default_board_model():
    grid = [
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
        [EMPTY, PEG,   EMPTY, PEG,   EMPTY, PEG,   EMPTY],
        [EMPTY, EMPTY, PEG,   EMPTY, PEG,   EMPTY, EMPTY],
    ]
    slot_scores = [10, 20, 50, 100, 50, 20, 10]
    board_model = BoardModel(grid, slot_scores)
    return board_model

def print_expected_values(board_model):
    expected_values_list = graph_dp.compute_expected_values(board_model)
    print("Expected values per column:")
    for column in range(board_model.number_of_columns):
        print("Column", column, ":", expected_values_list[column])

def demo_ai_move(board_model):
    best_column, best_value = graph_dp.choose_best_column(board_model)
    print("The AI has chosen the column", best_column, "with the expected value of", best_value)
    path_list, final_slot_column, score = simulation.simulate_fall_and_score(board_model, best_column)
    print("The AI's path:", path_list)
    print("The AI's final slot column:", final_slot_column)
    print("The AI's score this run:", score)

def demo_human_move(board_model, human_column):
    print("Player one has chosen the column", human_column)
    path_list, final_slot_column, score = simulation.simulate_fall_and_score(board_model, human_column)
    print("Player one's path:", path_list)
    print("Player one's final slot column:", final_slot_column)
    print("Player one's score this run:", score)
def main():
    board_model = create_default_board_model()
    print_expected_values(board_model)

    human_column = 3
    demo_human_move(board_model, human_column)

    demo_ai_move(board_model)

if __name__ == "__main__":
    main()
