import pygame, sys, random

# Settings (Constants)
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
CELL_SIZE = 20
CELL_WIDTH = SCREEN_WIDTH // CELL_SIZE
CELL_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (200, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
GRAY  = (40, 40, 40)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sssssnake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.reset_game()

    def reset_game(self):
        start_x = random.randint(5, CELL_WIDTH - 6)
        start_y = random.randint(5, CELL_HEIGHT - 6)
        self.snake = [
            pygame.Vector2(start_x, start_y),
            pygame.Vector2(start_x - 1, start_y),
            pygame.Vector2(start_x - 2, start_y)
        ]
        self.direction = pygame.Vector2(1, 0) # Direcrtion (RIGHT)
        self.spawn_apple()
        
        # Progress variables
        self.score = 0
        self.level = 1
        self.current_fps = 10
        self.foods_per_level = 4

    def spawn_apple(self):
        while True:
            self.apple = pygame.Vector2(
                random.randint(0, CELL_WIDTH - 1),
                random.randint(0, CELL_HEIGHT - 1)
            )
            if self.apple not in self.snake:
                break

        
    def draw_elements(self):
        # Draw grid
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
            
        # Draw apple
        apple_rect = pygame.Rect(self.apple.x * CELL_SIZE, self.apple.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, RED, apple_rect)

        # Draw snake
        for index, block in enumerate(self.snake):
            x, y = block.x * CELL_SIZE, block.y * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            
            # Colors of snake
            color = DARK_GREEN if index == 0 else GREEN
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1) # Тонкая обводка блоков

    def game_over_logic(self):
        font_big = pygame.font.SysFont("Arial", 80, bold=True)
        text = font_big.render("CRASHED!", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        pygame.display.update()
        pygame.time.delay(2000)
        self.reset_game()

    def update(self):
        """Logic of motion and collisions"""
        # Creating new head due to direction
        new_head = self.snake[0] + self.direction

        # Collision with borders
        if not (0 <= new_head.x < CELL_WIDTH and 0 <= new_head.y < CELL_HEIGHT):
            self.game_over_logic()
            return

        # Check of self collision
        if new_head in self.snake:
            self.game_over_logic()
            return

        self.snake.insert(0, new_head)

        # Check of eating an apple
        if new_head == self.apple:
            self.score += 1
            
            # Logic of levels
            if self.score % self.foods_per_level == 0:
                self.level += 1
                self.current_fps += 2
                
            self.spawn_apple()
        else:
            self.snake.pop() # remove tail if did'nt eat an apple

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_w] and self.direction.y != 1:
                        self.direction = pygame.Vector2(0, -1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s] and self.direction.y != -1:
                        self.direction = pygame.Vector2(0, 1)
                    elif event.key in [pygame.K_LEFT, pygame.K_a] and self.direction.x != 1:
                        self.direction = pygame.Vector2(-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d] and self.direction.x != -1:
                        self.direction = pygame.Vector2(1, 0)

            self.update()
            self.screen.fill(BLACK)
            self.draw_elements()
            
            # Interface
            score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
            level_surf = self.font.render(f"Level: {self.level}", True, GREEN)
            
            self.screen.blit(score_surf, (10, 10))
            self.screen.blit(level_surf, (10, 35))

            pygame.display.update()
            self.clock.tick(self.current_fps)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()