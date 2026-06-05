try:
    from .animal import Animal
except ImportError:
    from animal import Animal


class Fish(Animal):
    PREY = "prey"
    PREDATOR = "predator"
    SPECIES = (PREY, PREDATOR)

    def __init__(
        self,
        power,
        place,
        name="fish",
        vmax=0,
        species=PREY,
        is_youth=False,
        is_starving=False,
        age=0,
    ):
        if species not in self.SPECIES:
            raise ValueError("species must be 'prey' or 'predator'")

        super().__init__(name=name, power=power, vmax=vmax)
        self.place = place
        self.species = species
        self.is_youth = is_youth
        self.is_starving = is_starving
        self.age = age
        self.is_alive = True

    def reproduce(self):
        if self.is_starving:
            return None

        return Fish(
            power=self.power,
            place=self.place,
            species=self.species,
            is_youth=True,
            is_starving=False,
            age=0,
        )

    def death(self):
        self.is_alive = False
        return None

    def move(self, place):
        self.place = place
        return True

    def can_eat(self, other):
        return (
            self.is_alive
            and self.species == self.PREDATOR
            and isinstance(other, Fish)
            and other.is_alive
            and other.species == self.PREY
            and self.place == other.place
        )

    def eat(self, other):
        if not self.can_eat(other):
            return False

        other.death()
        self.is_starving = False
        return True
