import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Minimalist Theme)
DARK_BG = (20, 20, 20)
NEON_CYAN = (100, 200, 255)
NEON_PINK = (255, 100, 150)
NEON_YELLOW = (255, 200, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Block colors
BLOCK_COLORS = [
    (231, 76, 60),   # Red
    (230, 126, 34),  # Orange
    (241, 196, 15),  # Yellow
    (46, 204, 113),  # Green
    (52, 152, 219)   # Blue
]

# Game variables
score = 0
level = 1
lives = 3
blocks_destroyed = 0
game_state = "MENU"  # MENU, PLAYING, GAME_OVER

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BLOCK BREAKER")
clock = pygame.time.Clock()

# Fonts
try:
    title_font = pygame.font.SysFont('arial', 60, bold=True)
    font_large = pygame.font.SysFont('arial', 40, bold=True)
    font_medium = pygame.font.SysFont('arial', 24, bold=True)
    font_small = pygame.font.SysFont('arial', 18)
except:
    title_font = pygame.font.Font(None, 60)
    font_large = pygame.font.Font(None, 40)
    font_medium = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)


class Paddle:
    def __init__(self):
        self.width = 120
        self.height = 15
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 30
        self.speed = 8
        
    def move(self, direction):
        if direction == "LEFT" and self.x > 0:
            self.x -= self.speed
        elif direction == "RIGHT" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def draw(self, surface):
        # Draw simple paddle
        pygame.draw.rect(surface, NEON_CYAN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 2)


class Ball:
    def __init__(self, paddle_x):
        self.radius = 8
        self.x = paddle_x + 60
        self.y = SCREEN_HEIGHT - 50
        self.dx = 0
        self.dy = 0
        self.speed = 5
        self.launched = False
    
    def launch(self):
        if not self.launched:
            self.launched = True
            self.dx = random.choice([-2, -1, 1, 2])
            self.dy = -self.speed
    
    def move(self, paddle):
        if not self.launched:
            self.x = paddle.x + paddle.width // 2
            self.y = paddle.y - 20
            return
        
        self.x += self.dx
        self.y += self.dy
        
        # Wall collision
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.dx = -self.dx
        
        if self.y - self.radius <= 0:
            self.dy = -self.dy
        
        # Paddle collision
        if (self.y + self.radius >= paddle.y and 
            self.y - self.radius <= paddle.y + paddle.height and
            self.x >= paddle.x and 
            self.x <= paddle.x + paddle.width):
            
            # Calculate angle based on hit position
            hit_pos = (self.x - paddle.x) / paddle.width
            angle = (hit_pos - 0.5) * 3  # -1.5 to 1.5
            self.dx = angle * self.speed
            self.dy = -abs(self.dy)
    
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, NEON_CYAN, (int(self.x), int(self.y)), self.radius, 2)


class Block:
    def __init__(self, x, y, color):
        self.width = 90
        self.height = 30
        self.x = x
        self.y = y
        self.color = color
        self.visible = True
    
    def draw(self, surface):
        if self.visible:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 3)
            # Inner shadow
            pygame.draw.rect(surface, (0, 0, 0, 100), (self.x + 2, self.y + 2, self.width - 4, self.height - 4), 1)
    
    def check_collision(self, ball):
        if not self.visible:
            return False
        
        if (ball.x + ball.radius > self.x and 
            ball.x - ball.radius < self.x + self.width and
            ball.y + ball.radius > self.y and 
            ball.y - ball.radius < self.y + self.height):
            return True
        return False


def create_blocks():
    blocks = []
    rows = 5
    cols = 8
    padding = 5
    offset_top = 80
    offset_left = 25
    
    for row in range(rows):
        for col in range(cols):
            x = col * (90 + padding) + offset_left
            y = row * (30 + padding) + offset_top
            color = BLOCK_COLORS[row]
            blocks.append(Block(x, y, color))
    
    return blocks


def draw_text_with_shadow(surface, text, font, color, x, y, center=False):
    # Shadow
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x + 2, y + 2)
    else:
        text_rect.topleft = (x + 2, y + 2)
    surface.blit(text_surface, text_rect)
    
    # Main text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def draw_menu():
    # Draw gradient background
    for y in range(SCREEN_HEIGHT):
        progress = y / SCREEN_HEIGHT
        r = int(20 + (30 - 20) * progress)
        g = int(20 + (30 - 20) * progress)
        b = int(20 + (40 - 20) * progress)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Title
    draw_text_with_shadow(screen, "BLOCK BREAKER", title_font, NEON_CYAN, 
                         SCREEN_WIDTH // 2, 180, center=True)
    
    # # Subtitle
    # draw_text_with_shadow(screen, "ARCADE EDITION", font_medium, NEON_PINK, 
    #                      SCREEN_WIDTH // 2, 260, center=True)
    
    # START button
    button_width = 200
    button_height = 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = 360
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Check if mouse is hovering over button
    if button_rect.collidepoint(mouse_pos):
        # Hover state
        pygame.draw.rect(screen, NEON_CYAN, button_rect)
        draw_text_with_shadow(screen, "START", font_large, DARK_BG, 
                             SCREEN_WIDTH // 2, button_y + 30, center=True)
    else:
        # Normal state
        pygame.draw.rect(screen, DARK_BG, button_rect)
        pygame.draw.rect(screen, NEON_CYAN, button_rect, 3)
        draw_text_with_shadow(screen, "START", font_large, NEON_CYAN, 
                             SCREEN_WIDTH // 2, button_y + 30, center=True)
    
    # Controls info - smaller
    draw_text_with_shadow(screen, "Arrow Keys or Mouse to Move Paddle", font_small, GRAY, 
                         SCREEN_WIDTH // 2, 480, center=True)
    draw_text_with_shadow(screen, "SPACE to Launch Ball", font_small, GRAY, 
                         SCREEN_WIDTH // 2, 510, center=True)
    
    return button_rect  # Return button rect for click detection


def draw_hud():
    # HUD background
    hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
    pygame.draw.rect(screen, (30, 30, 30), hud_rect)
    pygame.draw.line(screen, GRAY, (0, 60), (SCREEN_WIDTH, 60), 2)
    
    # Score
    draw_text_with_shadow(screen, "SCORE", font_small, GRAY, 30, 15)
    draw_text_with_shadow(screen, str(score), font_medium, WHITE, 30, 35)
    
    # Level
    draw_text_with_shadow(screen, "LEVEL", font_small, GRAY, 
                         SCREEN_WIDTH // 2 - 40, 15)
    draw_text_with_shadow(screen, str(level), font_medium, WHITE, 
                         SCREEN_WIDTH // 2 - 40, 35)
    
    # Lives (simple circles)
    draw_text_with_shadow(screen, "LIVES", font_small, GRAY, 
                         SCREEN_WIDTH - 150, 15)
    for i in range(lives):
        circle_x = SCREEN_WIDTH - 130 + i * 35
        pygame.draw.circle(screen, NEON_CYAN, (circle_x, 40), 10)
        pygame.draw.circle(screen, WHITE, (circle_x, 40), 10, 2)


def draw_game_over():
    screen.fill(DARK_BG)
    
    # Game Over title
    draw_text_with_shadow(screen, "GAME OVER", title_font, NEON_PINK, 
                         SCREEN_WIDTH // 2, 100, center=True)
    
    # Final Score
    draw_text_with_shadow(screen, "FINAL SCORE", font_medium, GRAY, 
                         SCREEN_WIDTH // 2, 200, center=True)
    draw_text_with_shadow(screen, str(score), font_large, NEON_YELLOW, 
                         SCREEN_WIDTH // 2, 250, center=True)
    
    # Stats box
    stats_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 320, 400, 120)
    pygame.draw.rect(screen, (40, 40, 40), stats_rect)
    pygame.draw.rect(screen, GRAY, stats_rect, 2)
    
    draw_text_with_shadow(screen, f"Level Reached: {level}", font_medium, WHITE, 
                         SCREEN_WIDTH // 2, 350, center=True)
    draw_text_with_shadow(screen, f"Blocks Destroyed: {blocks_destroyed}", font_medium, WHITE, 
                         SCREEN_WIDTH // 2, 390, center=True)
    
    # PLAY AGAIN button
    button_width = 250
    button_height = 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = 470
    
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, NEON_CYAN, button_rect)
        draw_text_with_shadow(screen, "PLAY AGAIN", font_large, DARK_BG, 
                             SCREEN_WIDTH // 2, button_y + 30, center=True)
    else:
        pygame.draw.rect(screen, DARK_BG, button_rect)
        pygame.draw.rect(screen, NEON_CYAN, button_rect, 3)
        draw_text_with_shadow(screen, "PLAY AGAIN", font_large, NEON_CYAN, 
                             SCREEN_WIDTH // 2, button_y + 30, center=True)
    
    # ESC instruction
    draw_text_with_shadow(screen, "Press ESC for Main Menu", font_small, GRAY, 
                         SCREEN_WIDTH // 2, 550, center=True)
    
    return button_rect


def reset_game():
    global score, level, lives, blocks_destroyed, paddle, ball, blocks
    score = 0
    level = 1
    lives = 3
    blocks_destroyed = 0
    paddle = Paddle()
    ball = Ball(paddle.x)
    blocks = create_blocks()


# Initialize game objects
paddle = Paddle()
ball = Ball(paddle.x)
blocks = create_blocks()

# Main game loop
running = True
start_button_rect = None
play_again_button_rect = None

while running:
    clock.tick(FPS)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "GAME_OVER":
                    game_state = "MENU"
            
            if event.key == pygame.K_RETURN:  # ENTER key
                if game_state == "MENU":
                    reset_game()
                    game_state = "PLAYING"
                elif game_state == "GAME_OVER":
                    reset_game()
                    game_state = "PLAYING"
            
            if event.key == pygame.K_SPACE:
                if game_state == "PLAYING":
                    ball.launch()
        
        # Mouse click detection
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check START button click
                if game_state == "MENU" and start_button_rect:
                    if start_button_rect.collidepoint(mouse_pos):
                        reset_game()
                        game_state = "PLAYING"
                
                # Check PLAY AGAIN button click
                if game_state == "GAME_OVER" and play_again_button_rect:
                    if play_again_button_rect.collidepoint(mouse_pos):
                        reset_game()
                        game_state = "PLAYING"
        
        if event.type == pygame.MOUSEMOTION and game_state == "PLAYING":
            paddle.x = event.pos[0] - paddle.width // 2
            paddle.x = max(0, min(paddle.x, SCREEN_WIDTH - paddle.width))
    
    # Game states
    if game_state == "MENU":
        start_button_rect = draw_menu()
    
    elif game_state == "PLAYING":
        # Update
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("LEFT")
        if keys[pygame.K_RIGHT]:
            paddle.move("RIGHT")
        
        ball.move(paddle)
        
        # Check ball out of bounds (lose life)
        if ball.y - ball.radius > SCREEN_HEIGHT:
            lives -= 1
            if lives <= 0:
                game_state = "GAME_OVER"
            else:
                ball = Ball(paddle.x)
        
        # Check block collisions
        for block in blocks:
            if block.check_collision(ball):
                ball.dy = -ball.dy
                block.visible = False
                score += 10
                blocks_destroyed += 1
        
        # Check level complete
        if all(not block.visible for block in blocks):
            level += 1
            score += 50  # Bonus
            ball.speed += 0.5
            blocks = create_blocks()
            ball = Ball(paddle.x)
        
        # Draw
        screen.fill(DARK_BG)
        
        # Draw game objects
        for block in blocks:
            block.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)
        draw_hud()
    
    elif game_state == "GAME_OVER":
        play_again_button_rect = draw_game_over()
    
    pygame.display.flip()

pygame.quit()
sys.exit()