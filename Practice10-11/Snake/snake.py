import pygame, sys, random
from pygame.locals import *

# Constant variables
FPS = 15
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
CELL_WIDTH = int(SCREEN_WIDTH/CELL_SIZE)
CELL_HEIGHT = int(SCREEN_HEIGHT/CELL_SIZE)

# Colors
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

# Directions and position of head
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HEAD = 0

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode(SCREEN_WIDTH, SCREEN_HEIGHT)
basic_font = pygame.font.SysFont("Arial", 18)
pygame.display.set_caption("Sssssnake")

# Initial position of snake
start_x = random.randint(5, CELL_WIDTH - 6)
start_y = random.randint(5, CELL_HEIGHT - 6)
snake_coords = [{"x": start_x, "y": start_y},
                {"x": start_x-1, "y": start_y},
                {"x": start_x-2, "y": start_y}]
direcrtion = RIGHT

apple = {'x': random.randint(0, CELL_WIDTH - 1), "y": random.randint(0, CELL_HEIGHT - 1)}

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if (event.key == K_LEFT or event.key == K_a) and direcrtion != RIGHT:
                direcrtion = LEFT
            elif (event.key == K_RIGHT or event.key == K_d) and direcrtion != LEFT:
                direcrtion = RIGHT
            elif (event.key == K_DOWN or event.key == K_s) and direcrtion != UP:
                direcrtion = DOWN
            elif (event.key == K_UP or event.key == K_w) and direcrtion != DOWN:
                direcrtion = UP

    # Collisions with edges or snake itself
    if snake_coords[HEAD]['x'] == -1 or snake_coords[HEAD]['x'] == CELL_WIDTH or snake_coords[HEAD]['y'] == -1 or snake_coords[HEAD]['y'] == CELL_HEIGHT:
        pass # Exit the game
    for snakeBody in snake_coords[1:]:
        if snakeBody["x"] == snake_coords[HEAD]['x'] and snakeBody['y'] == snake_coords[HEAD]['y']:
            pass # Exit the game
    
    # Collisions with apple
    if snake_coords[HEAD]['x'] == apple['x'] and snake_coords[HEAD]['y'] == apple['y']:
        apple = {'x': random.randint(0, CELL_WIDTH - 1), "y": random.randint(0, CELL_HEIGHT - 1)} # do not remove tail segment
    else:
        del snake_coords[-1] # remove tail segment

    if direcrtion == UP:
        newHead = {'x': snake_coords[HEAD]['x'], 'y': snake_coords[HEAD]['y'] - 1}
    elif direcrtion == DOWN:
        newHead = {'x': snake_coords[HEAD]['x'], 'y': snake_coords[HEAD]['y'] + 1}
    elif direcrtion == LEFT:
        newHead = {'x': snake_coords[HEAD]['x'] - 1, 'y': snake_coords[HEAD]['y']}
    elif direcrtion == RIGHT:
        newHead = {'x': snake_coords[HEAD]['x'] + 1, 'y': snake_coords[HEAD]['y']}
    snake_coords.insert(0, newHead)

    screen.fill(BGCOLOR)
    
    # Draw grid
    for x in range (0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, DARKGRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range (0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, DARKGRAY, (0, y), (SCREEN_WIDTH, y))

    # Draw worm
    for coord in snake_coords:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        snakeSegmentRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, DARKGREEN, snakeSegmentRect)
        snakeInnerSegmentRect = pygame.Rect(x+4, y+4, CELL_SIZE - 8, CELL_SIZE - 8)
        pygame.draw.rect(screen, GREEN, snakeInnerSegmentRect)
    
    # Draw apple
    x = apple['x'] * CELL_SIZE
    y = apple['y'] * CELL_SIZE
    appleRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, appleRect)

    # Draw score
    score = len(snake_coords - 3)
    score_text = basic_font.render("Score: %s" % (score), True, WHITE)
    score_rect = score_text.get_rect()
    score_rect.topleft = (SCREEN_WIDTH - 120, 10)
    screen.blit(score_text, score_rect)

    pygame.display.update()
    clock.tick(FPS)