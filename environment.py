import time

try:
    from animal.ant import Ant, Ant_herd
except ImportError:
    Ant = None
    Ant_herd = None


class Environment:
    def __init__(self):
        self.is_low_tide = False
        self.day = 1
        self.organism_list = []
        self.ant_list = []
        self.ant_herd_list = []
        self.current_tick = 0
        self.ticks_per_day = 60 * 60
        self.tide_interval_seconds = 60
        self.last_tide_change = time.monotonic()
        self.use_biome_rules = True

    def add_organism(self, organism):
        self.organism_list.append(organism)

        if Ant is not None and isinstance(organism, Ant):
            self.ant_list.append(organism)
        elif Ant_herd is not None and isinstance(organism, Ant_herd):
            self.ant_list.append(organism)
            self.ant_herd_list.append(organism)

        return organism

    def remove_organism(self, organism):
        if organism in self.organism_list:
            self.organism_list.remove(organism)
        if organism in self.ant_list:
            self.ant_list.remove(organism)
        if organism in self.ant_herd_list:
            self.ant_herd_list.remove(organism)

    def change_tide(self):
        self.is_low_tide = not self.is_low_tide
        self.last_tide_change = time.monotonic()
        state = "low tide" if self.is_low_tide else "high tide"
        print(f"[environment] tide changed: {state}")

    def trigger_timelapse_destruction(self):
        print("[environment] timelapse destruction started")
        self.organism_list.clear()
        self.ant_list.clear()
        self.ant_herd_list.clear()

    def update(self):
        self.current_tick += 1

        if time.monotonic() - self.last_tide_change >= self.tide_interval_seconds:
            self.change_tide()

        if self.current_tick % self.ticks_per_day == 0:
            self.day += 1
            if self.day >= 7:
                self.trigger_timelapse_destruction()
                return False

        for organism in list(self.organism_list):
            if hasattr(organism, "update_tick"):
                organism.update_tick(self)

        for organism in list(self.organism_list):
            if hasattr(organism, "alive") and not organism.alive:
                self.remove_organism(organism)

        return True
