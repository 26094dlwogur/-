import math
import random

try:
    from .animal import Animal
    from .fish import Fish
    from .mudskipper import Mudskipper
except ImportError:
    from animal import Animal
    from fish import Fish
    from mudskipper import Mudskipper


def _clamp(value, low, high):
    return max(low, min(high, value))


class Bird(Animal):
    SPRITE = "bird"
    SKY_ZONE = (0, 30, 1280, 160)

    def __init__(self, x=None, y=None):
        super().__init__(
            name="bird",
            power=8,
            vmax=3.5,
            x=random.uniform(50, 1230) if x is None else x,
            y=random.uniform(30, 130) if y is None else y,
            is_youth=False,
        )
        self.habitat = "sky"
        self._max_hunger = 60
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-0.5, 0.5)
        self._dive_target = None
        self.event_log = []

    def move(self, environment):
        self.age += 1
        self._tick_hunger()
        self.event_log.clear()
        if not self.alive:
            return False

        if getattr(environment, "is_low_tide", False) and not getattr(environment, "use_biome_rules", False):
            self._hunt(environment)
        else:
            self._dive_target = None

        self._fly()
        return True

    def _fly(self):
        x0, y0, x1, y1 = self.SKY_ZONE
        if self._dive_target is not None and self._dive_target.alive:
            dx = self._dive_target.x - self.x
            dy = self._dive_target.y - self.y
            distance = math.hypot(dx, dy) or 1
            self.place = (
                self.x + dx / distance * self.vmax,
                self.y + dy / distance * self.vmax,
            )
        else:
            self.vx = _clamp(self.vx * 0.99 + random.uniform(-0.2, 0.2), -2, 2)
            self.vy = _clamp(self.vy * 0.99 + random.uniform(-0.1, 0.1), -1, 1)
            self.place = (
                self.x + self.vx + random.uniform(-0.4, 0.4),
                self.y + self.vy + random.uniform(-0.2, 0.2),
            )

        if self.x < x0 or self.x > x1:
            self.vx *= -1
        if self.y < y0 or self.y > y1:
            self.vy *= -1

        self.place = (_clamp(self.x, x0, x1), _clamp(self.y, y0, y1))

    def _hunt(self, environment):
        targets = [
            animal
            for animal in environment.organism_list
            if animal.alive and isinstance(animal, (Fish, Mudskipper))
        ]
        if not targets:
            self._dive_target = None
            return

        target = min(targets, key=lambda animal: self.get_distance(animal))
        self._dive_target = target
        if self.get_distance(target) < 20 and random.random() < 0.4:
            target.death()
            self._eat()
            self._dive_target = None
            self.event_log.append(f"bird hunted {target.name}")

    def reproduce(self):
        if not self.alive or self.is_starving:
            return None
        if self.age > 30 and random.random() < 0.003:
            return Bird(x=self.x + random.uniform(-20, 20), y=self.y + random.uniform(-10, 10))
        return None
