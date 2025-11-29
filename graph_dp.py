EMPTY = 0
PEG = 1

def node_for_peg(row, column):
    return ("peg", row, column)

def node_for_slot(column):
    return ("slot", column)

def build_graph(board_model):
    neighbors = {}
    start_nodes = {}

    peg_list = board_model.get_pegs()

    for peg_row, peg_column in peg_list:
        peg_node = node_for_peg(peg_row, peg_column)
        if peg_node not in neighbors:
            neighbors[peg_node] = []

        left_child, right_child = board_model.get_children_of_peg(peg_row, peg_column)

        for child in (left_child, right_child):
            if child is None:
                continue
            if type(child) == int:
                slot_column = child
                slot_node = node_for_slot(slot_column)
                if slot_node not in neighbors:
                    neighbors[slot_node] = []
                neighbors[peg_node].append((slot_node, 0.5))
            else:
                child_row, child_column = child
                child_peg_node = node_for_peg(child_row, child_column)
                if child_peg_node not in neighbors:
                    neighbors[child_peg_node] = []
                neighbors[peg_node].append((child_peg_node, 0.5))

    number_of_columns = board_model.number_of_columns

    for column in range(number_of_columns):
        start_node = first_node_for_column(board_model, column)
        start_nodes[column] = start_node
        if start_node is not None and start_node not in neighbors:
            neighbors[start_node] = []

    return neighbors, start_nodes
def first_node_for_column(board_model, column):
    row = 0
    while row < board_model.number_of_rows and board_model.is_empty(row, column):
        row = row + 1

    if row < board_model.number_of_rows and board_model.is_peg(row, column):
        return node_for_peg(row, column)

    return node_for_slot(column)

def compute_expected_values(board_model):
    neighbors, start_nodes = build_graph(board_model)
    expected_value = {}

    def expected_value_for_node(node):
        if node in expected_value:
            return expected_value[node]
        kind = node[0]

        if kind == "slot":
            slot_column = node[1]
            value = float(board_model.get_slot_score_at_column(slot_column))
            expected_value[node] = value
            return value

        neighbor_list = neighbors.get(node, [])

        if not neighbor_list:
            value = 0.0
            expected_value[node] = value
            return value

        total = 0.0
        for child_node, probability in neighbor_list:
            child_value = expected_value_for_node(child_node)
            total = total + probability * child_value

        expected_value[node] = total
        return total

    result_list = []
    for column in range(board_model.number_of_columns):
        start_node = start_nodes.get(column)
        if start_node is None:
            result_list.append(0.0)
        else:
            result_list.append(expected_value_for_node(start_node))

    return result_list

def choose_best_column(board_model):
    expected_values_list = compute_expected_values(board_model)
    best_column = 0
    best_value = expected_values_list[0]

    for column in range(1, len(expected_values_list)):
        if expected_values_list[column] > best_value:
            best_value = expected_values_list[column]
            best_column = column

    return best_column, best_value