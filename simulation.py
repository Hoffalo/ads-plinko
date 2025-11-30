import random

def first_peg_position_for_column(board_model, column):
    if column < 0 or column >= board_model.number_of_columns:
        raise ValueError("Column is out of bounds")
    row = 0
    #move down until we find a peg or reach the bottom
    while row < board_model.number_of_rows and board_model.is_empty(row, column):
        row = row + 1
    if row < board_model.number_of_rows and board_model.is_peg(row, column):
        return (row, column)
    return None

def simulate_fall(board_model, start_column):
    position = first_peg_position_for_column(board_model, start_column)
    path_list = [] #store all the pegs the ball touches

    if position is None:
        final_slot_column = start_column
        return path_list, final_slot_column

    current_row, current_column = position
    path_list.append((current_row, current_column))

    while True:
        left_child, right_child = board_model.get_children_of_peg(current_row, current_column)

        if left_child is None and right_child is None:
            return path_list, None
# check this again
        random_value = random.random()
        if random_value < 0.5:
            chosen_child = left_child
            if chosen_child is None:
                chosen_child = right_child
        else:
            chosen_child = right_child
            if chosen_child is None:
                chosen_child = left_child

        if chosen_child is None:
            return path_list, None
#if the chosen child is an int, that means its a slot column
        if type(chosen_child) == int:
            final_slot_column = chosen_child
            return path_list, final_slot_column
        
#if not a slot then it must be another peg
        child_row, child_column = chosen_child
        current_row = child_row
        current_column = child_column
        path_list.append((current_row, current_column))

def simulate_fall_and_score(board_model, start_column):
    path_list, final_slot_column = simulate_fall(board_model, start_column)
    if final_slot_column is None:
        score = 0
    else:
        score = board_model.get_slot_score_at_column(final_slot_column)
    return path_list, final_slot_column, score
