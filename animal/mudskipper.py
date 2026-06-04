class Mudskipper:
    def __init__(self, power, place, is_hidden=False, is_starving=False, age=0):
        self.power = power
        self.place = place
        self.is_hidden = is_hidden
        self.is_starving = is_starving
        self.age = age

    def reproduce(self):
        if self.is_starving:
            return None

        return Mudskipper(
            power=self.power,
            place=self.place,
            is_hidden=False,
            is_starving=False,
            age=0,
        )

    def death(self):
        return None

    def move(self, place):
        self.place = place
        self.is_hidden = False
        return True

    def hide(self):
        self.is_hidden = True
        return True
