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


class Crab(Animal):
    SPRITE = "crab"
    MUD_ZONE = (100, 480, 1180, 680)

    def __init__(self, x=None, y=None):
        super().__init__(
            name="crab",
            power=5,
            vmax=2,
            x=random.uniform(200, 1080) if x is None else x,
            y=random.uniform(500, 640) if y is None else y,
            is_youth=False,
        )
        self.habitat = "mud"
        self._max_hunger = 50
        self.is_hidden = False
        self.event_log = []

    def move(self, environment):
        self.age += 1
        self._tick_hunger()
        self.event_log.clear()
        if not self.alive:
            return False

        if getattr(environment, "is_low_tide", False):
            self.is_hidden = False
            self._wander_mud()
            if not getattr(environment, "use_biome_rules", False):
                self._hunt(environment)
        else:
            self.is_hidden = True
            self.place = (self.x, min(self.y + 1, 720))
        return True

    def _wander_mud(self):
        x0, y0, x1, y1 = self.MUD_ZONE
        self.place = (
            _clamp(self.x + random.uniform(-2, 2), x0, x1),
            _clamp(self.y + random.uniform(-1, 1), y0, y1),
        )

    def _hunt(self, environment):
        for animal in list(environment.organism_list):
            if not animal.alive or not isinstance(animal, (Fish, Mudskipper)):
                continue

            if math.hypot(animal.x - self.x, animal.y - self.y) < 30 and random.random() < 0.35:
                animal.death()
                self._eat()
                self.event_log.append(f"crab hunted {animal.name}")
                return

    def reproduce(self):
        if not self.alive or self.is_starving:
            return None
        if self.age > 30 and random.random() < 0.004:
            return Crab(x=self.x + random.uniform(-15, 15), y=self.y + random.uniform(-10, 10))
        return None
