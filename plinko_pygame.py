import pygame
from board import BoardModel, EMPTY, PEG
import graph_dp
import simulation

FULLSCREEN = False

COLOR_BACKGROUND   = (10, 5, 35)
COLOR_BOARD_PANEL  = (7, 20, 70)
COLOR_BOARD_BORDER = (0, 180, 255)
COLOR_BOARD_GLOW   = (255, 0, 200)
COLOR_GRID         = (40, 100, 190)
COLOR_PEG_OUTER    = (0, 255, 255)
COLOR_PEG_INNER    = (180, 255, 255)

# Each slot column will use one of these base colors (rainbow style)
SLOT_BASE_COLORS = [
    (0, 220, 255),   # cyan
    (0, 255, 200),   # aqua-green
    (120, 255, 120), # green
    (255, 220, 0),   # yellow
    (255, 170, 0),   # orange
    (255, 80, 120),  # pink
    (180, 80, 255)   # purple
]
COLOR_SLOT_BORDER  = (255, 255, 255)
COLOR_SLOT_TEXT    = (10, 10, 20)

COLOR_TEXT         = (230, 230, 250)
COLOR_HUMAN_BALL   = (255, 105, 255)
COLOR_AI_BALL      = (255, 255, 120)
COLOR_HUD_PANEL    = (30, 15, 80)

BALL_RADIUS = 10
PEG_RADIUS_OUTER = 5
PEG_RADIUS_INNER = 3

TOP_MARGIN = 60
BOTTOM_MARGIN_FOR_BOARD = 60
BOTTOM_HUD_HEIGHT = 90

board_model = None
human_score = 0
ai_score = 0
round_number = 1
max_rounds = 5

game_state = "WAIT_CLICK"
ball_x = 0.0
ball_y = 0.0
ball_color = COLOR_HUMAN_BALL
path_points = []
path_index = 0
ball_speed = 10.0

last_human_round_score = 0
last_ai_round_score = 0


def create_default_board_model():
    # Bigger Plinko board: 35 rows (tall), 25 columns (wide)
    number_of_rows = 35
    number_of_columns = 25

    # Start with all cells empty
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

    # Staggered peg pattern inside (no pegs in row 0 so the top is free)
    row_index = 1
    while row_index < number_of_rows:
        if row_index % 2 == 0:
            # even rows: pegs in odd columns 1,3,5,... up to column before last
            column = 1
            while column < number_of_columns - 1:
                grid[row_index][column] = PEG
                column = column + 2
        else:
            # odd rows: pegs in even columns 2,4,6,...
            column = 2
            while column < number_of_columns - 1:
                grid[row_index][column] = PEG
                column = column + 2
        row_index = row_index + 1

    # Ragged vertical walls on left and right edges
    row_index = 1
    while row_index < number_of_rows:
        grid[row_index][0] = PEG
        grid[row_index][number_of_columns - 1] = PEG
        row_index = row_index + 1

    # Slot scores: center high, edges low, computed automatically
    slot_scores = []
    center_column = (number_of_columns - 1) // 2
    column_index = 0
    while column_index < number_of_columns:
        distance = column_index - center_column
        if distance < 0:
            distance = -distance
        # Highest value at the center, decreasing toward edges
        value = 300 - distance * 15
        if value < 10:
            value = 10
        slot_scores.append(value)
        column_index = column_index + 1

    board_model_local = BoardModel(grid, slot_scores)
    return board_model_local

def compute_layout(screen_width, screen_height):
    rows = board_model.number_of_rows
    cols = board_model.number_of_columns
    gap_rows = 2
    slot_rows = 1
    total_rows = rows + gap_rows + slot_rows

    available_height = screen_height - TOP_MARGIN - BOTTOM_MARGIN_FOR_BOARD - BOTTOM_HUD_HEIGHT
    cell_size_by_height = available_height / float(total_rows)

    # Let the board use up to 90% of the screen width
    max_board_width = screen_width * 0.9
    cell_size_by_width = max_board_width / float(cols)

    cell_size = min(cell_size_by_height, cell_size_by_width)

    board_height = cell_size * total_rows
    board_width = cell_size * cols

    board_left = (screen_width - board_width) / 2.0
    board_top = TOP_MARGIN

    layout = {
        "board_left": board_left,
        "board_top": board_top,
        "board_width": board_width,
        "board_height": board_height,
        "cell_size": cell_size,
        "gap_rows": gap_rows,
        "total_rows": total_rows
    }
    return layout


def grid_to_pixel(layout, row, column):
    x = layout["board_left"] + (column + 0.5) * layout["cell_size"]
    y = layout["board_top"] + (row + 0.5) * layout["cell_size"]
    return x, y


def build_path_points(layout, start_column, path_list, final_slot_column):
    points = []

    start_x, start_y = grid_to_pixel(layout, -1, start_column)
    points.append((start_x, start_y))

    index = 0
    while index < len(path_list):
        row, column = path_list[index]
        x, y = grid_to_pixel(layout, row, column)
        points.append((x, y))
        index = index + 1

    if final_slot_column is not None:
        rows = board_model.number_of_rows
        gap_rows = layout["gap_rows"]
        slot_row = rows + gap_rows
        x_slot, y_slot = grid_to_pixel(layout, slot_row, final_slot_column)
        points.append((x_slot, y_slot))

    return points


def handle_human_click(layout, mouse_x, mouse_y):
    global game_state, ball_x, ball_y, ball_color
    global path_points, path_index, last_human_round_score

    if game_state != "WAIT_CLICK":
        return

    board_left = layout["board_left"]
    board_width = layout["board_width"]
    cell_size = layout["cell_size"]
    board_top = layout["board_top"]
    board_height = layout["board_height"]

    if mouse_y < board_top or mouse_y > board_top + board_height:
        return

    relative_x = mouse_x - board_left
    if relative_x < 0 or relative_x > board_width:
        return

    column = int(relative_x / cell_size)
    if column < 0 or column >= board_model.number_of_columns:
        return

    path_list, final_slot_column, score_value = simulation.simulate_fall_and_score(
        board_model,
        column
    )
    last_human_round_score = score_value

    points = build_path_points(layout, column, path_list, final_slot_column)
    path_points[:] = points
    global path_index
    path_index = 1
    global ball_x, ball_y
    ball_x, ball_y = points[0]
    ball_color = COLOR_HUMAN_BALL
    globals()["game_state"] = "ANIM_HUMAN"


def start_ai_turn(layout):
    global game_state, ball_x, ball_y, ball_color
    global path_points, path_index, last_ai_round_score

    ai_column, ai_expected_value = graph_dp.choose_best_column(board_model)
    path_list, final_slot_column, score_value = simulation.simulate_fall_and_score(
        board_model,
        ai_column
    )
    last_ai_round_score = score_value

    points = build_path_points(layout, ai_column, path_list, final_slot_column)
    path_points[:] = points
    path_index = 1
    ball_x, ball_y = points[0]
    ball_color = COLOR_AI_BALL
    globals()["game_state"] = "ANIM_AI"


def update_animation():
    global ball_x, ball_y, path_index, game_state
    global human_score, ai_score, round_number

    if game_state != "ANIM_HUMAN" and game_state != "ANIM_AI":
        return

    if path_index >= len(path_points):
        if game_state == "ANIM_HUMAN":
            human_score = human_score + last_human_round_score
            globals()["game_state"] = "AFTER_HUMAN"
        else:
            ai_score = ai_score + last_ai_round_score
            round_number = round_number + 1
            if round_number > max_rounds:
                globals()["game_state"] = "GAME_OVER"
            else:
                globals()["game_state"] = "WAIT_CLICK"
        return

    target_x, target_y = path_points[path_index]
    dx = target_x - ball_x
    dy = target_y - ball_y
    distance_sq = dx * dx + dy * dy

    if distance_sq <= ball_speed * ball_speed:
        ball_x = target_x
        ball_y = target_y
        path_index = path_index + 1
    else:
        distance = distance_sq ** 0.5
        if distance == 0:
            path_index = path_index + 1
            return
        step_x = ball_speed * dx / distance
        step_y = ball_speed * dy / distance
        ball_x = ball_x + step_x
        ball_y = ball_y + step_y


def draw_neon_frame(surface, layout):
    board_left = layout["board_left"]
    board_top = layout["board_top"]
    board_width = layout["board_width"]
    board_height = layout["board_height"]

    outer_rect = pygame.Rect(
        int(board_left - 25),
        int(board_top - 50),
        int(board_width + 50),
        int(board_height + 80)
    )
    pygame.draw.rect(surface, COLOR_BOARD_GLOW, outer_rect, border_radius=30)

    inner_rect = outer_rect.inflate(-14, -14)
    pygame.draw.rect(surface, COLOR_BOARD_BORDER, inner_rect, border_radius=24)

    panel_rect = pygame.Rect(
        int(board_left),
        int(board_top),
        int(board_width),
        int(board_height)
    )
    pygame.draw.rect(surface, COLOR_BOARD_PANEL, panel_rect)

    rail_width = layout["cell_size"] * 0.6
    left_rail = pygame.Rect(
        int(board_left),
        int(board_top),
        int(rail_width),
        int(board_height)
    )
    right_rail = pygame.Rect(
        int(board_left + board_width - rail_width),
        int(board_top),
        int(rail_width),
        int(board_height)
    )
    pygame.draw.rect(surface, COLOR_BOARD_BORDER, left_rail)
    pygame.draw.rect(surface, COLOR_BOARD_BORDER, right_rail)


def draw_board(surface, layout, font_small):
    surface.fill(COLOR_BACKGROUND)
    draw_neon_frame(surface, layout)

    cell = layout["cell_size"]
    board_left = layout["board_left"]
    board_top = layout["board_top"]
    rows = board_model.number_of_rows
    cols = board_model.number_of_columns
    gap_rows = layout["gap_rows"]

    row_index = 0
    while row_index <= rows + gap_rows:
        y = board_top + row_index * cell
        pygame.draw.line(
            surface,
            COLOR_GRID,
            (board_left, y),
            (board_left + cols * cell, y),
            1
        )
        row_index = row_index + 1

    col_index = 0
    while col_index <= cols:
        x = board_left + col_index * cell
        pygame.draw.line(
            surface,
            COLOR_GRID,
            (x, board_top),
            (x, board_top + (rows + gap_rows) * cell),
            1
        )
        col_index = col_index + 1

    row = 0
    while row < rows:
        column = 0
        while column < cols:
            if board_model.is_peg(row, column):
                x, y = grid_to_pixel(layout, row, column)
                pygame.draw.circle(
                    surface,
                    COLOR_PEG_OUTER,
                    (int(x), int(y)),
                    PEG_RADIUS_OUTER
                )
                pygame.draw.circle(
                    surface,
                    COLOR_PEG_INNER,
                    (int(x), int(y - 1)),
                    PEG_RADIUS_INNER
                )
            column = column + 1
        row = row + 1

    slot_row = rows + gap_rows
    column = 0
    while column < cols:
        x, y = grid_to_pixel(layout, slot_row, column)
        base_color = SLOT_BASE_COLORS[column % len(SLOT_BASE_COLORS)]

        # Make the slot bar taller and more prominent
        rect_width = cell - 4
        rect_height = cell * 1.3
        rect_left = int(x - rect_width / 2)
        rect_top = int(y - rect_height / 2 + cell * 0.2)

        rect = pygame.Rect(
            rect_left,
            rect_top,
            int(rect_width),
            int(rect_height)
        )
        pygame.draw.rect(surface, base_color, rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_SLOT_BORDER, rect, 2, border_radius=6)

        score_value = board_model.get_slot_score_at_column(column)
        text_surface = font_small.render(str(score_value), True, COLOR_SLOT_TEXT)
        text_rect = text_surface.get_rect(center=(x, rect_top + rect_height / 2 + cell * 0.1))
        surface.blit(text_surface, text_rect)

        column = column + 1


def draw_ball(surface):
    if game_state == "ANIM_HUMAN" or game_state == "ANIM_AI":
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(ball_x), int(ball_y - 2)),
            BALL_RADIUS - 4
        )
        pygame.draw.circle(
            surface,
            ball_color,
            (int(ball_x), int(ball_y)),
            BALL_RADIUS
        )


def draw_hud(surface, layout, font_small, font_big, font_huge):
    screen_width, screen_height = surface.get_size()

    hud_rect = pygame.Rect(
        0,
        screen_height - BOTTOM_HUD_HEIGHT,
        screen_width,
        BOTTOM_HUD_HEIGHT
    )
    pygame.draw.rect(surface, COLOR_HUD_PANEL, hud_rect)

    header_text = f"H {human_score}   R {round_number}/{max_rounds}   AI {ai_score}"
    header_surface = font_big.render(header_text, True, COLOR_TEXT)
    header_rect = header_surface.get_rect()
    header_rect.midleft = (20, screen_height - BOTTOM_HUD_HEIGHT / 2)
    surface.blit(header_surface, header_rect)

    if game_state == "WAIT_CLICK":
        msg = "Click anywhere on the board to drop your ball"
    elif game_state == "ANIM_HUMAN":
        msg = "Human ball falling..."
    elif game_state == "ANIM_AI":
        msg = "AI ball falling..."
    elif game_state == "AFTER_HUMAN":
        msg = f"Human gained {last_human_round_score}"
    elif game_state == "GAME_OVER":
        if human_score > ai_score:
            msg = f"GAME OVER – Human +{human_score - ai_score}"
        elif ai_score > human_score:
            msg = f"GAME OVER – AI +{ai_score - human_score}"
        else:
            msg = "GAME OVER – Tie"
    else:
        msg = ""

    msg_surface = font_small.render(msg, True, COLOR_TEXT)
    msg_rect = msg_surface.get_rect()
    msg_rect.midright = (screen_width - 20, screen_height - BOTTOM_HUD_HEIGHT / 2)
    surface.blit(msg_surface, msg_rect)

    if game_state == "GAME_OVER":
        if human_score > ai_score:
            winner_text = "HUMAN WINS"
            color = COLOR_HUMAN_BALL
        elif ai_score > human_score:
            winner_text = "AI WINS"
            color = COLOR_AI_BALL
        else:
            winner_text = "TIE"
            color = COLOR_TEXT

        winner_surface = font_huge.render(winner_text, True, color)
        winner_rect = winner_surface.get_rect()
        winner_rect.center = (screen_width / 2, TOP_MARGIN / 2)
        surface.blit(winner_surface, winner_rect)


def main():
    global board_model, game_state

    pygame.init()

    info = pygame.display.Info()
    sw = info.current_w
    sh = info.current_h

    if FULLSCREEN:
        screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)
    else:
        width = int(sw * 0.9)
        height = int(sh * 0.9)
        screen = pygame.display.set_mode((width, height))
        sw, sh = width, height

    pygame.display.set_caption("Plinko – Neon edition")

    board_model_local = create_default_board_model()
    globals()["board_model"] = board_model_local

    layout = compute_layout(sw, sh)

    font_small = pygame.font.SysFont("arial", 10, bold=True)
    font_big   = pygame.font.SysFont("arial", 30, bold=True)
    font_huge  = pygame.font.SysFont("arial", 70, bold=True)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_human_click(layout, event.pos[0], event.pos[1])

        update_animation()

        if game_state == "AFTER_HUMAN":
            start_ai_turn(layout)

        draw_board(screen, layout, font_small)
        draw_ball(screen)
        draw_hud(screen, layout, font_small, font_big, font_huge)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
