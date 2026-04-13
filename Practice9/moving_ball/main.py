import pygame
from ball import Ball

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")
clock = pygame.time.Clock()

ball = Ball(WIDTH // 2, HEIGHT // 2, 25, RED, WIDTH, HEIGHT)

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move(0, -ball.step)
            if event.key == pygame.K_DOWN:
                ball.move(0, ball.step)
            if event.key == pygame.K_LEFT:
                ball.move(-ball.step, 0)
            if event.key == pygame.K_RIGHT:
                ball.move(ball.step, 0)
        
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
