import math
import sys
import time
import tkinter as tk
from pathlib import Path

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from animal.ant import Ant, Ant_herd
from animal.fish import Fish
from animal.mudskipper import Mudskipper


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.acceleration = 1.8
        self.friction = 0.88
        self.max_speed = 22.5

    def update(self, keys):
        if keys["Left"]:
            self.vx -= self.acceleration
        if keys["Right"]:
            self.vx += self.acceleration
        if keys["Up"]:
            self.vy -= self.acceleration
        if keys["Down"]:
            self.vy += self.acceleration

        self.vx *= self.friction
        self.vy *= self.friction
        self.vx = max(-self.max_speed, min(self.max_speed, self.vx))
        self.vy = max(-self.max_speed, min(self.max_speed, self.vy))
        self.x += self.vx
        self.y += self.vy


class GameObject:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, camera):
        pass


class Background(GameObject):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.tree_image = self.load_tree_image()

    def load_tree_image(self):
        image_path = PROJECT_ROOT / "mangrove.png"
        if Image is None or ImageTk is None or not image_path.exists():
            return None

        image = Image.open(image_path)
        image = image.resize((340, 340))
        return ImageTk.PhotoImage(image)

    def draw(self, camera):
        self.canvas.delete("world")
        ox = -camera.x
        oy = -camera.y

        self.canvas.create_rectangle(0, 0, 900, 600, fill="#87CEEB", outline="", tags="world")
        self.draw_cloud(ox + 100, oy + 80)
        self.draw_cloud(ox + 450, oy + 120)
        self.draw_cloud(ox + 850, oy + 70)
        self.draw_cloud(ox + 1400, oy + 90)

        self.canvas.create_rectangle(
            ox - 10000, oy + 330,
            ox + 10000, oy + 100000,
            fill="#2f6f73",
            outline="",
            tags="world"
        )
        self.canvas.create_rectangle(
            ox - 10000, oy + 520,
            ox + 10000, oy + 100000,
            fill="#5a3e2b",
            outline="",
            tags="world"
        )
        self.canvas.create_polygon(
            ox - 10000, oy + 520,
            ox + 700, oy + 520,
            ox + 900, oy + 470,
            ox + 1050, oy + 520,
            ox + 1050, oy + 100000,
            ox - 10000, oy + 100000,
            fill="#5a3e2b",
            outline="",
            tags="world",
        )
        self.canvas.create_polygon(
            ox + 1200, oy + 280,
            ox + 10000, oy + 280,
            ox + 10000, oy + 100000,
            ox + 1200, oy + 100000,
            ox + 1050, oy + 520,
            fill="#5a3e2b",
            outline="",
            tags="world"
        )

        for x, y in [(0, 400), (240, 400), (430, 400), (620, 400), (890, 400)]:
            self.draw_tree(ox + x, oy + y)

    def draw_tree(self, x, ground_y):
        if self.tree_image is not None:
            self.canvas.create_image(x, ground_y, image=self.tree_image, anchor="s", tags="world")
            return

        self.canvas.create_rectangle(
            x - 12, ground_y - 150,
            x + 12, ground_y,
            fill="#7a4f2a",
            outline="",
            tags="world"
        )
        self.canvas.create_oval(
            x - 70, ground_y - 235,
            x + 70, ground_y - 115,
            fill="#236b4b",
            outline="",
            tags="world"
        )

    def draw_cloud(self, x, y):
        self.canvas.create_oval(x - 40, y, x + 40, y + 40, fill="white", outline="", tags="world")
        self.canvas.create_oval(x, y - 20, x + 80, y + 40, fill="white", outline="", tags="world")
        self.canvas.create_oval(x + 50, y, x + 130, y + 40, fill="white", outline="", tags="world")


class TimeDisplay(GameObject):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.start_time = time.time()

    def draw(self, camera=None):
        self.canvas.delete("ui_time")
        elapsed = int(time.time() - self.start_time)
        minute = elapsed // 60
        second = elapsed % 60
        self.canvas.create_text(
            820, 30,
            text=f"{minute:02d}:{second:02d}",
            fill="white",
            font=("Arial", 20, "bold"),
            tags="ui_time"
        )


class AnimalEnvironment:
    def __init__(self):
        self.organism_list = []
        self.ant_list = []
        self.ant_herd_list = []

    def add(self, animal):
        self.organism_list.append(animal)
        if isinstance(animal, (Ant, Ant_herd)):
            self.ant_list.append(animal)
        return animal

    def sync_ant_organisms(self):
        non_ants = [
            animal
            for animal in self.organism_list
            if not isinstance(animal, (Ant, Ant_herd))
        ]
        self.organism_list = non_ants + list(self.ant_list)


class AnimalLayer(GameObject):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.environment = AnimalEnvironment()
        self.frame = 0
        self.fish_count = 0
        self.mudskipper_count = 0
        self.ant_count = 0
        self.seed_animals()

    def seed_animals(self):
        self.add_fish(Fish.PREY)
        self.add_fish(Fish.PREDATOR)
        self.add_mudskipper()

        for index in range(12):
            ant = Ant(
                x=1010 + index * 7,
                y=510 + (index % 3) * 5,
                v_xm=0.35,
                v_ym=0,
                name=f"ant_{index + 1}",
                is_youth=False,
            )
            self.environment.add(ant)
            self.ant_count += 1

        first_ant = self.environment.ant_list[0]
        first_ant.call_herd(self.environment, radius=120)
        self.environment.sync_ant_organisms()

    def add_fish(self, species=Fish.PREY):
        self.fish_count += 1
        base_x = 260 if species == Fish.PREY else 570
        base_y = 390 if species == Fish.PREY else 365
        fish = Fish(
            power=1 if species == Fish.PREY else 3,
            place=(base_x + self.fish_count * 18, base_y),
            name=f"{species}_fish_{self.fish_count}",
            vmax=2,
            species=species,
        )
        return self.environment.add(fish)

    def add_mudskipper(self):
        self.mudskipper_count += 1
        mudskipper = Mudskipper(
            power=2,
            place=(760 + self.mudskipper_count * 28, 510),
            name=f"mudskipper_{self.mudskipper_count}",
            vmax=1,
        )
        return self.environment.add(mudskipper)

    def add_ant(self):
        self.ant_count += 1
        ant = Ant(
            x=980 + (self.ant_count % 10) * 10,
            y=500 + (self.ant_count % 4) * 7,
            v_xm=0.35,
            v_ym=0,
            name=f"ant_{self.ant_count}",
            is_youth=False,
        )
        return self.environment.add(ant)

    def update(self):
        self.frame += 1

        for animal in list(self.environment.organism_list):
            if isinstance(animal, Fish):
                x, y = animal.place
                direction = 1 if animal.species == Fish.PREY else -1
                animal.move((x + 0.25 * direction, y + math.sin(self.frame / 20) * 0.08))
            elif isinstance(animal, Mudskipper) and self.frame % 160 == 0:
                if animal.is_hidden:
                    animal.move(animal.place)
                else:
                    animal.hide()

        for animal in list(self.environment.ant_list):
            if isinstance(animal, Ant_herd):
                animal.move(self.environment, radius=70)

        self.environment.sync_ant_organisms()

    def draw(self, camera):
        self.canvas.delete("animals")
        self.update()

        for animal in self.environment.organism_list:
            self.draw_animal(animal, camera)

        self.draw_panel()

    def draw_animal(self, animal, camera):
        x = animal.x - camera.x
        y = animal.y - camera.y

        if isinstance(animal, Fish):
            self.draw_fish(x, y, animal)
        elif isinstance(animal, Mudskipper):
            self.draw_mudskipper(x, y, animal)
        elif isinstance(animal, Ant_herd):
            self.draw_ant_herd(x, y, animal)
        elif isinstance(animal, Ant):
            self.draw_ant(x, y)

    def draw_fish(self, x, y, fish):
        color = "#f2c94c" if fish.species == Fish.PREY else "#d94841"
        tail_direction = -1 if fish.species == Fish.PREY else 1
        self.canvas.create_oval(x - 18, y - 9, x + 18, y + 9, fill=color, outline="", tags="animals")
        self.canvas.create_polygon(
            x - 18 * tail_direction, y,
            x - 32 * tail_direction, y - 10,
            x - 32 * tail_direction, y + 10,
            fill=color,
            outline="",
            tags="animals"
        )
        self.canvas.create_oval(
            x + 9 * tail_direction, y - 3,
            x + 13 * tail_direction, y + 1,
            fill="black",
            outline="",
            tags="animals"
        )

    def draw_mudskipper(self, x, y, mudskipper):
        body = "#8b6f47" if not mudskipper.is_hidden else "#5a3e2b"
        self.canvas.create_oval(x - 24, y - 9, x + 24, y + 9, fill=body, outline="", tags="animals")
        self.canvas.create_oval(x - 12, y - 18, x - 2, y - 8, fill="#f6e8bd", outline="", tags="animals")
        self.canvas.create_oval(x + 2, y - 18, x + 12, y - 8, fill="#f6e8bd", outline="", tags="animals")
        self.canvas.create_oval(x - 9, y - 15, x - 6, y - 12, fill="black", outline="", tags="animals")
        self.canvas.create_oval(x + 6, y - 15, x + 9, y - 12, fill="black", outline="", tags="animals")

    def draw_ant(self, x, y):
        for dx in (-7, 0, 7):
            self.canvas.create_oval(x + dx - 4, y - 4, x + dx + 4, y + 4, fill="#17110c", outline="", tags="animals")
        for dx in (-7, 0, 7):
            self.canvas.create_line(x + dx, y, x + dx - 5, y - 7, fill="#17110c", tags="animals")
            self.canvas.create_line(x + dx, y, x + dx + 5, y + 7, fill="#17110c", tags="animals")

    def draw_ant_herd(self, x, y, herd):
        radius = max(16, min(38, herd.ant_count * 1.7))
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill="#211610",
            outline="#f0c36a",
            width=2,
            tags="animals"
        )
        self.canvas.create_text(
            x, y,
            text=str(herd.ant_count),
            fill="#f7e6b2",
            font=("Arial", 12, "bold"),
            tags="animals"
        )

    def draw_panel(self):
        fish = sum(isinstance(animal, Fish) and animal.is_alive for animal in self.environment.organism_list)
        mudskippers = sum(isinstance(animal, Mudskipper) and animal.is_alive for animal in self.environment.organism_list)
        ants = sum(isinstance(animal, Ant) for animal in self.environment.ant_list)
        herds = sum(isinstance(animal, Ant_herd) for animal in self.environment.ant_list)

        self.canvas.create_rectangle(12, 12, 245, 92, fill="#0d2730", outline="", tags="animals")
        self.canvas.create_text(
            26, 28,
            anchor="w",
            text=f"Fish {fish}   Mudskipper {mudskippers}",
            fill="white",
            font=("Arial", 11, "bold"),
            tags="animals"
        )
        self.canvas.create_text(
            26, 52,
            anchor="w",
            text=f"Ants {ants}   Herds {herds}",
            fill="white",
            font=("Arial", 11, "bold"),
            tags="animals"
        )
        self.canvas.create_text(
            26, 76,
            anchor="w",
            text="Buttons: add animals",
            fill="#b7dce3",
            font=("Arial", 9),
            tags="animals"
        )


class MangroveSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mangrove Simulation")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=900, height=600, highlightthickness=0)
        self.canvas.pack()

        self.keys = {
            "Left": False,
            "Right": False,
            "Up": False,
            "Down": False,
        }

        self.camera = Camera()
        self.background = Background(self.canvas)
        self.animal_layer = AnimalLayer(self.canvas)
        self.time_display = TimeDisplay(self.canvas)

        self.create_controls()
        self.bind_keys()
        self.game_loop()

    def create_controls(self):
        controls = tk.Frame(self.root, bg="#0d2730")
        controls.place(x=12, y=100)

        tk.Button(controls, text="Fish", command=lambda: self.animal_layer.add_fish(Fish.PREY)).grid(
            row=0, column=0, padx=2, pady=2
        )
        tk.Button(controls, text="Predator", command=lambda: self.animal_layer.add_fish(Fish.PREDATOR)).grid(
            row=0, column=1, padx=2, pady=2
        )
        tk.Button(controls, text="Mudskipper", command=self.animal_layer.add_mudskipper).grid(
            row=1, column=0, padx=2, pady=2
        )
        tk.Button(controls, text="Ant", command=self.animal_layer.add_ant).grid(
            row=1, column=1, padx=2, pady=2
        )

    def bind_keys(self):
        self.root.bind("<KeyPress-Left>", lambda event: self.set_key("Left", True))
        self.root.bind("<KeyPress-Right>", lambda event: self.set_key("Right", True))
        self.root.bind("<KeyPress-Up>", lambda event: self.set_key("Up", True))
        self.root.bind("<KeyPress-Down>", lambda event: self.set_key("Down", True))
        self.root.bind("<KeyRelease-Left>", lambda event: self.set_key("Left", False))
        self.root.bind("<KeyRelease-Right>", lambda event: self.set_key("Right", False))
        self.root.bind("<KeyRelease-Up>", lambda event: self.set_key("Up", False))
        self.root.bind("<KeyRelease-Down>", lambda event: self.set_key("Down", False))

    def set_key(self, key, value):
        self.keys[key] = value

    def game_loop(self):
        self.camera.update(self.keys)
        self.background.draw(self.camera)
        self.animal_layer.draw(self.camera)
        self.time_display.draw()
        self.root.after(16, self.game_loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MangroveSimulation()
    app.run()
