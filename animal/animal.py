import inspect
import math


class Animal:
    TICKS_PER_SECOND = 60

    def __init__(
        self,
        name,
        power,
        vmax=0,
        x=0.0,
        y=0.0,
        is_youth=True,
        is_starving=False,
    ):
        self.name = name
        self.power = power
        self.vmax = vmax
        self.place = (x, y)
        self.vx = 0.0
        self.vy = 0.0
        self.is_youth = is_youth
        self.is_starving = is_starving
        self.age = 0
        self.is_alive = True
        self._max_hunger = 100
        self._hunger = 0

    @property
    def alive(self):
        return self.is_alive

    @alive.setter
    def alive(self, value):
        self.is_alive = value

    @property
    def x(self):
        return self.place[0]

    @property
    def y(self):
        return self.place[1]

    @property
    def px(self):
        return self.x

    @px.setter
    def px(self, value):
        self.place = (value, self.y)

    @property
    def py(self):
        return self.y

    @py.setter
    def py(self, value):
        self.place = (self.x, value)

    def get_distance(self, partner):
        return math.hypot(self.x - partner.x, self.y - partner.y)

    def update_status(self):
        pass

    def calculate_velocity(self):
        pass

    def move(self):
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > self.vmax:
            ratio = self.vmax / current_speed
            self.vx *= ratio
            self.vy *= ratio

        self.place = (
            self.x + self.vx / self.TICKS_PER_SECOND,
            self.y + self.vy / self.TICKS_PER_SECOND,
        )

    def update_tick(self, environment=None):
        self.update_status()
        self.calculate_velocity()

        parameters = inspect.signature(self.move).parameters
        parameter_names = list(parameters)
        if (
            environment is not None
            and parameter_names
            and parameter_names[0] in ("environment", "env")
        ):
            self.move(environment)
        elif not parameter_names:
            self.move()

    def _tick_hunger(self):
        self._hunger += 1
        if self._hunger >= self._max_hunger:
            self.is_starving = True

    def _eat(self):
        self._hunger = 0
        self.is_starving = False

    def check_reproduce_condition(self, partner=None):
        return self.is_alive and not self.is_starving

    def reproduce(self, partner=None):
        return None

    def death(self, reason=None):
        self.is_alive = False
        if reason:
            print(f"[{self.name}] died: {reason}")
        return None
