import pygame, sys, json, os, math, random, time
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# ── Constants ────────────────────────────────────────────────────────────────
FPS            = 60
SCREEN_WIDTH   = 400
SCREEN_HEIGHT  = 600
LANES          = [60, 160, 260, 340]
N_COINS_THRESHOLD = 10

# Colours
RED    = (220, 50,  50)
BLACK  = (10,  10,  10)
WHITE  = (255, 255, 255)
BLUE   = (60,  120, 220)
GOLD   = (255, 200,  30)
GREEN  = (50,  200, 100)
GRAY   = (160, 160, 160)
DARK   = (25,  25,  35)
ACCENT = (255, 80,  80)

# Car colour options (name, body-colour, window-colour)
CAR_COLORS = [
    ("Red",    (220, 50,  50),  (180, 220, 255)),
    ("Blue",   (50,  100, 220), (180, 220, 255)),
    ("Green",  (50,  180, 80),  (180, 255, 200)),
    ("Yellow", (230, 200, 30),  (255, 240, 180)),
    ("Purple", (140, 60,  200), (200, 180, 255)),
]

# Difficulty presets  (enemy_speed, inc_interval_ms, spawn_rate_ms)
DIFFICULTIES = {
    "Easy":   {"base_speed": 4,   "inc": 0.15, "enemy_count": 1, "obs_count": 1},
    "Normal": {"base_speed": 5,   "inc": 0.20, "enemy_count": 2, "obs_count": 2},
    "Hard":   {"base_speed": 7,   "inc": 0.30, "enemy_count": 3, "obs_count": 3},
}

SETTINGS_FILE    = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

# ── Persistence helpers ───────────────────────────────────────────────────────
def load_settings():
    defaults = {"sound": True, "car_color": 0, "difficulty": "Normal"}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            defaults.update(data)
        except Exception:
            pass
    return defaults

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_leaderboard(lb):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)

def add_to_leaderboard(name, score, distance, coins):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score, "distance": distance, "coins": coins})
    lb.sort(key=lambda x: x["score"], reverse=True)
    lb = lb[:10]
    save_leaderboard(lb)
    return lb

# ── Asset helpers ────────────────────────────────────
def make_player_surface(car_idx):
    """Draw a top-down car sprite using the chosen colour."""
    w, h = 36, 60
    body_col, win_col = CAR_COLORS[car_idx][1], CAR_COLORS[car_idx][2]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(surf, body_col, (3, 4, w-6, h-8), border_radius=8)
    # Windshield
    pygame.draw.rect(surf, win_col, (7, 8, w-14, 12), border_radius=3)
    # Rear window
    pygame.draw.rect(surf, win_col, (7, h-20, w-14, 10), border_radius=3)
    # Wheels
    wheel_col = (40, 40, 40)
    for wx, wy in [(0,8),(w-6,8),(0,h-18),(w-6,h-18)]:
        pygame.draw.rect(surf, wheel_col, (wx, wy, 6, 10), border_radius=2)
    return surf

def make_enemy_surface():
    w, h = 36, 60
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (100, 100, 110), (3, 4, w-6, h-8), border_radius=8)
    pygame.draw.rect(surf, (180, 210, 255), (7, 8, w-14, 12), border_radius=3)
    pygame.draw.rect(surf, (180, 210, 255), (7, h-20, w-14, 10), border_radius=3)
    wheel_col = (40, 40, 40)
    for wx, wy in [(0,8),(w-6,8),(0,h-18),(w-6,h-18)]:
        pygame.draw.rect(surf, wheel_col, (wx, wy, 6, 10), border_radius=2)
    return surf

def load_or_make(path, fallback_fn, *args):
    """Try to load image; fall back to a drawn surface."""
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
    return fallback_fn(*args)

def make_coin_surface(size=25):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, GOLD, (size//2, size//2), size//2)
    pygame.draw.circle(surf, (200, 160, 0), (size//2, size//2), size//2, 2)
    f = pygame.font.SysFont("Arial", size-8, bold=True)
    t = f.render("$", True, (255, 255, 255))
    surf.blit(t, t.get_rect(center=(size//2, size//2)))
    return surf

def make_background():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill((60, 60, 65))
    # Road markings
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.rect(surf, (80, 80, 85), (0, y, SCREEN_WIDTH, 20))
    # Lane dividers
    for x in [110, 210, 310]:
        for y in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.rect(surf, (200, 200, 100), (x-1, y, 2, 15))
    # Sidewalks
    pygame.draw.rect(surf, (90, 75, 70), (0, 0, 40, SCREEN_HEIGHT))
    pygame.draw.rect(surf, (90, 75, 70), (360, 0, 40, SCREEN_HEIGHT))
    return surf

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_title  = pygame.font.SysFont("Impact", 64)
font_large  = pygame.font.SysFont("Verdana", 36, bold=True)
font_medium = pygame.font.SysFont("Verdana", 24)
font_small  = pygame.font.SysFont("Verdana", 18)
font_tiny   = pygame.font.SysFont("Verdana", 14)

# ── UI helpers ────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TURBO")
clock  = pygame.time.Clock()

def draw_gradient_bg(surface, top=(20,20,30), bottom=(40,40,60)):
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        r = int(top[0]*(1-t) + bottom[0]*t)
        g = int(top[1]*(1-t) + bottom[1]*t)
        b = int(top[2]*(1-t) + bottom[2]*t)
        pygame.draw.line(surface, (r,g,b), (0,y),(SCREEN_WIDTH,y))

class Button:
    def __init__(self, rect, text, color=ACCENT, text_color=WHITE, font=font_medium):
        self.rect      = pygame.Rect(rect)
        self.text      = text
        self.color     = color
        self.hov_color = tuple(min(255,c+40) for c in color)
        self.text_color= text_color
        self.font      = font
        self.hovered   = False

    def draw(self, surface):
        col = self.hov_color if self.hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        t = self.font.render(self.text, True, self.text_color)
        surface.blit(t, t.get_rect(center=self.rect.center))

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def draw_panel(surface, rect, alpha=180):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    pygame.draw.rect(s, (255,255,255,60), (0,0,rect[2],rect[3]), 2, border_radius=10)
    surface.blit(s, (rect[0], rect[1]))

# ── Sprite classes ────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, car_idx=0):
        super().__init__()
        self.base_image = make_player_surface(car_idx)
        self.image      = self.base_image.copy()
        self.rect       = self.image.get_rect(center=(200, 520))
        self.shielded   = False
        self.is_slowed  = False
        self._shield_anim = 0

    def move(self, speed_mult=1.0):
        keys = pygame.key.get_pressed()
        spd  = 2 if self.is_slowed else int(10 * speed_mult)
        if self.rect.left > 40   and keys[K_LEFT]:  self.rect.x -= spd
        if self.rect.right < 360 and keys[K_RIGHT]: self.rect.x += spd

    def draw_shield(self, surface):
        if self.shielded:
            self._shield_anim = (self._shield_anim + 3) % 360
            r = 28 + int(3 * math.sin(math.radians(self._shield_anim)))
            pygame.draw.circle(surface, (*BLUE, 120),
                               self.rect.center, r, 3)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = make_enemy_surface()
        self.rect  = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.center = (random.choice(LANES),
                            random.randint(-200, -50))

    def move(self, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()
            return True
        return False

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, otype):
        super().__init__()
        self.type = otype
        if otype == "Oil":
            self.image = pygame.Surface((44, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (30, 30, 30, 160), (0,0,44,24))
            pygame.draw.ellipse(self.image, (80, 60, 120, 100), (4,4,36,16))
        else:
            self.image = pygame.Surface((60, 18), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (160, 80, 20), (0,0,60,18), border_radius=4)
            for x in range(0,60,15):
                pygame.draw.rect(self.image, (120,60,10),(x,0,12,18), border_radius=2)
        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.center = (random.choice(LANES), random.randint(-1200, -100))

    def move(self, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

class PowerUp(pygame.sprite.Sprite):
    TYPES = ["Nitro", "Shield", "Repair"]
    COLORS = {"Nitro": GOLD, "Shield": BLUE, "Repair": GREEN}
    ICONS  = {"Nitro": "N", "Shield": "S", "Repair": "R"}

    def __init__(self):
        super().__init__()
        self.type = random.choice(self.TYPES)
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect()
        self.spawn_time = pygame.time.get_ticks()
        self.rect.center = (random.choice(LANES), random.randint(-600, -50))

    def _draw(self):
        self.image.fill((0,0,0,0))
        col = self.COLORS[self.type]
        pygame.draw.rect(self.image, (*col, 220), (0,0,32,32), border_radius=8)
        pygame.draw.rect(self.image, WHITE, (0,0,32,32), 2, border_radius=8)
        f = pygame.font.SysFont("Impact", 22)
        t = f.render(self.ICONS[self.type], True, WHITE)
        self.image.blit(t, t.get_rect(center=(16,16)))

    def respawn(self):
        self.type = random.choice(self.TYPES)
        self._draw()
        self.rect.center = (random.choice(LANES), random.randint(-600,-50))
        self.spawn_time = pygame.time.get_ticks()

    def move(self, speed):
        self.rect.y += speed - 1
        if self.rect.top > SCREEN_HEIGHT or \
           pygame.time.get_ticks() - self.spawn_time > 7000:
            self.respawn()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.weight = 1
        self._surfaces = {
            1: make_coin_surface(22),
            3: make_coin_surface(32),
            5: make_coin_surface(42),
        }
        self.respawn()

    def respawn(self):
        r = random.random()
        self.weight = 5 if r > 0.95 else (3 if r > 0.80 else 1)
        self.image  = self._surfaces[self.weight]
        self.rect   = self.image.get_rect()
        self.rect.center = (random.randint(50, SCREEN_WIDTH-50),
                            random.randint(-400, -20))

    def move(self, speed):
        self.rect.y += speed - 1
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

# ── Score calculator ──────────────────────────────────────────────────────────
def calculate_score(enemies_passed, coins, distance_m, powerup_bonuses):
    """
    Combined score:
      - 10 pts per enemy passed
      - coin_score * 5
      - 1 pt per metre driven
      - 50 pts per power-up collected (bonuses counter)
    """
    return (enemies_passed * 10
            + coins * 5
            + int(distance_m)
            + powerup_bonuses * 50)

# ── Screens ───────────────────────────────────────────────────────────────────

# ── Username entry ────────────────────────────────────────────────────────────
def screen_username():
    name = ""
    active = True
    prompt = font_medium.render("Enter your name:", True, WHITE)
    cursor_visible = True
    cursor_timer   = 0

    while active:
        dt = clock.tick(FPS)
        cursor_timer += dt
        if cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        draw_gradient_bg(screen)
        title = font_title.render("TURBO", True, ACCENT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 140)))

        draw_panel(screen, (60, 220, 280, 120))
        screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH//2, 255)))

        display = name + ("|" if cursor_visible else " ")
        name_surf = font_large.render(display, True, GOLD)
        screen.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH//2, 300)))

        hint = font_tiny.render("Press ENTER to continue", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, 380)))

        pygame.display.flip()

# ── Main menu ─────────────────────────────────────────────────────────────────
def screen_main_menu(settings):
    cx = SCREEN_WIDTH // 2
    buttons = {
        "play":        Button((cx-100, 220, 200, 45), "PLAY",     color=(50,180,80)),
        "leaderboard": Button((cx-100, 278, 200, 45), "SCORES",  color=(180,120,30)),
        "settings":    Button((cx-100, 336, 200, 45), "SETTINGS", color=(60,100,200)),
        "quit":        Button((cx-100, 394, 200, 45), "QUIT",     color=(180,40,40)),
    }
    angle = 0
    while True:
        angle = (angle + 0.5) % 360
        mx, my = pygame.mouse.get_pos()
        for b in buttons.values(): b.update((mx, my))

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            for key, btn in buttons.items():
                if btn.is_clicked(event):
                    return key

        draw_gradient_bg(screen, (15,15,25), (35,35,55))

        # Animated road lines
        for i, x in enumerate(LANES):
            for y in range(int(angle*3) % 40, SCREEN_HEIGHT, 40):
                pygame.draw.rect(screen, (50,50,60), (x-1, y, 2, 20))

        # Title
        glow = font_title.render("TURBO", True, (255,60,60))
        screen.blit(glow, glow.get_rect(center=(SCREEN_WIDTH//2+2, 122)))
        title = font_title.render("TURBO", True, ACCENT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 120)))

        sub = font_small.render("STREET RACER", True, GOLD)
        screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 165)))

        draw_panel(screen, (50, 205, 300, 250))
        for b in buttons.values(): b.draw(screen)

        diff_text = font_tiny.render(f"Difficulty: {settings['difficulty']}", True, GRAY)
        screen.blit(diff_text, diff_text.get_rect(center=(SCREEN_WIDTH//2, 470)))

        pygame.display.flip()
        clock.tick(FPS)

# ── Settings screen ───────────────────────────────────────────────────────────
def screen_settings(settings):
    cx = SCREEN_WIDTH // 2
    back_btn  = Button((cx-80, 530, 160, 40), "BACK", color=(80,80,100))
    sound_btn = Button((cx-80, 180, 160, 40), "", color=(60,100,60))
    diff_btn  = Button((cx-80, 240, 160, 40), "", color=(60,60,140), font=font_small)

    car_left  = Button((60,  310, 40, 40), "<", color=(60,60,80))
    car_right = Button((300, 310, 40, 40), ">", color=(60,60,80))

    def refresh_labels():
        sound_btn.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        sound_btn.color = (50,150,50) if settings['sound'] else (150,50,50)
        diff_keys = list(DIFFICULTIES.keys())
        diff_btn.text  = f"Difficulty: {settings['difficulty']}"

    refresh_labels()

    while True:
        mx, my = pygame.mouse.get_pos()
        for b in [back_btn, sound_btn, diff_btn, car_left, car_right]:
            b.update((mx, my))

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if back_btn.is_clicked(event):
                save_settings(settings)
                return
            if sound_btn.is_clicked(event):
                settings["sound"] = not settings["sound"]
                refresh_labels()
            if diff_btn.is_clicked(event):
                diffs = list(DIFFICULTIES.keys())
                idx = diffs.index(settings["difficulty"])
                settings["difficulty"] = diffs[(idx+1) % len(diffs)]
                refresh_labels()
            if car_left.is_clicked(event):
                settings["car_color"] = (settings["car_color"]-1) % len(CAR_COLORS)
            if car_right.is_clicked(event):
                settings["car_color"] = (settings["car_color"]+1) % len(CAR_COLORS)

        draw_gradient_bg(screen, (15,15,25), (35,35,55))
        title = font_large.render("SETTINGS", True, WHITE)
        screen.blit(title, title.get_rect(center=(cx, 60)))

        draw_panel(screen, (30, 155, 340, 420))

        sound_btn.draw(screen)
        diff_btn.draw(screen)

        # Car preview
        car_label = font_small.render("Car Color:", True, WHITE)
        screen.blit(car_label, car_label.get_rect(center=(cx, 295)))
        car_surf = make_player_surface(settings["car_color"])
        car_surf = pygame.transform.scale(car_surf, (54, 90))
        screen.blit(car_surf, car_surf.get_rect(center=(cx, 355)))
        car_name = font_small.render(CAR_COLORS[settings["car_color"]][0], True, GOLD)
        screen.blit(car_name, car_name.get_rect(center=(cx, 410)))

        car_left.draw(screen)
        car_right.draw(screen)

        # Difficulty description
        diff = settings["difficulty"]
        desc = {"Easy":"Relaxed pace, great for beginners",
                "Normal":"Classic experience",
                "Hard":"For the fearless driver"}
        desc_surf = font_tiny.render(desc[diff], True, GRAY)
        screen.blit(desc_surf, desc_surf.get_rect(center=(cx, 450)))

        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

# ── Leaderboard screen ────────────────────────────────────────────────────────
def screen_leaderboard():
    back_btn = Button((SCREEN_WIDTH//2-80, 550, 160, 40), "BACK", color=(80,80,100))
    lb = load_leaderboard()

    while True:
        mx, my = pygame.mouse.get_pos()
        back_btn.update((mx, my))

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if back_btn.is_clicked(event): return

        draw_gradient_bg(screen, (10,15,20), (20,30,40))
        title = font_large.render("TOP SCORES", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 50)))

        draw_panel(screen, (20, 80, 360, 450))

        headers = ["№", "Name", "Score", "Dist", "Coins"]
        hx      = [35, 80, 185, 270, 340]
        for i, (h, x) in enumerate(zip(headers, hx)):
            hs = font_tiny.render(h, True, GOLD)
            screen.blit(hs, (x, 90))

        pygame.draw.line(screen, GOLD, (25, 108), (375, 108), 1)

        for rank, entry in enumerate(lb, 1):
            y   = 115 + (rank-1)*38
            row_bg = (255,215,0,30) if rank == 1 else (255,255,255,10)
            s = pygame.Surface((355,34), pygame.SRCALPHA)
            s.fill(row_bg)
            screen.blit(s, (22, y))

            medal = {1:"1",2:"2",3:"3"}.get(rank, str(rank))
            cols  = [medal, entry.get("name","?")[:8],
                     str(entry.get("score",0)),
                     f"{entry.get('distance',0)}m",
                     str(entry.get("coins",0))]
            colors= [GOLD if rank<=3 else WHITE]*5

            for col_txt, x, col in zip(cols, hx, colors):
                ts = font_tiny.render(col_txt, True, col)
                screen.blit(ts, (x, y+9))

        if not lb:
            empty = font_small.render("No scores yet!", True, GRAY)
            screen.blit(empty, empty.get_rect(center=(SCREEN_WIDTH//2, 280)))

        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

# ── Game Over screen ──────────────────────────────────────────────────────────
def screen_game_over(score, distance, coins, enemies_passed, username):
    add_to_leaderboard(username, score, distance, coins)
    cx = SCREEN_WIDTH // 2

    retry_btn = Button((cx-110, 430, 200, 45), "RETRY",     color=(50,150,50))
    menu_btn  = Button((cx-110, 488, 200, 45), "MAIN MENU", color=(60,80,150))

    shake = 20
    while True:
        mx, my = pygame.mouse.get_pos()
        retry_btn.update((mx, my))
        menu_btn.update((mx, my))

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if retry_btn.is_clicked(event): return "retry"
            if menu_btn.is_clicked(event):  return "menu"

        draw_gradient_bg(screen, (40,10,10), (15,5,5))

        if shake > 0:
            ox, oy = random.randint(-shake,shake)//4, random.randint(-shake,shake)//4
            shake -= 1
        else:
            ox, oy = 0, 0

        go_text = font_title.render("GAME OVER", True, ACCENT)
        screen.blit(go_text, go_text.get_rect(center=(cx+ox, 110+oy)))

        draw_panel(screen, (40, 170, 320, 240))

        stats = [
            ("SCORE",    str(score),           GOLD),
            ("DISTANCE", f"{distance} m",      WHITE),
            ("COINS",    str(coins),            GOLD),
            ("ENEMIES",  str(enemies_passed),   WHITE),
        ]
        for i, (label, val, col) in enumerate(stats):
            y = 185 + i*52
            ls = font_tiny.render(label, True, GRAY)
            vs = font_medium.render(val,   True, col)
            screen.blit(ls, (60, y))
            screen.blit(vs, (60, y+16))

        retry_btn.draw(screen)
        menu_btn.draw(screen)

        player_surf = font_tiny.render(f"Player: {username}", True, GRAY)
        screen.blit(player_surf, player_surf.get_rect(center=(cx, 555)))

        pygame.display.flip()
        clock.tick(FPS)

# ── Main Game ─────────────────────────────────────────────────────────────────
def run_game(username, settings):
    diff_cfg  = DIFFICULTIES[settings["difficulty"]]
    SPEED     = diff_cfg["base_speed"]
    sound_on  = settings["sound"]

    bg = make_background()

    # Sprites
    P1 = Player(settings["car_color"])
    n_enemies = diff_cfg["enemy_count"]
    n_obs     = diff_cfg["obs_count"]

    enemies   = pygame.sprite.Group(*[Enemy()   for _ in range(n_enemies)])
    obstacles = pygame.sprite.Group(*[Obstacle("Oil") for _ in range(n_obs//2+1)],
                                    *[Obstacle("Barrier") for _ in range(max(1,n_obs//2))])
    powerups  = pygame.sprite.Group(PowerUp())
    coins_grp = pygame.sprite.Group(*[Coin() for _ in range(3)])

    all_sprites = pygame.sprite.Group(P1, enemies, obstacles, powerups, coins_grp)

    # Score state
    SCORE           = 0   # enemies passed
    COIN_SCORE      = 0
    POWERUP_BONUSES = 0
    ACTIVE_POWERUP  = None
    POWERUP_TIMER   = 0
    distance_px     = 0   # pixels scrolled
    PIXELS_PER_M    = 10

    INC_SPEED = pygame.USEREVENT + 1
    pygame.time.set_timer(INC_SPEED, 1000)

    # Try to load crash sound
    crash_sound = None
    if sound_on:
        for path in [r"PP2\TSIS3\assets\sounds\crash.wav",
                     "assets/sounds/crash.wav", "crash.wav"]:
            if os.path.exists(path):
                try: crash_sound = pygame.mixer.Sound(path)
                except Exception: pass
                break

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == K_ESCAPE: return "menu", 0, 0, 0, 0
            if event.type == INC_SPEED:
                SPEED += diff_cfg["inc"]

        # ── Move ────────────────────────────────────────────────────────────
        nitro = (ACTIVE_POWERUP == "Nitro")
        P1.move(speed_mult=1.5 if nitro else 1.0)

        for e in enemies:
            # Count passed enemies
            if e.move(SPEED):
                SCORE += 1
        for o in obstacles: o.move(SPEED)
        for p in powerups:  p.move(SPEED)
        for c in coins_grp: c.move(SPEED)

        distance_px += SPEED

        # ── Draw ────────────────────────────────────────────────────────────
        screen.blit(bg, (0, 0))
        for s in [*enemies, *obstacles, *powerups, *coins_grp]:
            screen.blit(s.image, s.rect)
        screen.blit(P1.image, P1.rect)
        P1.draw_shield(screen)

        # ── Collisions ──────────────────────────────────────────────────────
        # Coins
        for coin in pygame.sprite.spritecollide(P1, coins_grp, False):
            old = COIN_SCORE
            COIN_SCORE += coin.weight
            coin.respawn()
            if (COIN_SCORE // N_COINS_THRESHOLD) > (old // N_COINS_THRESHOLD):
                SPEED += 1.0

        # Power-ups
        pu = pygame.sprite.spritecollideany(P1, powerups)
        if pu:
            ACTIVE_POWERUP   = pu.type
            POWERUP_BONUSES += 1
            if ACTIVE_POWERUP == "Shield":
                P1.shielded    = True
                POWERUP_TIMER  = pygame.time.get_ticks() + 5000
            elif ACTIVE_POWERUP == "Nitro":
                POWERUP_TIMER  = pygame.time.get_ticks() + 3000
            elif ACTIVE_POWERUP == "Repair":
                for o in obstacles: o.respawn()
            pu.respawn()

        # Power-up expiry
        P1.is_slowed = False
        if ACTIVE_POWERUP and ACTIVE_POWERUP != "Repair":
            if pygame.time.get_ticks() > POWERUP_TIMER:
                ACTIVE_POWERUP = None
                P1.shielded    = False

        # Obstacles
        obs_hit = pygame.sprite.spritecollideany(P1, obstacles)
        if obs_hit:
            if obs_hit.type == "Oil":
                P1.is_slowed = True
            elif obs_hit.type == "Barrier":
                if P1.shielded:
                    P1.shielded = False; ACTIVE_POWERUP = None; obs_hit.respawn()
                else:
                    # Game over
                    dist_m = int(distance_px / PIXELS_PER_M)
                    sc     = calculate_score(SCORE, COIN_SCORE, dist_m, POWERUP_BONUSES)
                    return "gameover", sc, dist_m, COIN_SCORE, SCORE

        # Enemies
        if pygame.sprite.spritecollideany(P1, enemies):
            if P1.shielded:
                P1.shielded = False; ACTIVE_POWERUP = None
                for e in enemies: e.respawn()
            else:
                if crash_sound: crash_sound.play()
                dist_m = int(distance_px / PIXELS_PER_M)
                sc     = calculate_score(SCORE, COIN_SCORE, dist_m, POWERUP_BONUSES)
                return "gameover", sc, dist_m, COIN_SCORE, SCORE

        
        # ── HUD ─────────────────────────────────────────────────────────────
        dist_m = int(distance_px / PIXELS_PER_M)
        sc     = calculate_score(SCORE, COIN_SCORE, dist_m, POWERUP_BONUSES)

        draw_panel(screen, (0, 0, SCREEN_WIDTH, 55), alpha=140)

        score_s  = font_small.render(f"Score: {sc}", True, WHITE)
        coins_s  = font_small.render(f"Coins: {COIN_SCORE}", True, GOLD)
        dist_s   = font_small.render(f"{dist_m}m", True, (180,220,255))
        spd_s    = font_tiny.render(f"SPD {SPEED:.1f}", True, GRAY)

        screen.blit(score_s,  (8,  8))
        screen.blit(coins_s,  (8,  28))
        screen.blit(dist_s,   (SCREEN_WIDTH//2 - dist_s.get_width()//2, 18))
        screen.blit(spd_s,    (SCREEN_WIDTH - 60, 35))

        # Power-up banner
        if ACTIVE_POWERUP:
            tl = max(0, math.ceil((POWERUP_TIMER - pygame.time.get_ticks())/1000))
            col = {"Nitro": GOLD, "Shield": BLUE, "Repair": GREEN}[ACTIVE_POWERUP]
            if ACTIVE_POWERUP == "Repair":
                ptxt = font_small.render("REPAIR ACTIVE", True, col)
            else:
                ptxt = font_small.render(f"{ACTIVE_POWERUP.upper()}: {tl}s", True, col)
            screen.blit(ptxt, ptxt.get_rect(topright=(SCREEN_WIDTH-8, 8)))

        pygame.display.flip()

    dist_m = int(distance_px / PIXELS_PER_M)
    sc = calculate_score(SCORE, COIN_SCORE, dist_m, POWERUP_BONUSES)
    return "gameover", sc, dist_m, COIN_SCORE, SCORE


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    settings = load_settings()
    username = screen_username()

    while True:
        action = screen_main_menu(settings)

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            screen_leaderboard()

        elif action == "settings":
            screen_settings(settings)

        elif action == "play":
            while True:
                result, score, dist, coins, enemies = run_game(username, settings)

                if result == "menu":
                    break

                # Game over screen
                next_action = screen_game_over(score, dist, coins, enemies, username)
                if next_action == "menu":
                    break
                elif next_action == "retry":
                    continue   # loop again → run_game

if __name__ == "__main__":
    main()