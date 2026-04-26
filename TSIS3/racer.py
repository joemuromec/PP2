import pygame, sys
from pygame.locals import *
import random, time, math

pygame.init()

# Настройки FPS
FPS = 60
FramePerSecond = pygame.time.Clock()

# Цвета
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE  = (0, 0, 255)
GOLD  = (255, 215, 0)

# Шрифты
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Загрузка фона
background = pygame.image.load(r"PP2\TSIS3\assets\images\AnimatedStreet.png")

# Параметры экрана
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TURBO")

# Полосы движения (центральные координаты X)
LANES = [60, 160, 260, 340]

# Глобальные переменные
SPEED = 5
SCORE = 0
COIN_SCORE = 0
ACTIVE_POWERUP = None
POWERUP_TIMER = 0
# Порог монет, при котором Enemy ускоряется дополнительно
N_COINS_THRESHOLD = 10

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"PP2\TSIS3\assets\images\Enemy.png")
        self.rect = self.image.get_rect()
        self.respawn()
        
    def respawn(self):
        self.rect.center = (random.choice(LANES), -50)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.respawn()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"PP2\TSIS3\assets\images\Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (200, 520)
        self.shielded = False
        self.is_slowed = False
    
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        move_speed = 10 if ACTIVE_POWERUP == "Nitro" else 5
        if self.is_slowed:
            move_speed = 2
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-move_speed, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(move_speed, 0)


class Obstacle(pygame.sprite.Sprite):
    # Препятствия: лужи (замедляют) и барьеры (убивают)
    def __init__(self, type):
        super().__init__()
        self.type = type
        if type == "Oil":
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (50, 50, 50, 150), (20, 20), 20)
        else: # Barrier
            self.image = pygame.Surface((60, 20))
            self.image.fill((150, 75, 0))
        self.rect = self.image.get_rect()
        self.respawn()
    
    def respawn(self):
        self.rect.center = (random.choice(LANES), random.randint(-1000, -100))

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.types = ["Nitro", "Shield", "Repair"]
        self.type = random.choice(self.types)
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE if self.type == "Shield" else RED if self.type == "Repair" else GOLD)
        self.rect = self.image.get_rect()
        self.spawn_time = pygame.time.get_ticks()
        self.respawn()

    def respawn(self):
        self.type = random.choice(self.types)
        if self.type == "Shield":
            self.image.fill(BLUE)
        elif self.type == "Repair":
            self.image.fill(RED)
        elif self.type == "Nitro":
            self.image.fill(GOLD)
        font = pygame.font.SysFont("Arial", 20)
        char = self.type[0] # Берем первую букву (N, S или R)
        text_surf = font.render(char, True, (255, 255, 255))
        self.image.blit(text_surf, (8, 5))

        self.rect.center = (random.choice(LANES), random.randint(-500, -50))
        self.spawn_time = pygame.time.get_ticks()
    
    def move(self):
        self.rect.move_ip(0, SPEED - 1)
        # Исчезает через 7 секунд, если не собрано
        if self.rect.top > SCREEN_HEIGHT or (pygame.time.get_ticks() - self.spawn_time > 7000):
            self.respawn()

# Монеты с разным весом
class Coin(pygame.sprite.Sprite): 
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"PP2\TSIS3\assets\images\coin.png")
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

enemies = pygame.sprite.Group(Enemy())
coins = pygame.sprite.Group(Coin())
obstacles = pygame.sprite.Group(Obstacle("Oil"), Obstacle("Barrier"))
powerups = pygame.sprite.Group(PowerUp())
all_sprites = pygame.sprite.Group(P1)
all_sprites.add(enemies, obstacles, powerups, coins)

# Событие постепенного ускорения (раз в секунду)
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


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

        # Увеличиваем скорость Enemy, когда игрок набирает N монет
        # Проверяем, пересекли ли мы порог (каждые 10 монет)
        if (COIN_SCORE // N_COINS_THRESHOLD) > (old_coin_score // N_COINS_THRESHOLD):
            SPEED += 1.0 # Дополнительный рывок скорости
            print(f"Bonus Speed! Current speed: {SPEED}")

    # Коллизии с бонусами
    pu_hit = pygame.sprite.spritecollideany(P1, powerups)
    if pu_hit:
        ACTIVE_POWERUP = pu_hit.type
        if ACTIVE_POWERUP == "Shield":
            P1.shielded = True
            POWERUP_TIMER = pygame.time.get_ticks() + 5000
        elif ACTIVE_POWERUP == "Nitro":
            POWERUP_TIMER = pygame.time.get_ticks() + 3000
        elif ACTIVE_POWERUP == "Repair":
            # В текущей логике Repair просто сбрасывает препятствия
            for obs in obstacles: obs.respawn()
        pu_hit.respawn()

    P1.is_slowed = False # Сбрасываем каждый кадр

    # Коллизии с препятствиями
    obs_hit = pygame.sprite.spritecollideany(P1, obstacles)
    if obs_hit:
        if obs_hit.type == "Oil":
            # Эффект замедления (просто сдвигаем игрока назад)
            P1.is_slowed = True
        elif obs_hit.type == "Barrier":
            if not P1.shielded:
                # Game over
                pygame.quit()
                sys.exit()
            else:
                P1.shielded = False
                ACTIVE_POWERUP = None
                obs_hit.respawn()
                

    # Столкновение с врагом
    if pygame.sprite.spritecollideany(P1, enemies):
        if not P1.shielded:
            pygame.mixer.Sound(r"PP2\TSIS3\assets\sounds\crash.wav").play()
            time.sleep(0.5)
            screen.fill(RED)
            screen.blit(game_over, (30, 250))
            pygame.display.update()
            for entity in all_sprites:
                entity.kill()
            time.sleep(2)
            pygame.quit()
            sys.exit()
        else:
            P1.shielded = False
            ACTIVE_POWERUP = None
            for e in enemies: e.respawn()

        

    
    if ACTIVE_POWERUP:
        # Логика таймера бонусов
        time_left_ms = POWERUP_TIMER - pygame.time.get_ticks()
        remaining_time = max(0, math.ceil(time_left_ms / 1000))
        if time_left_ms <= 0:
            ACTIVE_POWERUP = None
            P1.shielded = False
        elif ACTIVE_POWERUP == "Repair":
            p_color = RED
            powerup_str = f"{ACTIVE_POWERUP.upper()}"
            powerup_text = font_small.render(powerup_str, True, p_color)
            screen.blit(powerup_text, (10, 50))
        else:
            p_color = GOLD if ACTIVE_POWERUP == "Nitro" else BLUE
            powerup_str = f"{ACTIVE_POWERUP.upper()}: {remaining_time}s"
            powerup_text = font_small.render(powerup_str, True, p_color)
            screen.blit(powerup_text, (10, 30))
    
    # Отрисовка текста
    scores = font_small.render("Enemies: " + str(SCORE), True, BLACK)
    coin_text = font_small.render("Coins: " + str(COIN_SCORE), True, BLACK)
    screen.blit(scores, (10, 10))
    screen.blit(coin_text, (SCREEN_WIDTH - 120, 10))

    pygame.display.update()
    FramePerSecond.tick(FPS)