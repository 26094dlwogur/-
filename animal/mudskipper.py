try:
    from .animal import Animal
except ImportError:
    from animal import Animal


class Mudskipper(Animal):
    def __init__(
        self,
        power,
        place,
        name="mudskipper",
        vmax=0,
        is_hidden=False,
        is_starving=False,
        age=0,
    ):
        super().__init__(name=name, power=power, vmax=vmax)
        self.place = place
        self.is_hidden = is_hidden
        self.is_starving = is_starving
        self.age = age
        self.is_alive = True

    def reproduce(self):
        if self.is_starving:
            return None

        return Mudskipper(
            power=self.power,
            place=self.place,
            name=self.name,
            vmax=self.vmax,
            is_hidden=False,
            is_starving=False,
            age=0,
        )

    def death(self):
        self.is_alive = False
        return None

    def move(self, place):
        self.place = place
        self.is_hidden = False
        return True

    def hide(self):
        self.is_hidden = True
        return True
