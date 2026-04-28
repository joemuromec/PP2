# config.py — shared constants

# ── Constants ──────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 480
CELL_SIZE     = 20
CELL_WIDTH    = SCREEN_WIDTH  // CELL_SIZE
CELL_HEIGHT   = SCREEN_HEIGHT // CELL_SIZE
 
FPS_BASE = 10        # starting game speed (ticks/sec)
 
# ── Colours (defaults; overridden by settings) ──────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0  )
GRAY       = (40,  40,  40 )
DARK_GRAY  = (20,  20,  20 )
RED        = (200, 0,   0  )
GOLD       = (255, 215, 0  )
GREEN      = (0,   200, 0  )
DARK_GREEN = (0,   120, 0  )
BLUE       = (50,  120, 255)
PURPLE     = (160, 0,   220)
ORANGE     = (255, 140, 0  )
TEAL       = (0,   200, 180)
POISON_COL = (120, 0,   40 )   # dark-red/maroon
 
# ── Power-up palette ─────────────────────────────────────────────────────────
PU_COLORS = {
    "speed":  ORANGE,
    "slow":   TEAL,
    "shield": BLUE,
}
 
# ── Timing ───────────────────────────────────────────────────────────────────
GOLD_FOOD_TIMER_MS = 5_000
POISON_TIMER_MS    = 6_000
POWERUP_TIMER_MS   = 8_000    # disappears from field
POWERUP_EFFECT_MS  = 5_000    # effect duration after collection
 
# ── Level rules ──────────────────────────────────────────────────────────────
SCORE_PER_LEVEL      = 5      # score points needed to advance
OBSTACLE_START_LEVEL = 3      # obstacles appear from this level
OBSTACLES_PER_LEVEL  = 3      # extra blocks added each new level ≥ 3
