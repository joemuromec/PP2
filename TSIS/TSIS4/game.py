# game.py — SnakeGame core logic
#
# Features implemented
#   3.2 Poison food     — dark-red item; -2 segments; len≤1 → game over
#   3.3 Power-ups       — speed boost / slow motion / shield; 8 s field TTL
#   3.4 Obstacles       — static wall blocks from level 3 onward
#   3.5 Settings        — snake colour, grid toggle, sound toggle

import pygame
import random
import math
from config import *

class SnakeGame:
    # ── Construction / reset ──────────────────────────────────────────────────
    def __init__(self, username: str, settings: dict, personal_best: int = 0):
        self.username     = username
        self.settings     = settings
        self.personal_best = personal_best

        self.screen = pygame.display.get_surface()
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_sm = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_md = pygame.font.SysFont("Consolas", 26, bold=True)
        self.font_lg = pygame.font.SysFont("Impact",   72)

        self.reset()

    def reset(self):
        """Full game-state reset (called at start and after game-over → retry)."""
        sx = random.randint(5, CELL_WIDTH  - 6)
        sy = random.randint(5, CELL_HEIGHT - 6)
        self.snake     = [pygame.Vector2(sx, sy),
                          pygame.Vector2(sx-1, sy),
                          pygame.Vector2(sx-2, sy)]
        self.direction = pygame.Vector2(1, 0)
        self.next_dir  = pygame.Vector2(1, 0)  # buffered input

        self.score       = 0
        self.level       = 1
        self.current_fps = FPS_BASE

        self.obstacles: list[pygame.Vector2] = []

        # Food / power-up state
        self.food         = None
        self.poison       = None
        self.powerup_item = None       # item on the field

        # Active effect state
        self.active_effect      = None   # "speed" | "slow" | "shield"
        self.effect_end_ms      = 0
        self.shield_triggered   = False

        # Spawn
        self._spawn_food()
        self._maybe_spawn_poison()
        self._maybe_spawn_powerup()

    # ── Occupied cells helper ─────────────────────────────────────────────────
    def _occupied(self) -> set:
        occ = set(tuple(v) for v in self.snake)
        occ.update(tuple(v) for v in self.obstacles)
        if self.food:         occ.add(tuple(self.food["pos"]))
        if self.poison:       occ.add(tuple(self.poison["pos"]))
        if self.powerup_item: occ.add(tuple(self.powerup_item["pos"]))
        return occ

    def _free_cell(self) -> pygame.Vector2:
        occ = self._occupied()
        while True:
            p = pygame.Vector2(random.randint(0, CELL_WIDTH-1),
                               random.randint(0, CELL_HEIGHT-1))
            if tuple(p) not in occ:
                return p

    # ── Spawners ──────────────────────────────────────────────────────────────
    def _spawn_food(self):
        pos = self._free_cell()
        now = pygame.time.get_ticks()
        if random.random() < 0.2:
            self.food = {"pos": pos, "color": GOLD, "weight": 3,
                         "ttl": GOLD_FOOD_TIMER_MS, "born": now, "special": True}
        else:
            self.food = {"pos": pos, "color": RED,  "weight": 1,
                         "ttl": None, "born": now, "special": False}

    def _maybe_spawn_poison(self):
        """30 % chance to have a poison item on the field."""
        if self.poison is None and random.random() < 0.30:
            self.poison = {"pos": self._free_cell(),
                           "born": pygame.time.get_ticks(),
                           "ttl":  POISON_TIMER_MS}

    def _maybe_spawn_powerup(self):
        """~25 % chance to have a power-up on the field (only one at a time)."""
        if self.powerup_item is None and random.random() < 0.25:
            kind = random.choice(["speed", "slow", "shield"])
            self.powerup_item = {"pos":  self._free_cell(),
                                 "kind": kind,
                                 "born": pygame.time.get_ticks(),
                                 "ttl":  POWERUP_TIMER_MS}

    def _place_obstacles(self):
        """Randomly place wall blocks, ensuring the snake is not trapped."""
        if self.level < OBSTACLE_START_LEVEL:
            return
        count = (self.level - OBSTACLE_START_LEVEL + 1) * OBSTACLES_PER_LEVEL
        head  = self.snake[0]
        occ   = set(tuple(v) for v in self.snake)
        # Keep a safe zone around head
        safe = {(head.x + dx, head.y + dy)
                for dx in range(-3, 4) for dy in range(-3, 4)}
        placed = 0
        attempts = 0
        while placed < count and attempts < 2000:
            attempts += 1
            p = pygame.Vector2(random.randint(1, CELL_WIDTH-2),
                               random.randint(1, CELL_HEIGHT-2))
            t = tuple(p)
            if t in occ or t in safe:
                continue
            self.obstacles.append(p)
            occ.add(t)
            placed += 1

    # ── Level-up ──────────────────────────────────────────────────────────────
    def _check_level_up(self):
        new_level = self.score // SCORE_PER_LEVEL + 1
        if new_level > self.level:
            self.level       = new_level
            self.current_fps = FPS_BASE + (self.level - 1) * 2
            # Clear old obstacles and re-place
            self.obstacles = []
            self._place_obstacles()

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_input(self, event):
        """Call from main loop on KEYDOWN events. Returns 'quit' or None."""
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            d = self.next_dir
            if event.key in (pygame.K_UP,    pygame.K_w) and d.y != 1:
                self.next_dir = pygame.Vector2(0, -1)
            elif event.key in (pygame.K_DOWN,  pygame.K_s) and d.y != -1:
                self.next_dir = pygame.Vector2(0,  1)
            elif event.key in (pygame.K_LEFT,  pygame.K_a) and d.x != 1:
                self.next_dir = pygame.Vector2(-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and d.x != -1:
                self.next_dir = pygame.Vector2(1,  0)
        return None

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self) -> str | None:
        """
        Advance one game tick.
        Returns:
          'gameover' — collision / poison death
          None       — still running
        """
        now = pygame.time.get_ticks()

        # Expire active power-up effect
        if self.active_effect and now > self.effect_end_ms:
            self._clear_effect()

        # Apply buffered direction
        self.direction = self.next_dir

        # Expire field items
        if self.food and self.food["ttl"] and \
                now - self.food["born"] > self.food["ttl"]:
            self._spawn_food()

        if self.poison and now - self.poison["born"] > self.poison["ttl"]:
            self.poison = None
            self._maybe_spawn_poison()

        if self.powerup_item and \
                now - self.powerup_item["born"] > self.powerup_item["ttl"]:
            self.powerup_item = None
            self._maybe_spawn_powerup()

        new_head = self.snake[0] + self.direction

        # ── Collision detection ───────────────────────────────────────────
        hit_wall = not (0 <= new_head.x < CELL_WIDTH and
                        0 <= new_head.y < CELL_HEIGHT)
        hit_self = new_head in self.snake
        hit_obs  = new_head in self.obstacles

        if hit_wall or hit_self or hit_obs:
            if self.active_effect == "shield" and not self.shield_triggered:
                # Shield absorbs ONE collision
                self.shield_triggered = True
                self._clear_effect()
                pygame.time.delay(1000)
                # Nudge snake back — don't move this tick
                return None
            return "gameover"

        self.snake.insert(0, new_head)

        ate_something = False

        # ── Eat normal / gold food ────────────────────────────────────────
        if new_head == self.food["pos"]:
            self.score += self.food["weight"]
            self._check_level_up()
            self._spawn_food()
            self._maybe_spawn_poison()
            self._maybe_spawn_powerup()
            ate_something = True

        # ── Eat poison ───────────────────────────────────────────────────
        elif self.poison and new_head == self.poison["pos"]:
            self.poison = None
            self._maybe_spawn_poison()
            ate_something = False
            # Shorten snake by 2
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            if len(self.snake) <= 1:
                return "gameover"

        # ── Collect power-up ─────────────────────────────────────────────
        elif self.powerup_item and new_head == self.powerup_item["pos"]:
            self._apply_effect(self.powerup_item["kind"])
            self.powerup_item = None
            self._maybe_spawn_powerup()
            ate_something = True

        if not ate_something:
            self.snake.pop()

        return None

    # ── Power-up effect helpers ───────────────────────────────────────────────
    def _apply_effect(self, kind: str):
        self.active_effect = kind
        self.effect_end_ms = pygame.time.get_ticks() + POWERUP_EFFECT_MS
        self.shield_triggered = False
        if kind == "speed":
            self.current_fps = FPS_BASE + (self.level - 1) * 2 + 5
        elif kind == "slow":
            self.current_fps = max(3, FPS_BASE + (self.level - 1) * 2 - 4)

    def _clear_effect(self):
        # Restore base speed for level
        self.current_fps = FPS_BASE + (self.level - 1) * 2
        self.active_effect = None

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        now = pygame.time.get_ticks()
        scr = self.screen

        scr.fill(BLACK)

        # Grid
        if self.settings.get("grid", True):
            for x in range(0, SCREEN_WIDTH,  CELL_SIZE):
                pygame.draw.line(scr, GRAY, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(scr, GRAY, (0, y), (SCREEN_WIDTH, y))

        # Obstacles
        for ob in self.obstacles:
            r = pygame.Rect(ob.x*CELL_SIZE, ob.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(scr, (120, 80, 40), r)
            pygame.draw.rect(scr, (80,  50, 20), r, 2)

        # Food
        if self.food:
            fp  = self.food["pos"]
            fr  = pygame.Rect(fp.x*CELL_SIZE, fp.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(scr, self.food["color"], fr)
            pygame.draw.rect(scr, WHITE, fr, 1)
            if self.food["special"]:
                elapsed = now - self.food["born"]
                frac    = max(0, 1 - elapsed / self.food["ttl"])
                bar_w   = int(frac * CELL_SIZE)
                pygame.draw.rect(scr, WHITE,
                                 (fp.x*CELL_SIZE, fp.y*CELL_SIZE - 4, bar_w, 3))

        # Poison food
        if self.poison:
            pp = self.poison["pos"]
            pr = pygame.Rect(pp.x*CELL_SIZE, pp.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(scr, POISON_COL, pr)
            pygame.draw.rect(scr, (200, 50, 100), pr, 1)
            # Skull indicator (tiny X)
            cx2, cy2 = pr.centerx, pr.centery
            pygame.draw.line(scr, WHITE, (cx2-4, cy2-4), (cx2+4, cy2+4), 2)
            pygame.draw.line(scr, WHITE, (cx2+4, cy2-4), (cx2-4, cy2+4), 2)
            # Timer bar
            elapsed  = now - self.poison["born"]
            frac     = max(0, 1 - elapsed / self.poison["ttl"])
            pygame.draw.rect(scr, POISON_COL,
                             (pp.x*CELL_SIZE, pp.y*CELL_SIZE - 4,
                              int(frac * CELL_SIZE), 3))

        # Power-up item
        if self.powerup_item:
            pu  = self.powerup_item
            pos = pu["pos"]
            pr  = pygame.Rect(pos.x*CELL_SIZE, pos.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            col = PU_COLORS[pu["kind"]]
            # Pulsing glow
            pulse = int(4 * abs(math.sin(now / 300)))
            glow_r = pr.inflate(pulse*2, pulse*2)
            pygame.draw.rect(scr, (*col, 80), glow_r, border_radius=4)
            pygame.draw.rect(scr, col, pr, border_radius=3)
            # Letter label
            lbl = {"speed": "N", "slow": "S", "shield": "⌂"}[pu["kind"]]
            ls  = self.font_sm.render(lbl, True, WHITE)
            scr.blit(ls, ls.get_rect(center=pr.center))
            # Timer bar
            elapsed = now - pu["born"]
            frac    = max(0, 1 - elapsed / pu["ttl"])
            pygame.draw.rect(scr, col,
                             (pos.x*CELL_SIZE, pos.y*CELL_SIZE - 4,
                              int(frac * CELL_SIZE), 3))

        # Snake
        snake_col = tuple(self.settings.get("snake_color", list(GREEN)))
        dark_col  = tuple(max(0, c - 80) for c in snake_col)
        for i, seg in enumerate(self.snake):
            r = pygame.Rect(seg.x*CELL_SIZE, seg.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            c = dark_col if i == 0 else snake_col
            pygame.draw.rect(scr, c, r, border_radius=3)
            pygame.draw.rect(scr, WHITE, r, 1, border_radius=3)

            # Eyes on head
            if i == 0:
                ex1 = r.x + 5 + int(self.direction.x * 5)
                ey1 = r.y + 5 + int(self.direction.y * 5)
                ex2 = r.x + 13 + int(self.direction.x * 5)
                ey2 = r.y + 5  + int(self.direction.y * 5)
                pygame.draw.circle(scr, WHITE, (ex1, ey1), 3)
                pygame.draw.circle(scr, WHITE, (ex2, ey2), 3)
                pygame.draw.circle(scr, BLACK, (ex1, ey1), 1)
                pygame.draw.circle(scr, BLACK, (ex2, ey2), 1)

        # Shield visual
        if self.active_effect == "shield":
            pulse = int(3 * abs(math.sin(now / 200)))
            hr    = pygame.Rect(self.snake[0].x*CELL_SIZE - pulse,
                                self.snake[0].y*CELL_SIZE - pulse,
                                CELL_SIZE + pulse*2, CELL_SIZE + pulse*2)
            s = pygame.Surface((hr.w, hr.h), pygame.SRCALPHA)
            pygame.draw.rect(s, (*BLUE, 100), s.get_rect(), border_radius=5)
            scr.blit(s, hr.topleft)

        # ── HUD ──────────────────────────────────────────────────────────────
        self._draw_hud(now)

    def _draw_hud(self, now: int):
        scr = self.screen
        # Top bar background
        bar = pygame.Surface((SCREEN_WIDTH, 38), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 160))
        scr.blit(bar, (0, 0))

        score_s = self.font_sm.render(f"Score: {self.score}", True, WHITE)
        level_s = self.font_sm.render(f"Level: {self.level}", True, GREEN)
        best_s  = self.font_sm.render(f"PB: {self.personal_best}",  True, GOLD)
        user_s  = self.font_sm.render(self.username, True, (180, 180, 255))

        scr.blit(score_s, (8,  6))
        scr.blit(level_s, (8,  22))
        scr.blit(best_s,  (SCREEN_WIDTH//2 - 40, 6))
        scr.blit(user_s,  (SCREEN_WIDTH - user_s.get_width() - 8, 6))

        # Active power-up status
        if self.active_effect:
            remaining = max(0, self.effect_end_ms - now)
            col  = PU_COLORS.get(self.active_effect, WHITE)
            lbl  = {"speed": "NITRO", "slow": "SLOW", "shield": "SHIELD"}
            txt  = self.font_sm.render(
                f"{lbl[self.active_effect]} {remaining//1000}s", True, col)
            scr.blit(txt, txt.get_rect(topright=(SCREEN_WIDTH - 8, 22)))

    # ── Game-over flash ───────────────────────────────────────────────────────
    def show_crash(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((180, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_lg.render("CRASHED!", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        pygame.display.flip()
        pygame.time.delay(1200)