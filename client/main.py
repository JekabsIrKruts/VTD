"""Pygame screens, buttons, input handling, and drawing for the game model."""

# CLIENT CODE MAP
# 1. API score submission and display/texture helpers.
# 2. Question and Mama Frog screens.
# 3. Main menu, completion, and game-over screens.
# 4. play_game(): game setup, input, simulation, and board drawing.
# 5. main(): moves between the menu and game screens.

import json
import math
import random
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path

import pygame

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.rules import (
    ENEMY_TYPES,
    GRASS_GREEN,
    PATH_1,
    PATH_1_END_X,
    PATH_1_THICKNESS,
    PATH_SEGMENTS,
    PLAYER_MAX_HP,
    ROAD_BLUE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TOWER_TYPES,
    WINGS_PER_HP,
    Game,
)


SCALE_X = 1.0
SCALE_Y = 1.0
_AURA_SURFACES = {}
TEXTURE_DIR = Path(project_root) / "assets" / "textures"
BOARD_TEXTURE_SCALE = 1.5
_TEXTURES = {}
_SCALED_TEXTURES = {}
ENEMY_TEXTURES = {
    "musas": "musa",
    "scorpion_musas": "Scorpion_musa",
    "stalk_eyed_musas": "Stalk-eyed_musa",
    "bee_musas": "bee_fly",
    "mydas_musas": "mydas_fly",
    "picture_winged_musas": "picture-winged_fly",
    "mama_musa": "mama_musa",
}
TOWER_TEXTURES = {
    "hairy_frog": "hairy_frog",
    "flea toad": "flea_toad",
    "black rain frog": "black_rain_frog",
    "surinam horned frog": "surinam_horned_frog",
    "glass frog": "glass_frog",
}
SCORE_API_URL = "http://127.0.0.1:8000/scores"
API_CHECK_URL = f"{SCORE_API_URL}/top"


# SCORE API
def api_is_available():
    """Check whether a working leaderboard API already responds locally."""
    try:
        with urllib.request.urlopen(API_CHECK_URL, timeout=0.35) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def start_api_server():
    """Start Uvicorn silently if needed and return only the process we own."""
    if api_is_available():
        return None

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
    try:
        server = subprocess.Popen(
            command,
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )
    except OSError:
        return None

    startup_deadline = time.monotonic() + 10
    while time.monotonic() < startup_deadline:
        if api_is_available():
            return server
        if server.poll() is not None:
            return None
        time.sleep(0.1)

    stop_api_server(server)
    return None


def stop_api_server(server):
    """Stop the Uvicorn process started by this game, leaving existing servers alone."""
    if server is None or server.poll() is not None:
        return
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait(timeout=5)


def submit_score(username, score):
    """Send the final username and score to the local leaderboard API."""
    payload = json.dumps({"username": username, "score": int(score)}).encode("utf-8")
    request = urllib.request.Request(
        SCORE_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            if response.status == 201:
                return "Score saved successfully!"
            return f"API returned HTTP {response.status}."
    except urllib.error.HTTPError as error:
        if error.code == 422:
            return "Please enter a valid username and score."
        return f"Could not save score (HTTP {error.code})."
    except (urllib.error.URLError, TimeoutError):
        return "Could not reach the API server."


# DISPLAY SCALING AND DRAWING HELPERS
def create_screen():
    """Create the game window and calculate its display scaling factors."""
    global SCALE_X, SCALE_Y
    screen = pygame.display.get_surface()
    if not pygame.display.get_init() or screen is None:
        info = pygame.display.Info()
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
    width, height = screen.get_size()
    SCALE_X, SCALE_Y = width / SCREEN_WIDTH, height / SCREEN_HEIGHT
    return screen


def screen_position(point):
    """Scale a logical game coordinate to the current display resolution."""
    return round(point[0] * SCALE_X), round(point[1] * SCALE_Y)


def canvas_position(point):
    """Convert a mouse or display coordinate back to logical game space."""
    return round(point[0] / SCALE_X), round(point[1] / SCALE_Y)


def screen_rect(rect):
    """Scale a logical Pygame rectangle for the current display resolution."""
    return pygame.Rect(
        round(rect.x * SCALE_X), round(rect.y * SCALE_Y),
        round(rect.width * SCALE_X), round(rect.height * SCALE_Y),
    )


def scaled_radius(radius):
    """Scale a drawing size to match the current display dimensions."""
    return round(radius * (SCALE_X + SCALE_Y) / 2)


def load_textures():
    """Load the game's PNG sprites once the display has been initialized."""
    if _TEXTURES:
        return
    for image_path in TEXTURE_DIR.glob("*.png"):
        texture = pygame.image.load(str(image_path)).convert_alpha()
        if image_path.stem in {"mydas_fly", "surinam_horned_frog_rocket"}:
            texture = remove_edge_black_background(texture)
        visible_bounds = texture.get_bounding_rect()
        _TEXTURES[image_path.stem] = texture.subsurface(visible_bounds).copy()


def remove_edge_black_background(image):
    """Make edge-connected black background transparent without erasing sprite details."""
    cleaned = image.copy()
    width, height = cleaned.get_size()
    pending = deque()
    visited = bytearray(width * height)

    for x in range(width):
        pending.append((x, 0))
        pending.append((x, height - 1))
    for y in range(height):
        pending.append((0, y))
        pending.append((width - 1, y))

    while pending:
        x, y = pending.popleft()
        index = y * width + x
        if visited[index]:
            continue
        visited[index] = 1
        red, green, blue, alpha = cleaned.get_at((x, y))
        brightness = max(red, green, blue)
        if alpha == 0 or brightness > 30:
            continue

        cleaned.set_at((x, y), (red, green, blue, round(alpha * brightness / 30)))
        if x > 0:
            pending.append((x - 1, y))
        if x + 1 < width:
            pending.append((x + 1, y))
        if y > 0:
            pending.append((x, y - 1))
        if y + 1 < height:
            pending.append((x, y + 1))
    return cleaned


def tower_texture(tower_type, upgrade_tier):
    """Return the sprite name for a frog's current upgrade tier."""
    suffix = f"_T{upgrade_tier}" if upgrade_tier else ""
    return f"{TOWER_TEXTURES[tower_type]}{suffix}"


def draw_texture(screen, texture_name, center, logical_size, alpha=255, rotation=None):
    """Draw a cached, scaled pixel-art sprite centered at a logical position."""
    source = _TEXTURES.get(texture_name)
    if source is None:
        return False

    size = max(1, scaled_radius(logical_size))
    cache_key = (texture_name, size)
    sprite = _SCALED_TEXTURES.get(cache_key)
    if sprite is None:
        source_width, source_height = source.get_size()
        if source_width >= source_height:
            scaled_size = (size, max(1, round(size * source_height / source_width)))
        else:
            scaled_size = (max(1, round(size * source_width / source_height)), size)
        sprite = pygame.transform.scale(source, scaled_size)
        _SCALED_TEXTURES[cache_key] = sprite

    if rotation is not None:
        rotation = round(rotation / 5) * 5
        rotated_key = (texture_name, size, rotation)
        rotated_sprite = _SCALED_TEXTURES.get(rotated_key)
        if rotated_sprite is None:
            rotated_sprite = pygame.transform.rotate(sprite, rotation)
            _SCALED_TEXTURES[rotated_key] = rotated_sprite
        sprite = rotated_sprite

    if alpha < 255:
        sprite = sprite.copy()
        sprite.set_alpha(max(0, alpha))
    screen.blit(sprite, sprite.get_rect(center=screen_position(center)))
    return True


def draw_tower_aura(screen, center, logical_radius, color, alpha):
    """Draw a cached translucent range circle for a frog's special aura."""
    radius = max(1, scaled_radius(logical_radius))
    cache_key = (radius, color, alpha)
    aura = _AURA_SURFACES.get(cache_key)
    if aura is None:
        diameter = radius * 2
        aura = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(aura, (*color, alpha), (radius, radius), radius)
        _AURA_SURFACES[cache_key] = aura
    screen_center = screen_position(center)
    screen.blit(aura, (screen_center[0] - radius, screen_center[1] - radius))


def font(size):
    """Create a font sized for the current display resolution."""
    return pygame.font.Font(None, max(1, scaled_radius(size)))


def blit_at(screen, image, position):
    """Draw an image at a logical coordinate after scaling it."""
    screen.blit(image, screen_position(position))


def blit_centered(screen, image, center):
    """Draw an image centered at a logical coordinate after scaling it."""
    screen.blit(image, image.get_rect(center=screen_position(center)))


def wrap_text(text, selected_font, max_width):
    """Wrap words into lines that fit the requested pixel width."""
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and selected_font.size(candidate)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


# QUESTION AND MAMA FROG SCREENS
def show_answer_feedback(screen, clock, result):
    """Show a brief correct/incorrect popup and report whether the window stayed open."""
    popup = pygame.Rect(285, 180, 230, 90)
    is_correct = result == "correct"
    color = (45, 140, 65) if is_correct else (175, 55, 55)
    label = "Correct!" if is_correct else "Incorrect!"

    pygame.draw.rect(screen, color, screen_rect(popup), border_radius=scaled_radius(10))
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        screen_rect(popup),
        width=max(1, scaled_radius(3)),
        border_radius=scaled_radius(10),
    )
    blit_centered(screen, font(38).render(label, True, (255, 255, 255)), popup.center)
    pygame.display.flip()

    feedback_ends_at = pygame.time.get_ticks() + 900
    while pygame.time.get_ticks() < feedback_ends_at:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        clock.tick(60)
    return True


def show_question(screen, clock, data, can_skip, topic):
    """Show a three-answer quiz and return correct, incorrect, skip, or quit."""
    answers = list(data["answers"])
    correct_text = answers.pop(data["correct"])
    correct_index = random.randrange(3)
    answers.insert(correct_index, correct_text)
    title_font, answer_font = font(42), font(34)
    # QUESTION BUTTONS: three answers and an optional frog-question skip.
    buttons = [pygame.Rect(120, 190 + i * 65, 560, 52) for i in range(3)]
    skip_button = pygame.Rect(300, 400, 200, 40)

    while True:
        answer_result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = canvas_position(event.pos)
                for index, button in enumerate(buttons):
                    if button.collidepoint(pos):
                        answer_result = "correct" if index == correct_index else "incorrect"
                        break
                if answer_result is not None:
                    break
                if can_skip and skip_button.collidepoint(pos):
                    return "skip"
            if event.type == pygame.KEYDOWN and event.unicode in {"1", "2", "3"}:
                answer_result = "correct" if int(event.unicode) - 1 == correct_index else "incorrect"
                break

        screen.fill(GRASS_GREEN)
        blit_centered(screen, font(34).render(topic, True, (255, 255, 255)), (400, 45))
        for i, line in enumerate(textwrap.wrap(data["question"], width=42)):
            blit_centered(screen, title_font.render(line, True, (255, 255, 255)), (400, 105 + i * 42))
        mouse = canvas_position(pygame.mouse.get_pos())
        for index, (button, answer) in enumerate(zip(buttons, answers)):
            color = (80, 160, 90) if button.collidepoint(mouse) else (55, 125, 70)
            pygame.draw.rect(screen, color, screen_rect(button), border_radius=scaled_radius(8))
            blit_centered(screen, answer_font.render(f"{index + 1}. {answer}", True, (255, 255, 255)), button.center)
        if can_skip:
            color = (110, 110, 110) if skip_button.collidepoint(mouse) else (80, 80, 80)
            pygame.draw.rect(screen, color, screen_rect(skip_button), border_radius=scaled_radius(8))
            blit_centered(screen, answer_font.render("Skip", True, (255, 255, 255)), skip_button.center)
        if answer_result is not None:
            return answer_result if show_answer_feedback(screen, clock, answer_result) else "quit"
        pygame.display.flip()
        clock.tick(60)


def show_mama_offer(screen, clock, game):
    """Show the HP trade and blessing choices before wave six."""
    title_font, body_font, button_font = font(44), font(28), font(23)
    # MAMA FROG CONTROLS: HP slider, trade, continue, and full-health blessing.
    slider = pygame.Rect(245, 215, 390, 8)
    trade_button = pygame.Rect(145, 325, 190, 58)
    continue_button = pygame.Rect(355, 325, 165, 58)
    blessing_button = pygame.Rect(540, 325, 220, 58)
    max_offer = max(0, game.player_hp - 1)
    offer = 0
    dragging = False

    def value_at(mouse_x):
        """Convert the slider's horizontal mouse position to an HP amount."""
        if max_offer == 0:
            return 0
        progress = (mouse_x - slider.left) / slider.width
        return round(max_offer * max(0.0, min(1.0, progress)))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = canvas_position(event.pos)
                if slider.inflate(0, 32).collidepoint(pos):
                    dragging, offer = True, value_at(pos[0])
                elif trade_button.collidepoint(pos):
                    game.apply_mama_frog_offer("trade", offer)
                    return "done"
                elif continue_button.collidepoint(pos):
                    game.apply_mama_frog_offer("continue")
                    return "done"
                elif game.player_hp == PLAYER_MAX_HP and blessing_button.collidepoint(pos):
                    game.apply_mama_frog_offer("blessing")
                    return "done"
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                offer = value_at(canvas_position(event.pos)[0])

        screen.fill(GRASS_GREEN)
        blit_centered(screen, title_font.render("Mama Frog's Offering", True, (255, 255, 255)), (400, 42))
        description = body_font.render("Trade current HP for wings, or keep your strength.", True, (255, 255, 255))
        blit_centered(screen, description, (400, 88))


        pygame.draw.ellipse(screen, (35, 185, 75), screen_rect(pygame.Rect(70, 190, 135, 95)))
        for eye_x in (105, 170):
            pygame.draw.circle(screen, (35, 185, 75), screen_position((eye_x, 203)), scaled_radius(22))
            pygame.draw.circle(screen, (255, 255, 255), screen_position((eye_x, 203)), scaled_radius(10))
            pygame.draw.circle(screen, (10, 20, 10), screen_position((eye_x, 203)), scaled_radius(5))
        crown = ((92, 170), (100, 145), (118, 165), (137, 140), (154, 165), (175, 145), (181, 170))
        pygame.draw.polygon(screen, (255, 220, 20), [screen_position(point) for point in crown])

        blit_centered(screen, body_font.render(f"HP to offer: {offer} / {max_offer}", True, (255, 255, 255)), (440, 165))
        pygame.draw.line(screen, (205, 230, 205), screen_position((slider.left, slider.centery)), screen_position((slider.right, slider.centery)), scaled_radius(8))
        progress = offer / max_offer if max_offer else 0
        handle_x = slider.left + round(slider.width * progress)
        pygame.draw.circle(screen, (255, 220, 20), screen_position((handle_x, slider.centery)), scaled_radius(13))
        wings = offer * WINGS_PER_HP
        blit_centered(screen, body_font.render(f"Wings received: {wings}", True, (255, 255, 255)), (440, 265))

        mouse = canvas_position(pygame.mouse.get_pos())
        for button, label in ((trade_button, "Trade HP"), (continue_button, "Continue")):
            color = (80, 160, 90) if button.collidepoint(mouse) else (55, 125, 70)
            pygame.draw.rect(screen, color, screen_rect(button), border_radius=scaled_radius(8))
            blit_centered(screen, button_font.render(label, True, (255, 255, 255)), button.center)
        if game.player_hp == PLAYER_MAX_HP:
            color = (185, 145, 20) if blessing_button.collidepoint(mouse) else (145, 110, 15)
            pygame.draw.rect(screen, color, screen_rect(blessing_button), border_radius=scaled_radius(8))
            for i, label in enumerate(("Give all but 1 HP", "Receive blessing")):
                blit_centered(screen, button_font.render(label, True, (255, 255, 255)), (blessing_button.centerx, blessing_button.y + 18 + i * 22))
        else:
            blit_centered(screen, button_font.render("Blessing needs full HP", True, (210, 210, 210)), blessing_button.center)
        pygame.display.flip()
        clock.tick(60)


# MAIN MENU AND END SCREENS
def show_menu():
    """Draw the title menu and return whether the player chose Play."""
    pygame.init()
    screen, clock = create_screen(), pygame.time.Clock()
    pygame.display.set_caption("Vardes Tower Defense")
    # MAIN MENU BUTTONS: start a game or close the application.
    play_button, exit_button = pygame.Rect(260, 260, 270, 60), pygame.Rect(260, 330, 270, 60)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = canvas_position(event.pos)
                if play_button.collidepoint(pos):
                    return True
                if exit_button.collidepoint(pos):
                    return False
        screen.fill(GRASS_GREEN)
        blit_centered(screen, font(150).render("VTD", True, (255, 255, 255)), (400, 80))
        blit_centered(screen, font(80).render("Vardes Tower Defense", True, (255, 255, 255)), (400, 160))
        mouse = canvas_position(pygame.mouse.get_pos())
        for rect, label in ((play_button, "Play"), (exit_button, "Exit")):
            color = (80, 160, 90) if rect.collidepoint(mouse) else (55, 155, 70)
            pygame.draw.rect(screen, color, screen_rect(rect), border_radius=scaled_radius(10))
            blit_centered(screen, font(40).render(label, True, (255, 255, 255)), rect.center)
        pygame.display.flip()
        clock.tick(60)


def show_end_menu(total_score):
    """Show the completed-game score, navigation, and score-saving controls."""
    screen, clock = create_screen(), pygame.time.Clock()
    pygame.display.set_caption("Round Complete")
    # COMPLETION BUTTONS: return to menu, save the score, or exit.
    menu = pygame.Rect(45, 285, 220, 60)
    save = pygame.Rect(290, 285, 220, 60)
    exit_button = pygame.Rect(535, 285, 220, 60)
    back = pygame.Rect(290, 350, 220, 55)
    username, save_mode, notice = "", False, ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if save_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_mode = False
                    elif event.key == pygame.K_RETURN:
                        if not username.strip():
                            notice = "Please enter a username first."
                        else:
                            notice = submit_score(username.strip(), total_score)
                        username, save_mode = "", False
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.unicode and event.unicode.isprintable() and len(username) < 20:
                        username += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back.collidepoint(canvas_position(event.pos)):
                    save_mode = False
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = canvas_position(event.pos)
                if menu.collidepoint(pos):
                    return "menu"
                if save.collidepoint(pos):
                    username, notice, save_mode = "", "", True
                elif exit_button.collidepoint(pos):
                    return "exit"

        screen.fill(GRASS_GREEN)
        mouse = canvas_position(pygame.mouse.get_pos())
        if save_mode:
            blit_centered(screen, font(100).render("Save Score", True, (255, 255, 255)), (400, 85))
            blit_centered(screen, font(38).render("Enter username, then press Enter:", True, (255, 255, 255)), (400, 175))
            box = pygame.Rect(180, 210, 440, 55)
            pygame.draw.rect(screen, (255, 255, 255), screen_rect(box), border_radius=scaled_radius(6))
            blit_at(screen, font(38).render(username, True, (30, 30, 30)), (box.x + 12, box.y + 10))
            blit_centered(screen, font(30).render("Press Enter to save username.", True, (255, 255, 255)), (400, 285))
            pygame.draw.rect(screen, (55, 155, 70), screen_rect(back), border_radius=scaled_radius(10))
            blit_centered(screen, font(40).render("Back", True, (255, 255, 255)), back.center)
        else:
            blit_centered(screen, font(100).render("Game Complete", True, (255, 255, 255)), (400, 85))
            blit_centered(screen, font(54).render(f"Total score: {total_score}", True, (255, 255, 255)), (400, 180))
            if notice:
                blit_centered(screen, font(28).render(notice, True, (255, 255, 255)), (400, 235))
            for rect, label in ((menu, "Main Menu"), (save, "Save Score"), (exit_button, "Exit")):
                color = (80, 160, 90) if rect.collidepoint(mouse) else (55, 155, 70)
                pygame.draw.rect(screen, color, screen_rect(rect), border_radius=scaled_radius(10))
                blit_centered(screen, font(40).render(label, True, (255, 255, 255)), rect.center)
        pygame.display.flip()
        clock.tick(60)


def show_game_over(total_score):
    """Show the game-over score and return the player's menu or exit choice."""
    screen, clock = create_screen(), pygame.time.Clock()
    pygame.display.set_caption("Game Over")
    # GAME-OVER BUTTONS: return to the menu or exit the game.
    menu, exit_button = pygame.Rect(150, 285, 220, 60), pygame.Rect(430, 285, 220, 60)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = canvas_position(event.pos)
                if menu.collidepoint(pos):
                    return "menu"
                if exit_button.collidepoint(pos):
                    return "exit"
        screen.fill(GRASS_GREEN)
        blit_centered(screen, font(110).render("GAME OVER", True, (255, 255, 255)), (400, 100))
        blit_centered(screen, font(54).render(f"Total score: {total_score}", True, (255, 255, 255)), (400, 190))
        mouse = canvas_position(pygame.mouse.get_pos())
        for rect, label in ((menu, "Main Menu"), (exit_button, "Exit")):
            color = (80, 160, 90) if rect.collidepoint(mouse) else (55, 155, 70)
            pygame.draw.rect(screen, color, screen_rect(rect), border_radius=scaled_radius(10))
            blit_centered(screen, font(40).render(label, True, (255, 255, 255)), rect.center)
        pygame.display.flip()
        clock.tick(60)


def play_game():
    """Run gameplay input, simulation, buttons, popups, and board drawing."""
    screen, clock = create_screen(), pygame.time.Clock()
    load_textures()
    pygame.display.set_caption("VTD")
    game = Game()

    # TOWER PICKER BUTTONS: card positions and widths are set here.
    tower_left, tower_gap, tower_right = 8, 6, SCREEN_WIDTH - 120
    tower_width = (tower_right - tower_left - tower_gap * (len(TOWER_TYPES) - 1)) // len(TOWER_TYPES)
    tower_buttons = {
        tower: pygame.Rect(tower_left + i * (tower_width + tower_gap), 3, tower_width, 49)
        for i, tower in enumerate(TOWER_TYPES)
    }
    # BOARD ACTION BUTTONS: pause and next-wave controls.
    pause_button = pygame.Rect(SCREEN_WIDTH - 110, 6, 100, 42)
    next_round_button = pygame.Rect(SCREEN_WIDTH - 190, 85, 170, 44)
    # WAVE PREVIEW BUTTONS: close the popup or start the shown wave.
    popup_rect = pygame.Rect(125, 75, 550, 320)
    close_button = pygame.Rect(popup_rect.right - 38, popup_rect.y + 10, 28, 28)
    start_button = pygame.Rect(popup_rect.x + 18, popup_rect.bottom - 58, 205, 42)
    # FROG UPGRADE AND PAUSE BUTTONS: purchase, resume, return, or exit.
    upgrade_popup_rect = pygame.Rect(160, 55, 480, 340)
    upgrade_close_button = pygame.Rect(upgrade_popup_rect.right - 34, upgrade_popup_rect.y + 8, 26, 26)
    upgrade_buy_button = pygame.Rect(upgrade_popup_rect.x + 22, upgrade_popup_rect.bottom - 50, 150, 36)
    resume_button = pygame.Rect(280, 190, 240, 52)
    menu_button = pygame.Rect(280, 255, 240, 52)
    pause_exit_button = pygame.Rect(280, 320, 240, 52)
    forbidden = [*tower_buttons.values(), pause_button, next_round_button]
    forbidden_boxes = [(r.x, r.y, r.width, r.height) for r in forbidden]

    dragging_tower = None
    paused = False
    paused_frame = None
    popup_open = False
    upgrade_popup_open = False
    selected_tower_index = None
    return_menu = False
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))

    while True:
        dt = clock.tick(60) / 1000.0
        if game.needs_round_question():
            upgrade_popup_open = False
            selected_tower_index = None
            if game.mama_offer_is_due():
                offer_result = show_mama_offer(screen, clock, game)
                if offer_result == "quit":
                    return None
            question_data, topic, may_skip = game.next_question()
            result = show_question(screen, clock, question_data, may_skip, topic)
            if result == "quit":
                return None
            game.resolve_question(result, topic == "Fly question")

        # BUTTON INPUT: route mouse clicks to pause, upgrades, waves, and placement.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = canvas_position(event.pos)
                if paused:
                    if resume_button.collidepoint(pos):
                        paused, paused_frame = False, None
                    elif menu_button.collidepoint(pos):
                        return_menu = True
                        break
                    elif pause_exit_button.collidepoint(pos):
                        return None
                elif upgrade_popup_open:
                    if upgrade_close_button.collidepoint(pos):
                        upgrade_popup_open = False
                        selected_tower_index = None
                    elif upgrade_popup_rect.collidepoint(pos):
                        if selected_tower_index is not None and upgrade_buy_button.collidepoint(pos):
                            game.upgrade_tower(selected_tower_index)
                    else:
                        upgrade_popup_open = False
                        selected_tower_index = None
                elif game.planning_phase and popup_open:
                    if close_button.collidepoint(pos):
                        popup_open = False
                    elif start_button.collidepoint(pos):
                        game.start_next_wave()
                        popup_open = False
                elif game.planning_phase and next_round_button.collidepoint(pos):
                    popup_open = True
                else:
                    selected = next((key for key, rect in tower_buttons.items() if rect.collidepoint(pos) and game.wings >= TOWER_TYPES[key]["price"]), None)
                    if selected:
                        dragging_tower = selected
                    elif pause_button.collidepoint(pos):
                        paused, paused_frame = True, screen.copy()
                    else:
                        selected_tower_index = next(
                            (
                                index
                                for index, tower in enumerate(game.towers)
                                if pygame.Rect(
                                    round(tower["x"] - game.tower_data(tower)["size"] / 2),
                                    round(tower["y"] - game.tower_data(tower)["size"] / 2),
                                    game.tower_data(tower)["size"],
                                    game.tower_data(tower)["size"],
                                ).collidepoint(pos)
                            ),
                            None,
                        )
                        upgrade_popup_open = selected_tower_index is not None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_tower:
                game.place_tower(canvas_position(event.pos), dragging_tower, forbidden_boxes)
                dragging_tower = None

        if return_menu:
            return "menu", game.total_score
        if paused:
            screen.blit(paused_frame, (0, 0))
            screen.blit(overlay, (0, 0))
            blit_centered(screen, font(58).render("Paused", True, (255, 255, 255)), (400, 115))
            mouse = canvas_position(pygame.mouse.get_pos())
            for rect, label in ((resume_button, "Resume"), (menu_button, "Main Menu"), (pause_exit_button, "Exit")):
                color = (80, 160, 90) if rect.collidepoint(mouse) else (55, 125, 70)
                pygame.draw.rect(screen, color, screen_rect(rect), border_radius=scaled_radius(8))
                blit_centered(screen, font(36).render(label, True, (255, 255, 255)), rect.center)
            pygame.display.flip()
            continue

        game.update(dt)
        if game.game_over:
            return "game_over", game.total_score
        if game.game_finished:
            return "complete", game.total_score

        # BOARD DRAWING: route, frogs, enemies, shots, and temporary effects.
        screen.fill(GRASS_GREEN)
        pygame.draw.line(screen, ROAD_BLUE, screen_position((0, PATH_1)), screen_position((PATH_1_END_X, PATH_1)), scaled_radius(PATH_1_THICKNESS))
        previous = (PATH_1_END_X - 25, PATH_1)
        for end_x, end_y, width in PATH_SEGMENTS[1:]:
            point = (end_x, end_y)
            pygame.draw.line(screen, ROAD_BLUE, screen_position(previous), screen_position(point), scaled_radius(width))
            previous = point
        for index, (joint_x, joint_y, width) in enumerate(PATH_SEGMENTS[:-1]):
            radius = max(width, PATH_SEGMENTS[index + 1][2]) // 2
            pygame.draw.circle(screen, ROAD_BLUE, screen_position((joint_x, joint_y)), scaled_radius(radius))

        mouse = canvas_position(pygame.mouse.get_pos())
        for tower in game.towers:
            data = game.tower_data(tower)
            if "zone_damage_per_second" in data:
                draw_tower_aura(
                    screen,
                    (tower["x"], tower["y"]),
                    data["range"],
                    data["zone_color"],
                    data["zone_alpha"],
                )
            rect = pygame.Rect(round(tower["x"] - data["size"] / 2), round(tower["y"] - data["size"] / 2), data["size"], data["size"])
            draw_texture(
                screen,
                tower_texture(tower["type"], tower["upgrade_tier"]),
                (tower["x"], tower["y"]),
                data["size"] * BOARD_TEXTURE_SCALE,
                rotation=tower.get("aim_rotation", 0.0),
            )

        for enemy in game.enemies:
            x, y = game.enemy_position(enemy)
            data = ENEMY_TYPES[enemy["type"]]
            draw_texture(
                screen,
                ENEMY_TEXTURES[enemy["type"]],
                (x, y),
                data["radius"] * 2 * BOARD_TEXTURE_SCALE,
            )
            bar_width = max(20, round(data["radius"] * 2 * BOARD_TEXTURE_SCALE))
            bar = pygame.Rect(round(x - bar_width / 2), round(y - data["radius"] * BOARD_TEXTURE_SCALE - 8), bar_width, 4)
            pygame.draw.rect(screen, (100, 25, 25), screen_rect(bar))
            fill = pygame.Rect(bar.x, bar.y, round(bar.width * max(0, enemy["hp"] / enemy["max_hp"])), bar.height)
            pygame.draw.rect(screen, (70, 220, 80), screen_rect(fill))

        for enemy in game.defeated_enemies:
            x, y = game.enemy_position(enemy)
            fade = max(0.0, enemy["fade_remaining"] / enemy["fade_duration"])
            draw_texture(
                screen,
                ENEMY_TEXTURES[enemy["type"]],
                (x, y),
                ENEMY_TYPES[enemy["type"]]["radius"] * 2 * BOARD_TEXTURE_SCALE,
                alpha=round(fade * 255),
            )

        for shot in game.projectiles:
            texture_name = shot.get("projectile_sprite")
            if texture_name:
                target_x, target_y = game.enemy_position(shot["target"])
                rotation = -math.degrees(math.atan2(target_y - shot["y"], target_x - shot["x"])) - 90
                draw_texture(
                    screen,
                    texture_name,
                    (shot["x"], shot["y"]),
                    shot["size"] * 2,
                    rotation=rotation if texture_name != "black_rain_frog_T3_projectile" else None,
                )
            else:
                pygame.draw.circle(screen, shot["color"], screen_position((shot["x"], shot["y"])), scaled_radius(shot["size"]))

        for effect in game.effects:
            progress = 1.0 - effect["remaining"] / effect["duration"]
            radius = max(3, scaled_radius(effect["radius"] * progress))
            pygame.draw.circle(
                screen,
                effect["color"],
                screen_position((effect["x"], effect["y"])),
                radius,
                width=max(2, scaled_radius(3)),
            )

        for tower in game.towers:
            data = game.tower_data(tower)
            tower_rect = pygame.Rect(round(tower["x"] - data["size"] / 2), round(tower["y"] - data["size"] / 2), data["size"], data["size"])
            if tower_rect.collidepoint(mouse):
                pygame.draw.circle(screen, (170, 230, 180), screen_position((tower["x"], tower["y"])), scaled_radius(data["range"]), width=max(1, scaled_radius(3)))

        # HUD AND TOWER PICKER: scores, HP, wings, and frog selection cards.
        hud_font = font(28)
        blit_at(screen, hud_font.render(f"Wave: {min(game.current_wave, game.wave_count)}/{game.wave_count}", True, (255, 255, 255)), (SCREEN_WIDTH - 185, 60))
        pygame.draw.rect(screen, (25, 85, 48), screen_rect(pygame.Rect(0, 0, SCREEN_WIDTH, 55)))
        for tower_type, rect in tower_buttons.items():
            data = TOWER_TYPES[tower_type]
            affordable = game.wings >= data["price"]
            hover = rect.collidepoint(mouse)
            color = (75, 75, 75) if not affordable else ((90, 170, 85) if hover else (55, 125, 70))
            pygame.draw.rect(screen, color, screen_rect(rect), border_radius=scaled_radius(6))
            surface_rect = screen_rect(rect)
            draw_texture(screen, tower_texture(tower_type, 0), (rect.x + 23, rect.centery), 38)
            label_size = 14
            label_font = font(label_size)
            label_width = surface_rect.width - scaled_radius(48)
            lines = wrap_text(data["name"], label_font, label_width) + [f"{data['price']}ω"]
            while len(lines) * label_font.get_linesize() > surface_rect.height - scaled_radius(2) and label_size > 10:
                label_size -= 1
                label_font = font(label_size)
                lines = wrap_text(data["name"], label_font, label_width) + [f"{data['price']}ω"]
            first_y = surface_rect.centery - len(lines) * label_font.get_linesize() // 2
            for i, line in enumerate(lines):
                label = label_font.render(line, True, (255, 255, 255))
                screen.blit(label, label.get_rect(midleft=(surface_rect.left + scaled_radius(46), first_y + label_font.get_linesize() // 2 + i * label_font.get_linesize())))

        if dragging_tower:
            data = TOWER_TYPES[dragging_tower]
            pygame.draw.circle(screen, (170, 230, 180), screen_position(mouse), scaled_radius(data["range"]), width=max(1, scaled_radius(3)))
            valid = game.can_place_tower(mouse, dragging_tower, forbidden_boxes)
            rect = pygame.Rect(round(mouse[0] - data["size"] / 2), round(mouse[1] - data["size"] / 2), data["size"], data["size"])
            draw_texture(screen, tower_texture(dragging_tower, 0), mouse, data["size"] * BOARD_TEXTURE_SCALE, alpha=180)
            pygame.draw.rect(
                screen,
                (80, 230, 100) if valid else (230, 70, 70),
                screen_rect(rect),
                width=max(1, scaled_radius(2)),
            )

        blit_at(screen, hud_font.render(f"Round points: {round(game.round_score)}", True, (255, 255, 255)), (10, 60))
        blit_at(screen, hud_font.render(f"Total score: {game.total_score}", True, (255, 255, 255)), (10, 88))
        blit_at(screen, hud_font.render(f"HP: {game.player_hp}/{PLAYER_MAX_HP}", True, (255, 255, 255)), (615, 135))
        blit_at(screen, hud_font.render(f"Wings (ω): {game.wings}", True, (255, 255, 255)), (615, 170))

        # VISIBLE BOARD BUTTON: open the pause menu.
        pygame.draw.rect(screen, (55, 125, 70), screen_rect(pause_button), border_radius=scaled_radius(8))
        blit_centered(screen, font(40).render("Pause", True, (255, 255, 255)), pause_button.center)

        # NEXT WAVE BUTTON AND PREVIEW: list enemies and launch the queued wave.
        if game.planning_phase:
            pygame.draw.rect(screen, (55, 145, 75), screen_rect(next_round_button), border_radius=scaled_radius(8))
            blit_centered(screen, font(28).render("Next Round", True, (255, 255, 255)), next_round_button.center)
            if popup_open:
                screen.blit(overlay, (0, 0))
                pygame.draw.rect(screen, (35, 105, 58), screen_rect(popup_rect), border_radius=scaled_radius(12))
                pygame.draw.rect(screen, (205, 230, 205), screen_rect(popup_rect), width=max(1, scaled_radius(3)), border_radius=scaled_radius(12))
                blit_at(screen, font(40).render(f"Wave {game.current_wave + 1} Enemies", True, (255, 255, 255)), (popup_rect.x + 20, popup_rect.y + 18))
                pygame.draw.rect(screen, (165, 55, 55), screen_rect(close_button), border_radius=scaled_radius(5))
                blit_centered(screen, font(28).render("X", True, (255, 255, 255)), close_button.center)
                for x, label in ((popup_rect.x + 24, "Look"), (popup_rect.x + 95, "Enemy type"), (popup_rect.x + 390, "How many")):
                    blit_at(screen, font(20).render(label, True, (205, 230, 205)), (x, popup_rect.y + 65))
                counts = game.next_wave_summary()
                for i, (enemy_type, amount) in enumerate(counts):
                    row_y = popup_rect.y + 102 + i * 40
                    draw_texture(
                        screen,
                        ENEMY_TEXTURES[enemy_type],
                        (popup_rect.x + 48, row_y + 12),
                        36,
                    )
                    blit_at(screen, font(28).render(enemy_type.replace("_", " ").title(), True, (255, 255, 255)), (popup_rect.x + 95, row_y))
                    blit_at(screen, font(28).render(str(amount), True, (255, 255, 255)), (popup_rect.x + 420, row_y))
                color = (90, 180, 95) if start_button.collidepoint(mouse) else (65, 145, 75)
                pygame.draw.rect(screen, color, screen_rect(start_button), border_radius=scaled_radius(7))
                blit_centered(screen, font(28).render("Start Wave", True, (255, 255, 255)), start_button.center)

        # UPGRADE POPUP: show the next tier, description, and wing price.
        if upgrade_popup_open and selected_tower_index is not None:
            tower = game.towers[selected_tower_index]
            current_data = game.tower_data(tower)
            upgrade_data = game.next_upgrade_data(tower)
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (35, 105, 58), screen_rect(upgrade_popup_rect), border_radius=scaled_radius(10))
            pygame.draw.rect(screen, (205, 230, 205), screen_rect(upgrade_popup_rect), width=max(1, scaled_radius(3)), border_radius=scaled_radius(10))
            pygame.draw.rect(screen, (165, 55, 55), screen_rect(upgrade_close_button), border_radius=scaled_radius(5))
            blit_centered(screen, font(23).render("X", True, (255, 255, 255)), upgrade_close_button.center)
            if upgrade_data is None:
                draw_texture(screen, tower_texture(tower["type"], tower["upgrade_tier"]), (upgrade_popup_rect.x + 50, upgrade_popup_rect.y + 48), 58)
                blit_at(screen, font(26).render(f"{current_data['name']} - Max level", True, (255, 255, 255)), (upgrade_popup_rect.x + 88, upgrade_popup_rect.y + 24))
            else:
                draw_texture(screen, tower_texture(tower["type"], tower["upgrade_tier"] + 1), (upgrade_popup_rect.x + 50, upgrade_popup_rect.y + 48), 58)
                blit_at(screen, font(26).render(upgrade_data['name'], True, (255, 255, 255)), (upgrade_popup_rect.x + 88, upgrade_popup_rect.y + 18))
                blit_at(screen, font(22).render(f"Price: {upgrade_data['price']}ω", True, (255, 255, 255)), (upgrade_popup_rect.x + 88, upgrade_popup_rect.y + 52))
                description_font = font(18)
                popup_width = screen_rect(upgrade_popup_rect).width - scaled_radius(44)
                line_spacing = max(18, round(description_font.get_linesize() / SCALE_Y))
                description_y = upgrade_popup_rect.y + 88
                for description_row in upgrade_data.get("description", ["No description set."]):
                    wrapped_row = wrap_text(description_row, description_font, popup_width)
                    for line in wrapped_row:
                        description_label = description_font.render(line, True, (225, 240, 225))
                        blit_at(screen, description_label, (upgrade_popup_rect.x + 22, description_y))
                        description_y += line_spacing
                can_afford = game.wings >= upgrade_data["price"]
                hover_upgrade = upgrade_buy_button.collidepoint(mouse)
                buy_color = (75, 75, 75) if not can_afford else ((90, 180, 95) if hover_upgrade else (65, 145, 75))
                pygame.draw.rect(screen, buy_color, screen_rect(upgrade_buy_button), border_radius=scaled_radius(7))
                blit_centered(screen, font(24).render("Upgrade", True, (255, 255, 255)), upgrade_buy_button.center)
                blit_at(screen, font(20).render(f"Wings (ω): {game.wings}", True, (225, 240, 225)), (upgrade_popup_rect.x + 190, upgrade_popup_rect.bottom - 44))

        pygame.display.flip()


def main():
    """Start Pygame and move between the menu, game, and ending screens."""
    api_server = start_api_server()
    try:
        pygame.init()
        while show_menu():
            result = play_game()
            if result is None:
                break
            kind, score = result
            if kind == "menu":
                continue
            action = show_game_over(score) if kind == "game_over" else show_end_menu(score)
            if action == "exit":
                break
    finally:
        if pygame.get_init():
            pygame.quit()
        stop_api_server(api_server)


if __name__ == "__main__":
    main()
