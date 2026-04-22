import pygame, sys
from pygame.locals import *
import random, time

pygame.init()

# Настройки FPS
FPS = 60
FramePerSecond = pygame.time.Clock()

# Цвета
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Шрифты
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Загрузка фона
background = pygame.image.load(r"Practice10-11\Racer\AnimatedStreet.png")

# Параметры экрана
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TURBO")

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"Practice10-11\Racer\Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.bottom > 600):
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(30, 370), 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"Practice10-11\Racer\Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
    
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)

# Монеты с разным весом
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"Practice10-11\Racer\coin.png")
        self.rect = self.image.get_rect()
        self.weight = 1 # Значение веса по умолчанию
        self.respawn()
    
    def move(self):
        self.rect.move_ip(0, 5)
        if (self.rect.top > SCREEN_HEIGHT):
            self.respawn()

    def respawn(self):
        # Генерируем случайный вес: 1 (80% шанс), 3 (15% шанс) или 5 (5% шанс)
        choice = random.random()
        if choice < 0.8:
            self.weight = 1
            # Обычный размер
            self.image_display = pygame.transform.scale(self.image, (25, 25))
        elif choice < 0.95:
            self.weight = 3
            # Серебряная/средняя монета — чуть больше
            self.image_display = pygame.transform.scale(self.image, (35, 35))
        else:
            self.weight = 5
            # Золотая/тяжелая монета — самая большая
            self.image_display = pygame.transform.scale(self.image, (45, 45))
            
        self.rect = self.image_display.get_rect()
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# Инициализация спрайтов
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group()
enemies.add(E1)
coins = pygame.sprite.Group()
coins.add(C1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Событие постепенного ускорения (раз в секунду)
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Глобальные переменные состояния
SPEED = 5
SCORE = 0
COIN_SCORE = 0
# Порог монет, при котором Enemy ускоряется дополнительно
N_COINS_THRESHOLD = 10 

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        # Постоянное ускорение со временем
        if event.type == INC_SPEED:
            SPEED += 0.2

    screen.blit(background, (0, 0))

    # Отрисовка текста
    scores = font_small.render("Enemies: " + str(SCORE), True, BLACK)
    coin_text = font_small.render("Coins: " + str(COIN_SCORE), True, BLACK)
    screen.blit(scores, (10, 10))
    screen.blit(coin_text, (SCREEN_WIDTH - 120, 10))

    # Отрисовка и движение всех объектов
    for entity in all_sprites:
        # Для монеты отрисовываем именно масштабированное изображение
        if isinstance(entity, Coin):
            screen.blit(entity.image_display, entity.rect)
        else:
            screen.blit(entity.image, entity.rect)
        entity.move()
    
    # Обработка сбора монет
    coin_collisions = pygame.sprite.spritecollide(P1, coins, False)
    for coin in coin_collisions:
        old_coin_score = COIN_SCORE
        COIN_SCORE += coin.weight # Добавляем вес монеты к общему счету
        coin.respawn()

        # ЗАДАНИЕ: Увеличиваем скорость Enemy, когда игрок набирает N монет
        # Проверяем, пересекли ли мы порог (например, каждые 10 монет)
        if (COIN_SCORE // N_COINS_THRESHOLD) > (old_coin_score // N_COINS_THRESHOLD):
            SPEED += 1.0 # Дополнительный рывок скорости
            print(f"Bonus Speed! Current speed: {SPEED}")

    # Столкновение с врагом
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound(r"Practice10-11\Racer\crash.wav").play()
        time.sleep(0.5)
        screen.fill(RED)
        screen.blit(game_over, (30, 250))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSecond.tick(FPS)