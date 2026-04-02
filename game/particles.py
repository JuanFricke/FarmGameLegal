"""
Simple confetti particle system for successful harvests.
Each particle is a coloured rectangle that flies outward and fades.
"""
from __future__ import annotations
import random
import math
import pygame

_COLORS = [
    (255, 215,   0),   # gold
    (80,  220, 120),   # green
    (100, 180, 255),   # sky blue
    (255, 100, 180),   # pink
    (255, 160,  50),   # orange
    (180, 100, 255),   # purple
    (255, 255, 100),   # yellow
]

_GRAVITY = 0.18
_PARTICLE_COUNT = 40


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "color", "alpha", "size", "rot", "rot_speed")

    def __init__(self, cx: float, cy: float) -> None:
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2.0, 6.0)
        self.x = cx
        self.y = cy
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(1, 3)
        self.color = random.choice(_COLORS)
        self.alpha = 255
        self.size = random.randint(4, 9)
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)

    def update(self) -> bool:
        """Advance one frame. Returns False when the particle should be removed."""
        self.vy += _GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.rot += self.rot_speed
        self.alpha = max(0, self.alpha - 4)
        return self.alpha > 0

    def draw(self, surface: pygame.Surface) -> None:
        if self.alpha <= 0:
            return
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        r, g, b = self.color
        s.fill((r, g, b, self.alpha))
        rotated = pygame.transform.rotate(s, self.rot)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)


class ParticleSystem:
    def __init__(self) -> None:
        self._particles: list[Particle] = []

    def burst(self, cx: float, cy: float, count: int = _PARTICLE_COUNT) -> None:
        """Emit a confetti burst centred at (cx, cy)."""
        for _ in range(count):
            self._particles.append(Particle(cx, cy))

    def update(self) -> None:
        self._particles = [p for p in self._particles if p.update()]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self._particles:
            p.draw(surface)

    @property
    def is_empty(self) -> bool:
        return len(self._particles) == 0
