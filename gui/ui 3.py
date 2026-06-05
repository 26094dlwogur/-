import tkinter as tk
import time
from PIL import Image, ImageTk


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

        image = Image.open("mangrove.png")

        image = image.resize((340, 340))

        self.tree_image = ImageTk.PhotoImage(image)

    def draw(self, camera):
        self.canvas.delete("world")

        ox = -camera.x
        oy = -camera.y

    # 하늘
        self.canvas.create_rectangle(
            0, 0, 900, 600,
            fill="#87CEEB",
            outline="",
            tags="world"
        )

    # 구름
        self.draw_cloud(ox + 100, oy + 80)
        self.draw_cloud(ox + 450, oy + 120)
        self.draw_cloud(ox + 850, oy + 70)
        self.draw_cloud(ox + 1400, oy + 90)

    # 전체 물: 먼저 깔기
        self.canvas.create_rectangle(
            ox - 10000,
            oy + 330,
            ox + 10000,
            oy + 100000,
            fill="#2f6f73",
            outline="",
            tags="world"
        )

    # 전체 아래 흙: 물 밑/지형 아래가 비지 않게 깔기
        self.canvas.create_rectangle(
            ox - 10000,
            oy + 520,
            ox + 10000,
            oy + 100000,
            fill="#5a3e2b",
            outline="",
            tags="world"
        )

    # 왼쪽 저지대 지형
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

    # 오른쪽 고지대 지형
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

    # 나무
        tree_positions = [
            (0, 400),(240, 400),
            (430, 400),
            (620, 400),
            (890, 400),
            
        ]

        for x, y in tree_positions:
            self.draw_tree(ox + x, oy + y)

    
    def draw_tree(self, x, ground_y):
        self.canvas.create_image(
            x,
            ground_y,
            image=self.tree_image,
            anchor="s",
            tags="world"
        )

    def draw_cloud(self, x, y):
        self.canvas.create_oval(
            x - 40, y,
            x + 40, y + 40,
            fill="white",
            outline="",
            tags="world"
        )

        self.canvas.create_oval(
            x, y - 20,
            x + 80, y + 40,
            fill="white",
            outline="",
            tags="world"
        )

        self.canvas.create_oval(
            x + 50, y,
            x + 130, y + 40,
            fill="white",
            outline="",
            tags="world"
        )


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
            font=("맑은 고딕", 20, "bold"),
            tags="ui_time"
        )


class MangroveSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("맹그로브 늪지 생태계")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=900,
            height=600,
            highlightthickness=0
        )
        self.canvas.pack()

        self.keys = {
            "Left": False,
            "Right": False,
            "Up": False,
            "Down": False
        }

        self.camera = Camera()
        self.background = Background(self.canvas)
        self.time_display = TimeDisplay(self.canvas)

        self.bind_keys()
        self.game_loop()

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
        self.time_display.draw()

        self.root.after(16, self.game_loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MangroveSimulation()
    app.run()