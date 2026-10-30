"""A tiny Pygame prototype: one red circle moves along a straight path."""

import math

import pygame


# Window size in pixels. Change these two values to make the window larger or smaller.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

# The path is a horizontal road across the middle of the window.
PATH_1 = SCREEN_HEIGHT // 2
PATH_1_THICKNESS = 50
PATH_1_END_X = 500

PATH_2_THICKNESS = 50
PATH_2_END_X = 500
PATH_2_END_Y = 80

PATH_3_THICKNESS = 50
PATH_3_END_X = 200
PATH_3_END_Y = 80

PATH_4_THICKNESS = 50
PATH_4_END_X = 200
PATH_4_END_Y = 400

PATH_5_THICKNESS = 50
PATH_5_END_X = 830
PATH_5_END_Y = 400

# Each item is one segment's endpoint and road width.
# A segment starts automatically at the endpoint of the previous segment.
# Add more endpoint tuples at the bottom to extend the winding path.
PATH_SEGMENTS = [
    (PATH_1_END_X - 25, PATH_1, PATH_1_THICKNESS),
    (PATH_2_END_X - 25, PATH_2_END_Y, PATH_2_THICKNESS),
    (PATH_3_END_X - 25, PATH_3_END_Y, PATH_3_THICKNESS),
    (PATH_4_END_X - 25, PATH_4_END_Y, PATH_4_THICKNESS),
    (PATH_5_END_X - 25, PATH_5_END_Y, PATH_5_THICKNESS),
]


# The moving circle represents the simple enemy from the tower-defense idea.
CIRCLE_RADIUS = 14
CIRCLE_SPEED = 2000  # Pixels travelled per second (constant speed).

# Colors use the familiar (red, green, blue) format.
GRASS_GREEN = (30, 112, 57)
ROAD_BLUE = (112, 148, 190)
ENEMY_RED = (230, 55, 55)


def send_musas(enemies):
    """Add one enemy at the beginning of the track."""
    enemies.append(float(CIRCLE_RADIUS))

def main():
    """Create the window and keep drawing frames until it is closed."""
    pygame.init()

    # Set up the game window and a clock used to keep movement smooth.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("VTD")
    clock = pygame.time.Clock()

    # Build connected segments from the endpoint list and calculate their lengths.
    route_segments = []
    segment_start = (0.0, float(PATH_1))
    total_path_length = 0.0

    for end_x, end_y, _thickness in PATH_SEGMENTS:
        segment_end = (float(end_x), float(end_y))
        segment_length = math.hypot(
            segment_end[0] - segment_start[0],
            segment_end[1] - segment_start[1],
        )
        route_segments.append((segment_start, segment_end, segment_length))
        total_path_length += segment_length
        segment_start = segment_end

    # Each value stores one enemy's distance along the route.
    enemies = []
    musas_beigas = 0
    musas_font = pygame.font.Font(None, 28)
    musas_button = pygame.Rect(SCREEN_WIDTH - 190, 15, 175, 48)
    musas_label = musas_font.render("Send enemy", True, (255, 255, 255))
    running = True

    # Keep the game responsive by checking for window events every frame.
    while running:
        # Measure the time since the previous frame. Multiplying speed by this
        # value means the circle moves at the same rate on different computers.
        seconds_since_last_frame = clock.tick(60) / 1000.0

        # Closing the window ends the loop and lets Pygame shut down cleanly.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if musas_button.collidepoint(event.pos):
                    send_musas(enemies)

        # Move enemies along the route, counting and removing each one at the end.
        for enemy_index in range(len(enemies) - 1, -1, -1):
            enemies[enemy_index] = min(
                enemies[enemy_index] + CIRCLE_SPEED * seconds_since_last_frame,
                total_path_length,
            )
            if enemies[enemy_index] >= total_path_length:
                musas_beigas += 1
                enemies.pop(enemy_index)

        # Draw the background and road. The visible first path extends 25 pixels
        # past the circle's turn point, matching your original smooth overlap.
        screen.fill(GRASS_GREEN)
        pygame.draw.line(
            screen,
            ROAD_BLUE,
            (0, PATH_1),
            (PATH_1_END_X, PATH_1),
            PATH_1_THICKNESS,
        )

        # The circle's turn point is PATH_1_END_X - 25, so begin the next
        # visible segment there. The first path's extra 25 pixels overlap it.
        previous_point = (PATH_1_END_X - 25, PATH_1)
        for end_x, end_y, thickness in PATH_SEGMENTS[1:]:
            next_point = (end_x, end_y)
            pygame.draw.line(screen, ROAD_BLUE, previous_point, next_point, thickness)
            previous_point = next_point

        # Thick line segments can leave a notch at a turn. Add a rounded join
        # on each shared endpoint, using half the wider adjoining road width.
        for joint_index, (joint_x, joint_y, current_thickness) in enumerate(
            PATH_SEGMENTS[:-1]
        ):
            next_thickness = PATH_SEGMENTS[joint_index + 1][2]
            joint_radius = max(current_thickness, next_thickness) // 2
            pygame.draw.circle(
                screen,
                ROAD_BLUE,
                (joint_x, joint_y),
                joint_radius,
            )

        # Draw each enemy at its current position along the connected segments.
        for distance_along_path in enemies:
            remaining_distance = distance_along_path
            circle_x, circle_y = route_segments[-1][1]
            for start, end, segment_length in route_segments:
                if remaining_distance <= segment_length:
                    progress = remaining_distance / segment_length if segment_length else 1.0
                    circle_x = start[0] + (end[0] - start[0]) * progress
                    circle_y = start[1] + (end[1] - start[1]) * progress
                    break
                remaining_distance -= segment_length

            pygame.draw.circle(
                screen,
                ENEMY_RED,
                (round(circle_x), round(circle_y)),
                CIRCLE_RADIUS,
            )

        # The button stays over the track display in the top-right corner.
        pygame.draw.rect(screen, (55, 155, 70), musas_button, border_radius=8)
        screen.blit(musas_label, musas_label.get_rect(center=musas_button.center))

        # Show how many enemies are currently on the track.
        count_label = musas_font.render(f"Musas beigas: {musas_beigas}", True, (255, 255, 255))
        screen.blit(count_label, (SCREEN_WIDTH - 190, 72))

        # Show the finished frame. Pygame displays it when this call is made.
        pygame.display.flip()

    # Release Pygame's window and input resources when the user closes it.
    pygame.quit()


def show_menu():
    """Show Play and Exit buttons; return True when Play is selected."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vardes Tower Defense")
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 150)
    subtitle_font = pygame.font.Font(None, 80)
    button_font = pygame.font.Font(None, 40)

    play_button = pygame.Rect(360 - 100, 260, 270, 60)
    exit_button = pygame.Rect(360 - 100, 330, 270, 60)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos):
                    return True
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    return False

        screen.fill(GRASS_GREEN)
        title = title_font.render("VTD", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 80)))

        subtitle = subtitle_font.render("Vardes Tower Defense", True, (255, 255, 255))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160)))

        mouse_pos = pygame.mouse.get_pos()
        for button, label in ((play_button, "Play"), (exit_button, "Exit")):
            color = (80, 160, 90) if button.collidepoint(mouse_pos) else (55, 155, 70)
            pygame.draw.rect(screen, color, button, border_radius=10)
            text = button_font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=button.center))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return False


# This check lets the file be run directly with Python.
if __name__ == "__main__":
    if show_menu():
        main()
