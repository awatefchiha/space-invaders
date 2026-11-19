import math
import random
from pathlib import Path
import pygame
from pygame import mixer


# Configuration

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_SPEED = 180      
ENEMY_SPEED = 120       
ENEMY_DROP_DISTANCE = 40 
BULLET_SPEED = 420       

PLAYER_START_X = 370
PLAYER_START_Y = 480
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 64
ENEMY_WIDTH = 64
ENEMY_HEIGHT = 64

NUMBER_OF_ENEMIES = 6
ENEMY_START_MIN_Y = 50
ENEMY_START_MAX_Y = 150

BACKGROUND_COLOR = (0, 0, 0)
SCORE_COLOR = (255, 255, 255)


# Asset paths

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"


def asset_path(filename):
    """Return the full path to a file inside the assets folder."""
    return ASSETS_DIR / filename


# Pygame setup and game assets

pygame.init()
mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 32)

background_image = pygame.image.load(asset_path("background.png")).convert()
player_image = pygame.image.load(asset_path("player.png")).convert_alpha()
enemy_image = pygame.image.load(asset_path("enemy.png")).convert_alpha()
bullet_image = pygame.image.load(asset_path("bullet.png")).convert_alpha()
icon_image = pygame.image.load(asset_path("ufo.png")).convert_alpha()

pygame.display.set_icon(icon_image)

# Load the background music and sound effects.
mixer.music.load(asset_path("background.wav"))
mixer.music.play(-1)

laser_sound = mixer.Sound(asset_path("laser.wav"))
explosion_sound = mixer.Sound(asset_path("explosion.wav"))


# Game state

player_x = PLAYER_START_X
player_y = PLAYER_START_Y
player_direction = 0  # -1 = left, 0 = stationary, 1 = right

score = 0

# Each enemy has its own position and horizontal direction.
enemies = []
for _ in range(NUMBER_OF_ENEMIES):
    enemies.append({
        "x": random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH),
        "y": random.randint(ENEMY_START_MIN_Y, ENEMY_START_MAX_Y),
        "direction": 1,
    })

# A single bullet can be on screen at a time.
bullet_x = 0
bullet_y = player_y
bullet_is_firing = False


# Drawing functions

def draw_background():
    """Draw the background image."""
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_image, (0, 0))


def draw_player():
    """Draw the player's spaceship at its current position."""
    screen.blit(player_image, (player_x, player_y))


def draw_enemies():
    """Draw every enemy using its current position."""
    for enemy_data in enemies:
        screen.blit(enemy_image, (enemy_data["x"], enemy_data["y"]))


def draw_bullet():
    """Draw the bullet only while it is travelling."""
    if bullet_is_firing:
        screen.blit(bullet_image, (bullet_x + 16, bullet_y + 10))


def draw_score():
    """Render and display the current score."""
    score_text = font.render(f"Score: {score}", True, SCORE_COLOR)
    screen.blit(score_text, (10, 10))


# Input and movement

def handle_input():
    """Read keyboard and window events."""
    global player_direction, bullet_x, bullet_y, bullet_is_firing

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_direction = -1
            elif event.key == pygame.K_RIGHT:
                player_direction = 1
            elif event.key == pygame.K_SPACE and not bullet_is_firing:
                # Start a new bullet at the spaceship's current position.
                bullet_x = player_x
                bullet_y = player_y
                bullet_is_firing = True
                laser_sound.play()

        if event.type == pygame.KEYUP:
            # Stop horizontal movement when the arrow key is released.
            if event.key == pygame.K_LEFT and player_direction == -1:
                player_direction = 0
            elif event.key == pygame.K_RIGHT and player_direction == 1:
                player_direction = 0

    return True


def move_player(delta_time):
    """Move the spaceship and keep it inside the screen."""
    global player_x

    player_x += player_direction * PLAYER_SPEED * delta_time
    player_x = max(0, min(player_x, SCREEN_WIDTH - PLAYER_WIDTH))


def move_enemies(delta_time):
    """Move enemies horizontally and drop them when they reach a screen edge."""
    for enemy_data in enemies:
        enemy_data["x"] += (
            enemy_data["direction"] * ENEMY_SPEED * delta_time
        )

        # Reverse direction and move down when an enemy reaches either edge.
        if enemy_data["x"] <= 0:
            enemy_data["x"] = 0
            enemy_data["direction"] = 1
            enemy_data["y"] += ENEMY_DROP_DISTANCE
        elif enemy_data["x"] >= SCREEN_WIDTH - ENEMY_WIDTH:
            enemy_data["x"] = SCREEN_WIDTH - ENEMY_WIDTH
            enemy_data["direction"] = -1
            enemy_data["y"] += ENEMY_DROP_DISTANCE


def move_bullet(delta_time):
    """Move the bullet upward; reset it after it leaves the screen."""
    global bullet_y, bullet_is_firing

    if bullet_is_firing:
        bullet_y -= BULLET_SPEED * delta_time

        if bullet_y < 0:
            bullet_y = player_y
            bullet_is_firing = False


# Collision detection and scoring

def check_collisions():
    """Check whether the active bullet hits an enemy."""
    global score, bullet_y, bullet_is_firing

    if not bullet_is_firing:
        return

    bullet_rect = bullet_image.get_rect(topleft=(bullet_x + 16, bullet_y + 10))

    for enemy_data in enemies:
        enemy_rect = enemy_image.get_rect(
            topleft=(enemy_data["x"], enemy_data["y"])
        )

        if bullet_rect.colliderect(enemy_rect):
            explosion_sound.play()
            score += 1

            bullet_y = player_y
            bullet_is_firing = False

            enemy_data["x"] = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
            enemy_data["y"] = random.randint(
                ENEMY_START_MIN_Y, ENEMY_START_MAX_Y
            )
            enemy_data["direction"] = 1
            break


# Main game loop

def main():
    """Run the game until the player closes the window."""
    running = True

    while running:
        delta_time = clock.tick(FPS) / 1000.0

        running = handle_input()
        if not running:
            break

        move_player(delta_time)
        move_enemies(delta_time)
        move_bullet(delta_time)
        check_collisions()

        draw_background()
        draw_enemies()
        draw_bullet()
        draw_player()
        draw_score()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
