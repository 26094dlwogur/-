try:
    from .animal import Animal
except ImportError:
    from animal import Animal


class Ant(Animal):
    def __init__(self, x, y, v_xm, v_ym, name, is_youth=False, is_starving=False):
        super().__init__(name=name, power=1, vmax=max(abs(v_xm), abs(v_ym)), x=x, y=y)
        self.v_xm = v_xm
        self.v_ym = v_ym
        self.vx = v_xm
        self.vy = v_ym
        self.is_youth = is_youth
        self.is_starving = is_starving
        self.is_herd = False

    def call_herd(self, environment, radius):
        radius_squared = radius ** 2
        ant_list = [
            ant
            for ant in environment.ant_list
            if isinstance(ant, Ant)
            and not ant.is_youth
            and not ant.is_herd
            and (ant.x - self.x) ** 2 + (ant.y - self.y) ** 2 <= radius_squared
        ]

        if len(ant_list) < 10:
            return None

        herd = Ant_herd(
            x=self.x,
            y=self.y,
            v_xm=self.v_xm,
            v_ym=self.v_ym,
            power=self.power,
            name=f"{self.name}_herd",
            ant_list=ant_list,
        )

        environment.ant_list = [
            ant for ant in environment.ant_list if ant not in ant_list
        ]
        environment.ant_list.append(herd)

        if hasattr(environment, "ant_herd_list"):
            environment.ant_herd_list.append(herd)

        return herd


class Ant_herd(Animal):
    def __init__(self, x, y, v_xm, v_ym, power, name, ant_list):
        self.ant_list = ant_list
        self.ant_count = len(ant_list)
        herd_power = self.get_herd_power()
        super().__init__(
            name=name,
            power=herd_power,
            vmax=max(abs(v_xm), abs(v_ym)),
            x=x,
            y=y,
        )
        self.v_xm = v_xm
        self.v_ym = v_ym
        self.vx = v_xm
        self.vy = v_ym
        self.is_herd = True

    def get_herd_power(self):
        return 10 if self.ant_count >= 20 else self.ant_count * 0.5

    def update_herd_power(self):
        self.ant_count = len(self.ant_list)
        self.power = self.get_herd_power()

    def absorb_nearby_ants(self, environment, radius):
        radius_squared = radius ** 2
        nearby_ants = [
            ant
            for ant in environment.ant_list
            if isinstance(ant, Ant)
            and not ant.is_youth
            and not ant.is_herd
            and (ant.x - self.x) ** 2 + (ant.y - self.y) ** 2 <= radius_squared
        ]

        if not nearby_ants:
            return []

        self.ant_list.extend(nearby_ants)
        self.update_herd_power()
        environment.ant_list = [
            ant for ant in environment.ant_list if ant not in nearby_ants
        ]

        return nearby_ants

    def move(self, environment, radius=60):
        self.place = (self.x + self.v_xm, self.y + self.v_ym)
        return self.absorb_nearby_ants(environment, radius)


AntHerd = Ant_herd
