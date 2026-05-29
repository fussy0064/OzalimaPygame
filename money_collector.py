from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pygame

# Constants 
BASE_DIR = Path(__file__).resolve().parent

SCREEN_WIDTH  = 960
SCREEN_HEIGHT = 540
FPS           = 60
GROUND_Y      = 442
PLAYER_Y      = 400
PLAYER_SPEED  = 390.0

WHITE  = (245, 247, 255)
RED    = (230, 86, 94)
GREEN  = (76, 214, 135)
YELLOW = (255, 219, 102)


#Utility functions 
def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def lerp_color(a: tuple[int,int,int], b: tuple[int,int,int], t: float) -> tuple[int,int,int]:
    t = clamp(t, 0.0, 1.0)
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def try_load_image(paths: list[str], fallback: pygame.Surface, size: tuple[int,int]) -> pygame.Surface:
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
    surface = pygame.Surface(size)
    for y in range(size[1]):
        color = lerp_color((11, 15, 28), (28, 24, 44), y / max(1, size[1] - 1))
        pygame.draw.line(surface, color, (0, y), (size[0], y))
    return surface


# Fallback sprite builders 
def build_coin_surface(size: tuple[int,int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    r = min(w, h) // 2 - 2
    pygame.draw.circle(surf, (255, 228, 126), (cx, cy), r)
    pygame.draw.circle(surf, (255, 248, 215), (cx - 6, cy - 7), r//2)
    pygame.draw.circle(surf, (195, 132, 16),  (cx, cy), r, 3)
    pygame.draw.circle(surf, (255, 201, 60),  (cx, cy), r - 4, 2)
    pygame.draw.line(surf, (255, 245, 179), (cx-10, cy-12), (cx-2,  cy-20), 3)
    pygame.draw.line(surf, (255, 245, 179), (cx+5,  cy-9),  (cx+14, cy-17), 2)
    return surf


def build_note_surface(size: tuple[int,int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    body  = pygame.Rect(4, 6, w - 8, h - 12)
    inner = pygame.Rect(12, 15, w - 24, h - 30)
    pygame.draw.rect(surf, (54, 190, 131), body,  border_radius=8)
    pygame.draw.rect(surf, (22, 110, 74),  body,  width=3, border_radius=8)
    pygame.draw.polygon(surf, (220, 247, 231), [(w-17,8),(w-6,18),(w-17,18)])
    pygame.draw.rect(surf, (232, 255, 245), inner, width=2, border_radius=5)
    pygame.draw.circle(surf, (232, 255, 245), (w//2, h//2), min(w,h)//5, 2)
    pygame.draw.line(surf, (232, 255, 245), (inner.left+4, inner.centery), (inner.right-4, inner.centery), 2)
    return surf


def build_woman_surface(size: tuple[int,int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    cx = w // 2
    pygame.draw.ellipse(surf, (0,0,0,55), pygame.Rect(cx-30, h-14, 60, 10))
    pygame.draw.circle(surf, (246, 211, 183), (cx, 29), 18)
    pygame.draw.circle(surf, (79, 47, 27),    (cx, 26), 22)
    pygame.draw.polygon(surf, (79, 47, 27), [(cx-24,24),(cx-34,54),(cx-14,62),(cx-10,28)])
    pygame.draw.polygon(surf, (79, 47, 27), [(cx+24,24),(cx+34,54),(cx+14,62),(cx+10,28)])
    pygame.draw.circle(surf, (246, 211, 183), (cx-2, 28), 17)
    pygame.draw.line(surf, (64, 41, 27), (cx-8, 28), (cx+8, 28), 2)
    pygame.draw.polygon(surf, (175, 109, 255), [(cx,48),(cx-27,94),(cx+27,94)])
    pygame.draw.polygon(surf, (231, 211, 255), [(cx,50),(cx-12,63),(cx+12,63)])
    pygame.draw.line(surf, (246, 211, 183), (cx-18,58), (cx-34,79), 6)
    pygame.draw.line(surf, (246, 211, 183), (cx+18,58), (cx+34,79), 6)
    pygame.draw.line(surf, (175, 109, 255), (cx-11,90), (cx-17,117), 7)
    pygame.draw.line(surf, (175, 109, 255), (cx+11,90), (cx+17,117), 7)
    pygame.draw.circle(surf, (48, 58, 76), (cx-17, 117), 5)
    pygame.draw.circle(surf, (48, 58, 76), (cx+17, 117), 5)
    pygame.draw.polygon(surf, (42, 30, 56), [(cx-27,94),(cx+27,94),(cx,125)], 2)
    return surf


# Background 
def draw_background(surface: pygame.Surface, background_image: pygame.Surface) -> None:
    surface.blit(background_image, (0, 0))


# Text helpers 
def draw_text(surface, text, font, color, x, y, *, center=False) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect


def draw_multiline_center(surface, lines, font, color, cx, cy, gap=8) -> None:
    total = len(lines) * font.get_linesize() + (len(lines) - 1) * gap
    start_y = cy - total // 2
    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        rect = rendered.get_rect(center=(cx, start_y + i * (font.get_linesize() + gap)))
        surface.blit(rendered, rect)


# Effects 
@dataclass
class FloatingText:
    text:     str
    color:    tuple[int, int, int]
    position: pygame.Vector2
    life:     float = 1.0
    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, -42))

    def update(self, dt: float) -> bool:
        self.life       -= dt
        self.position   += self.velocity * dt
        self.velocity.y -= 16 * dt
        return self.life > 0

    def draw(self, surface, font) -> None:
        alpha = int(clamp(self.life, 0.0, 1.0) * 255)
        rendered = font.render(self.text, True, self.color)
        rendered.set_alpha(alpha)
        rect = rendered.get_rect(center=(int(self.position.x), int(self.position.y)))
        surface.blit(rendered, rect)


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color:    tuple[int, int, int]
    radius:   float
    life:     float

    def update(self, dt: float) -> bool:
        self.life     -= dt
        self.position += self.velocity * dt
        self.velocity.y += 280 * dt
        return self.life > 0

    def draw(self, surface) -> None:
        alpha = int(clamp(self.life / 0.55, 0.0, 1.0) * 255)
        size  = int(self.radius * 4)
        dot   = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*self.color, alpha), (size//2, size//2), int(self.radius))
        rect  = dot.get_rect(center=(int(self.position.x), int(self.position.y)))
        surface.blit(dot, rect)


# Player 
class Player:
    def __init__(self, assets: dict[str, pygame.Surface]) -> None:
        self.assets     = assets
        self.character  = "woman"
        self.position   = pygame.Vector2(SCREEN_WIDTH * 0.5, PLAYER_Y)
        self.speed      = PLAYER_SPEED
        self.idle_timer = 0.0
        self.width      = 104
        self.height     = 124

    def collision_rect(self) -> pygame.Rect:
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

    def draw(self, surface, font) -> None:
        sprite = self.assets[self.character]
        bob    = math.sin(self.idle_timer * 5.0) * 4.0
        scale  = 1.0 + math.sin(self.idle_timer * 3.0) * 0.01
        scaled = pygame.transform.smoothscale(sprite, (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
        rect   = scaled.get_rect(center=(int(self.position.x), int(self.position.y + bob)))

        shadow = pygame.Surface((rect.width + 24, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,80), (8, 3, rect.width, 14))
        surface.blit(shadow, shadow.get_rect(center=(rect.centerx, rect.bottom - 4)))

        surface.blit(scaled, rect)

        pill = pygame.Rect(0, 0, 106, 28)
        pill.midbottom = (rect.centerx, rect.top - 10)
        pygame.draw.rect(surface, (30, 34, 52), pill, border_radius=14)
        pygame.draw.rect(surface, (85, 98,132), pill, width=2, border_radius=14)
        draw_text(surface, "OZALIMA", font, WHITE, pill.centerx, pill.centery - 1, center=True)


# Falling objects 
class FallingObject:
    kind = "object"

    def __init__(self, image: pygame.Surface, x: float, y: float, speed: float) -> None:
        self.image      = image
        self.position   = pygame.Vector2(x, y)
        self.speed      = speed
        self.rotation   = random.uniform(0.0, 360.0)
        self.spin_speed = random.uniform(90.0, 180.0)
        self.drift      = random.uniform(-24.0, 24.0)
        self.time_alive = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return self.transformed_image().get_rect(
            center=(int(self.position.x), int(self.position.y))
        )

    def transformed_image(self) -> pygame.Surface:
        return pygame.transform.rotozoom(self.image, self.rotation, 1.0)

    def update(self, dt: float, difficulty: float) -> bool:
        self.time_alive += dt
        self.position.y += self.speed * dt
        self.position.x += math.sin(self.time_alive * 2.4) * self.drift * dt * 0.4
        self.rotation   += self.spin_speed * dt
        self.speed      += difficulty * dt * 7.0
        return self.position.y < SCREEN_HEIGHT + 90

    def draw(self, surface) -> None:
        transformed = self.transformed_image()
        rect = transformed.get_rect(center=(int(self.position.x), int(self.position.y)))

        shadow = pygame.Surface((rect.width + 16, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,70), (10, rect.height - 6, rect.width - 6, 12))
        surface.blit(shadow, shadow.get_rect(center=(rect.centerx, rect.bottom - 2)))

        surface.blit(transformed, rect)


class Coin(FallingObject):
    kind = "coin"


class Note(FallingObject):
    kind = "note"


# Game Manager 
class GameManager:

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("MoneyCollector")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock  = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 38, bold=True)
        self.ui_font    = pygame.font.SysFont("arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.large_font = pygame.font.SysFont("arial", 64, bold=True)

        self.background_image = self._load_background_image()
        self.assets = self._load_assets()
        self.reset_game()

    # Asset loading 
    def _load_assets(self) -> dict[str, pygame.Surface]:
        return {
            "woman": try_load_image(["assets/woman.png"],
                                    build_woman_surface((104,124)), (104,124)),
            "coin":  try_load_image(["assets/coin.png", "assets/coin1.png"],
                                    build_coin_surface((52,52)),  (52,52)),
            "note":  try_load_image(["assets/note.jpeg", "assets/Note1.png"],
                                    build_note_surface((82,58)),  (82,58)),
        }

    def _load_background_image(self) -> pygame.Surface:
        background_path = BASE_DIR / "assets/background.jpeg"
        if background_path.exists():
            try:
                image = pygame.image.load(str(background_path)).convert()
                return pygame.transform.smoothscale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except pygame.error:
                pass
        return build_background_fallback((SCREEN_WIDTH, SCREEN_HEIGHT))

    # State reset 
    def reset_game(self) -> None:
        self.player    = Player(self.assets)
        self.objects:     list[FallingObject] = []
        self.float_texts: list[FloatingText]  = []
        self.particles:   list[Particle]      = []

        self.score           = 0
        self.notes_collected = 0
        self.lives           = 3
        self.level           = 1
        self.level_speed_bonus = 0

        self.level_banner       = ""
        self.level_banner_timer = 0.0

        self.paused    = False
        self.game_over = False
        self.won       = False

        self.elapsed        = 0.0
        self.spawn_timer    = 0.0
        self.spawn_interval = 1.0

        self.flash_timer = 0.0   # white flash on good collect

    # Difficulty 
    def get_difficulty(self) -> float:
        return self.elapsed / 14.0

    # Spawning 
    def spawn_object(self) -> None:
        difficulty = self.get_difficulty()
        x = random.randint(48, SCREEN_WIDTH - 48)
        speed = 150 + self.level_speed_bonus * 12 + difficulty * 14 + random.uniform(0, 48)

        if random.random() < 0.55:
            self.objects.append(Coin(self.assets["coin"], x, -48, speed))
        else:
            self.objects.append(Note(self.assets["note"], x, -48, speed + 6))

    # Level state 
    def update_level_state(self) -> None:
        prev = self.level

        if self.notes_collected >= 75:
            self.level, self.level_speed_bonus = 3, 6
            if not self.won:
                self.won = self.game_over = True
                self._show_banner("Ozalima Won", 2.0)

        elif self.notes_collected >= 50:
            self.level, self.level_speed_bonus = 3, 4   # FIX: was incorrectly set to level 3 before 75 notes
            if prev < 3:
                self._show_banner("Level 2 Finished", 1.8)

        elif self.notes_collected >= 25:
            self.level, self.level_speed_bonus = 2, 2   # FIX: was incorrectly set to level 3
            if prev < 2:
                self._show_banner("Level 1 Finished", 1.8)

        else:
            self.level, self.level_speed_bonus = 1, 0

    def _show_banner(self, text: str, duration: float) -> None:
        self.level_banner       = text
        self.level_banner_timer = duration

    # Collection logic 
    def apply_collection(self, obj: FallingObject) -> None:
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

            if self.lives <= 0:
                self.game_over = True
                self.won       = False
                self._show_banner("Ozalima Die", 2.5)
                print("Ozalima Die")

    def _spawn_burst(self, pos: pygame.Vector2, color: tuple[int,int,int]) -> None:
        for _ in range(10):
            angle = random.uniform(0.0, math.tau)
            speed = random.uniform(70.0, 240.0)
            vel   = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed - 90)
            self.particles.append(Particle(pygame.Vector2(pos), vel, color, random.uniform(2.0, 4.0), 0.55))

    # Events 
    def handle_events(self) -> bool:
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
        if self.paused or self.game_over:
            self._update_effects(dt)
            return

        self.elapsed     += dt
        self.spawn_timer += dt
        self.flash_timer  = max(0.0, self.flash_timer - dt)

        self.spawn_interval = max(0.30, 1.0 - self.get_difficulty() * 0.05 - self.level_speed_bonus * 0.02)

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self.spawn_object()
            if self.get_difficulty() > 2.5 and random.random() < 0.28:
                self.spawn_object()

        self._update_objects(dt)
        self._update_effects(dt)

    def _update_objects(self, dt: float) -> None:
        player_rect = self.player.collision_rect()
        difficulty  = self.get_difficulty()
        surviving   = []
        for obj in self.objects:
            if self.game_over:          # FIX: stop processing once game ends
                break
            alive = obj.update(dt, difficulty)
            if alive and obj.rect.colliderect(player_rect):
                self.apply_collection(obj)
            elif alive:
                surviving.append(obj)
        self.objects = surviving

    def _update_effects(self, dt: float) -> None:
        self.float_texts = [t for t in self.float_texts if t.update(dt)]
        self.particles   = [p for p in self.particles   if p.update(dt)]
        self.level_banner_timer = max(0.0, self.level_banner_timer - dt)

    #Draw 
    def draw(self) -> None:
        draw_background(self.screen, self.background_image)

        for obj  in self.objects:     obj.draw(self.screen)
        for p    in self.particles:   p.draw(self.screen)
        for text in self.float_texts: text.draw(self.screen, self.ui_font)
        self.player.draw(self.screen, self.ui_font)

        self._draw_hud()
        self._draw_level_banner()

        if self.paused:    self._draw_pause()
        if self.game_over: self._draw_game_over()

        if self.flash_timer > 0.0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 40))
            self.screen.blit(flash, (0, 0))

        pygame.display.flip()

    def _draw_hud(self) -> None:
        bar = pygame.Rect(18, 14, SCREEN_WIDTH - 36, 70)
        pygame.draw.rect(self.screen, (18,22,36), bar, border_radius=18)
        pygame.draw.rect(self.screen, (78,95,128), bar, width=2, border_radius=18)

        draw_text(self.screen, f"Score: {self.score}",           self.title_font, WHITE,  34,  27)
        draw_text(self.screen, f"Lives: {self.lives}",           self.title_font,
                  RED if self.lives == 1 else WHITE,                              260, 27)
        draw_text(self.screen, f"Level: {self.level}",           self.ui_font,  YELLOW, 430, 31)
        draw_text(self.screen, f"Notes: {self.notes_collected}", self.ui_font,  GREEN,  540, 31)
        draw_text(self.screen, f"Speed +{self.level_speed_bonus}", self.ui_font, WHITE, 700, 31)

    def _draw_level_banner(self) -> None:
        if self.level_banner_timer <= 0.0:
            return
        banner = pygame.Rect(0, 0, 320, 42)
        banner.center = (SCREEN_WIDTH // 2, 106)
        pygame.draw.rect(self.screen, (20,24,38), banner, border_radius=18)
        pygame.draw.rect(self.screen, (255,219,102), banner, width=2, border_radius=18)
        draw_text(self.screen, self.level_banner, self.ui_font, WHITE, banner.centerx, banner.centery, center=True)

    def _draw_dim_overlay(self) -> None:
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

        border  = (76, 214, 135) if self.won else (255, 110, 120)
        fill    = (12, 28, 20)  if self.won else (16, 20, 33)
        heading = "Ozalima Won" if self.won else "Ozalima Die"

        pygame.draw.rect(self.screen, fill,   panel, border_radius=24)
        pygame.draw.rect(self.screen, border, panel, width=3, border_radius=24)
        draw_text(self.screen, heading,                            self.large_font, WHITE,  panel.centerx, panel.top + 70,  center=True)
        draw_text(self.screen, f"Final Score: {self.score}",       self.title_font, YELLOW, panel.centerx, panel.top + 150, center=True)
        draw_text(self.screen, f"Notes Collected: {self.notes_collected}", self.ui_font, WHITE, panel.centerx, panel.top + 195, center=True)
        draw_multiline_center(self.screen, ["Press R to restart", "Press Escape to quit"],
                              self.ui_font, WHITE, panel.centerx, panel.top + 275, 8)

    # Main loop 
    def run(self) -> None:
        running = True
        while running:
            dt      = self.clock.tick(FPS) / 1000.0
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
