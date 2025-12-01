import pygame
import pygame.gfxdraw
from board import BoardModel, EMPTY, PEG
import graph_dp
import simulation
import math

FULLSCREEN = False

# --- COLOR PALETTE (Neon / Cyberpunk) ---
COLOR_BG_TOP       = (15, 10, 40)
COLOR_BG_BOTTOM    = (40, 20, 70)
COLOR_CABINET_BG   = (20, 15, 50)
COLOR_CABINET_BORDER = (180, 50, 220) # Purple/Pink border
COLOR_WALL_DECO    = (0, 200, 255)    # Cyan zig-zags

COLOR_GRID_LINES   = (255, 255, 255, 10) # Very faint grid

# Pegs
COLOR_PEG_GLOW     = (0, 150, 255)
COLOR_PEG_CORE     = (200, 240, 255)

# Balls
COLOR_HUMAN_BALL   = (255, 50, 200)   # Hot Pink
COLOR_AI_BALL      = (255, 220, 50)   # Bright Yellow

# Slots (Heatmap style: Pink=High, Blue=Low)
COLOR_SLOT_HIGH    = (255, 0, 100)
COLOR_SLOT_MID     = (180, 0, 200)
COLOR_SLOT_LOW     = (0, 100, 255)
COLOR_SLOT_TEXT    = (255, 255, 255)

# HUD
COLOR_HUD_BG       = (20, 10, 40, 200)
COLOR_HUD_BORDER   = (100, 50, 150)
COLOR_TEXT_MAIN    = (255, 255, 255)
COLOR_TEXT_ACCENT  = (0, 255, 255)

BALL_RADIUS = 9
PEG_RADIUS = 3

TOP_MARGIN = 50
BOTTOM_MARGIN_FOR_BOARD = 80
BOTTOM_HUD_HEIGHT = 100

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
ball_speed = 10.0 # Slightly faster for better feel

last_human_round_score = 0
last_ai_round_score = 0


# --- LOGIC SECTIONS (Kept mostly original) ---

def create_default_board_model():
    number_of_rows = 16  # Reduced rows slightly for better aspect ratio on screen
    number_of_columns = 15

    grid = []
    for r in range(number_of_rows):
        row = [EMPTY] * number_of_columns
        grid.append(row)

    # Standard Plinko Offset Pattern
    for r in range(1, number_of_rows):
        is_even_row = (r % 2 == 0)
        # Even rows: pegs at 1, 3, 5...
        # Odd rows: pegs at 2, 4, 6... 
        # (Logic adjusted to match original offset style)
        start_col = 1 if is_even_row else 2
        for c in range(start_col, number_of_columns - 1, 2):
            grid[r][c] = PEG

    # Walls
    for r in range(1, number_of_rows):
        grid[r][0] = PEG
        grid[r][number_of_columns - 1] = PEG

    # Calculate Slot Scores (Center = Highest)
    slot_scores = []
    center_column = (number_of_columns - 1) // 2
    for c in range(number_of_columns):
        distance = abs(c - center_column)
        # Exponential drop off for more excitement
        if distance == 0: value = 1000
        elif distance == 1: value = 500
        elif distance == 2: value = 200
        elif distance == 3: value = 100
        elif distance == 4: value = 50
        else: value = 10
        slot_scores.append(value)

    return BoardModel(grid, slot_scores)

def compute_layout(screen_width, screen_height):
    rows = board_model.number_of_rows
    cols = board_model.number_of_columns
    
    # We want the board to be centered and have specific margins
    avail_w = screen_width * 0.65 # Use 65% width to leave room for side UI look
    avail_h = screen_height - TOP_MARGIN - BOTTOM_HUD_HEIGHT - 20
    
    total_rows = rows + 1 # +1 for slots area
    
    cell_h = avail_h / total_rows
    cell_w = avail_w / cols
    cell_size = min(cell_h, cell_w)
    
    board_width = cell_size * cols
    board_height = cell_size * total_rows
    
    board_left = (screen_width - board_width) / 2
    board_top = TOP_MARGIN + (avail_h - board_height) / 2
    
    return {
        "board_left": board_left,
        "board_top": board_top,
        "board_width": board_width,
        "board_height": board_height,
        "cell_size": cell_size,
        "gap_rows": 1
    }

def grid_to_pixel(layout, row, column):
    # Center the peg in the cell
    x = layout["board_left"] + (column + 0.5) * layout["cell_size"]
    y = layout["board_top"] + (row + 0.5) * layout["cell_size"]
    return x, y

def build_path_points(layout, start_column, path_list, final_slot_column):
    points = []
    # Start slightly above board
    start_x, start_y = grid_to_pixel(layout, -1, start_column)
    points.append((start_x, start_y))

    for (r, c) in path_list:
        x, y = grid_to_pixel(layout, r, c)
        points.append((x, y))

    if final_slot_column is not None:
        rows = board_model.number_of_rows
        # Drop into the slot visually
        x_slot, y_slot = grid_to_pixel(layout, rows, final_slot_column)
        points.append((x_slot, y_slot))
        # Add a small bounce at the bottom
        points.append((x_slot, y_slot - 5))
        points.append((x_slot, y_slot))

    return points

def handle_human_click(layout, mouse_x, mouse_y):
    global game_state, ball_x, ball_y, ball_color
    global path_points, path_index, last_human_round_score

    if game_state != "WAIT_CLICK":
        return

    # Hitbox for the top drop area
    board_left = layout["board_left"]
    board_width = layout["board_width"]
    
    # Allow clicking slightly above the board
    if not (board_left < mouse_x < board_left + board_width):
        return
    if mouse_y > layout["board_top"] + layout["board_height"]:
        return

    relative_x = mouse_x - board_left
    column = int(relative_x / layout["cell_size"])
    
    if column < 0: column = 0
    if column >= board_model.number_of_columns: column = board_model.number_of_columns - 1

    # Logic
    path_list, final_slot_column, score_value = simulation.simulate_fall_and_score(
        board_model, column
    )
    last_human_round_score = score_value

    points = build_path_points(layout, column, path_list, final_slot_column)
    path_points[:] = points
    path_index = 1
    ball_x, ball_y = points[0]
    ball_color = COLOR_HUMAN_BALL
    game_state = "ANIM_HUMAN"

def start_ai_turn(layout):
    global game_state, ball_x, ball_y, ball_color
    global path_points, path_index, last_ai_round_score

    ai_column, _ = graph_dp.choose_best_column(board_model)
    path_list, final_slot_column, score_value = simulation.simulate_fall_and_score(
        board_model, ai_column
    )
    last_ai_round_score = score_value

    points = build_path_points(layout, ai_column, path_list, final_slot_column)
    path_points[:] = points
    path_index = 1
    ball_x, ball_y = points[0]
    ball_color = COLOR_AI_BALL
    game_state = "ANIM_AI"

def update_animation():
    global ball_x, ball_y, path_index, game_state
    global human_score, ai_score, round_number

    if game_state not in ("ANIM_HUMAN", "ANIM_AI"):
        return

    if path_index >= len(path_points):
        if game_state == "ANIM_HUMAN":
            human_score += last_human_round_score
            game_state = "AFTER_HUMAN"
        else:
            ai_score += last_ai_round_score
            round_number += 1
            if round_number > max_rounds:
                game_state = "GAME_OVER"
            else:
                game_state = "WAIT_CLICK"
        return

    target_x, target_y = path_points[path_index]
    dx = target_x - ball_x
    dy = target_y - ball_y
    dist = math.hypot(dx, dy)

    if dist <= ball_speed:
        ball_x = target_x
        ball_y = target_y
        path_index += 1
    else:
        ball_x += (dx / dist) * ball_speed
        ball_y += (dy / dist) * ball_speed


# --- RENDER HELPERS ---

def draw_vertical_gradient(surface, top_color, bottom_color):
    """ Fills the surface with a vertical gradient """
    height = surface.get_height()
    # Draw strictly integer rectangles to avoid gaps
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

def draw_glowing_circle(surface, color, center, radius, glow_radius):
    """ Draws a solid circle with a translucent glow around it """
    # Glow (Draw multiple transparent circles)
    x, y = center
    for r in range(glow_radius, radius, -2):
        alpha = int(100 * (1 - (r / glow_radius)))
        if alpha < 0: alpha = 0
        pygame.gfxdraw.filled_circle(surface, int(x), int(y), r, (*color, alpha))
    
    # Core
    pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), radius)

def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def draw_neon_board_bg(surface, layout):
    """ Draws the decorative cabinet around the board """
    l = layout["board_left"]
    t = layout["board_top"]
    w = layout["board_width"]
    h = layout["board_height"]
    cs = layout["cell_size"]

    # Main Cabinet Body (Rounded Rect)
    padding = 20
    rect = pygame.Rect(l - padding, t - padding, w + padding*2, h + padding*2 + 20)
    
    # Draw dark backing
    pygame.draw.rect(surface, COLOR_CABINET_BG, rect, border_radius=30)
    # Draw glowing border
    pygame.draw.rect(surface, COLOR_CABINET_BORDER, rect, width=4, border_radius=30)
    pygame.draw.rect(surface, (100, 20, 100), rect.inflate(4,4), width=2, border_radius=30)

    # Zig-Zag Decoration on sides (The "Bumper" look)
    # Left Side
    rows = board_model.number_of_rows
    for r in range(rows):
        if r % 2 != 0: continue
        # Triangle pointing in
        y_pos = t + (r + 0.5) * cs
        p1 = (l - 5, y_pos - cs/2)
        p2 = (l + 10, y_pos)
        p3 = (l - 5, y_pos + cs/2)
        pygame.draw.polygon(surface, COLOR_WALL_DECO, [p1, p2, p3])
        # Right Side
        p1 = (l + w + 5, y_pos - cs/2)
        p2 = (l + w - 10, y_pos)
        p3 = (l + w + 5, y_pos + cs/2)
        pygame.draw.polygon(surface, COLOR_WALL_DECO, [p1, p2, p3])

def draw_slots(surface, layout, font):
    cols = board_model.number_of_columns
    rows = board_model.number_of_rows
    cs = layout["cell_size"]
    
    y_start = layout["board_top"] + rows * cs
    
    max_score = 1000
    
    for c in range(cols):
        x = layout["board_left"] + c * cs
        score = board_model.get_slot_score_at_column(c)
        
        # Determine Color based on score (Heatmap)
        t = score / max_score # 0.0 to 1.0
        # Lerp between Blue (Low) -> Purple -> Pink (High)
        if t < 0.5:
            color = lerp_color(COLOR_SLOT_LOW, COLOR_SLOT_MID, t * 2)
        else:
            color = lerp_color(COLOR_SLOT_MID, COLOR_SLOT_HIGH, (t - 0.5) * 2)
        
        # Draw "Light Beam" gradient going up
        # Create a small surface for the beam
        beam_h = int(cs * 2)
        beam_surf = pygame.Surface((int(cs), beam_h), pygame.SRCALPHA)
        for i in range(beam_h):
            alpha = int(50 * (1 - i/beam_h)) # Fade out going up
            pygame.draw.line(beam_surf, (*color, alpha), (0, beam_h - i), (int(cs), beam_h - i))
        surface.blit(beam_surf, (x, y_start - beam_h))

        # Draw Slot Box
        slot_rect = pygame.Rect(x + 2, y_start, cs - 4, cs * 1.5)
        
        # Fill
        s = pygame.Surface((slot_rect.width, slot_rect.height), pygame.SRCALPHA)
        s.fill((*color, 100)) # Semi transparent fill
        surface.blit(s, slot_rect.topleft)
        
        # Border
        pygame.draw.rect(surface, color, slot_rect, 2, border_radius=5)
        
        # Text (Vertical if space is tight, or small)
        txt_img = font.render(str(score), True, COLOR_SLOT_TEXT)
        # Rotate text if too wide
        if txt_img.get_width() > cs - 4:
            txt_img = pygame.transform.rotate(txt_img, 90)
            
        txt_rect = txt_img.get_rect(center=slot_rect.center)
        surface.blit(txt_img, txt_rect)


def draw_game(screen, layout, glow_surface, font_slot, font_hud, font_title):
    w, h = screen.get_size()
    
    # 1. Background
    draw_vertical_gradient(screen, COLOR_BG_TOP, COLOR_BG_BOTTOM)
    
    # 2. Draw Board Structure
    draw_neon_board_bg(screen, layout)
    
    # 3. Draw Pegs (Static)
    rows = board_model.number_of_rows
    cols = board_model.number_of_columns
    
    # Prepare Glow Layer (Clear it)
    glow_surface.fill((0,0,0,0))
    
    for r in range(rows):
        for c in range(cols):
            if board_model.is_peg(r, c):
                px, py = grid_to_pixel(layout, r, c)
                # Draw Glow on glow_surface
                pygame.draw.circle(glow_surface, (*COLOR_PEG_GLOW, 100), (int(px), int(py)), PEG_RADIUS + 4)
                # Draw Core on main screen
                pygame.draw.circle(screen, COLOR_PEG_CORE, (int(px), int(py)), PEG_RADIUS)
    
    # 4. Draw Slots
    draw_slots(screen, layout, font_slot)
    
    # 5. Draw Ball (with glow)
    if game_state in ("ANIM_HUMAN", "ANIM_AI"):
        # Glow
        pygame.draw.circle(glow_surface, (*ball_color, 150), (int(ball_x), int(ball_y)), BALL_RADIUS + 8)
        # Core
        pygame.draw.circle(screen, (255, 255, 255), (int(ball_x), int(ball_y)), BALL_RADIUS)
        pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), BALL_RADIUS - 2)

    # Blit Glow Surface (Additive Blend for neon look)
    screen.blit(glow_surface, (0,0), special_flags=pygame.BLEND_ADD)
    
    # 6. Draw Right-Side "Details" Panel (Visual only, based on reference)
    panel_w = 200
    panel_x = w - panel_w - 20
    panel_rect = pygame.Rect(panel_x, layout["board_top"], panel_w, layout["board_height"])
    
    # Panel Background
    s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, 100), s.get_rect(), border_radius=15)
    screen.blit(s, panel_rect.topleft)
    pygame.draw.rect(screen, COLOR_HUD_BORDER, panel_rect, 2, border_radius=15)
    
    # Panel Title
    title = font_hud.render("Stats", True, COLOR_TEXT_ACCENT)
    screen.blit(title, (panel_x + 20, layout["board_top"] + 20))
    
    # Stats Content
    stats = [
        f"Round: {round_number}/{max_rounds}",
        "",
        "HUMAN",
        f"{human_score}",
        "",
        "AI",
        f"{ai_score}"
    ]
    
    dy = 60
    for line in stats:
        if line in ["HUMAN", "AI"]:
            col = COLOR_TEXT_ACCENT
        else:
            col = COLOR_TEXT_MAIN
        
        txt = font_hud.render(line, True, col)
        screen.blit(txt, (panel_x + 20, layout["board_top"] + dy))
        dy += 35

    # 7. Draw Bottom HUD / Game Over
    hud_rect = pygame.Rect(w/2 - 300, h - BOTTOM_HUD_HEIGHT + 10, 600, BOTTOM_HUD_HEIGHT - 20)
    
    s_hud = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s_hud, COLOR_HUD_BG, s_hud.get_rect(), border_radius=20)
    screen.blit(s_hud, hud_rect.topleft)
    pygame.draw.rect(screen, COLOR_HUD_BORDER, hud_rect, 2, border_radius=20)
    
    # Status Text
    status_text = ""
    if game_state == "WAIT_CLICK": status_text = "CLICK TO DROP BALL"
    elif game_state == "ANIM_HUMAN": status_text = "DROPPING..."
    elif game_state == "ANIM_AI": status_text = "AI TURN..."
    elif game_state == "AFTER_HUMAN": status_text = f"SCORED +{last_human_round_score}"
    elif game_state == "GAME_OVER": 
        if human_score > ai_score: status_text = "YOU WIN!"
        elif ai_score > human_score: status_text = "AI WINS!"
        else: status_text = "TIE!"
        
    status_img = font_title.render(status_text, True, COLOR_TEXT_MAIN)
    status_rect = status_img.get_rect(center=hud_rect.center)
    screen.blit(status_img, status_rect)


def main():
    global board_model

    pygame.init()
    
    # Window Setup
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

    pygame.display.set_caption("Plinko: Neon Edition")

    board_model = create_default_board_model()
    layout = compute_layout(sw, sh)
    
    # Surface for additive blending (Glows)
    glow_surface = pygame.Surface((sw, sh), pygame.SRCALPHA)

    # Fonts
    font_slot = pygame.font.SysFont("segoeui", 12, bold=True)
    font_hud  = pygame.font.SysFont("segoeui", 24)
    font_title = pygame.font.SysFont("segoeui", 40, bold=True)

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
            # Small delay logic could go here, but for now instant transition
            start_ai_turn(layout)

        draw_game(screen, layout, glow_surface, font_slot, font_hud, font_title)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()