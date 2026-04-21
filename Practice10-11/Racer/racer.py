import pygame, sys
from pygame.locals import *
import random, time

pygame.init()

FPS = 60
FramePerSecond = pygame.time.Clock()

# Colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Background image
background = pygame.image.load(r"Practice10-11\Racer\AnimatedStreet.png")

#Screen info
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(WHITE)
pygame.display.set_caption("TURBO")

# Object Classes
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

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"Practice10-11\Racer\coin.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)
    
    def move(self):
        self.rect.move_ip(0, 5)
        if (self.rect.top > SCREEN_HEIGHT):
            self.respawn()

    def respawn(self):
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)
        
    

# Sprites
P1 = Player()
E1 = Enemy()
C1 = Coin()

# Sprites Groups
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# User event
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# State variables
SPEED = 5
SCORE = 0
COIN_SCORE = 0

# Game loop
running = True
while running:
    # Events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == INC_SPEED:
            SPEED += 0.5

    # Background
    screen.blit(background, (0, 0))

    # Enemy score
    scores = font_small.render("Enemies: " + str(SCORE), True, BLACK)
    screen.blit(scores, (10, 10))
    
    # Coin score
    coin_text = font_small.render("Coins: " + str(COIN_SCORE), True, BLACK)
    screen.blit(coin_text, (SCREEN_WIDTH - 100, 10))

    for entity in all_sprites:
        screen.blit(entity.image, entity.rect)
        entity.move()
    
    coin_collisions = pygame.sprite.spritecollide(P1, coins, False)
    for coin in coin_collisions:
        COIN_SCORE += 1
        coin.respawn()

    # Collisions
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