import math
import random
import sys
import time
import tkinter as tk
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    Image = None
    ImageDraw = None
    ImageTk = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from animal import Ant, Bird, Crab, Fish, Mudskipper, WatergunFish
from environment import Environment


TREE_BRANCH_PATH = [
    (-120, 326),
    (70, 306),
    (250, 286),
    (445, 298),
    (625, 288),
    (770, 268),
    (900, 250),
    (1040, 230),
    (1165, 216),
]


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.acceleration = 1.8
        self.friction = 0.88
        self.max_speed = 22.5
        self.min_x = -700
        self.max_x = 1600
        self.min_y = -1500
        self.max_y = 2000
        self.bounce = 1.5

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

        if self.x < self.min_x:
            self.x = self.min_x
            self.vx = -self.vx * self.bounce
        if self.x > self.max_x:
            self.x = self.max_x
            self.vx = -self.vx * self.bounce
        if self.y < self.min_y:
            self.y = self.min_y
            self.vy = -self.vy * self.bounce
        if self.y > self.max_y:
            self.y = self.max_y
            self.vy = -self.vy * self.bounce


class GameObject:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, camera):
        pass


class Background(GameObject):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.tree_images = self.create_tree_images()

    def create_tree_images(self):
        if Image is None or ImageDraw is None or ImageTk is None:
            return {}

        return {
            "back": self.create_tree_sprite(170, 300, 0.82),
            "mid": self.create_tree_sprite(250, 430, 1.08),
            "front": self.create_tree_sprite(330, 560, 1.35),
        }

    def draw(self, camera, is_low_tide=False):
        self.canvas.delete("world")
        ox = -camera.x
        oy = -camera.y

        self.canvas.create_rectangle(0, 0, 900, 600, fill="#243f3c", outline="", tags="world")
        self.draw_sky()
        self.draw_mist(ox, oy)
        self.draw_distant_forest(ox, oy)
        self.draw_water(ox, oy, is_low_tide)
        self.draw_mud_banks(ox, oy)
        self.draw_back_tree_line(ox, oy)
        self.draw_mid_tree_line(ox, oy)
        self.draw_hanging_roots(ox, oy)
        self.draw_prop_roots(ox, oy)
        self.draw_tree_branches(ox, oy)
        self.draw_reeds(ox, oy)
        self.draw_foreground_leaves(ox, oy)

    def draw_sky(self):
        bands = [
            (0, 80, "#243f3c"),
            (80, 180, "#345850"),
            (180, 290, "#58715b"),
            (290, 350, "#75815d"),
        ]
        for y1, y2, color in bands:
            self.canvas.create_rectangle(0, y1, 900, y2, fill=color, outline="", tags="world")

    def draw_mist(self, ox, oy):
        for y, color in [(95, "#6f897f"), (155, "#829682"), (245, "#9b9c76")]:
            self.canvas.create_rectangle(0, oy + y, 900, oy + y + 28, fill=color, outline="", stipple="gray25", tags="world")
        for x in range(-160, 1120, 260):
            self.draw_cloud(ox + x, oy + 108, "#d8dec7", 0.72)

    def draw_distant_forest(self, ox, oy):
        self.canvas.create_rectangle(0, oy + 280, 900, oy + 360, fill="#274638", outline="", tags="world")
        for x in range(-120, 1110, 54):
            height = 84 + ((x // 54) % 4) * 18
            crown = "#1f3b2f" if (x // 54) % 2 else "#2a4c38"
            self.canvas.create_polygon(
                ox + x - 52, oy + 322,
                ox + x - 18, oy + 322 - height,
                ox + x + 18, oy + 322 - height - 18,
                ox + x + 56, oy + 322,
                fill=crown,
                outline="",
                smooth=True,
                tags="world",
            )
            self.canvas.create_line(
                ox + x + 2, oy + 290,
                ox + x + 2, oy + 405,
                fill="#1b2e25",
                width=3,
                tags="world"
            )
        self.canvas.create_rectangle(0, oy + 340, 900, oy + 362, fill="#7f8360", outline="", stipple="gray50", tags="world")

    def draw_water(self, ox, oy, is_low_tide=False):
        if is_low_tide:
            self.canvas.create_polygon(
                ox - 10000, oy + 518,
                ox + 220, oy + 522,
                ox + 430, oy + 508,
                ox + 650, oy + 520,
                ox + 820, oy + 498,
                ox + 1050, oy + 470,
                ox + 10000, oy + 462,
                ox + 10000, oy + 532,
                ox - 10000, oy + 548,
                fill="#4f9fa0",
                outline="",
                stipple="gray25",
                tags="world",
            )
            for points in [
                [(150, 526), (260, 520), (378, 528), (430, 540)],
                [(465, 505), (585, 512), (705, 504), (765, 512)],
                [(790, 492), (910, 478), (1065, 466), (1160, 468)],
            ]:
                coords = []
                for x, y in points:
                    coords.extend([ox + x, oy + y])
                self.canvas.create_line(*coords, fill="#b7e6df", width=2, smooth=True, tags="world")
            return

        surface_y = 378
        self.canvas.create_rectangle(ox - 10000, oy + surface_y, ox + 10000, oy + 545, fill="#3f8f91", outline="", tags="world")
        self.canvas.create_line(0, oy + surface_y, 900, oy + surface_y, fill="#b7e6df", width=2, tags="world")

    def draw_mud_banks(self, ox, oy):
        self.canvas.create_polygon(
            ox - 10000, oy + 548,
            ox + 80, oy + 540,
            ox + 235, oy + 522,
            ox + 360, oy + 532,
            ox + 520, oy + 562,
            ox + 660, oy + 548,
            ox + 805, oy + 510,
            ox + 960, oy + 464,
            ox + 1160, oy + 408,
            ox + 10000, oy + 392,
            ox + 10000, oy + 100000,
            ox - 10000, oy + 100000,
            fill="#5a3e2b",
            outline="",
            tags="world",
        )
        self.canvas.create_polygon(
            ox - 10000, oy + 535,
            ox + 130, oy + 530,
            ox + 270, oy + 512,
            ox + 430, oy + 546,
            ox + 600, oy + 558,
            ox + 760, oy + 512,
            ox + 930, oy + 462,
            ox + 1120, oy + 418,
            ox + 10000, oy + 405,
            ox + 10000, oy + 100000,
            ox - 10000, oy + 100000,
            fill="#4a3023",
            outline="",
            tags="world",
        )
        self.canvas.create_polygon(
            ox - 100, oy + 556,
            ox + 90, oy + 520,
            ox + 260, oy + 528,
            ox + 365, oy + 568,
            ox + 215, oy + 592,
            ox - 100, oy + 590,
            fill="#61432d",
            outline="",
            tags="world",
        )
        for points, color, width in [
            ([(0, 542), (190, 528), (372, 546), (590, 558), (775, 512), (900, 474)], "#765438", 2),
            ([(0, 565), (180, 552), (390, 570), (610, 582), (800, 540), (930, 496)], "#37261e", 2),
            ([(650, 548), (760, 510), (900, 464), (1050, 424), (900, 444)], "#75583a", 3),
            ([(735, 534), (840, 500), (990, 454), (1140, 416)], "#39271f", 2),
        ]:
            coords = []
            for x, y in points:
                coords.extend([ox + x, oy + y])
            self.canvas.create_line(*coords, fill=color, width=width, smooth=True, tags="world")
        for x in range(-70, 1010, 95):
            shore_y = 552 - max(0, x - 650) * 0.16
            self.canvas.create_oval(ox + x, oy + shore_y, ox + x + 40, oy + shore_y + 8, fill="#725b39", outline="", tags="world")
            self.canvas.create_oval(ox + x + 24, oy + shore_y + 27, ox + x + 40, oy + shore_y + 32, fill="#30231d", outline="", tags="world")

    def draw_back_tree_line(self, ox, oy):
        for x, size in [
            (-230, "back"),
            (-80, "back"),
            (70, "back"),
            (220, "back"),
            (380, "back"),
            (535, "back"),
            (700, "back"),
            (850, "back"),
            (1015, "back"),
        ]:
            y = self.mud_floor_y(x, layer="back")
            self.draw_tree(ox + x, oy + y, size)

    def draw_mid_tree_line(self, ox, oy):
        for x, y, size in self.mid_tree_specs():
            self.draw_tree(ox + x, oy + y, size)

    def mid_tree_specs(self):
        return [
            (x, self.mud_floor_y(x, layer="front"), size)
            for x, size in [
                (-290, "mid"),
                (-120, "front"),
                (70, "mid"),
                (250, "front"),
                (445, "mid"),
                (625, "front"),
                (770, "mid"),
                (900, "front"),
                (1040, "mid"),
                (1165, "front"),
            ]
        ]

    def mud_floor_y(self, x, layer="front"):
        points = [
            (-300, 570),
            (-80, 560),
            (160, 560),
            (360, 572),
            (600, 562),
            (760, 525),
            (930, 475),
            (1120, 420),
            (1250, 405),
        ]
        if x <= points[0][0]:
            y = points[0][1]
        elif x >= points[-1][0]:
            y = points[-1][1]
        else:
            y = points[-1][1]
            for (x0, y0), (x1, y1) in zip(points, points[1:]):
                if x0 <= x <= x1:
                    ratio = (x - x0) / (x1 - x0)
                    y = y0 + (y1 - y0) * ratio
                    break

        return y

    def draw_tree(self, x, ground_y, size="mid"):
        shadow_width = {"back": 46, "mid": 66, "front": 86}.get(size, 66)
        self.canvas.create_oval(
            x - shadow_width,
            ground_y - 5,
            x + shadow_width,
            ground_y + 7,
            fill="#2f2119",
            outline="",
            stipple="gray50",
            tags="world"
        )
        image = self.tree_images.get(size)
        if image is not None:
            self.canvas.create_image(x, ground_y, image=image, anchor="s", tags="world")
            return

        self.canvas.create_rectangle(x - 14, ground_y - 250, x + 14, ground_y, fill="#7a4f2a", outline="", tags="world")
        self.canvas.create_oval(x - 82, ground_y - 350, x + 82, ground_y - 205, fill="#236b4b", outline="", tags="world")

    def draw_tree_branches(self, ox, oy):
        for start, end in zip(TREE_BRANCH_PATH, TREE_BRANCH_PATH[1:]):
            x0, y0 = start
            x1, y1 = end
            mid_x = (x0 + x1) / 2
            mid_y = min(y0, y1) - 18 + math.sin((x0 + x1) * 0.01) * 8
            coords = [ox + x0, oy + y0, ox + mid_x, oy + mid_y, ox + x1, oy + y1]
            width = 13 if x0 < 650 else 11
            self.canvas.create_line(
                *coords,
                fill="#24170f",
                width=width + 5,
                smooth=True,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
                tags="world",
            )
            self.canvas.create_line(
                *coords,
                fill="#604020",
                width=width,
                smooth=True,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
                tags="world",
            )
            self.canvas.create_line(
                *coords,
                fill="#9a6a34",
                width=2,
                smooth=True,
                capstyle=tk.ROUND,
                tags="world",
            )

        for x, y in TREE_BRANCH_PATH:
            self.canvas.create_oval(ox + x - 13, oy + y - 9, ox + x + 13, oy + y + 9, fill="#3a2416", outline="", tags="world")
            self.canvas.create_oval(ox + x - 7, oy + y - 5, ox + x + 8, oy + y + 5, fill="#6d4828", outline="", tags="world")

        for branch_x, branch_y, end_x, end_y, width in [
            (70, 306, 18, 250, 8),
            (250, 286, 310, 238, 7),
            (445, 298, 500, 244, 8),
            (625, 288, 570, 238, 7),
            (770, 268, 825, 220, 7),
            (1040, 230, 1105, 190, 6),
        ]:
            self.canvas.create_line(
                ox + branch_x, oy + branch_y,
                ox + (branch_x + end_x) / 2, oy + min(branch_y, end_y) - 10,
                ox + end_x, oy + end_y,
                fill="#2a1c13",
                width=width + 3,
                smooth=True,
                capstyle=tk.ROUND,
                tags="world",
            )
            self.canvas.create_line(
                ox + branch_x, oy + branch_y,
                ox + (branch_x + end_x) / 2, oy + min(branch_y, end_y) - 10,
                ox + end_x, oy + end_y,
                fill="#704a27",
                width=width,
                smooth=True,
                capstyle=tk.ROUND,
                tags="world",
            )

    def create_tree_sprite(self, width, height, scale):
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        cx = width // 2
        base = height - 1
        trunk_top = int(height * 0.45)
        trunk_color = (72, 57, 34, 255)
        root_color = (48, 39, 25, 255)

        draw.line([(cx - 4 * scale, base), (cx - 2 * scale, trunk_top)], fill=trunk_color, width=max(8, int(11 * scale)))
        draw.line([(cx + 5 * scale, base), (cx + 2 * scale, trunk_top + 20 * scale)], fill=(56, 43, 27, 255), width=max(5, int(7 * scale)))

        for spread in [-0.34, -0.22, -0.11, 0.0, 0.12, 0.24, 0.36]:
            end_x = cx + int(width * spread)
            mid_x = cx + int(width * spread * 0.42)
            width_px = max(2, int(4 * scale * (1 - abs(spread) * 0.8)))
            draw.line(
                [(cx, base - 42 * scale), (mid_x, base - 18 * scale), (end_x, base)],
                fill=root_color,
                width=width_px,
            )
            draw.ellipse(
                (
                    end_x - 2 * scale,
                    base - 1 * scale,
                    end_x + 2 * scale,
                    base + 1,
                ),
                fill=root_color,
            )

        leaf_colors = [
            (28, 65, 40, 245),
            (43, 90, 50, 245),
            (76, 115, 58, 238),
            (114, 138, 67, 225),
        ]
        clusters = [
            (-0.24, 0.33, 0.27),
            (-0.10, 0.23, 0.29),
            (0.10, 0.23, 0.3),
            (0.24, 0.33, 0.27),
            (0.00, 0.14, 0.25),
            (-0.30, 0.44, 0.21),
            (0.30, 0.44, 0.21),
        ]
        branch_color = (55, 43, 25, 255)
        for index, (x_ratio, y_ratio, radius_ratio) in enumerate(clusters):
            lx = cx + int(width * x_ratio)
            ly = int(height * y_ratio)
            start_y = max(trunk_top, ly + int(height * 0.20))
            joint_x = cx + int((lx - cx) * 0.38)
            joint_y = ly + int(height * 0.12)
            branch_width = max(2, int((5 - min(index, 4) * 0.35) * scale))
            draw.line(
                [(cx, start_y), (joint_x, joint_y), (lx, ly)],
                fill=branch_color,
                width=branch_width,
                joint="curve",
            )

        for index, (x_ratio, y_ratio, radius_ratio) in enumerate(clusters):
            color = leaf_colors[index % len(leaf_colors)]
            lx = cx + int(width * x_ratio)
            ly = int(height * y_ratio)
            rx = int(width * radius_ratio)
            ry = int(height * radius_ratio * 0.58)
            draw.ellipse((lx - rx, ly - ry, lx + rx, ly + ry), fill=color)
            draw.ellipse((lx - rx // 2, ly - ry - 8 * scale, lx + rx // 2, ly + ry // 2), fill=leaf_colors[(index + 1) % len(leaf_colors)])

        canopy_fill = (38, 78, 43, 235)
        draw.ellipse(
            (
                cx - int(width * 0.24),
                int(height * 0.24),
                cx + int(width * 0.24),
                int(height * 0.52),
            ),
            fill=canopy_fill,
        )

        vine_color = (46, 42, 22, 210)
        for index, x_ratio in enumerate([-0.34, -0.22, -0.08, 0.08, 0.23, 0.35]):
            vx = cx + int(width * x_ratio)
            start = int(height * (0.28 + (index % 3) * 0.035))
            end = int(height * (0.55 + (index % 4) * 0.05))
            draw.line([(vx, start), (vx + (index % 2) * 5 - 2, end)], fill=vine_color, width=max(1, int(2 * scale)))

        return ImageTk.PhotoImage(image)

    def draw_prop_roots(self, ox, oy):
        for x, y, size in self.mid_tree_specs():
            self.draw_root_cluster(ox + x, oy + y, size)

    def draw_root_cluster(self, x, y, size):
        scale = {"back": 0.72, "mid": 0.9, "front": 1.08}.get(size, 0.9)
        root_start_offset = {"back": 54, "mid": 70, "front": 88}.get(size, 70)
        root_color = "#2b2418"
        spreads = [-96, -68, -42, -16, 16, 42, 68, 96]
        trunk_base_y = y - root_start_offset
        ground_y = y
        for index, spread in enumerate(spreads):
            width = max(2, int(4 * scale - abs(index - 3.5) * 0.2))
            shoulder_y = trunk_base_y + (20 + (index % 2) * 10) * scale
            knee_y = ground_y - (34 + (index % 4) * 9) * scale
            foot_y = ground_y
            drift = (-7, 4, -3, 8, -5, 6, -4, 5)[index]
            foot_x = x + spread * scale
            self.canvas.create_line(
                x, trunk_base_y,
                x + (spread * 0.22 + drift) * scale, shoulder_y,
                x + (spread * 0.58 - drift * 0.4) * scale, knee_y,
                foot_x, foot_y,
                fill=root_color,
                width=width,
                smooth=True,
                tags="world"
            )
            self.canvas.create_oval(
                foot_x - 3 * scale,
                foot_y - 2,
                foot_x + 3 * scale,
                foot_y + 2,
                fill=root_color,
                outline="",
                tags="world"
            )
            if index in (1, 3, 5):
                self.canvas.create_line(
                    x + spread * 0.55 * scale, knee_y,
                    foot_x, foot_y,
                    fill="#1d1811",
                    width=1,
                    smooth=True,
                    tags="world"
                )

    def draw_hanging_roots(self, ox, oy):
        for x in range(-220, 1240, 42):
            top = 246 + ((x // 34) % 6) * 17
            length = 34 + ((x // 34) % 5) * 9
            self.canvas.create_line(
                ox + x, oy + top,
                ox + x + ((x // 34) % 3 - 1) * 7, oy + top + length,
                fill="#41542a",
                width=1,
                smooth=True,
                tags="world"
            )

    def draw_reeds(self, ox, oy):
        for x in range(-90, 1040, 30):
            height = 24 + ((x // 30) % 5) * 9
            lean = -10 + ((x // 30) % 4) * 5
            self.canvas.create_line(ox + x, oy + 535, ox + x + lean, oy + 535 - height, fill="#243d24", width=2, tags="world")
            self.canvas.create_line(ox + x + 4, oy + 536, ox + x + 4 - lean, oy + 542 - height, fill="#506b31", width=1, tags="world")
            if (x // 30) % 3 == 0:
                self.canvas.create_oval(ox + x + lean - 4, oy + 531 - height, ox + x + lean + 4, oy + 542 - height, fill="#806b36", outline="", tags="world")

    def draw_foreground_leaves(self, ox, oy):
        for x in range(-120, 1020, 95):
            y = 20 + ((x // 95) % 4) * 18
            self.canvas.create_oval(ox + x - 70, oy + y - 32, ox + x + 84, oy + y + 45, fill="#173121", outline="", stipple="gray50", tags="world")
            self.canvas.create_oval(ox + x - 34, oy + y - 46, ox + x + 62, oy + y + 18, fill="#274a2f", outline="", stipple="gray50", tags="world")

    def draw_cloud(self, x, y, color="#dfe8d5", scale=1.0):
        self.canvas.create_oval(x - 44 * scale, y, x + 44 * scale, y + 34 * scale, fill=color, outline="", stipple="gray50", tags="world")
        self.canvas.create_oval(x - 4 * scale, y - 18 * scale, x + 82 * scale, y + 36 * scale, fill=color, outline="", stipple="gray50", tags="world")
        self.canvas.create_oval(x + 50 * scale, y, x + 132 * scale, y + 34 * scale, fill=color, outline="", stipple="gray50", tags="world")


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

    def hide(self):
        self.canvas.delete("ui_time")


class AnimalLayer(GameObject):
    POOL_ZONE = (140, 470, 430, 565)
    CHANNEL_ZONE = (430, 360, 760, 545)
    MUD_WATER_ZONE = (760, 430, 1160, 565)
    SEA_ESCAPE_X = 1240
    LOW_TIDE_REFUGES = {
        "pool": (285, 514),
        "channel": (595, 448),
        "mud_water": (910, 493),
    }

    def __init__(self, canvas):
        super().__init__(canvas)
        self.environment = Environment()
        self.frame = 0
        self.was_low_tide = self.environment.is_low_tide
        self.sea_fish = []
        self.counts = {
            "fish": 0,
            "predator": 0,
            "mudskipper": 0,
            "watergun": 0,
            "bird": 0,
            "crab": 0,
            "ant": 0,
        }
        self.seed_animals()

    def seed_animals(self):
        for _ in range(6):
            self.add_fish(Fish.PREY)
        for _ in range(2):
            self.add_fish(Fish.PREDATOR)
        self.add_mudskipper()
        self.add_watergun_fish()
        self.add_bird()
        self.add_crab()
        for _ in range(6):
            self.add_ant()

    def add_fish(self, species=Fish.PREY, place=None, is_youth=False, power=None):
        key = "fish" if species == Fish.PREY else "predator"
        self.counts[key] += 1
        if place is not None:
            x, y = place
        elif species == Fish.PREY:
            nursery_slots = [(260, 396), (350, 408), (500, 386), (635, 404), (835, 462), (990, 448)]
            x, y = nursery_slots[(self.counts[key] - 1) % len(nursery_slots)]
            x += (self.counts[key] // len(nursery_slots)) * 18
        else:
            predator_slots = [(555, 382), (675, 398)]
            x, y = predator_slots[(self.counts[key] - 1) % len(predator_slots)]
            x += (self.counts[key] // len(predator_slots)) * 16
        fish = Fish(
            power=power if power is not None else (1 if species == Fish.PREY else 3),
            place=(x, y),
            name=key,
            vmax=2,
            species=species,
            is_youth=is_youth,
        )
        return self.environment.add_organism(fish)

    def add_mudskipper(self):
        self.counts["mudskipper"] += 1
        animal = Mudskipper(
            power=2,
            place=(720 + self.counts["mudskipper"] * 34, 510),
            name="mudskipper",
            vmax=1,
        )
        return self.environment.add_organism(animal)

    def add_watergun_fish(self):
        self.counts["watergun"] += 1
        animal = WatergunFish(
            hit_chance=0.6,
            x=390 + self.counts["watergun"] * 28,
            y=370,
        )
        return self.environment.add_organism(animal)

    def add_bird(self):
        self.counts["bird"] += 1
        animal = Bird(x=170 + self.counts["bird"] * 45, y=105)
        return self.environment.add_organism(animal)

    def add_crab(self):
        self.counts["crab"] += 1
        animal = Crab(x=830 + self.counts["crab"] * 26, y=545)
        return self.environment.add_organism(animal)

    def add_ant(self):
        self.counts["ant"] += 1
        animal = Ant(
            x=960 + (self.counts["ant"] % 12) * 13,
            y=498 + (self.counts["ant"] % 4) * 7,
            v_xm=0.18,
            v_ym=0,
            name="ant",
            is_youth=False,
        )
        return self.environment.add_organism(animal)

    def toggle_tide(self):
        self.environment.change_tide()

    def update(self):
        self.frame += 1
        self.restore_fish_if_tide_returns()
        self.animate_simple_animals()
        self.environment.update()
        self.move_branch_walkers()
        self.restore_fish_if_tide_returns()

    def restore_fish_if_tide_returns(self):
        if self.was_low_tide and not self.environment.is_low_tide:
            self.restore_sea_fish()
        self.was_low_tide = self.environment.is_low_tide

    def restore_sea_fish(self):
        for index, fish in enumerate(list(self.sea_fish)):
            fish.is_alive = True
            fish.is_youth = False
            fish.is_starving = False
            fish.escape_fade = 0.2
            fish.returning_from_sea = True
            fish.swim_vx = 0.0
            fish.swim_vy = 0.0
            fish.draw_x = 1080 + index * 34
            fish.draw_y = 424 + (index % 3) * 12
            fish.move((1080 + index * 34, 424 + (index % 3) * 12))
            self.environment.add_organism(fish)
        self.sea_fish.clear()

    def animate_simple_animals(self):
        for animal in list(self.environment.organism_list):
            if not self.is_alive(animal):
                continue
            if isinstance(animal, Fish):
                self.move_fish_for_tide(animal)
            elif isinstance(animal, Mudskipper):
                self.move_mudskipper_for_tide(animal)
        self.apply_biome_interactions()
        self.apply_basic_life_cycles()
        self.remove_dead_animals()

    def move_branch_walkers(self):
        for animal in list(self.environment.organism_list):
            if not self.is_alive(animal):
                continue
            if isinstance(animal, Ant):
                self.move_on_elevated_branch(animal, speed=0.74, lane=-5)
            elif isinstance(animal, Crab):
                animal.is_hidden = False
                self.move_on_elevated_branch(animal, speed=1.65, lane=7)

    def move_on_elevated_branch(self, animal, speed, lane):
        target_index = getattr(animal, "branch_target_index", None)
        if target_index is None:
            target_index = self.nearest_branch_point_index(animal.x, animal.y)
            animal.branch_target_index = target_index
            animal.branch_direction = 1 if target_index < len(TREE_BRANCH_PATH) - 1 else -1

        target_x, target_y = TREE_BRANCH_PATH[target_index]
        target_y += lane
        next_x, next_y = self.move_point_toward(animal.x, animal.y, target_x, target_y, speed)
        animal.place = (next_x, next_y)

        if math.hypot(animal.x - target_x, animal.y - target_y) > speed + 0.2:
            return

        direction = getattr(animal, "branch_direction", 1)
        next_index = target_index + direction
        if next_index >= len(TREE_BRANCH_PATH):
            next_index = len(TREE_BRANCH_PATH) - 2
            direction = -1
        elif next_index < 0:
            next_index = 1
            direction = 1

        animal.branch_target_index = next_index
        animal.branch_direction = direction

    def nearest_branch_point_index(self, x, y):
        return min(
            range(len(TREE_BRANCH_PATH)),
            key=lambda index: math.hypot(TREE_BRANCH_PATH[index][0] - x, TREE_BRANCH_PATH[index][1] - y),
        )

    def move_fish_for_tide(self, fish):
        if self.environment.is_low_tide:
            if hasattr(fish, "returning_from_sea"):
                del fish.returning_from_sea
            if fish.species == Fish.PREY and not fish.is_youth:
                self.move_adult_fish_to_sea(fish)
                return

            zone = self.fish_low_tide_zone(fish)
            target_x, target_y = self.fish_low_tide_target(fish, zone)
            speed = 0.45 if fish.species == Fish.PREY else 0.62
            next_x, next_y = self.smooth_swim_toward(fish, target_x, target_y, speed, turn=0.055)
            fish.move(self.clamp_refuge_entry(next_x, next_y, zone, margin=16))
            return

        if getattr(fish, "returning_from_sea", False):
            self.move_returning_fish(fish)
            return
        if hasattr(fish, "escape_fade"):
            fish.escape_fade = 1.0
        phase_offset = getattr(fish, "swim_phase", None)
        if phase_offset is None:
            phase_offset = (fish.x * 0.037 + fish.y * 0.019) % (math.pi * 2)
            fish.swim_phase = phase_offset
            fish.swim_vx = 0.0
            fish.swim_vy = 0.0
        if fish.species == Fish.PREY:
            if not hasattr(fish, "_patrol_cx"):
                fish._patrol_cx = max(240, min(660, fish.x))
            target_x = fish._patrol_cx + math.sin(self.frame * 0.016 + phase_offset) * 60
            target_y = 392 + math.sin(self.frame * 0.024 + phase_offset * 1.4) * 12
            fish.move(self.smooth_swim_toward(fish, target_x, target_y, 0.28, turn=0.048))
        else:
            if not hasattr(fish, "_patrol_cx"):
                fish._patrol_cx = max(480, min(710, fish.x))
            target_x = fish._patrol_cx + math.sin(self.frame * 0.013 + phase_offset) * 48
            target_y = 376 + math.sin(self.frame * 0.02 + phase_offset * 1.2) * 10
            fish.move(self.smooth_swim_toward(fish, target_x, target_y, 0.32, turn=0.052))
        if fish.species == Fish.PREY and self.frame % 120 == 0:
            fish.age += 1
            fish.power = min(fish.power + 0.15, 3)
            if fish.age >= 3:
                fish.is_youth = False

    def fish_low_tide_zone(self, fish):
        if fish.species == Fish.PREDATOR:
            return self.CHANNEL_ZONE
        if fish.x < self.CHANNEL_ZONE[0]:
            return self.POOL_ZONE
        if fish.x < self.CHANNEL_ZONE[2]:
            return self.CHANNEL_ZONE
        return self.MUD_WATER_ZONE

    def fish_low_tide_target(self, fish, zone):
        if zone == self.POOL_ZONE:
            target_x, target_y = self.LOW_TIDE_REFUGES["pool"]
        elif zone == self.CHANNEL_ZONE:
            target_x, target_y = self.LOW_TIDE_REFUGES["channel"]
        else:
            target_x, target_y = self.LOW_TIDE_REFUGES["mud_water"]

        offset = getattr(fish, "refuge_offset", None)
        if offset is None:
            offset = (
                math.sin(fish.x * 0.071 + fish.y * 0.019) * 32,
                math.cos(fish.x * 0.047 + fish.y * 0.031) * 13,
            )
            fish.refuge_offset = offset

        drift_x = 0
        drift_y = 0
        return target_x + offset[0] + drift_x, target_y + offset[1] + drift_y

    def move_adult_fish_to_sea(self, fish):
        fade = getattr(fish, "escape_fade", 1.0)
        target_y = 468
        next_x, next_y = self.smooth_swim_toward(fish, self.SEA_ESCAPE_X + 40, target_y, 0.9, turn=0.035)
        fish.escape_fade = max(0, fade - 0.006)
        fish.move((next_x, next_y))
        if fish.escape_fade <= 0 or fish.x >= self.SEA_ESCAPE_X:
            self.send_fish_to_sea(fish)

    def send_fish_to_sea(self, fish):
        fish.escape_fade = 0
        fish.swim_vx = 0.0
        fish.swim_vy = 0.0
        fish.draw_x = fish.x
        fish.draw_y = fish.y
        self.environment.remove_organism(fish)
        if fish not in self.sea_fish:
            self.sea_fish.append(fish)

    def move_returning_fish(self, fish):
        fade = min(1.0, getattr(fish, "escape_fade", 0.2) + 0.012)
        target_y = 398
        next_x, next_y = self.smooth_swim_toward(fish, 650, target_y, 0.72, turn=0.035)
        fish.escape_fade = fade
        fish.move((next_x, next_y))
        if fish.x <= 700 or fade >= 1.0:
            fish.escape_fade = 1.0
            del fish.returning_from_sea

    def move_mudskipper_for_tide(self, mudskipper):
        if self.environment.is_low_tide:
            mudskipper.is_hidden = False
            target = getattr(mudskipper, "_wander_target", None)
            if target is None or math.hypot(mudskipper.x - target[0], mudskipper.y - target[1]) < 5:
                x0, y0, x1, y1 = self.MUD_WATER_ZONE
                mudskipper._wander_target = (
                    random.uniform(x0 + 14, x1 - 14),
                    random.uniform(y0 + 14, y1 - 14),
                )
            tx, ty = mudskipper._wander_target
            next_x, next_y = self.move_point_toward(mudskipper.x, mudskipper.y, tx, ty, 0.55)
            mudskipper.move(self.clamp_to_zone(next_x, next_y, self.MUD_WATER_ZONE, margin=12))
            return

        if self.frame % 160 == 0:
            mudskipper.hide()

    def move_point_toward(self, x, y, target_x, target_y, speed):
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        if distance <= speed or distance == 0:
            return target_x, target_y
        ease_speed = min(speed, max(0.08, distance * 0.035))
        return x + dx / distance * ease_speed, y + dy / distance * ease_speed

    def ensure_fish_motion(self, fish):
        phase = getattr(fish, "swim_phase", None)
        if phase is None:
            phase = (fish.x * 0.037 + fish.y * 0.019) % (math.pi * 2)
            fish.swim_phase = phase
            fish.swim_vx = 0.0
            fish.swim_vy = 0.0
        return phase

    def smooth_swim_toward(self, fish, target_x, target_y, max_speed, turn=0.05):
        self.ensure_fish_motion(fish)
        dx = target_x - fish.x
        dy = target_y - fish.y
        distance = math.hypot(dx, dy)
        if distance < 0.001:
            desired_vx = 0.0
            desired_vy = 0.0
        else:
            speed = min(max_speed, max(0.04, distance * 0.025))
            desired_vx = dx / distance * speed
            desired_vy = dy / distance * speed

        fish.swim_vx += (desired_vx - fish.swim_vx) * turn
        fish.swim_vy += (desired_vy - fish.swim_vy) * turn
        if abs(fish.swim_vx) < 0.001:
            fish.swim_vx = 0.0
        if abs(fish.swim_vy) < 0.001:
            fish.swim_vy = 0.0
        return fish.x + fish.swim_vx, fish.y + fish.swim_vy

    def clamp_refuge_entry(self, x, y, zone, margin=0):
        x0, y0, x1, y1 = zone
        min_y = y0 + margin
        max_y = y1 - margin
        if y < min_y:
            clamped_y = y
        else:
            clamped_y = max(min_y, min(max_y, y))
        return (
            max(x0 + margin, min(x1 - margin, x)),
            clamped_y,
        )

    def apply_biome_interactions(self):
        if self.environment.is_low_tide:
            self.low_tide_predation()
        else:
            self.high_tide_nursery()

    def high_tide_nursery(self):
        prey_fish = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, Fish) and animal.species == Fish.PREY and self.is_alive(animal)
        ]
        if self.frame % 600 == 0 and len(prey_fish) < 12:
            self.spawn_juvenile_fish((360 + (len(prey_fish) % 5) * 75, 396))

    def apply_basic_life_cycles(self):
        if self.frame % 60 == 0:
            for animal in list(self.environment.organism_list):
                if not self.is_alive(animal):
                    continue
                if isinstance(animal, Fish):
                    self.tick_fish_life(animal)
                elif isinstance(animal, Mudskipper):
                    animal.age += 1

        if self.environment.is_low_tide:
            self.reproduce_low_tide_animals()
        else:
            self.reproduce_nursery_fish()
            self.reproduce_high_tide_animals()

    def tick_fish_life(self, fish):
        fish.age += 1
        if fish.species == Fish.PREY and not self.environment.is_low_tide:
            fish.power = min(fish.power + 0.05, 3)
            if fish.age >= 5:
                fish.is_youth = False
        elif fish.species == Fish.PREDATOR and self.frame % 180 == 0:
            channel_prey = [
                animal for animal in self.environment.organism_list
                if isinstance(animal, Fish)
                and animal.species == Fish.PREY
                and self.is_alive(animal)
                and self.in_zone(animal, self.CHANNEL_ZONE)
            ]
            fish.is_starving = not channel_prey
            fish.power = min(fish.power + 0.08, 4)
            if fish.age >= 8:
                fish.is_youth = False

        if fish.is_starving and fish.age > 18 and self.frame % 300 == 0:
            self.kill_animal(fish)

    def reproduce_nursery_fish(self):
        if self.frame % 480 != 0:
            return
        adults = [
            fish for fish in self.environment.organism_list
            if isinstance(fish, Fish)
            and fish.species == Fish.PREY
            and self.is_alive(fish)
            and not fish.is_youth
            and not fish.is_starving
        ]
        prey_count = sum(
            isinstance(animal, Fish) and animal.species == Fish.PREY
            for animal in self.environment.organism_list
        )
        if len(adults) >= 2 and prey_count < 16:
            parent = adults[self.frame // 480 % len(adults)]
            self.spawn_juvenile_fish((parent.x + 18, parent.y + 8))

    def reproduce_low_tide_animals(self):
        if self.frame % 900 != 0:
            return
        for animal_type, limit, offset in [
            (Mudskipper, 5, (22, -4)),
            (Crab, 5, (18, 6)),
        ]:
            adults = [
                animal for animal in self.environment.organism_list
                if isinstance(animal, animal_type)
                and self.is_alive(animal)
                and animal.age > 8
                and not getattr(animal, "is_starving", False)
            ]
            current = sum(isinstance(animal, animal_type) for animal in self.environment.organism_list)
            if len(adults) >= 1 and current < limit:
                parent = adults[0]
                if animal_type is Mudskipper:
                    self.add_mudskipper_at(parent.x + offset[0], parent.y + offset[1])
                else:
                    self.add_crab_at(parent.x + offset[0], parent.y + offset[1])

    def reproduce_high_tide_animals(self):
        if self.frame % 1200 != 0:
            return

        prey_count = sum(
            isinstance(animal, Fish) and animal.species == Fish.PREY
            for animal in self.environment.organism_list
        )
        predator_count = sum(
            isinstance(animal, Fish) and animal.species == Fish.PREDATOR
            for animal in self.environment.organism_list
        )
        if prey_count >= 8 and predator_count < 4:
            self.add_fish(Fish.PREDATOR, place=(610 + predator_count * 24, 386), is_youth=True, power=2)

        bird_count = sum(isinstance(animal, Bird) for animal in self.environment.organism_list)
        if prey_count >= 6 and bird_count < 3:
            self.add_bird_at(205 + bird_count * 46, 96)

        watergun_count = sum(isinstance(animal, WatergunFish) for animal in self.environment.organism_list)
        if watergun_count < 3:
            self.add_watergun_fish_at(430 + watergun_count * 34, 372)

    def spawn_juvenile_fish(self, place):
        return self.add_fish(Fish.PREY, place=place, is_youth=True, power=0.55)

    def add_mudskipper_at(self, x, y):
        self.counts["mudskipper"] += 1
        animal = Mudskipper(
            power=1.4,
            place=self.clamp_to_zone(x, y, self.MUD_WATER_ZONE, margin=12),
            name="mudskipper",
            vmax=1,
            age=0,
        )
        return self.environment.add_organism(animal)

    def add_crab_at(self, x, y):
        self.counts["crab"] += 1
        x, y = self.clamp_to_zone(x, y, self.MUD_WATER_ZONE, margin=12)
        animal = Crab(x=x, y=y)
        animal.age = 0
        return self.environment.add_organism(animal)

    def add_bird_at(self, x, y):
        self.counts["bird"] += 1
        animal = Bird(x=x, y=y)
        animal.age = 0
        return self.environment.add_organism(animal)

    def add_watergun_fish_at(self, x, y):
        self.counts["watergun"] += 1
        animal = WatergunFish(hit_chance=0.6, x=x, y=y)
        animal.age = 0
        return self.environment.add_organism(animal)

    def low_tide_predation(self):
        self.hunt_in_zone(Bird, Fish, Fish.PREY, self.POOL_ZONE, interval=35, range_px=26)
        self.hunt_in_zone(Crab, Fish, Fish.PREY, self.POOL_ZONE, interval=42, range_px=24)
        self.hunt_in_zone(Fish, Fish, Fish.PREY, self.CHANNEL_ZONE, predator_species=Fish.PREDATOR, interval=28, range_px=24)
        self.hunt_in_zone(Mudskipper, Fish, Fish.PREY, self.MUD_WATER_ZONE, interval=44, range_px=23)
        self.hunt_in_zone(Crab, Fish, Fish.PREY, self.MUD_WATER_ZONE, interval=42, range_px=24)

    def hunt_in_zone(
        self,
        predator_type,
        prey_type,
        prey_species,
        zone,
        predator_species=None,
        interval=30,
        range_px=24,
    ):
        if self.frame % interval != 0:
            return

        predators = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, predator_type) and self.is_alive(animal)
        ]
        if predator_species is not None:
            predators = [
                animal for animal in predators
                if getattr(animal, "species", None) == predator_species
            ]
        prey = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, prey_type)
            and self.is_alive(animal)
            and getattr(animal, "species", prey_species) == prey_species
            and self.in_zone(animal, zone)
        ]
        if not predators or not prey:
            return

        for predator in predators:
            if isinstance(predator, Bird) and predator.y > 220:
                predator.place = (predator.x, predator.y + (170 - predator.y) * 0.12)
            if not self.predator_can_hunt_zone(predator, zone):
                continue

            target = min(prey, key=lambda animal: self.distance(predator, animal))
            self.move_predator_toward(predator, target, zone)
            if self.distance(predator, target) <= range_px and target in prey:
                self.kill_animal(target)
                prey.remove(target)
                if hasattr(predator, "_eat"):
                    predator._eat()
                if not prey:
                    return

    def predator_can_hunt_zone(self, predator, zone):
        if isinstance(predator, Bird):
            return True
        return self.in_zone(predator, zone, extra=90)

    def move_predator_toward(self, predator, target, zone):
        speed = 3.4 if isinstance(predator, Bird) else 1.3
        dx = target.x - predator.x
        dy = target.y - predator.y
        distance = math.hypot(dx, dy) or 1
        next_x = predator.x + dx / distance * speed
        next_y = predator.y + dy / distance * speed
        if isinstance(predator, Bird):
            x0, _, x1, _ = zone
            predator.place = (
                max(x0 + 8, min(x1 - 8, next_x)),
                max(95, min(target.y - 6, next_y)),
            )
            return
        predator.place = self.clamp_to_zone(next_x, next_y, zone, margin=8)

    def clamp_to_zone(self, x, y, zone, margin=0):
        x0, y0, x1, y1 = zone
        return (
            max(x0 + margin, min(x1 - margin, x)),
            max(y0 + margin, min(y1 - margin, y)),
        )

    def in_zone(self, animal, zone, extra=0):
        x0, y0, x1, y1 = zone
        return x0 - extra <= animal.x <= x1 + extra and y0 - extra <= animal.y <= y1 + extra

    def distance(self, a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def is_alive(self, animal):
        return getattr(animal, "alive", getattr(animal, "is_alive", True))

    def kill_animal(self, animal):
        try:
            animal.death("eaten in biome interaction")
        except TypeError:
            animal.death()

    def remove_dead_animals(self):
        for animal in list(self.environment.organism_list):
            if not self.is_alive(animal):
                self.environment.remove_organism(animal)

    def draw(self, camera):
        self.canvas.delete("animals")
        self.update()
        for animal in self.environment.organism_list:
            if not self.is_alive(animal):
                continue
            self.draw_animal(animal, camera)
        self.draw_panel()

    def draw_animal(self, animal, camera):
        if isinstance(animal, (Fish, WatergunFish)):
            x, y = self.render_swimmer_position(animal, camera)
        else:
            x = animal.x - camera.x
            y = animal.y - camera.y

        if isinstance(animal, WatergunFish):
            self.draw_watergun_fish(x, y)
        elif isinstance(animal, Fish):
            self.draw_fish(x, y, animal)
        elif isinstance(animal, Mudskipper):
            self.draw_mudskipper(x, y, animal)
        elif isinstance(animal, Bird):
            self.draw_bird(x, y, animal)
        elif isinstance(animal, Crab):
            self.draw_crab(x, y, animal)
        elif isinstance(animal, Ant):
            self.draw_ant(x, y)

    def render_swimmer_position(self, swimmer, camera):
        draw_x = getattr(swimmer, "draw_x", None)
        draw_y = getattr(swimmer, "draw_y", None)
        if draw_x is None or draw_y is None or math.hypot(swimmer.x - draw_x, swimmer.y - draw_y) > 120:
            swimmer.draw_x = swimmer.x
            swimmer.draw_y = swimmer.y
        else:
            swimmer.draw_x += (swimmer.x - swimmer.draw_x) * 0.22
            swimmer.draw_y += (swimmer.y - swimmer.draw_y) * 0.22
        return round(swimmer.draw_x - camera.x, 1), round(swimmer.draw_y - camera.y, 1)

    def fade_color(self, color, fade, background="#4f9fa0"):
        color = color.lstrip("#")
        background = background.lstrip("#")
        r1, g1, b1 = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r2, g2, b2 = int(background[0:2], 16), int(background[2:4], 16), int(background[4:6], 16)
        r = int(r2 + (r1 - r2) * fade)
        g = int(g2 + (g1 - g2) * fade)
        b = int(b2 + (b1 - b2) * fade)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_fish(self, x, y, fish):
        if fish.species == Fish.PREDATOR:
            self.draw_predator_fish(x, y, fish)
            return

        fade = getattr(fish, "escape_fade", 1.0)
        scale = (0.72 if fish.is_youth else 1.0) * max(0.35, fade)
        body = self.fade_color("#f5d85b" if not fish.is_youth else "#ffe88a", fade)
        stripe = self.fade_color("#c58a22", fade)
        outline = self.fade_color("#7a5a16", fade)
        d = 1 if getattr(fish, "swim_vx", 0.001) >= 0 else -1
        rx = 17 * scale
        ry = 8 * scale
        self.canvas.create_oval(x - rx, y - ry, x + rx, y + ry, fill=body, outline=outline, width=1, tags="animals")
        self.canvas.create_polygon(
            x - d * rx, y,
            x - d * (rx + 13 * scale), y - 8 * scale,
            x - d * (rx + 13 * scale), y + 8 * scale,
            fill=body,
            outline=outline,
            tags="animals"
        )
        for dx in (-6, 2, 9):
            self.canvas.create_line(x + d * dx * scale, y - ry + 2, x + d * (dx - 4) * scale, y + ry - 2, fill=stripe, width=1, tags="animals")
        if fade > 0.3:
            ex1 = x + min(d * 8, d * 12) * scale
            ex2 = x + max(d * 8, d * 12) * scale
            self.canvas.create_oval(ex1, y - 3 * scale, ex2, y + 1 * scale, fill="black", outline="", tags="animals")
        if fish.is_youth and fade > 0.45:
            glow = self.fade_color("#fff4b8", fade)
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=glow, outline="", tags="animals")

    def draw_predator_fish(self, x, y, fish):
        scale = 0.82 if fish.is_youth else 1.0
        body = "#c7352f"
        dark = "#5b1416"
        d = 1 if getattr(fish, "swim_vx", -0.001) >= 0 else -1
        self.canvas.create_oval(x - 26 * scale, y - 12 * scale, x + 26 * scale, y + 12 * scale, fill=body, outline=dark, width=2, tags="animals")
        self.canvas.create_polygon(x - d * 25 * scale, y, x - d * 43 * scale, y - 14 * scale, x - d * 43 * scale, y + 14 * scale, fill=dark, outline="", tags="animals")
        self.canvas.create_polygon(x + d * 12 * scale, y - 10 * scale, x - d * 4 * scale, y - 24 * scale, x - d * 14 * scale, y - 9 * scale, fill=dark, outline="", tags="animals")
        self.canvas.create_polygon(x + d * 23 * scale, y - 4 * scale, x + d * 33 * scale, y, x + d * 23 * scale, y + 4 * scale, fill="#f2f2e6", outline="", tags="animals")
        ex = x + d * 14.5 * scale
        ehalf = 2.5 * scale
        self.canvas.create_oval(ex - ehalf, y - 5 * scale, ex + ehalf, y, fill="black", outline="", tags="animals")
        self.canvas.create_line(x + d * 22 * scale, y + 5 * scale, x + d * 6 * scale, y + 8 * scale, fill=dark, width=2, tags="animals")

    def draw_watergun_fish(self, x, y):
        self.canvas.create_oval(x - 21, y - 10, x + 21, y + 10, fill="#45c7d8", outline="", tags="animals")
        self.canvas.create_polygon(x - 21, y, x - 36, y - 11, x - 36, y + 11, fill="#45c7d8", outline="", tags="animals")
        self.canvas.create_line(x + 15, y - 2, x + 38, y - 20, fill="#d9f7ff", width=2, tags="animals")
        self.canvas.create_oval(x + 9, y - 4, x + 13, y, fill="black", outline="", tags="animals")

    def draw_mudskipper(self, x, y, mudskipper):
        body = "#8b6f47" if not mudskipper.is_hidden else "#5a3e2b"
        self.canvas.create_oval(x - 24, y - 9, x + 24, y + 9, fill=body, outline="", tags="animals")
        self.canvas.create_oval(x - 12, y - 18, x - 2, y - 8, fill="#f6e8bd", outline="", tags="animals")
        self.canvas.create_oval(x + 2, y - 18, x + 12, y - 8, fill="#f6e8bd", outline="", tags="animals")
        self.canvas.create_oval(x - 9, y - 15, x - 6, y - 12, fill="black", outline="", tags="animals")
        self.canvas.create_oval(x + 6, y - 15, x + 9, y - 12, fill="black", outline="", tags="animals")

    def draw_bird(self, x, y, bird=None):
        age = getattr(bird, "age", 0) if bird is not None else 0
        flap = math.sin(age * 0.18) * 9
        self.canvas.create_polygon(x - 18, y, x, y - 10, x + 18, y, x, y + 6, fill="#f8fafc", outline="#475569", tags="animals")
        self.canvas.create_arc(x - 34, y - 12 + flap, x + 2, y + 16 + flap, start=15, extent=145, outline="#f8fafc", width=2, tags="animals")
        self.canvas.create_arc(x - 2, y - 12 + flap, x + 34, y + 16 + flap, start=20, extent=145, outline="#f8fafc", width=2, tags="animals")

    def draw_crab(self, x, y, crab):
        color = "#c2410c" if not crab.is_hidden else "#7c2d12"
        self.canvas.create_oval(x - 18, y - 10, x + 18, y + 10, fill=color, outline="", tags="animals")
        self.canvas.create_oval(x - 28, y - 8, x - 16, y + 4, fill=color, outline="", tags="animals")
        self.canvas.create_oval(x + 16, y - 8, x + 28, y + 4, fill=color, outline="", tags="animals")
        for dx in (-12, -4, 4, 12):
            self.canvas.create_line(x + dx, y + 6, x + dx - 8, y + 16, fill=color, width=2, tags="animals")
            self.canvas.create_line(x + dx, y + 6, x + dx + 8, y + 16, fill=color, width=2, tags="animals")

    def draw_ant(self, x, y):
        for dx in (-7, 0, 7):
            self.canvas.create_oval(x + dx - 4, y - 4, x + dx + 4, y + 4, fill="#17110c", outline="", tags="animals")
        for dx in (-7, 0, 7):
            self.canvas.create_line(x + dx, y, x + dx - 5, y - 7, fill="#17110c", tags="animals")
            self.canvas.create_line(x + dx, y, x + dx + 5, y + 7, fill="#17110c", tags="animals")

    def draw_panel(self):
        counts = {
            "fish": sum(isinstance(a, Fish) for a in self.environment.organism_list),
            "mudskipper": sum(isinstance(a, Mudskipper) for a in self.environment.organism_list),
            "bird": sum(isinstance(a, Bird) for a in self.environment.organism_list),
            "crab": sum(isinstance(a, Crab) for a in self.environment.organism_list),
            "watergun": sum(isinstance(a, WatergunFish) for a in self.environment.organism_list),
            "ant": sum(isinstance(a, Ant) for a in self.environment.organism_list),
        }
        tide = "간조" if self.environment.is_low_tide else "만조"
        self.canvas.create_rectangle(12, 210, 250, 312, fill="#0d2730", outline="", tags="animals")
        self.canvas.create_text(26, 228, anchor="w", text=f"조수: {tide}", fill="white", font=("맑은 고딕", 11, "bold"), tags="animals")
        self.canvas.create_text(26, 252, anchor="w", text=f"물고기 {counts['fish']}  망둥어 {counts['mudskipper']}  개미 {counts['ant']}", fill="white", font=("맑은 고딕", 10), tags="animals")
        self.canvas.create_text(26, 274, anchor="w", text=f"새 {counts['bird']}  게 {counts['crab']}", fill="white", font=("맑은 고딕", 10), tags="animals")
        self.canvas.create_text(26, 296, anchor="w", text=f"물총고기 {counts['watergun']}", fill="white", font=("맑은 고딕", 10), tags="animals")


    def draw_panel(self):
        counts = {
            "fish": sum(isinstance(a, Fish) for a in self.environment.organism_list),
            "mudskipper": sum(isinstance(a, Mudskipper) for a in self.environment.organism_list),
            "bird": sum(isinstance(a, Bird) for a in self.environment.organism_list),
            "crab": sum(isinstance(a, Crab) for a in self.environment.organism_list),
            "watergun": sum(isinstance(a, WatergunFish) for a in self.environment.organism_list),
            "ant": sum(isinstance(a, Ant) for a in self.environment.organism_list),
        }
        tide = "low tide" if self.environment.is_low_tide else "high tide"
        self.canvas.create_rectangle(12, 210, 250, 312, fill="#0d2730", outline="", tags="animals")
        self.canvas.create_text(26, 228, anchor="w", text=f"Tide: {tide}", fill="white", font=("Arial", 11, "bold"), tags="animals")
        self.canvas.create_text(26, 252, anchor="w", text=f"Fish {counts['fish']}  Mud {counts['mudskipper']}  Ant {counts['ant']}", fill="white", font=("Arial", 10), tags="animals")
        self.canvas.create_text(26, 274, anchor="w", text=f"Bird {counts['bird']}  Crab {counts['crab']}", fill="white", font=("Arial", 10), tags="animals")
        self.canvas.create_text(26, 296, anchor="w", text=f"Watergun {counts['watergun']}", fill="white", font=("Arial", 10), tags="animals")


class MenuPanel:
    def __init__(self, canvas):
        self.canvas = canvas
        self.visible = False
        self.ui_hide_checked = False
        self.camera_text = None
        self.biome_text = None

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        self.visible = True
        self.canvas.delete("menu_panel")
        self.canvas.create_rectangle(18, 50, 220, 200, fill="#1f2937", stipple="gray50", outline="#d1d5db", width=1, tags="menu_panel")
        self.canvas.create_text(30, 68, text="UI 숨기기", fill="#f3f4f6", font=("맑은 고딕", 13), anchor="w", tags="menu_panel")
        checkbox = "■" if self.ui_hide_checked else "□"
        box = self.canvas.create_text(128, 65, text=checkbox, fill="#f3f4f6", font=("맑은 고딕", 19), anchor="center", tags="menu_panel")
        self.canvas.create_rectangle(30, 88, 130, 112, fill="#b91c1c", outline="white", width=1, tags="menu_panel")
        self.canvas.create_text(80, 100, text="강제종료", fill="white", font=("맑은 고딕", 10, "bold"), tags="menu_panel")
        self.camera_text = self.canvas.create_text(30, 132, text="카메라 좌표:", fill="#f3f4f6", font=("맑은 고딕", 9), anchor="w", tags="menu_panel")
        self.biome_text = self.canvas.create_text(30, 150, text="현재 바이옴: none", fill="#f3f4f6", font=("맑은 고딕", 9), anchor="w", tags="menu_panel")
        self.canvas.tag_bind(box, "<Button-1>", self.toggle_checkbox)
        self.raise_to_top()

    def hide(self):
        self.visible = False
        self.canvas.delete("menu_panel")
        self.camera_text = None
        self.biome_text = None

    def toggle_checkbox(self, event=None):
        self.ui_hide_checked = not self.ui_hide_checked
        self.show()

    def update_info(self, camera):
        if self.camera_text is not None:
            self.canvas.itemconfig(self.camera_text, text=f"카메라 좌표: ({int(camera.x)}, {int(camera.y)})")
        if self.biome_text is not None:
            self.canvas.itemconfig(self.biome_text, text="현재 바이옴: none")

    def raise_to_top(self):
        self.canvas.tag_raise("menu_panel")


class MiniMap(GameObject):
    def __init__(self, canvas, camera):
        super().__init__(canvas)
        self.camera = camera
        self.x = 720
        self.y = 70
        self.width = 150
        self.height = 95

    def draw(self, camera=None):
        self.canvas.delete("minimap")
        self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width,
            self.y + self.height,
            fill="#1f2937",
            stipple="gray50",
            outline="white",
            width=1,
            tags="minimap"
        )
        x_ratio = (self.camera.x - self.camera.min_x) / (self.camera.max_x - self.camera.min_x)
        y_ratio = (self.camera.y - self.camera.min_y) / (self.camera.max_y - self.camera.min_y)
        dot_x = self.x + x_ratio * self.width
        dot_y = self.y + y_ratio * self.height
        self.canvas.create_oval(dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4, fill="red", outline="white", tags="minimap")
        self.canvas.create_text(self.x + 8, self.y + 8, text="MINI MAP", fill="white", font=("맑은 고딕", 8), anchor="nw", tags="minimap")

    def hide(self):
        self.canvas.delete("minimap")

    def raise_to_top(self):
        self.canvas.tag_raise("minimap")


class CleanMenuPanel:
    def __init__(self, canvas):
        self.canvas = canvas
        self.visible = False
        self.ui_hide_checked = False
        self.camera_text = None
        self.biome_text = None

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        self.visible = True
        self.canvas.delete("menu_panel")
        self.canvas.create_rectangle(
            18, 50, 220, 200,
            fill="#1f2937",
            stipple="gray50",
            outline="#d1d5db",
            width=1,
            tags="menu_panel"
        )
        self.canvas.create_text(30, 68, text="Hide UI", fill="#f3f4f6", font=("Arial", 13), anchor="w", tags="menu_panel")
        checkbox = "[x]" if self.ui_hide_checked else "[ ]"
        box = self.canvas.create_text(128, 68, text=checkbox, fill="#f3f4f6", font=("Arial", 14), anchor="center", tags="menu_panel")
        self.canvas.create_rectangle(30, 88, 130, 112, fill="#b91c1c", outline="white", width=1, tags="menu_panel")
        self.canvas.create_text(80, 100, text="Exit", fill="white", font=("Arial", 10, "bold"), tags="menu_panel")
        self.camera_text = self.canvas.create_text(30, 132, text="Camera: (0, 0)", fill="#f3f4f6", font=("Arial", 9), anchor="w", tags="menu_panel")
        self.biome_text = self.canvas.create_text(30, 150, text="Biome: mangrove", fill="#f3f4f6", font=("Arial", 9), anchor="w", tags="menu_panel")
        self.canvas.tag_bind(box, "<Button-1>", self.toggle_checkbox)
        self.raise_to_top()

    def hide(self):
        self.visible = False
        self.canvas.delete("menu_panel")
        self.camera_text = None
        self.biome_text = None

    def toggle_checkbox(self, event=None):
        self.ui_hide_checked = not self.ui_hide_checked
        self.show()

    def update_info(self, camera):
        if self.camera_text is not None:
            self.canvas.itemconfig(self.camera_text, text=f"Camera: ({int(camera.x)}, {int(camera.y)})")
        if self.biome_text is not None:
            self.canvas.itemconfig(self.biome_text, text="Biome: mangrove")

    def raise_to_top(self):
        self.canvas.tag_raise("menu_panel")


class MenuButton:
    def __init__(self, canvas, menu_panel):
        self.canvas = canvas
        self.menu_panel = menu_panel
        self.click_area = self.canvas.create_rectangle(18, 12, 55, 45, outline="", fill="", tags="menu_button")
        self.lines = []

        for y in [20, 28, 36]:
            line = self.canvas.create_line(22, y, 48, y, fill="#f3f4f6", width=2, capstyle=tk.ROUND, tags="menu_button")
            self.lines.append(line)

        self.canvas.tag_bind(self.click_area, "<Button-1>", self.on_click)
        for line in self.lines:
            self.canvas.tag_bind(line, "<Button-1>", self.on_click)

    def on_click(self, event=None):
        self.menu_panel.toggle()

    def raise_to_top(self):
        self.canvas.tag_raise("menu_button")


class AnimalControls:
    def __init__(self, root, animal_layer):
        self.root = root
        self.animal_layer = animal_layer
        self.frame = tk.Frame(root, bg="#0d2730")
        self.frame.place(x=12, y=112)
        self.build()

    def build(self):
        buttons = [
            ("물고기", lambda: self.animal_layer.add_fish(Fish.PREY)),
            ("포식자", lambda: self.animal_layer.add_fish(Fish.PREDATOR)),
            ("망둥어", self.animal_layer.add_mudskipper),
            ("물총고기", self.animal_layer.add_watergun_fish),
            ("새", self.animal_layer.add_bird),
            ("게", self.animal_layer.add_crab),
            ("개미", self.animal_layer.add_ant),
            ("조수", self.animal_layer.toggle_tide),
        ]
        for index, (text, command) in enumerate(buttons):
            tk.Button(
                self.frame,
                text=text,
                width=9,
                command=command,
                bg="#f3f4f6",
                activebackground="#d1d5db",
                font=("맑은 고딕", 9),
            ).grid(
                row=index // 2,
                column=index % 2,
                padx=2,
                pady=2
            )


class CleanAnimalControls:
    def __init__(self, root, animal_layer):
        self.animal_layer = animal_layer
        self.frame = tk.Frame(root, bg="#0d2730")
        self.frame.place(x=12, y=112)
        self.build()

    def build(self):
        buttons = [
            ("Fish", lambda: self.animal_layer.add_fish(Fish.PREY)),
            ("Predator", lambda: self.animal_layer.add_fish(Fish.PREDATOR)),
            ("Mud", self.animal_layer.add_mudskipper),
            ("Watergun", self.animal_layer.add_watergun_fish),
            ("Bird", self.animal_layer.add_bird),
            ("Crab", self.animal_layer.add_crab),
            ("Ant", self.animal_layer.add_ant),
            ("Tide", self.animal_layer.toggle_tide),
        ]
        for index, (text, command) in enumerate(buttons):
            tk.Button(
                self.frame,
                text=text,
                width=9,
                command=command,
                bg="#f3f4f6",
                activebackground="#d1d5db",
                font=("Arial", 9),
            ).grid(row=index // 2, column=index % 2, padx=2, pady=2)


class MangroveSimulation:
    FRAME_DELAY_MS = 8

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("맹그로브 늪지 생태계")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=900, height=600, highlightthickness=0)
        self.canvas.pack()

        self.keys = {"Left": False, "Right": False, "Up": False, "Down": False}
        self.camera = Camera()
        self.background = Background(self.canvas)
        self.animal_layer = AnimalLayer(self.canvas)
        self.time_display = TimeDisplay(self.canvas)
        self.minimap = MiniMap(self.canvas, self.camera)
        self.menu_panel = CleanMenuPanel(self.canvas)
        self.menu_button = MenuButton(self.canvas, self.menu_panel)
        self.animal_controls = CleanAnimalControls(self.root, self.animal_layer)
        self.root.title("Mangrove Simulation UI 4")

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
        self.background.draw(self.camera, self.animal_layer.environment.is_low_tide)
        self.animal_layer.draw(self.camera)

        if self.menu_panel.ui_hide_checked:
            self.time_display.hide()
            self.minimap.hide()
        else:
            self.time_display.draw()
            self.minimap.draw()
            self.minimap.raise_to_top()

        self.menu_button.raise_to_top()
        if self.menu_panel.visible:
            self.menu_panel.update_info(self.camera)
            self.menu_panel.raise_to_top()

        self.root.after(self.FRAME_DELAY_MS, self.game_loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MangroveSimulation()
    app.run()
