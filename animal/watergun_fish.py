import math
import random

try:
    from .animal import Animal
    from .ant import Ant, Ant_herd
except ImportError:
    from animal import Animal
    from ant import Ant, Ant_herd


class WatergunFish(Animal):
    def __init__(self, hit_chance=0.6, x=420, y=375):
        super().__init__(
            name="watergun_fish",
            power=5,
            vmax=2,
            x=x,
            y=y,
            is_youth=False,
        )
        self.hit_chance = max(0.0, min(1.0, hit_chance))
        self.habitat = "water"
        self.home_x = x
        self.home_y = y
        self._max_hunger = 30
        self.event_log = []

    def move(self, environment):
        self.age += 1
        self._tick_hunger()
        self.event_log.clear()
        if not self.alive:
            return False

        self._wander()
        self._try_shoot(environment)
        return True

    def _wander(self):
        target_x = self.home_x + math.sin(self.age / 75) * 18
        target_y = self.home_y + math.cos(self.age / 90) * 7
        self.place = (
            self.x + (target_x - self.x) * 0.035,
            self.y + (target_y - self.y) * 0.035,
        )

    def shoot(self, ant):
        hit = random.random() < self.hit_chance
        result = "hit" if hit else "miss"
        self.event_log.append(f"watergun fish shot {ant.name}: {result}")
        return hit

    def _try_shoot(self, environment):
        for animal in list(environment.organism_list):
            if isinstance(animal, (Ant, Ant_herd)) and animal.alive:
                if abs(animal.x - self.x) <= 190 and animal.y < self.y:
                    if self.shoot(animal):
                        animal.death("shot by watergun fish")
                        self._eat()
                    return

    def reproduce(self):
        if not self.alive or self.is_starving:
            return None
        if self.age > 30 and random.random() < 0.03:
            return WatergunFish(hit_chance=self.hit_chance, x=self.x + 12, y=self.y)
        return None

    def __repr__(self):
        state = "starving" if self.is_starving else "normal"
        return (
            f"WatergunFish(power={self.power}, "
            f"hit_chance={self.hit_chance:.0%}, age={self.age}, {state})"
        )
