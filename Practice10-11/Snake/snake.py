import pygame, sys, random

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
CELL_SIZE = 20
CELL_WIDTH = SCREEN_WIDTH // CELL_SIZE
CELL_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (200, 0, 0)      # Обычная еда
GOLD  = (255, 215, 0)    # Супер-еда
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
GRAY  = (40, 40, 40)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ssssssnake: Power-ups & Timers")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.reset_game()

    def reset_game(self):
        """Сброс всех параметров игры"""
        start_x = random.randint(5, CELL_WIDTH - 6)
        start_y = random.randint(5, CELL_HEIGHT - 6)
        self.snake = [
            pygame.Vector2(start_x, start_y),
            pygame.Vector2(start_x - 1, start_y),
            pygame.Vector2(start_x - 2, start_y)
        ]
        self.direction = pygame.Vector2(1, 0)
        
        self.score = 0
        self.level = 1
        self.current_fps = 10
        self.foods_per_level = 5
        
        self.spawn_food()

    def spawn_food(self):
        """Создание еды с весом и таймером"""
        while True:
            pos = pygame.Vector2(
                random.randint(0, CELL_WIDTH - 1),
                random.randint(0, CELL_HEIGHT - 1)
            )
            if pos not in self.snake:
                break
        
        # Определяем тип еды (20% шанс на золотую еду)
        if random.random() < 0.2:
            self.food = {
                "pos": pos,
                "color": GOLD,
                "weight": 3,
                "timer": 5000, # Исчезнет через 5 секунд (в миллисекундах)
                "is_special": True
            }
        else:
            self.food = {
                "pos": pos,
                "color": RED,
                "weight": 1,
                "timer": None, # Обычная еда не исчезает
                "is_special": False
            }
        
        # Засекаем время появления
        self.food_spawn_time = pygame.time.get_ticks()

    def draw_elements(self):
        """Отрисовка сетки, еды и змейки"""
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
            
        # Отрисовка еды
        f_pos = self.food["pos"]
        food_rect = pygame.Rect(f_pos.x * CELL_SIZE, f_pos.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, self.food["color"], food_rect)

        # Отрисовка таймера для золотой еды
        if self.food["is_special"]:
            time_left = self.food["timer"] - (pygame.time.get_ticks() - self.food_spawn_time)
            if time_left > 0:
                # Рисуем полоску времени над едой
                timer_width = (time_left / self.food["timer"]) * CELL_SIZE
                pygame.draw.rect(self.screen, WHITE, (f_pos.x * CELL_SIZE, f_pos.y * CELL_SIZE - 5, timer_width, 3))

        # Отрисовка змейки
        for index, block in enumerate(self.snake):
            rect = pygame.Rect(block.x * CELL_SIZE, block.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = DARK_GREEN if index == 0 else GREEN
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

    def update(self):
        """Логика перемещения, поедания и уровней"""
        
        # Проверка таймера еды
        if self.food["is_special"]:
            elapsed = pygame.time.get_ticks() - self.food_spawn_time
            if elapsed > self.food["timer"]:
                self.spawn_food() # Еда исчезла, создаем новую
                return

        new_head = self.snake[0] + self.direction

        # Проверка столкновений
        if not (0 <= new_head.x < CELL_WIDTH and 0 <= new_head.y < CELL_HEIGHT) or new_head in self.snake:
            self.reset_game()
            return

        self.snake.insert(0, new_head)

        # Поедание еды
        if new_head == self.food["pos"]:
            self.score += self.food["weight"] # Учитываем вес еды
            
            # Повышение уровня
            if self.score // self.foods_per_level > self.level - 1:
                self.level += 1
                self.current_fps += 2
            
            self.spawn_food()
        else:
            self.snake.pop()

    def run(self):
        """Главный цикл управления"""
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
            
            # Отображение данных
            score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
            level_surf = self.font.render(f"Level: {self.level}", True, GREEN)
            self.screen.blit(score_surf, (10, 10))
            self.screen.blit(level_surf, (10, 35))

            pygame.display.update()
            self.clock.tick(self.current_fps)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()