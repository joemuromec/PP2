import pygame
import os
from player import MusicPlayer

pygame.init()
pygame.mixer.init()

current_dir = os.path.dirname(os.path.abspath(__file__))
music_path = os.path.join(current_dir, "music")
screen = pygame.display.set_mode((600, 300))
pygame.display.set_caption("Music Player")
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

player = MusicPlayer(music_path)

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.prev_track()
            elif event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_UP:
                player.set_volume(0.1)
            elif event.key == pygame.K_DOWN:
                player.set_volume(-0.1)

    pygame.draw.rect(screen, (100, 100, 100), (50, 150, 500, 10))
    current_time = player.get_pos_seconds()
    progress_width = (current_time * 5) % 500
    pygame.draw.rect(screen, (0, 255, 0), (50, 150, progress_width, 10))

    vol_bar_height = int(player.volume * 100)
    pygame.draw.rect(screen, (200, 200, 200), (550, 50, 20, 100))
    pygame.draw.rect(screen, (141, 10, 207), (550, 150 - vol_bar_height, 20, vol_bar_height))

    vol_text = font.render(f"Vol:{int(player.volume * 100)}%", True, (255, 255, 255))
    screen.blit(vol_text, (500, 160))

    minutes = current_time // 60
    seconds = current_time % 60
    time_str = f"{minutes:02}:{seconds:02}"
    time_text = font.render(time_str, True, (255, 255, 255))
    screen.blit(time_text, (50, 160))

    track_text = font.render(f"Track: {player.get_current_track_name()}", True, (255, 255, 255))
    status = "Playing" if player.is_playing else "Stopped"
    status_text = font.render(f"Status: {status}", True , (0, 255, 0) if player.is_playing else (255, 0, 0))

    controls_text = font.render("P: Play | S: Stop | N: Next | B: Previous | Q: Quit", True, (200, 200, 200))

    screen.blit(track_text, (50, 50))
    screen.blit(status_text, (50, 100))
    screen.blit(controls_text, (50, 200))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()