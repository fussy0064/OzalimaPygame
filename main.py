"""
MoneyCollector — Pygame arcade game
Character: Ozalima
Goal: Collect falling notes (+10 score). Avoid coins (lose 1 life, -5 score).
Win: Collect 75 notes. Lose: Run out of 3 lives.
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pygame

# ── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent   # Folder where this script lives

SCREEN_WIDTH  = 960
SCREEN_HEIGHT = 540
FPS           = 60
GROUND_Y      = 442   # Y where the ground starts (city silhouette sits here)
PLAYER_Y      = 400   # Player's fixed vertical position
PLAYER_SPEED  = 390.0 # Horizontal pixels per second

WHITE  = (245, 247, 255)
RED    = (230, 86, 94)
GREEN  = (76, 214, 135)
YELLOW = (255, 219, 102)


# ── Utility functions ─────────────────────────────────────────────────────────
def clamp(value: float, minimum: float, maximum: float) -> float:
    """Keep a number inside [minimum, maximum]."""
    return max(minimum, min(maximum, value))


def lerp_color(a: tuple[int,int,int], b: tuple[int,int,int], t: float) -> tuple[int,int,int]:
    """Blend two RGB colors. t=0 → a, t=1 → b."""
    t = clamp(t, 0.0, 1.0)
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def try_load_image(paths: list[str], fallback: pygame.Surface, size: tuple[int,int]) -> pygame.Surface:
    """Try to load a PNG/JPEG from disk. Return fallback surface if none found."""
    for path in paths:
        full = BASE_DIR / path
        if full.exists():
            try:
                img = pygame.image.load(str(full)).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            except pygame.error:
                pass
    return pygame.transform.smoothscale(fallback, size)


def build_background_fallback(size: tuple[int, int]) -> pygame.Surface:
    """Build a simple sky-and-city fallback if the background image is missing."""
    surface = pygame.Surface(size)
    for y in range(size[1]):
        color = lerp_color((11, 15, 28), (28, 24, 44), y / max(1, size[1] - 1))
        pygame.draw.line(surface, color, (0, y), (size[0], y))
    return surface


# ── Fallback sprite builders (used when asset files are missing) ──────────────
def build_coin_surface(size: tuple[int,int]) -> pygame.Surface:
    """Draw a simple gold coin programmatically."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    r = min(w, h) // 2 - 2
    pygame.draw.circle(surf, (255, 228, 126), (cx, cy), r)            # gold body
    pygame.draw.circle(surf, (255, 248, 215), (cx - 6, cy - 7), r//2) # highlight
    pygame.draw.circle(surf, (195, 132, 16),  (cx, cy), r, 3)         # dark border
    pygame.draw.circle(surf, (255, 201, 60),  (cx, cy), r - 4, 2)     # inner ring
    pygame.draw.line(surf, (255, 245, 179), (cx-10, cy-12), (cx-2,  cy-20), 3)
    pygame.draw.line(surf, (255, 245, 179), (cx+5,  cy-9),  (cx+14, cy-17), 2)
    return surf


def build_note_surface(size: tuple[int,int]) -> pygame.Surface:
    """Draw a simple banknote programmatically."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    body  = pygame.Rect(4, 6, w - 8, h - 12)
    inner = pygame.Rect(12, 15, w - 24, h - 30)

    pygame.draw.rect(surf, (54, 190, 131), body,  border_radius=8)         # green body
    pygame.draw.rect(surf, (22, 110, 74),  body,  width=3, border_radius=8)# border
    pygame.draw.polygon(surf, (220, 247, 231), [(w-17,8),(w-6,18),(w-17,18)]) # corner fold
    pygame.draw.rect(surf, (232, 255, 245), inner, width=2, border_radius=5)
    pygame.draw.circle(surf, (232, 255, 245), (w//2, h//2), min(w,h)//5, 2)
    pygame.draw.line(surf, (232, 255, 245), (inner.left+4, inner.centery), (inner.right-4, inner.centery), 2)
    return surf


def build_woman_surface(size: tuple[int,int]) -> pygame.Surface:
    """Draw the Ozalima character programmatically."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    cx = w // 2

    # Shadow under feet
    pygame.draw.ellipse(surf, (0,0,0,55), pygame.Rect(cx-30, h-14, 60, 10))

    # Head & hair
    pygame.draw.circle(surf, (246, 211, 183), (cx, 29), 18)              # face
    pygame.draw.circle(surf, (79, 47, 27),    (cx, 26), 22)              # hair top
    pygame.draw.polygon(surf, (79, 47, 27), [(cx-24,24),(cx-34,54),(cx-14,62),(cx-10,28)]) # left hair
    pygame.draw.polygon(surf, (79, 47, 27), [(cx+24,24),(cx+34,54),(cx+14,62),(cx+10,28)]) # right hair
    pygame.draw.circle(surf, (246, 211, 183), (cx-2, 28), 17)            # face (over hair)
    pygame.draw.line(surf, (64, 41, 27), (cx-8, 28), (cx+8, 28), 2)     # mouth

    # Dress, arms, legs, shoes
    pygame.draw.polygon(surf, (175, 109, 255), [(cx,48),(cx-27,94),(cx+27,94)])         # dress
    pygame.draw.polygon(surf, (231, 211, 255), [(cx,50),(cx-12,63),(cx+12,63)])         # dress shine
    pygame.draw.line(surf, (246, 211, 183), (cx-18,58), (cx-34,79), 6)  # left arm
    pygame.draw.line(surf, (246, 211, 183), (cx+18,58), (cx+34,79), 6)  # right arm
    pygame.draw.line(surf, (175, 109, 255), (cx-11,90), (cx-17,117), 7) # left leg
    pygame.draw.line(surf, (175, 109, 255), (cx+11,90), (cx+17,117), 7) # right leg
    pygame.draw.circle(surf, (48, 58, 76), (cx-17, 117), 5)             # left shoe
    pygame.draw.circle(surf, (48, 58, 76), (cx+17, 117), 5)             # right shoe
    pygame.draw.polygon(surf, (42, 30, 56), [(cx-27,94),(cx+27,94),(cx,125)], 2) # skirt hem
    return surf


# ── Background drawing ────────────────────────────────────────────────────────
"""def draw_background(surface: pygame.Surface, t: float) -> None:
    
    Draw the animated night-city background:
      1. Gradient sky
      2. Soft glowing orbs (wobble over time)
      3. City silhouette with lit windows
      4. Ground lane
    t = elapsed game time (drives animations).
    
    # 1. Vertical gradient sky
    for y in range(SCREEN_HEIGHT):
        if y < SCREEN_HEIGHT * 0.55:
            color = lerp_color((11,15,28), (22,51,77), y / (SCREEN_HEIGHT * 0.55))
        else:
            color = lerp_color((22,51,77), (28,24,44), (y - SCREEN_HEIGHT*0.55) / (SCREEN_HEIGHT*0.45))
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

    # 2. Glowing orbs — each entry: (base_x, base_y, radius, RGBA, wobble_speed)
    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i, (bx, by, r, col, spd) in enumerate([
        (110, 84,  70, (82,  124, 255, 45), 0.8),
        (260, 130, 86, (255, 190, 70,  34), 1.2),
        (760, 90,  96, (135, 93,  255, 36), 0.9),
        (870, 168, 72, (82,  214, 165, 24), 1.4),
    ]):
        wx = bx + math.sin(t * spd + i) * 18
        wy = by + math.cos(t * spd * 0.7 + i * 1.3) * 12
        pygame.draw.circle(glow, col, (int(wx), int(wy)), r)
    surface.blit(glow, (0, 0))

    # 3. City silhouette — buildings + windows
    pygame.draw.rect(surface, (10,13,22), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    x = -10
    for i, bw in enumerate([80,55,95,70,60,88,54,100,74,62,90,56]):
        bh = 80 + (i % 4) * 22 + int(10 * math.sin(t * 0.4 + i))  # slight height wobble
        by = GROUND_Y - bh
        pygame.draw.rect(surface, (18,20,31), (x, by, bw, bh))
        if i % 2 == 0:  # add windows to every other building
            for row in range(3):
                for col in range(2):
                    wx, wy = x + 14 + col * 18, by + 14 + row * 20
                    if wx + 8 < SCREEN_WIDTH - 8:
                        pygame.draw.rect(surface, (255,226,121), (wx, wy, 8, 10))
        x += bw + 18

    # 4. Ground lane
    pygame.draw.rect(surface, (24,26,37), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT-GROUND_Y))
    pygame.draw.rect(surface, (50,62,83), (0, GROUND_Y-12, SCREEN_WIDTH, 16))
    pygame.draw.line(surface, (112,125,148), (0, GROUND_Y-10), (SCREEN_WIDTH, GROUND_Y-10), 2)
    for lx in range(0, SCREEN_WIDTH, 48):
        pygame.draw.line(surface, (89,99,121), (lx, GROUND_Y-2), (lx+24, GROUND_Y-2), 3)"""

def draw_background(surface: pygame.Surface, background_image: pygame.Surface) -> None:
    """Draw the loaded background image, scaled to the game window."""
    surface.blit(background_image, (0, 0))

# Text helpers
def draw_text(surface, text, font, color, x, y, *, center=False) -> pygame.Rect:
    """Blit text. If center=True, (x,y) is the centre; otherwise top-left."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    rect.center = (x, y) if center else (rect.left + x, rect.top + y)
    # Reposition: use topleft assignment for non-center to avoid double-offset
    if not center:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect


def draw_multiline_center(surface, lines, font, color, cx, cy, gap=8) -> None:
    """Draw multiple lines of text centred on (cx, cy)."""
    total = len(lines) * font.get_linesize() + (len(lines) - 1) * gap
    start_y = cy - total // 2
    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        rect = rendered.get_rect(center=(cx, start_y + i * (font.get_linesize() + gap)))
        surface.blit(rendered, rect)


# Effects
@dataclass
class FloatingText:
    """
    Score pop-up that floats upward and fades out.
    Examples: "+10", "-5"
    """
    text:     str
    color:    tuple[int, int, int]
    position: pygame.Vector2
    life:     float = 1.0  # seconds until gone
    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, -42))

    def update(self, dt: float) -> bool:
        """Move upward, decelerate, tick lifetime. Returns False when expired."""
        self.life       -= dt
        self.position   += self.velocity * dt
        self.velocity.y -= 16 * dt   # slow the rise over time
        return self.life > 0

    def draw(self, surface, font, shake_x=0, shake_y=0) -> None:
        alpha = int(clamp(self.life, 0.0, 1.0) * 255)
        rendered = font.render(self.text, True, self.color)
        rendered.set_alpha(alpha)
        rect = rendered.get_rect(center=(int(self.position.x) + shake_x, int(self.position.y) + shake_y))
        surface.blit(rendered, rect)


@dataclass
class Particle:
    """
    A single colour dot burst out on collection.
    Green burst = note caught. Red burst = coin caught.
    """
    position: pygame.Vector2
    velocity: pygame.Vector2
    color:    tuple[int, int, int]
    radius:   float
    life:     float  # seconds

    def update(self, dt: float) -> bool:
        """Apply gravity, move, tick. Returns False when expired."""
        self.life     -= dt
        self.position += self.velocity * dt
        self.velocity.y += 280 * dt   # gravity pulls particles down
        return self.life > 0

    def draw(self, surface, shake_x=0, shake_y=0) -> None:
        alpha = int(clamp(self.life / 0.55, 0.0, 1.0) * 255)
        size  = int(self.radius * 4)
        dot   = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*self.color, alpha), (size//2, size//2), int(self.radius))
        rect  = dot.get_rect(center=(int(self.position.x) + shake_x, int(self.position.y) + shake_y))
        surface.blit(dot, rect)


# Player
class Player:
    """
    Ozalima — moves left/right with arrow keys.
    Bobs up and down slightly when idle.
    """
    def __init__(self, assets: dict[str, pygame.Surface]) -> None:
        self.assets     = assets
        self.character  = "woman"
        self.position   = pygame.Vector2(SCREEN_WIDTH * 0.5, PLAYER_Y)
        self.speed      = PLAYER_SPEED
        self.idle_timer = 0.0
        self.width      = 104
        self.height     = 124

    def collision_rect(self) -> pygame.Rect:
        """Slightly smaller than the sprite so collisions feel fair."""
        return pygame.Rect(
            int(self.position.x) - (self.width  - 14) // 2,
            int(self.position.y) - (self.height - 10) // 2,
            self.width  - 14,
            self.height - 10,
        )

    def update(self, dt: float, move_left: bool, move_right: bool) -> None:
        h = (-1.0 if move_left else 0.0) + (1.0 if move_right else 0.0)
        self.position.x = clamp(
            self.position.x + h * self.speed * dt,
            self.width * 0.5 + 12,
            SCREEN_WIDTH - self.width * 0.5 - 12,
        )
        self.idle_timer += dt

    def draw(self, surface, font, shake_x=0, shake_y=0) -> None:
        sprite = self.assets[self.character]
        bob   = math.sin(self.idle_timer * 5.0) * 4.0
        scale = 1.0 + math.sin(self.idle_timer * 3.0) * 0.01
        scaled = pygame.transform.smoothscale(sprite, (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
        rect   = scaled.get_rect(center=(int(self.position.x) + shake_x, int(self.position.y + bob) + shake_y))

        # Foot shadow
        shadow = pygame.Surface((rect.width + 24, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,80), (8, 3, rect.width, 14))
        surface.blit(shadow, shadow.get_rect(center=(rect.centerx, rect.bottom - 4)))

        surface.blit(scaled, rect)

        # Name pill above character
        pill = pygame.Rect(0, 0, 106, 28)
        pill.midbottom = (rect.centerx, rect.top - 10)
        pygame.draw.rect(surface, (30, 34, 52), pill, border_radius=14)
        pygame.draw.rect(surface, (85, 98,132), pill, width=2, border_radius=14)
        draw_text(surface, "OZALIMA", font, WHITE, pill.centerx, pill.centery - 1, center=True)


# Falling objects 
class FallingObject:
    """
    Base class for anything that falls from the top of the screen.
    Subclasses: Coin (bad), Note (good).
    """
    kind = "object"

    def __init__(self, image: pygame.Surface, x: float, y: float, speed: float) -> None:
        self.image      = image
        self.position   = pygame.Vector2(x, y)
        self.speed      = speed
        self.rotation   = random.uniform(0.0, 360.0)     # starting angle (degrees)
        self.spin_speed = random.uniform(90.0, 180.0)    # deg/sec
        self.drift      = random.uniform(-24.0, 24.0)    # sideways sine wobble
        self.time_alive = 0.0

    @property
    def rect(self) -> pygame.Rect:
        """Bounding rect at current position (no shake offset)."""
        return self.transformed_image().get_rect(
            center=(int(self.position.x), int(self.position.y))
        )

    def transformed_image(self) -> pygame.Surface:
        """Return the sprite rotated to the current angle."""
        return pygame.transform.rotozoom(self.image, self.rotation, 1.0)

    def update(self, dt: float, difficulty: float) -> bool:
        """
        Move down, drift sideways, spin, and accelerate slightly.
        Returns False when the object has left the screen.
        """
        self.time_alive += dt
        self.position.y += self.speed * dt
        self.position.x += math.sin(self.time_alive * 2.4) * self.drift * dt * 0.4
        self.rotation   += self.spin_speed * dt
        self.speed      += difficulty * dt * 7.0   # gradual speed-up
        return self.position.y < SCREEN_HEIGHT + 90

    def draw(self, surface, shake_x=0, shake_y=0) -> None:
        transformed = self.transformed_image()
        rect = transformed.get_rect(center=(int(self.position.x) + shake_x, int(self.position.y) + shake_y))

        # Drop shadow below object
        shadow = pygame.Surface((rect.width + 16, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,70), (10, rect.height - 6, rect.width - 6, 12))
        surface.blit(shadow, shadow.get_rect(center=(rect.centerx, rect.bottom - 2)))

        surface.blit(transformed, rect)


class Coin(FallingObject):
    """Coin — catching this costs a life and deducts 5 score points."""
    kind = "coin"


class Note(FallingObject):
    """Banknote — catching this earns +10 score. Collect 75 to win."""
    kind = "note"


# Core game manager
class GameManager:
    """
    Owns everything: window, clock, assets, game state, and the main loop.

    Game Flow
    ---------
    Level 1 → Level 2 (25 notes) → Level 3 (50 notes) → Win (75 notes)
    Each level increases fall speed via level_speed_bonus.
    Lives start at 3; hitting zero triggers "Ozalima Die" game-over.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("MoneyCollector")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock  = pygame.time.Clock()

        # Fonts (sizes chosen for readability at 960×540)
        self.title_font = pygame.font.SysFont("arial", 38, bold=True)
        self.ui_font    = pygame.font.SysFont("arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.large_font = pygame.font.SysFont("arial", 64, bold=True)

        self.background_image = self._load_background_image()
        self.assets = self._load_assets()
        self.reset_game()

    # Asset loading
    def _load_assets(self) -> dict[str, pygame.Surface]:
        """Load sprites from disk; use programmatic fallbacks if files are missing."""
        return {
            "woman": try_load_image(["assets/woman.png"],
                                    build_woman_surface((104,124)), (104,124)),
            "coin":  try_load_image(["assets/coin.png", "assets/coin1.png"],
                                    build_coin_surface((52,52)),  (52,52)),
            "note":  try_load_image(["assets/note.jpeg", "assets/Note1.png"],
                                    build_note_surface((82,58)),  (82,58)),
        }

    def _load_background_image(self) -> pygame.Surface:
        """Load the background image after the display is initialized."""
        background_path = BASE_DIR / "background.jpeg"
        if background_path.exists():
            try:
                image = pygame.image.load(str(background_path)).convert()
                return pygame.transform.smoothscale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except pygame.error:
                pass
        return build_background_fallback((SCREEN_WIDTH, SCREEN_HEIGHT))

    # State reset 
    def reset_game(self) -> None:
        """Reset all mutable state to start a fresh game."""
        self.player    = Player(self.assets)
        self.objects:     list[FallingObject]  = []
        self.float_texts: list[FloatingText]   = []
        self.particles:   list[Particle]       = []

        # Scoring / progress
        self.score           = 0
        self.notes_collected = 0
        self.lives           = 3
        self.level           = 1
        self.level_speed_bonus = 0

        # Banner shown briefly on level transition
        self.level_banner       = ""
        self.level_banner_timer = 0.0

        # Flags
        self.paused   = False
        self.game_over = False
        self.won      = False

        # Timing
        self.elapsed       = 0.0
        self.spawn_timer   = 0.0
        self.spawn_interval = 1.0  # seconds between spawns (shrinks over time)

        # Visual effects
        self.flash_timer  = 0.0   # white screen flash on good collect
        self.screen_shake = 0.0   # seconds of shake remaining on bad collect

    # Difficulty
    def get_difficulty(self) -> float:
        """
        Linearly grows with time.
        Used to increase fall speed and spawn rate.
        """
        return self.elapsed / 14.0

    # Spawning 
    def spawn_object(self) -> None:
        """Create one Coin or Note at a random x position above the screen."""
        difficulty = self.get_difficulty()
        x     = random.randint(48, SCREEN_WIDTH - 48)
        speed = 150 + self.level_speed_bonus * 12 + difficulty * 14 + random.uniform(0, 48)

        if random.random() < 0.55:
            self.objects.append(Coin(self.assets["coin"], x, -48, speed))
        else:
            self.objects.append(Note(self.assets["note"], x, -48, speed + 6))  # notes fall a bit faster

    # Level progression 
    def update_level_state(self) -> None:
        """
        Promote Ozalima to the next level based on notes_collected.
        Thresholds: 25 → L2 | 50 → L3 | 75 → Win
        """
        prev = self.level

        if self.notes_collected >= 75:
            self.level, self.level_speed_bonus = 3, 6
            if not self.won:
                self.won = self.game_over = True
                self._show_banner("Level 3 Won", 2.0)

        elif self.notes_collected >= 50:
            self.level, self.level_speed_bonus, self.won = 3, 4, False
            if prev < 3:
                self._show_banner("Level 2 Finished", 1.8)

        elif self.notes_collected >= 25:
            self.level, self.level_speed_bonus, self.won = 2, 2, False
            if prev < 2:
                self._show_banner("Level 1 Finished", 1.8)

        else:
            self.level, self.level_speed_bonus, self.won = 1, 0, False

    def _show_banner(self, text: str, duration: float) -> None:
        """Helper: set the level transition banner text and timer."""
        self.level_banner       = text
        self.level_banner_timer = duration

    # Collection logic 
    def apply_collection(self, obj: FallingObject) -> None:
        """
        Called when the player touches a falling object.
        Note  → +10 score, green burst, screen flash, level-up check.
        Coin  → -5 score, lose 1 life, red burst, screen shake (or game-over).
        """
        if obj.kind == "note":
            self.score           += 10
            self.notes_collected += 1
            self._spawn_burst(obj.position, (255, 220, 90))
            self.float_texts.append(FloatingText("+10", GREEN, pygame.Vector2(obj.position)))
            self.flash_timer = 0.08
            self.update_level_state()
        else:  # coin
            self.score  = max(0, self.score - 5)
            self.lives -= 1
            self._spawn_burst(obj.position, (255, 110, 120))
            self.float_texts.append(FloatingText("-5", RED, pygame.Vector2(obj.position.x, obj.position.y - 24)))

            if self.lives > 0:
                self.screen_shake = 0.20
            else:
                self.game_over = True
                self.won       = False
                self._show_banner("Ozalima Die", 2.5)
                print("Ozalima Die")

    def _spawn_burst(self, pos: pygame.Vector2, color: tuple[int,int,int]) -> None:
        """Emit 10 particles in random directions from pos."""
        for _ in range(10):
            angle = random.uniform(0.0, math.tau)
            speed = random.uniform(70.0, 240.0)
            vel   = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed - 90)
            self.particles.append(Particle(pygame.Vector2(pos), vel, color, random.uniform(2.0, 4.0), 0.55))

    # Event handling
    def handle_events(self) -> bool:
        """Process input events. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True

    # Update 
    def update(self, dt: float) -> None:
        """Main update. Skips gameplay logic when paused or game-over."""
        if self.paused or self.game_over:
            self._update_effects(dt)
            return

        self.elapsed      += dt
        self.spawn_timer  += dt
        self.screen_shake  = max(0.0, self.screen_shake - dt)
        self.flash_timer   = max(0.0, self.flash_timer  - dt)

        # Spawn interval shrinks as difficulty grows (capped at 0.30 s)
        self.spawn_interval = max(0.30, 1.0 - self.get_difficulty() * 0.05 - self.level_speed_bonus * 0.02)

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self.spawn_object()
            # Occasionally spawn a second object at high difficulty
            if self.get_difficulty() > 2.5 and random.random() < 0.28:
                self.spawn_object()

        self._update_objects(dt)
        self._update_effects(dt)

    def _update_objects(self, dt: float) -> None:
        """Move falling objects; remove those off-screen or caught by player."""
        player_rect = self.player.collision_rect()
        difficulty  = self.get_difficulty()
        surviving   = []
        for obj in self.objects:
            alive = obj.update(dt, difficulty)
            if alive and obj.rect.colliderect(player_rect):
                self.apply_collection(obj)   # caught!
            elif alive:
                surviving.append(obj)        # still falling
        self.objects = surviving

    def _update_effects(self, dt: float) -> None:
        """Tick floating texts, particles, and level banner."""
        self.float_texts = [t for t in self.float_texts if t.update(dt)]
        self.particles   = [p for p in self.particles   if p.update(dt)]
        self.level_banner_timer = max(0.0, self.level_banner_timer - dt)

    # Draw 
    def _screen_shake_offset(self) -> tuple[int, int]:
        """Return a random pixel offset while the shake timer is active."""
        if self.game_over or self.screen_shake <= 0.0:
            return 0, 0
        mag = 7 if self.screen_shake > 0.10 else 3
        return random.randint(-mag, mag), random.randint(-mag, mag)

    def draw(self) -> None:
        draw_background(self.screen, self.background_image)
        sx, sy = self._screen_shake_offset()

        # Game objects (objects → particles → floating text → player)
        for obj  in self.objects:     obj.draw(self.screen, sx, sy)
        for p    in self.particles:   p.draw(self.screen, sx, sy)
        for text in self.float_texts: text.draw(self.screen, self.ui_font, sx, sy)
        self.player.draw(self.screen, self.ui_font, sx, sy)

        # HUD
        self._draw_hud()
        self._draw_level_banner()

        # Overlays (pause / game-over on top)
        if self.paused:    self._draw_pause()
        if self.game_over: self._draw_game_over()

        # Brief white flash on note collect
        if self.flash_timer > 0.0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 40))
            self.screen.blit(flash, (0, 0))

        pygame.display.flip()

    def _draw_hud(self) -> None:
        """Top bar: Score | Lives | Level | Notes | Speed bonus."""
        bar = pygame.Rect(18, 14, SCREEN_WIDTH - 36, 70)
        pygame.draw.rect(self.screen, (18,22,36), bar, border_radius=18)
        pygame.draw.rect(self.screen, (78,95,128), bar, width=2, border_radius=18)

        draw_text(self.screen, f"Score: {self.score}",        self.title_font, WHITE,  34,  27)
        draw_text(self.screen, f"Lives: {self.lives}",        self.title_font,
                  RED if self.lives == 1 else WHITE,                           260, 27)
        draw_text(self.screen, f"Level: {self.level}",        self.ui_font,  YELLOW, 430, 31)
        draw_text(self.screen, f"Notes: {self.notes_collected}", self.ui_font, GREEN, 540, 31)
        draw_text(self.screen, f"Speed +{self.level_speed_bonus}", self.ui_font, WHITE, 700, 31)

    def _draw_level_banner(self) -> None:
        """Show a brief banner (e.g. 'Level 1 Finished') in the centre of the screen."""
        if self.level_banner_timer <= 0.0:
            return
        banner = pygame.Rect(0, 0, 320, 42)
        banner.center = (SCREEN_WIDTH // 2, 106)
        pygame.draw.rect(self.screen, (20,24,38), banner, border_radius=18)
        pygame.draw.rect(self.screen, (255,219,102), banner, width=2, border_radius=18)
        draw_text(self.screen, self.level_banner, self.ui_font, WHITE, banner.centerx, banner.centery, center=True)

    def _draw_dim_overlay(self) -> None:
        """Semi-transparent dark overlay used behind pause / game-over panels."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 6, 10, 140))
        self.screen.blit(overlay, (0, 0))

    def _draw_pause(self) -> None:
        self._draw_dim_overlay()
        panel = pygame.Rect(0, 0, 540, 260)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (18,22,36), panel, border_radius=22)
        pygame.draw.rect(self.screen, (88,102,137), panel, width=3, border_radius=22)
        draw_multiline_center(self.screen, ["Paused", "Press P to resume"],
                              self.title_font, WHITE, panel.centerx, panel.centery - 18, 10)

    def _draw_game_over(self) -> None:
        self._draw_dim_overlay()
        panel = pygame.Rect(0, 0, 620, 360)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        border = (76, 214, 135) if self.won else (255, 110, 120)
        fill   = (12, 28, 20)  if self.won else (16, 20, 33)
        heading = "Ozalima Won" if self.won else "Ozalima Die"

        pygame.draw.rect(self.screen, fill,   panel, border_radius=24)
        pygame.draw.rect(self.screen, border, panel, width=3, border_radius=24)
        draw_text(self.screen, heading,                       self.large_font, WHITE,  panel.centerx, panel.top + 70,  center=True)
        draw_text(self.screen, f"Final Score: {self.score}",  self.title_font, YELLOW, panel.centerx, panel.top + 150, center=True)
        draw_text(self.screen, f"Notes Collected: {self.notes_collected}", self.ui_font, WHITE, panel.centerx, panel.top + 195, center=True)
        draw_multiline_center(self.screen, ["Press R to restart", "Press Escape to quit"],
                              self.ui_font, WHITE, panel.centerx, panel.top + 275, 8)

    # Main loop 
    def run(self) -> None:
        running = True
        while running:
            dt      = self.clock.tick(FPS) / 1000.0   # seconds since last frame
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


# Entry point
def main() -> None:
    GameManager().run()


if __name__ == "__main__":
    main()
