import pygame
import random
import math
from abc import ABC, abstractmethod


# ======== Basic Setup ========
WIDTH, HEIGHT = 960, 540
GROUND_Y = HEIGHT - 80
FPS = 60

WHITE = (245, 245, 245)
BLACK = (30, 30, 30)
GRAY = (80, 80, 80)
GREEN = (40, 170, 70)
BLUE = (60, 120, 255)
YELLOW = (250, 210, 60)
PURPLE = (175, 90, 255)
RED = (235, 80, 70)

pygame.init()
pygame.display.set_caption("Decorator Runner (pygame)")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)

# ======== Character Component Abstraction ========
class ICharacter(ABC):
    """Interface for the character so decorators can wrap it."""
    @abstractmethod
    def update(self, dt, keys): ...
    @abstractmethod
    def draw(self, surf): ...
    @abstractmethod
    def get_rect(self) -> pygame.Rect: ...
    @abstractmethod
    def get_base_speed(self) -> float: ...
    @abstractmethod
    def get_move_speed(self) -> float: ...
    @abstractmethod
    def get_jump_power(self) -> float: ...
    @abstractmethod
    def is_shielded(self) -> bool: ...
    @abstractmethod
    def damage(self, amount: int): ...
    @abstractmethod
    def get_state(self) -> dict: ...

# ======== Concrete Character ========
class SimpleCharacter(ICharacter):
    def __init__(self, x, y):
        self.w = 48
        self.h = 64
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False

        # core attributes (decorators can *read* these, but should not mutate directly)
        self._base_speed = 260.0
        self._jump_power = 500.0

        # gameplay state
        self.hp = 3
        self.facing = 1  # 1 right, -1 left
        self.color = BLUE

        # simple "animation" state
        self.leg_phase = 0.0

        self.frames = []
        
        def load_animation(prefix):
            frames = []
            for i in range(10):
                img = pygame.image.load(f"ninja/{prefix}__{i:03}.png").convert_alpha()
                img = pygame.transform.scale(img, (self.w, self.h))
                frames.append(img)
            return frames

        self.animations = {
            "idle": load_animation("Idle"),
            "run": load_animation("Run"),
            "jump": load_animation("Jump"),
            "dead": load_animation("Dead"),
            "slide": load_animation("Slide"),
        }

        self.current_anim = "idle"
        self.frame_index = 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def get_base_speed(self):  # not modified by decorators
        return self._base_speed

    def get_move_speed(self):  # may be overridden by decorators
        return self._base_speed

    def get_jump_power(self):  # may be overridden by decorators
        return self._jump_power

    def is_shielded(self):
        return False  # overridden by shield decorator

    def damage(self, amount: int):
        if not self.is_shielded():
            self.hp = max(0, self.hp - amount)

    def get_state(self):
        return {
            "hp": self.hp,
            "on_ground": self.on_ground,
            "vx": self.vx,
            "vy": self.vy
        }

    def _physics(self, dt, keys):
        # horizontal input
        ax = 0
        speed = self.get_move_speed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= speed
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += speed
            self.facing = 1

        # integrate horizontal velocity as immediate (arcade feel)
        self.vx = ax
        self.x += self.vx * dt

        # clamp to screen
        #self.x = max(0, min(self.x, WIDTH - self.w))

        # wrap around horizontally
        self.x %= WIDTH

        # jumping / gravity
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = -self.get_jump_power()
            self.on_ground = False

        # gravity
        self.vy += 1400 * dt
        self.y += self.vy * dt

        # ground collision
        if self.y + self.h >= GROUND_Y:
            self.y = GROUND_Y - self.h
            self.vy = 0
            self.on_ground = True

        # simple run animation phase update
        if abs(self.vx) > 1 and self.on_ground:
            self.leg_phase += dt * 12
        else:
            self.leg_phase *= (1 - min(1, dt * 8))

    def update(self, dt, keys):
        self._physics(dt, keys)
        if self.hp <= 0:
            self.current_anim = "dead"
        elif not self.on_ground:
            self.current_anim = "jump"
        elif abs(self.vx) > 1:
            self.current_anim = "run"
        else:
            self.current_anim = "idle"

        # avanzar animación
        self.frame_index += dt * 10
        if abs(self.vx) > 1 and self.on_ground:
            self.frame_index += dt * 10
        else:
            self.frame_index = 0

    def draw(self, surf):
        rect = self.get_rect()

        frames = self.animations[self.current_anim]
        frame = frames[int(self.frame_index) % len(frames)]

        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)

        surf.blit(frame, rect)        
        
    def set_hp(self, hp):
        self.hp = hp
# ======== Decorator Base ========
class CharacterDecorator(ICharacter):
    """Base class for all decorators; forwards to wrapped character."""
    def __init__(self, wrappee: ICharacter):
        self.wrappee = wrappee

    # forwarding
    def update(self, dt, keys): self.wrappee.update(dt, keys)
    def draw(self, surf): self.wrappee.draw(surf)
    def get_rect(self): return self.wrappee.get_rect()
    def get_base_speed(self): return self.wrappee.get_base_speed()
    def get_move_speed(self): return self.wrappee.get_move_speed()
    def get_jump_power(self): return self.wrappee.get_jump_power()
    def is_shielded(self): return self.wrappee.is_shielded()
    def damage(self, amount: int): self.wrappee.damage(amount)
    def get_state(self): return self.wrappee.get_state()

# A small utility: timed decorators auto-expire after `duration` seconds
class TimedDecorator(CharacterDecorator):
    def __init__(self, wrappee: ICharacter, duration: float):
        super().__init__(wrappee)
        self.remaining = duration

    def update(self, dt, keys):
        super().update(dt, keys)
        self.remaining -= dt

    def is_expired(self) -> bool:
        return self.remaining <= 0

# ======== Concrete Decorators ========
class SpeedBoost(TimedDecorator):
    def __init__(self, wrappee: ICharacter, duration=6.0, multiplier=1.6):
        super().__init__(wrappee, duration)
        self.multiplier = multiplier

    def get_move_speed(self):
        return self.wrappee.get_move_speed() * self.multiplier

    def draw(self, surf):
        # aura
        rect = self.get_rect().inflate(12, 12)
        pygame.draw.rect(surf, YELLOW, rect, width=3, border_radius=12)
        super().draw(surf)

class JumpBoost(TimedDecorator):
    def __init__(self, wrappee: ICharacter, duration=6.0, bonus=240.0):
        super().__init__(wrappee, duration)
        self.bonus = bonus

    def get_jump_power(self):
        return self.wrappee.get_jump_power() + self.bonus

    def draw(self, surf):
        rect = self.get_rect().inflate(8, 8)
        pygame.draw.rect(surf, PURPLE, rect, width=3, border_radius=10)
        super().draw(surf)

class Shield(TimedDecorator):
    def __init__(self, wrappee: ICharacter, duration=8.0):
        super().__init__(wrappee, duration)

    def is_shielded(self):
        return True

    def draw(self, surf):
        rect = self.get_rect().inflate(20, 20)
        pygame.draw.ellipse(surf, (80, 200, 255), rect, width=3)
        super().draw(surf)

# ======== World Objects (pickups & hazards) ========
class Pickup:
    def __init__(self, x, kind):
        self.kind = kind  # 'speed' | 'jump' | 'shield'
        self.rect = pygame.Rect(x, GROUND_Y - 20, 20, 20)
        self.color = {"speed": YELLOW, "jump": PURPLE, "shield": (80, 200, 255)}[kind]

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)

class Hazard:
    def __init__(self, x):
        self.rect = pygame.Rect(x, GROUND_Y - 14, 28, 14)
        self.color = RED

    def draw(self, surf):
        pygame.draw.polygon(
            surf,
            self.color,
            [
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.bottom),
            ],
        )

# ======== Helper: unwrap expired decorators ========
def strip_expired_decorators(character: ICharacter) -> ICharacter:
    """Recursively unwrap timed decorators that have expired."""
    # If not a TimedDecorator, nothing to do
    if not isinstance(character, CharacterDecorator):
        return character

    # First, ensure inner is stripped
    character.wrappee = strip_expired_decorators(character.wrappee)

    # Then check this decorator
    if isinstance(character, TimedDecorator) and character.is_expired():
        return character.wrappee  # drop this layer
    return character

# ======== Helper: push a decorator on top (composable) ========
def add_decorator(character: ICharacter, deco_cls):
    return deco_cls(character)

# ======== Game State ========
def spawn_level():
    pickups = []
    hazards = []
    # deterministic but varied layout
    x = 140
    for i in range(8):
        r = random.random()
        if r < 0.35:
            kind = random.choice(["speed", "jump", "shield"])
            pickups.append(Pickup(x, kind))
        elif r < 0.65:
            hazards.append(Hazard(x))
        x += random.randint(90, 160)
    return pickups, hazards

def draw_ground(surf):
    pygame.draw.rect(surf, (40, 45, 55), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # Stripe
    pygame.draw.line(surf, (55, 60, 70), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

def draw_ui(surf, character: ICharacter, active_effects: list[TimedDecorator], score: int):
    # HP and Score
    hp_text = font.render(f"HP: {character.get_state()['hp']}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    surf.blit(hp_text, (12, 10))
    surf.blit(score_text, (12, 32))

    # Effects timeline
    x0, y0 = 12, 56
    for eff in active_effects:
        if isinstance(eff, SpeedBoost):
            label, c = "Speed", YELLOW
        elif isinstance(eff, JumpBoost):
            label, c = "Jump", PURPLE
        elif isinstance(eff, Shield):
            label, c = "Shield", (80, 200, 255)
        else:
            label, c = eff.__class__.__name__, GRAY

        # bar with remaining time (normalized to its original duration)
        # we don't store original directly; estimate max as clamp
        # For display only, we draw a small static bar using remaining seconds
        bar_w = 140
        remaining = max(0.0, getattr(eff, "remaining", 0.0))
        pct = max(0.0, min(1.0, remaining / 8.0))  # 8s scale looks nice
        pygame.draw.rect(surf, GRAY, (x0, y0, bar_w, 10), border_radius=3)
        pygame.draw.rect(surf, c, (x0, y0, int(bar_w * pct), 10), border_radius=3)
        label_text = font.render(f"{label} {remaining:0.1f}s", True, WHITE)
        surf.blit(label_text, (x0 + bar_w + 8, y0 - 4))
        y0 += 18

def main():
    random.seed(7)

    # world
    pickups, hazards = spawn_level()
    character: ICharacter = SimpleCharacter(80, GROUND_Y - 64)
    character_original = character  # keep original reference for resets
    score = 0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Update character (decorators can modify behavior)
        character.update(dt, keys)

        # Check collisions with pickups
        crect = character.get_rect()
        acquired = []
        for p in pickups:
            if crect.colliderect(p.rect):
                if p.kind == "speed":
                    character = add_decorator(character, lambda w: SpeedBoost(w, duration=6.0, multiplier=1.6))
                elif p.kind == "jump":
                    character = add_decorator(character, lambda w: JumpBoost(w, duration=6.0, bonus=240.0))
                elif p.kind == "shield":
                    character = add_decorator(character, lambda w: Shield(w, duration=8.0))
                acquired.append(p)
                score += 10
        for p in acquired:
            pickups.remove(p)

        # Collisions with hazards
        for h in hazards[:]:
            if crect.colliderect(h.rect):
                character.damage(1)
                hazards.remove(h)   # consume the hazard
                score = max(0, score - 5)

        # Strip expired decorators
        character = strip_expired_decorators(character)

        # Respawn world items occasionally (keep the playground alive)
        if random.random() < 0.01 and len(pickups) < 7:
            kind = random.choice(["speed", "jump", "shield"])
            pickups.append(Pickup(random.randint(80, WIDTH - 80), kind))
        if random.random() < 0.008 and len(hazards) < 6:
            hazards.append(Hazard(random.randint(80, WIDTH - 80)))

        # ======== RENDER ========
        screen.fill((25, 28, 35))
        draw_ground(screen)

        for p in pickups:
            p.draw(screen)
        for h in hazards:
            h.draw(screen)

        # Collect active timed decorators (for UI)
        active_effects = []
        tmp = character
        while isinstance(tmp, CharacterDecorator):
            if isinstance(tmp, TimedDecorator):
                active_effects.append(tmp)
            tmp = tmp.wrappee

        character.draw(screen)
        draw_ui(screen, character, active_effects, score)

        # Game over banner
        if character.get_state()["hp"] <= 0:
            banner = font.render("Game Over — press ESC to quit OR press R to restart", True, RED)
            screen.blit(banner, (WIDTH // 2 - banner.get_width() // 2, 10))
            if keys[pygame.K_ESCAPE]:
                running = False
            if keys[pygame.K_r]:
                # Restart the game
                character_original.set_hp(3)  # reset HP

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()