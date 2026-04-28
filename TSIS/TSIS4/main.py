# main.py — entry point; all Pygame screens + main game loop

import pygame
import sys
import json
import os
import math

from config import *
import db
from game import SnakeGame

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ssssssnake")
clock  = pygame.time.Clock()

# ── Settings persistence ──────────────────────────────────────────────────────
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULTS = {"snake_color": list(GREEN), "grid": True, "sound": True}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)

def save_settings(s: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

# ── Font helpers ──────────────────────────────────────────────────────────────
F_TITLE  = pygame.font.SysFont("Impact",   60)
F_LARGE  = pygame.font.SysFont("Consolas", 32, bold=True)
F_MEDIUM = pygame.font.SysFont("Consolas", 22, bold=True)
F_SMALL  = pygame.font.SysFont("Consolas", 16)
F_TINY   = pygame.font.SysFont("Consolas", 13)

def txt(text, font, color=WHITE):
    return font.render(text, True, color)

# ── UI helpers ────────────────────────────────────────────────────────────────
def draw_bg():
    """Animated dark-green grid background."""
    screen.fill((5, 12, 5))
    t = pygame.time.get_ticks()
    offset = (t // 60) % CELL_SIZE
    for x in range(-CELL_SIZE, SCREEN_WIDTH + CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, (0, 30, 0), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(-CELL_SIZE + offset, SCREEN_HEIGHT + CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, (0, 30, 0), (0, y), (SCREEN_WIDTH, y))

def draw_panel(rect, alpha=200):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    pygame.draw.rect(s, (*GREEN, 80), s.get_rect(), 2, border_radius=8)
    screen.blit(s, (rect[0], rect[1]))

class Button:
    def __init__(self, rect, label, color=(0, 140, 0)):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.color   = color
        self.hovered = False

    def draw(self, surface=None):
        if surface is None:
            surface = screen
        col = tuple(min(255, c+50) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=6)
        s = F_MEDIUM.render(self.label, True, WHITE)
        surface.blit(s, s.get_rect(center=self.rect.center))

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# SCREEN: Username entry
def screen_username() -> str:
    name      = ""
    cursor_on = True
    cursor_t  = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        if now - cursor_t > 500:
            cursor_on = not cursor_on
            cursor_t  = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 20 and event.unicode.isprintable():
                    name += event.unicode

        draw_bg()

        # Title
        title_s = F_TITLE.render("SSSSNAKE", True, GREEN)
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH//2, 120)))

        draw_panel((100, 180, 440, 140))
        prompt = F_MEDIUM.render("Enter your username:", True, (180, 255, 180))
        screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH//2, 215)))

        display = name + ("|" if cursor_on else " ")
        name_s  = F_LARGE.render(display, True, GOLD)
        screen.blit(name_s, name_s.get_rect(center=(SCREEN_WIDTH//2, 265)))

        hint = F_SMALL.render("Press ENTER to continue", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, 370)))

        pygame.display.flip()
        clock.tick(30)


# SCREEN: Main Menu
def screen_main_menu(settings: dict) -> str:
    cx = SCREEN_WIDTH // 2
    btns = {
        "play":        Button((cx-100, 180, 200, 44), "PLAY",        (0,130,0)),
        "leaderboard": Button((cx-100, 236, 200, 44), "SCORES",     (120,90,0)),
        "settings":    Button((cx-100, 292, 200, 44), "SETTINGS",    (0,70,140)),
        "quit":        Button((cx-100, 348, 200, 44), "QUIT",        (140,0,0)),
    }

    while True:
        mx, my = pygame.mouse.get_pos()
        for b in btns.values(): b.update((mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            for key, btn in btns.items():
                if btn.clicked(event): return key

        draw_bg()

        title_s = F_TITLE.render("SSSSNAKE", True, GREEN)
        glow    = F_TITLE.render("SSSSNAKE", True, (0, 80, 0))
        screen.blit(glow,    glow.get_rect(   center=(SCREEN_WIDTH//2+2, 82)))
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH//2,   80)))

        sub = F_SMALL.render("Power-ups · Poison · Obstacles · Leaderboard", True, (120,200,120))
        screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 128)))

        draw_panel((cx-120, 165, 240, 244))
        for b in btns.values(): b.draw()

        diff_s = F_TINY.render(f"Grid: {'on' if settings['grid'] else 'off'}  "
                               f"Sound: {'on' if settings['sound'] else 'off'}", True, GRAY)
        screen.blit(diff_s, diff_s.get_rect(center=(SCREEN_WIDTH//2, 430)))

        pygame.display.flip()
        clock.tick(30)


# SCREEN: Settings
SNAKE_COLOUR_PRESETS = [
    ("Green",  [0, 200, 0]),
    ("Cyan",   [0, 210, 200]),
    ("Yellow", [220, 200, 0]),
    ("Pink",   [220, 80, 180]),
    ("White",  [220, 220, 220]),
]

def screen_settings(settings: dict):
    cx = SCREEN_WIDTH // 2

    grid_btn  = Button((cx-90, 160, 180, 40), "", (0,70,140))
    sound_btn = Button((cx-90, 216, 180, 40), "", (0,70,140))
    col_l     = Button((cx-160, 280, 36, 40), "<", (60,60,60))
    col_r     = Button((cx+124, 280, 36, 40), ">", (60,60,60))
    save_btn  = Button((cx-90, 380, 180, 44), "SAVE & BACK", (0,120,0))

    # Find current colour preset index
    col_idx = 0
    for i, (_, rgb) in enumerate(SNAKE_COLOUR_PRESETS):
        if settings["snake_color"] == rgb:
            col_idx = i; break

    def refresh():
        grid_btn.label  = f"Grid: {'ON' if settings['grid']  else 'OFF'}"
        sound_btn.label = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        settings["snake_color"] = SNAKE_COLOUR_PRESETS[col_idx][1]

    refresh()

    while True:
        mx, my = pygame.mouse.get_pos()
        for b in [grid_btn, sound_btn, col_l, col_r, save_btn]: b.update((mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if grid_btn.clicked(event):
                settings["grid"] = not settings["grid"]; refresh()
            if sound_btn.clicked(event):
                settings["sound"] = not settings["sound"]; refresh()
            if col_l.clicked(event):
                col_idx = (col_idx - 1) % len(SNAKE_COLOUR_PRESETS); refresh()
            if col_r.clicked(event):
                col_idx = (col_idx + 1) % len(SNAKE_COLOUR_PRESETS); refresh()
            if save_btn.clicked(event):
                save_settings(settings); return

        draw_bg()
        draw_panel((60, 50, 520, 400))

        title_s = F_LARGE.render("SETTINGS", True, GREEN)
        screen.blit(title_s, title_s.get_rect(center=(cx, 80)))

        grid_btn.draw(); sound_btn.draw()

        # Colour picker
        col_lbl = F_MEDIUM.render("Snake Color:", True, WHITE)
        screen.blit(col_lbl, col_lbl.get_rect(center=(cx, 265)))

        name, rgb = SNAKE_COLOUR_PRESETS[col_idx]
        swatch = pygame.Surface((80, 40))
        swatch.fill(rgb)
        pygame.draw.rect(swatch, WHITE, swatch.get_rect(), 2)
        screen.blit(swatch, swatch.get_rect(center=(cx, 300)))

        col_name_s = F_SMALL.render(name, True, WHITE)
        screen.blit(col_name_s, col_name_s.get_rect(center=(cx, 327)))

        col_l.draw(); col_r.draw()

        # Mini snake preview
        preview_x, preview_y = cx - 60, 348
        for i in range(5):
            r = pygame.Rect(preview_x + i*22, preview_y, 20, 20)
            c = tuple(max(0, v-80) for v in rgb) if i == 0 else tuple(rgb)
            pygame.draw.rect(screen, c, r, border_radius=3)
            pygame.draw.rect(screen, WHITE, r, 1, border_radius=3)

        save_btn.draw()

        pygame.display.flip()
        clock.tick(30)


# SCREEN: Leaderboard
def screen_leaderboard():
    back_btn = Button((SCREEN_WIDTH//2 - 80, 440, 160, 40), "BACK", (60,60,80))
    rows     = db.get_top10()

    while True:
        mx, my = pygame.mouse.get_pos()
        back_btn.update((mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if back_btn.clicked(event): return

        draw_bg()
        draw_panel((20, 20, SCREEN_WIDTH-40, 410))

        title_s = F_LARGE.render("TOP 10", True, GOLD)
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH//2, 50)))

        # Header
        cols_x = [35, 90, 250, 340, 440]
        headers = ["№", "Username", "Score", "Lvl", "Date"]
        for h, x in zip(headers, cols_x):
            screen.blit(F_TINY.render(h, True, GOLD), (x, 78))
        pygame.draw.line(screen, GOLD, (25, 94), (SCREEN_WIDTH-25, 94), 1)

        # Rows
        for i, row in enumerate(rows):
            y = 100 + i * 30
            bg = pygame.Surface((SCREEN_WIDTH-50, 26), pygame.SRCALPHA)
            bg.fill((255,215,0,20) if row.get("rank",i+1) <= 3 else (255,255,255,8))
            screen.blit(bg, (25, y))

            medal = {1:"1",2:"2",3:"3"}.get(row.get("rank",i+1), str(row.get("rank",i+1)))
            vals  = [medal,
                     str(row.get("username","?"))[:12],
                     str(row.get("score",0)),
                     str(row.get("level_reached","?")),
                     str(row.get("played_at",""))[:10]]
            col_c = GOLD if row.get("rank",i+1) <= 3 else WHITE
            for v, x in zip(vals, cols_x):
                screen.blit(F_TINY.render(v, True, col_c), (x, y+6))

        if not rows:
            empty = F_MEDIUM.render("No scores yet!", True, GRAY)
            screen.blit(empty, empty.get_rect(center=(SCREEN_WIDTH//2, 240)))

        back_btn.draw()
        pygame.display.flip()
        clock.tick(30)


# SCREEN: Game Over
def screen_game_over(score: int, level: int, personal_best: int,
                     username: str) -> str:
    # Save to DB
    db.save_session(username, score, level)
    new_pb = max(score, personal_best)

    cx = SCREEN_WIDTH // 2
    retry_btn = Button((cx-110, 350, 200, 44), "RETRY",     (0,120,0))
    menu_btn  = Button((cx-110, 406, 200, 44), "MAIN MENU", (0,60,140))

    is_pb = score >= personal_best and score > 0
    shake = 15

    while True:
        mx, my = pygame.mouse.get_pos()
        retry_btn.update((mx, my)); menu_btn.update((mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if retry_btn.clicked(event): return "retry"
            if menu_btn.clicked(event):  return "menu"

        draw_bg()
        draw_panel((40, 60, SCREEN_WIDTH-80, 360))

        # Shaky title
        import random as _r
        ox = _r.randint(-shake, shake)//4 if shake > 0 else 0
        shake = max(0, shake - 1)
        go_s = F_TITLE.render("GAME OVER", True, RED)
        screen.blit(go_s, go_s.get_rect(center=(cx+ox, 110)))

        stats = [
            ("Score",         str(score),          WHITE),
            ("Level reached", str(level),           GREEN),
            ("Personal best", str(new_pb),          GOLD if is_pb else WHITE),
        ]
        for i, (lbl, val, col) in enumerate(stats):
            y = 175 + i * 62
            l_s = F_SMALL.render(lbl, True, WHITE)
            v_s = F_LARGE.render(val,  True, col)
            screen.blit(l_s, l_s.get_rect(center=(cx, y-10)))
            screen.blit(v_s, v_s.get_rect(center=(cx, y+22)))

        if is_pb:
            pb_s = F_MEDIUM.render("NEW PERSONAL BEST!", True, GOLD)
            screen.blit(pb_s, pb_s.get_rect(center=(cx, 300)))

        retry_btn.draw(); menu_btn.draw()

        user_s = F_TINY.render(f"Player: {username}", True, (120,120,180))
        screen.blit(user_s, user_s.get_rect(center=(cx, 462)))

        pygame.display.flip()
        clock.tick(30)

    return "menu"


# Main loop
def main():
    db.init_db()
    settings = load_settings()
    username = screen_username()

    while True:
        action = screen_main_menu(settings)

        if action == "quit":
            save_settings(settings)
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            screen_leaderboard()

        elif action == "settings":
            screen_settings(settings)

        elif action == "play":
            # Fetch personal best before starting
            personal_best = db.get_personal_best(username)

            while True:
                game = SnakeGame(username, settings, personal_best)

                # ── Inner game loop ───────────────────────────────────────
                result = None
                while result is None:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        game.handle_input(event)

                    result = game.update()

                    game.draw()
                    pygame.display.flip()
                    clock.tick(game.current_fps)

                # Show crash animation, then game-over screen
                game.show_crash()
                next_action = screen_game_over(
                    game.score, game.level, personal_best, username)
                # Update PB for the retry loop
                personal_best = max(personal_best, game.score)

                if next_action == "retry":
                    continue      # inner while → new SnakeGame
                else:
                    break         # back to main menu


if __name__ == "__main__":
    main()