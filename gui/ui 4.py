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

from animal import Ant, Ant_herd, Bird, Crab, Fish, Mudskipper, WatergunFish
from environment import Environment


VIEW_W = 1280
VIEW_H = 720
VIEW_CX = VIEW_W // 2
VIEW_CY = VIEW_H // 2


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


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

MUD_FLOOR_POINTS = [
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


def mud_floor_level(x):
    points = MUD_FLOOR_POINTS
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            ratio = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * ratio
    return points[-1][1]


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

    def draw(self, camera, tide_level=0.0):
        self.canvas.delete("world")
        ox = -camera.x
        oy = -camera.y
        t = time.monotonic()

        self.canvas.create_rectangle(0, 0, VIEW_W, VIEW_H, fill="#243f3c", outline="", tags="world")
        self.draw_sky()
        self.draw_mist(ox, oy)
        self.draw_distant_forest(ox, oy)
        self.draw_water(ox, oy, tide_level, t)
        if tide_level < 0.35:
            self.draw_underwater_details(ox, oy, t)
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
            self.canvas.create_rectangle(0, y1, VIEW_W, y2, fill=color, outline="", tags="world")

    def draw_mist(self, ox, oy):
        for y, color in [(95, "#6f897f"), (155, "#829682"), (245, "#9b9c76")]:
            self.canvas.create_rectangle(0, oy + y, VIEW_W, oy + y + 28, fill=color, outline="", stipple="gray25", tags="world")
        for x in range(-560, 1520, 260):
            self.draw_cloud(ox + x, oy + 108, "#d8dec7", 0.72)

    def draw_distant_forest(self, ox, oy):
        self.canvas.create_rectangle(0, oy + 280, VIEW_W, oy + 360, fill="#274638", outline="", tags="world")
        for x in range(-520, 1560, 54):
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
        self.canvas.create_rectangle(0, oy + 340, VIEW_W, oy + 362, fill="#7f8360", outline="", stipple="gray50", tags="world")

    def draw_water(self, ox, oy, tide_level=0.0, t=0.0):
        if tide_level >= 0.97:
            self.draw_tide_pools(ox, oy, t)
            return

        eased = smoothstep(tide_level)
        surface_y = 378 + 174 * eased

        if tide_level > 0.55:
            self.draw_tide_pools(ox, oy, t)

        span = max(6.0, 545 - surface_y)
        for f0, f1, color in (
            (0.0, 0.25, "#3f8f91"),
            (0.25, 0.54, "#37807f"),
            (0.54, 0.79, "#2f6f6f"),
            (0.79, 1.0, "#286061"),
        ):
            y_top = surface_y + f0 * span
            if y_top >= 545:
                break
            y_bottom = min(545, surface_y + f1 * span)
            self.canvas.create_rectangle(ox - 10000, oy + y_top, ox + 10000, oy + y_bottom, fill=color, outline="", tags="world")

        wave_coords = []
        for sx in range(-40, VIEW_W + 41, 60):
            wave_y = surface_y + math.sin((sx - ox) * 0.022 + t * 1.8) * 2.6
            wave_coords.extend([sx, oy + wave_y])
        self.canvas.create_line(*wave_coords, fill="#b7e6df", width=2, smooth=True, tags="world")
        glint_coords = []
        for sx in range(-40, VIEW_W + 41, 90):
            glint_y = surface_y + 7 + math.sin((sx - ox) * 0.03 + t * 2.4 + 1.7) * 2.2
            glint_coords.extend([sx, oy + glint_y])
        self.canvas.create_line(*glint_coords, fill="#8fd0c6", width=1, smooth=True, tags="world")

    def draw_tide_pools(self, ox, oy, t):
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
                coords.extend([ox + x, oy + y + math.sin(t * 1.6 + x * 0.045) * 1.6])
            self.canvas.create_line(*coords, fill="#b7e6df", width=2, smooth=True, tags="world")

    def draw_underwater_details(self, ox, oy, t):
        for index, base_x in enumerate(range(-560, 1700, 240)):
            drift = math.sin(t * 0.4 + index) * 14
            top_x = ox + base_x + drift
            self.canvas.create_polygon(
                top_x, oy + 381,
                top_x + 34, oy + 381,
                top_x + 92, oy + 541,
                top_x + 24, oy + 541,
                fill="#a9ddcf",
                outline="",
                stipple="gray12",
                tags="world",
            )

        for x in range(-580, 1640, 110):
            sway = math.sin(t * 0.8 + x * 0.05) * 2
            for spread in (-16, -5, 7, 18):
                self.canvas.create_line(
                    ox + x + spread * 0.4, oy + 384,
                    ox + x + spread + sway, oy + 472 + (abs(spread) % 3) * 18,
                    fill="#2c4a4a" if spread % 2 else "#264243",
                    width=3 if abs(spread) < 10 else 2,
                    smooth=True,
                    tags="world",
                )

        for x in range(-560, 1660, 46):
            height = 26 + ((x // 46) % 4) * 10
            sway = math.sin(t * 1.5 + x * 0.12) * 6
            base_y = 543
            self.canvas.create_line(
                ox + x, oy + base_y,
                ox + x + sway * 0.5, oy + base_y - height * 0.55,
                ox + x + sway, oy + base_y - height,
                fill="#2e6b54" if (x // 46) % 2 else "#37755a",
                width=2,
                smooth=True,
                tags="world",
            )

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
        for x in range(-470, 1490, 95):
            shore_y = 552 - max(0, x - 650) * 0.16
            self.canvas.create_oval(ox + x, oy + shore_y, ox + x + 40, oy + shore_y + 8, fill="#725b39", outline="", tags="world")
            self.canvas.create_oval(ox + x + 24, oy + shore_y + 27, ox + x + 40, oy + shore_y + 32, fill="#30231d", outline="", tags="world")

    def draw_back_tree_line(self, ox, oy):
        for x, size in [
            (-530, "back"),
            (-380, "back"),
            (-230, "back"),
            (-80, "back"),
            (70, "back"),
            (220, "back"),
            (380, "back"),
            (535, "back"),
            (700, "back"),
            (850, "back"),
            (1015, "back"),
            (1180, "back"),
            (1340, "back"),
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
                (-460, "front"),
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
                (1300, "mid"),
            ]
        ]

    def mud_floor_y(self, x, layer="front"):
        return mud_floor_level(x)

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

        for spread in [-0.42, -0.3, -0.18, -0.08, 0.06, 0.16, 0.28, 0.4]:
            end_x = cx + int(width * spread)
            width_px = max(2, int(4 * scale * (1 - abs(spread) * 0.7)))
            start_y = base - 48 * scale
            arch = []
            for step in range(6):
                ratio = step / 5
                px = cx + (end_x - cx) * (ratio ** 0.72)
                py = start_y + (base - start_y) * (ratio ** 1.7)
                arch.append((px, py))
            draw.line(arch, fill=root_color, width=width_px, joint="curve")
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

        highlight = (118, 146, 74, 255)
        for index in range(24):
            hx = cx + int(math.sin(index * 2.4) * width * 0.3)
            hy = int(height * (0.17 + (index % 7) * 0.05))
            radius = max(2, int(2.6 * scale))
            draw.ellipse((hx - radius, hy - radius, hx + radius, hy + radius), fill=highlight)

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
        for x in range(-620, 1660, 42):
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
        for x in range(-490, 1460, 30):
            height = 24 + ((x // 30) % 5) * 9
            lean = -10 + ((x // 30) % 4) * 5
            self.canvas.create_line(ox + x, oy + 535, ox + x + lean, oy + 535 - height, fill="#243d24", width=2, tags="world")
            self.canvas.create_line(ox + x + 4, oy + 536, ox + x + 4 - lean, oy + 542 - height, fill="#506b31", width=1, tags="world")
            if (x // 30) % 3 == 0:
                self.canvas.create_oval(ox + x + lean - 4, oy + 531 - height, ox + x + lean + 4, oy + 542 - height, fill="#806b36", outline="", tags="world")

    def draw_foreground_leaves(self, ox, oy):
        for x in range(-520, 1430, 95):
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
    CHANNEL_ZONE = (430, 480, 760, 545)
    MUD_WATER_ZONE = (760, 440, 1160, 565)
    SEA_ESCAPE_X = 1240
    DAY_LENGTH = 7200
    LOW_TIDE_REFUGES = {
        "pool": (285, 520),
        "channel": (595, 512),
        "mud_water": (910, 495),
    }

    def __init__(self, canvas):
        super().__init__(canvas)
        self.environment = Environment()
        self.frame = 0
        self.was_low_tide = self.environment.is_low_tide
        self.environment.ticks_per_day = 10 ** 9
        self.sea_fish = []
        self.bubbles = []
        self.eggs = []
        self.event_feed = []
        self.corpses = []
        self.propagules = []
        self.saplings = []
        self.nests = []
        self.tide_level = 1.0 if self.environment.is_low_tide else 0.0
        self.weather = "clear"
        self.weather_timer = random.randint(1800, 3600)
        self.selected = None
        self.follow_selected = False
        self.pop_history = []
        self._was_night = False
        self._school_target = (650, 450)
        self._school_until = 0
        self._youth_school = []
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
        for _ in range(8):
            self.add_fish(Fish.PREY)
        for _ in range(2):
            self.add_fish(Fish.PREDATOR)
        for _ in range(3):
            self.add_mudskipper()
        for _ in range(2):
            self.add_watergun_fish()
        for _ in range(2):
            self.add_bird()
        for _ in range(3):
            self.add_crab()
        for _ in range(8):
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
        animal.is_youth = False
        animal._max_hunger = 130
        return self.environment.add_organism(animal)

    def add_watergun_fish(self):
        self.counts["watergun"] += 1
        animal = WatergunFish(
            hit_chance=0.6,
            x=390 + self.counts["watergun"] * 34,
            y=398,
        )
        animal._max_hunger = 5400
        return self.environment.add_organism(animal)

    def add_bird(self):
        self.counts["bird"] += 1
        animal = Bird(x=170 + self.counts["bird"] * 45, y=105)
        animal._max_hunger = 7200
        return self.environment.add_organism(animal)

    def add_crab(self):
        self.counts["crab"] += 1
        animal = Crab(x=830 + self.counts["crab"] * 26, y=545)
        animal._max_hunger = 9000
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
        self.update_bubbles()
        self.update_eggs()
        self.update_day_night()
        self.update_weather()
        self.update_corpses()
        self.update_propagules()
        self.update_nests()
        self.check_bird_migration()
        self.try_form_ant_herd()
        self.update_population_history()
        self.update_tide_level()
        self.restore_fish_if_tide_returns()

    def update_tide_level(self):
        target = 1.0 if self.environment.is_low_tide else 0.0
        delta = target - self.tide_level
        step = 0.0016
        if abs(delta) <= step:
            self.tide_level = target
        else:
            self.tide_level += step if delta > 0 else -step

    def current_surface_y(self):
        return 378 + 174 * smoothstep(self.tide_level)

    def restore_fish_if_tide_returns(self):
        if self.was_low_tide and not self.environment.is_low_tide:
            self.restore_sea_fish()
            self.log_event("만조: 물이 차오르고 물고기들이 돌아옵니다", "info")
        elif not self.was_low_tide and self.environment.is_low_tide:
            self.log_event("간조: 치어들이 웅덩이로 피신합니다", "info")
        self.was_low_tide = self.environment.is_low_tide

    def log_event(self, text, kind="info"):
        self.event_feed.append((time.monotonic(), text, kind))
        if len(self.event_feed) > 30:
            del self.event_feed[:-30]

    def zone_label(self, zone):
        if zone == self.POOL_ZONE:
            return "작은 웅덩이"
        if zone == self.CHANNEL_ZONE:
            return "중앙수로"
        if zone == self.MUD_WATER_ZONE:
            return "진흙 웅덩이"
        return "습지"

    def animal_label(self, animal):
        if isinstance(animal, WatergunFish):
            return "물총고기"
        if isinstance(animal, Fish):
            if animal.species == Fish.PREDATOR:
                return "포식자 물고기"
            return "치어" if animal.is_youth else "물고기"
        if isinstance(animal, Mudskipper):
            return "망둥어"
        if isinstance(animal, Bird):
            return "새"
        if isinstance(animal, Crab):
            return "게"
        if isinstance(animal, Ant):
            return "개미"
        return "생물"

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
        self._youth_school = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, Fish)
            and animal.species == Fish.PREY
            and animal.is_youth
            and self.is_alive(animal)
        ]
        for animal in list(self.environment.organism_list):
            if not self.is_alive(animal):
                continue
            if isinstance(animal, Fish):
                self.move_fish_for_tide(animal)
        self.apply_biome_interactions()
        self.apply_basic_life_cycles()
        self.remove_dead_animals()

    def move_branch_walkers(self):
        for animal in list(self.environment.organism_list):
            if not self.is_alive(animal):
                continue
            if isinstance(animal, Ant):
                if getattr(animal, "is_falling", False):
                    self.update_falling_ant(animal)
                else:
                    self.move_on_elevated_branch(animal, speed=0.9, lane=-5)
            elif isinstance(animal, Ant_herd):
                if getattr(animal, "is_falling", False):
                    self.herd_loses_ant(animal)
                else:
                    animal.age += 1
                    if animal.age > 5400 or not animal.ant_list:
                        self.disband_ant_herd(animal)
                    elif len(animal.ant_list) >= 20 and random.random() < 0.002:
                        self.split_ant_herd(animal)
                    else:
                        self.move_on_elevated_branch(animal, speed=1.0, lane=-5)
                        self.ant_herd_attack(animal)
            elif isinstance(animal, Crab):
                self.move_crab_on_mud(animal)
            elif isinstance(animal, Mudskipper):
                self.move_mudskipper_ground(animal)
            elif isinstance(animal, WatergunFish):
                self.adjust_watergun_home(animal)
            elif isinstance(animal, Bird):
                self.steer_bird(animal)

    def update_falling_ant(self, ant):
        if not hasattr(ant, "fall_drift"):
            ant.fall_drift = random.uniform(-0.4, 0.4)
            self.log_event("물총고기가 물줄기로 개미를 떨어뜨림!", "kill")
        ant.fall_vy = getattr(ant, "fall_vy", 0.0) + 0.32
        x = ant.x + ant.fall_drift
        y = ant.y + ant.fall_vy
        if self.environment.is_low_tide:
            landing_y = mud_floor_level(x) - 2
        else:
            landing_y = 382
        if y >= landing_y:
            ant.place = (x, landing_y)
            self.consume_fallen_ant(ant)
        else:
            ant.place = (x, y)

    def consume_fallen_ant(self, ant):
        ant.death("fell into the water")
        hunters = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, WatergunFish) and self.is_alive(animal)
        ]
        if hunters:
            nearest = min(hunters, key=lambda hunter: self.distance(hunter, ant))
            if self.distance(nearest, ant) <= 170:
                nearest._eat()
                self.log_event("물총고기가 떨어진 개미를 먹어치움", "kill")
        if not self.environment.is_low_tide:
            for _ in range(4):
                self.bubbles.append({
                    "x": ant.x + random.uniform(-5, 5),
                    "y": ant.y + random.uniform(0, 4),
                    "r": random.uniform(1.0, 2.2),
                    "drift": random.uniform(-0.25, 0.25),
                })

    def nearest_youth_prey(self, hunter, zones, max_dist):
        candidates = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, Fish)
            and animal.species == Fish.PREY
            and animal.is_youth
            and self.is_alive(animal)
            and any(self.in_zone(animal, zone) for zone in zones)
        ]
        if not candidates:
            return None
        target = min(candidates, key=lambda animal: self.distance(hunter, animal))
        if self.distance(hunter, target) > max_dist:
            return None
        return target

    def move_crab_on_mud(self, crab):
        if not self.environment.is_low_tide:
            burrow_x = getattr(crab, "_burrow_x", None)
            if burrow_x is None:
                burrow_x = random.uniform(870, 1120)
                crab._burrow_x = burrow_x
            if abs(crab.x - burrow_x) > 6:
                crab.is_hidden = False
                direction = 1 if burrow_x > crab.x else -1
                x = crab.x + direction * 1.6
            else:
                crab.is_hidden = True
                x = burrow_x
            crab.place = (x, min(586.0, mud_floor_level(x) + 8))
            return

        crab.is_hidden = False
        corpse = self.nearest_corpse(crab)
        if corpse is not None:
            next_x, next_y = self.move_point_toward(crab.x, crab.y, corpse["x"], corpse["y"], 1.25)
            crab.place = (next_x, min(586.0, next_y))
            return
        target = None
        if getattr(crab, "_eat_cd", 0) <= self.frame:
            target = self.nearest_youth_prey(crab, (self.POOL_ZONE, self.MUD_WATER_ZONE), max_dist=180)
        if target is not None:
            next_x, next_y = self.move_point_toward(crab.x, crab.y, target.x, target.y, 1.25)
            crab.place = (next_x, min(586.0, next_y))
            return

        x_min, x_max = -40, 1130
        state = getattr(crab, "_scuttle", None)
        if state is None or state["timer"] <= 0:
            moving = state is None or not state["moving"]
            direction = state["direction"] if state else random.choice((-1, 1))
            if moving and random.random() < 0.4:
                direction = -direction
            crab._scuttle = state = {
                "moving": moving,
                "direction": direction,
                "timer": random.randint(40, 100) if moving else random.randint(20, 60),
            }
        state["timer"] -= 1

        x = crab.x
        if state["moving"]:
            x += state["direction"] * 1.3
            if x < x_min or x > x_max:
                state["direction"] *= -1
        x = max(x_min, min(x_max, x))
        crab.place = (x, min(586.0, mud_floor_level(x) + 8))

    def move_mudskipper_ground(self, mud):
        if not self.environment.is_low_tide:
            burrow_x = getattr(mud, "_burrow_x", None)
            if burrow_x is None:
                burrow_x = random.uniform(930, 1140)
                mud._burrow_x = burrow_x
            if abs(mud.x - burrow_x) > 6:
                mud.is_hidden = False
                direction = 1 if burrow_x > mud.x else -1
                next_x = mud.x + direction * 1.5
                mud._hop_phase = getattr(mud, "_hop_phase", 0.0) + 0.3
                mud._bounce = abs(math.sin(mud._hop_phase)) * 5
                mud.place = (next_x, mud_floor_level(next_x) + 2)
            else:
                mud.is_hidden = True
                mud._bounce = 0.0
                mud.place = (burrow_x, mud_floor_level(burrow_x) + 2)
            return

        mud.is_hidden = False
        target = None
        if getattr(mud, "_eat_cd", 0) <= self.frame:
            target = self.nearest_youth_prey(mud, (self.MUD_WATER_ZONE,), max_dist=160)
        if target is not None:
            mud._hop_phase = getattr(mud, "_hop_phase", 0.0) + 0.34
            mud._bounce = abs(math.sin(mud._hop_phase)) * 5
            next_x, next_y = self.move_point_toward(mud.x, mud.y, target.x, target.y, 1.3)
            mud.place = self.clamp_to_zone(next_x, next_y, self.MUD_WATER_ZONE, margin=8)
            return

        x_range = (770, 1140)
        state = getattr(mud, "_skip", None)
        if state is None:
            state = {"target": None, "rest": random.randint(30, 90), "phase": random.uniform(0, math.pi * 2)}
            mud._skip = state

        if state["target"] is None:
            if state["rest"] > 0:
                state["rest"] -= 1
                mud._bounce = 0.0
                return
            state["target"] = random.uniform(*x_range)

        target_x = state["target"]
        direction = 1 if target_x > mud.x else -1
        next_x = mud.x + direction * 1.4
        state["phase"] += 0.3
        mud._bounce = abs(math.sin(state["phase"])) * 5
        mud.place = (next_x, mud_floor_level(next_x) + 2)

        if abs(next_x - target_x) < 4:
            state["target"] = None
            state["rest"] = random.randint(40, 140)
            mud._bounce = 0.0

    def steer_bird(self, bird):
        if (
            self.environment.is_low_tide
            and not self.is_night()
            and self.weather != "storm"
            and getattr(bird, "_eat_cd", 0) <= self.frame
        ):
            target = self.nearest_youth_prey(bird, (self.POOL_ZONE,), max_dist=470)
            if target is not None:
                bird._dive_target = target
                bird.__dict__["SKY_ZONE"] = (0, 30, 1280, 540)
                return
        bird._dive_target = None
        zone = bird.__dict__.get("SKY_ZONE")
        if zone is not None:
            floor = zone[3]
            if floor <= 160:
                del bird.__dict__["SKY_ZONE"]
            else:
                bird.__dict__["SKY_ZONE"] = (0, 30, 1280, max(160, floor - 2.5))

    def adjust_watergun_home(self, watergun):
        base = getattr(watergun, "_base_home", None)
        if base is None:
            base = (watergun.home_x, max(392.0, watergun.home_y))
            watergun._base_home = base

        if self.environment.is_low_tide:
            offset = getattr(watergun, "refuge_offset", None)
            if offset is None:
                offset = (random.uniform(-40, 40), random.uniform(4, 22))
                watergun.refuge_offset = offset
            refuge_x, refuge_y = self.LOW_TIDE_REFUGES["channel"]
            watergun.home_x = refuge_x + offset[0]
            watergun.home_y = refuge_y + offset[1]
        else:
            watergun.home_x, watergun.home_y = base

    def update_bubbles(self):
        if self.environment.is_low_tide:
            self.bubbles.clear()
            return
        if self.frame % 9 == 0 and len(self.bubbles) < 26:
            swimmers = [
                animal for animal in self.environment.organism_list
                if isinstance(animal, (Fish, WatergunFish)) and self.is_alive(animal)
            ]
            if swimmers:
                source = random.choice(swimmers)
                self.bubbles.append({
                    "x": source.x + random.uniform(-6, 6),
                    "y": source.y - 4,
                    "r": random.uniform(1.2, 2.6),
                    "drift": random.uniform(-0.2, 0.2),
                })
        for bubble in list(self.bubbles):
            bubble["y"] -= 0.55
            bubble["x"] += bubble["drift"] + math.sin(self.frame * 0.1 + bubble["y"] * 0.05) * 0.18
            if bubble["y"] <= 384:
                self.bubbles.remove(bubble)

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
            speed = 0.6 if fish.species == Fish.PREY else 0.78
            turn = 0.055
            if fish.y < 470:
                speed = 1.7
                turn = 0.1
            next_x, next_y = self.smooth_swim_toward(fish, target_x, target_y, speed, turn=turn)
            fish.move(self.clamp_refuge_entry(next_x, next_y, zone, margin=16))
            return

        if getattr(fish, "returning_from_sea", False):
            self.move_returning_fish(fish)
            return
        if hasattr(fish, "escape_fade"):
            fish.escape_fade = 1.0
        if hasattr(fish, "_refuge_name"):
            del fish._refuge_name
        if fish.species == Fish.PREY:
            if fish.is_youth:
                base_x, base_y = self.school_wander_target()
                phase = self.ensure_fish_motion(fish)
                target_x = base_x + math.sin(self.frame * 0.045 + phase) * 26
                target_y = base_y + math.cos(self.frame * 0.05 + phase * 1.3) * 11
                for other in self._youth_school:
                    if other is fish:
                        continue
                    dx = fish.x - other.x
                    dy = fish.y - other.y
                    dist = math.hypot(dx, dy) or 1.0
                    if dist < 16:
                        target_x += dx / dist * (16 - dist) * 2.2
                        target_y += dy / dist * (16 - dist) * 2.2
            else:
                target_x, target_y = self.wander_target(fish, (210, 1120), (392, 522), retarget_frames=280)
            threat = self.nearest_predator(fish)
            if threat is not None and self.distance(fish, threat) < 85:
                away_x = max(210, min(1120, fish.x + (fish.x - threat.x) * 2))
                away_y = max(392, min(522, fish.y + (fish.y - threat.y) * 2))
                target_x, target_y = away_x, away_y
                fish._wander_target = (away_x, away_y)
                fish._wander_until = self.frame + 45
                fish.move(self.smooth_swim_toward(fish, target_x, target_y, 0.95, turn=0.09))
            else:
                cruise = 0.7 if fish.is_youth else 0.62
                fish.move(self.smooth_swim_toward(fish, target_x, target_y, cruise, turn=0.06))
        else:
            target_x, target_y = self.wander_target(fish, (420, 980), (386, 505), retarget_frames=340)
            fish.move(self.smooth_swim_toward(fish, target_x, target_y, 0.55, turn=0.05))

    def wander_target(self, animal, x_range, y_range, retarget_frames=240):
        target = getattr(animal, "_wander_target", None)
        until = getattr(animal, "_wander_until", -1)
        reached = target is not None and math.hypot(animal.x - target[0], animal.y - target[1]) < 14
        if target is None or reached or self.frame >= until:
            target = (random.uniform(*x_range), random.uniform(*y_range))
            animal._wander_target = target
            animal._wander_until = self.frame + random.randint(retarget_frames // 2, retarget_frames)
        return target

    def nearest_predator(self, fish):
        predators = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, Fish)
            and animal.species == Fish.PREDATOR
            and self.is_alive(animal)
        ]
        if not predators:
            return None
        return min(predators, key=lambda predator: self.distance(fish, predator))

    def fish_low_tide_zone(self, fish):
        if fish.species == Fish.PREDATOR:
            return self.CHANNEL_ZONE
        name = getattr(fish, "_refuge_name", None)
        if name is None:
            zone_counts = {"pool": 0, "channel": 0, "mud_water": 0}
            for a in self.environment.organism_list:
                if isinstance(a, Fish) and a.species == Fish.PREY and a is not fish:
                    n = getattr(a, "_refuge_name", None)
                    if n in zone_counts:
                        zone_counts[n] += 1
            name = min(zone_counts, key=zone_counts.get)
            fish._refuge_name = name
        return {
            "pool": self.POOL_ZONE,
            "channel": self.CHANNEL_ZONE,
            "mud_water": self.MUD_WATER_ZONE,
        }[name]

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
        target_y = 508 if fish.x < 780 else 468
        next_x, next_y = self.smooth_swim_toward(fish, self.SEA_ESCAPE_X + 40, target_y, 1.1, turn=0.06)
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

    def apply_basic_life_cycles(self):
        if self.frame % 60 == 0:
            for animal in list(self.environment.organism_list):
                if not self.is_alive(animal):
                    continue
                if isinstance(animal, Fish):
                    self.tick_fish_life(animal)
                elif isinstance(animal, Mudskipper):
                    animal.age += 1
                    animal._tick_hunger()
                if isinstance(animal, (Bird, Crab, Mudskipper, WatergunFish)):
                    if animal._hunger > animal._max_hunger * 1.5:
                        self.kill_animal(animal)
                        self.add_corpse(animal)
                        self.log_event(f"{self.animal_label(animal)}가 굶어 죽었습니다", "kill")
            self.grow_youth()

        self.lay_fish_eggs()
        self.proximity_reproduction()

        if self.frame % 1800 == 0:
            ant_count = self.total_ant_count()
            if ant_count < 3:
                for _ in range(3):
                    self.add_ant()
                self.log_event("개미 무리가 숲에서 유입됨", "info")

        if self.frame % 3600 == 0:
            predator_count = sum(
                isinstance(animal, Fish) and animal.species == Fish.PREDATOR
                for animal in self.environment.organism_list
            )
            if predator_count < 2:
                self.add_fish(Fish.PREDATOR, place=(1130, 430), is_youth=False, power=3)
                self.log_event("바다에서 포식자 물고기가 들어옴", "info")
            rescue_specs = (
                (Bird, self.add_bird, "새"),
                (Crab, self.add_crab, "게"),
                (Mudskipper, self.add_mudskipper, "망둥어"),
                (WatergunFish, self.add_watergun_fish, "물총고기"),
            )
            for cls, adder, label in rescue_specs:
                if sum(isinstance(animal, cls) for animal in self.environment.organism_list) < 2:
                    adder()
                    self.log_event(f"{label}가 서식지에 새로 유입되었습니다", "info")

    def tick_fish_life(self, fish):
        fish.age += 1
        if fish.species == Fish.PREY and not self.environment.is_low_tide:
            fish.power = min(fish.power + 0.05, 3)
            if fish.age >= 40:
                fish.is_youth = False
        elif fish.species == Fish.PREDATOR and self.frame % 180 == 0:
            prey_exists = any(
                isinstance(animal, Fish)
                and animal.species == Fish.PREY
                and self.is_alive(animal)
                for animal in self.environment.organism_list
            )
            fish.is_starving = not prey_exists and not self.sea_fish
            fish.power = min(fish.power + 0.08, 4)
            if fish.age >= 8:
                fish.is_youth = False

        if fish.is_starving and fish.age > 18 and self.frame % 1800 == 0:
            self.kill_animal(fish)
            self.add_corpse(fish)
            self.log_event(f"{self.animal_label(fish)}가 굶어 죽었습니다", "kill")

    def lay_fish_eggs(self):
        if self.frame % 30 != 0 or len(self.eggs) >= 6:
            return
        for species, cap, cooldown, pair_dist in (
            (Fish.PREY, 18, 1400, 46),
            (Fish.PREDATOR, 5, 2800, 52),
        ):
            total = sum(
                isinstance(animal, Fish) and animal.species == species
                for animal in self.environment.organism_list
            )
            if total >= cap:
                continue
            adults = [
                animal for animal in self.environment.organism_list
                if isinstance(animal, Fish)
                and animal.species == species
                and self.is_alive(animal)
                and not animal.is_youth
                and not animal.is_starving
                and getattr(animal, "_egg_cd", 0) <= self.frame
            ]
            laid = False
            for index, first in enumerate(adults):
                if laid:
                    break
                for second in adults[index + 1:]:
                    if self.distance(first, second) > pair_dist:
                        continue
                    egg_x = (first.x + second.x) / 2
                    egg_y = max(392.0, min(530.0, (first.y + second.y) / 2))
                    self.eggs.append({"x": egg_x, "y": egg_y, "timer": 700, "species": species})
                    label = "물고기" if species == Fish.PREY else "포식자 물고기"
                    self.log_event(f"{label}가 알을 낳았습니다", "birth")
                    stamp = self.frame + cooldown
                    first._egg_cd = stamp + random.randint(0, 300)
                    second._egg_cd = stamp + random.randint(0, 300)
                    laid = True
                    break

    def update_eggs(self):
        for egg in list(self.eggs):
            egg["timer"] -= 1
            if egg["timer"] > 0:
                continue
            self.eggs.remove(egg)
            species = egg["species"]
            cap = 18 if species == Fish.PREY else 5
            total = sum(
                isinstance(animal, Fish) and animal.species == species
                for animal in self.environment.organism_list
            )
            hatch_count = max(0, min(random.randint(2, 3), cap - total))
            if hatch_count > 0:
                label = "치어" if species == Fish.PREY else "새끼 포식자"
                self.log_event(f"알에서 {label} {hatch_count}마리 부화", "birth")
            for _ in range(max(0, hatch_count)):
                place = (
                    egg["x"] + random.uniform(-12, 12),
                    max(392.0, min(530.0, egg["y"] + random.uniform(-8, 8))),
                )
                power = 0.55 if species == Fish.PREY else 1.5
                self.add_fish(species, place=place, is_youth=True, power=power)

    def total_ant_count(self):
        total = 0
        for animal in self.environment.organism_list:
            if isinstance(animal, Ant):
                total += 1
            elif isinstance(animal, Ant_herd):
                total += len(animal.ant_list)
        return total

    def day_phase(self):
        return (self.frame % self.DAY_LENGTH) / self.DAY_LENGTH

    def is_night(self):
        return 0.6 <= self.day_phase() < 0.97

    def darkness_level(self):
        phase = self.day_phase()
        if 0.52 <= phase < 0.6 or 0.93 <= phase < 0.97:
            return 1
        if 0.6 <= phase < 0.93:
            return 2
        return 0

    def update_day_night(self):
        night = self.is_night()
        if night != self._was_night:
            self._was_night = night
            self.log_event("밤이 되었습니다 — 새들이 잠듭니다" if night else "아침이 밝았습니다", "info")

    def update_weather(self):
        self.weather_timer -= 1
        if self.weather_timer > 0:
            return
        if self.weather == "clear":
            self.weather = "rain" if random.random() < 0.75 else "storm"
        elif random.random() < 0.65:
            self.weather = "clear"
        else:
            self.weather = "storm" if self.weather == "rain" else "rain"
        self.weather_timer = random.randint(1600, 3800)
        labels = {"clear": "비가 그치고 날이 갰습니다", "rain": "비가 내리기 시작합니다", "storm": "폭풍이 몰아칩니다!"}
        self.log_event(labels[self.weather], "info")

    def add_corpse(self, animal):
        self.corpses.append({"x": animal.x, "y": animal.y, "timer": 3600})

    def update_corpses(self):
        for corpse in list(self.corpses):
            corpse["timer"] -= 1
            ground = mud_floor_level(corpse["x"]) + 4
            if corpse["y"] < ground:
                corpse["y"] = min(ground, corpse["y"] + 1.1)
            if corpse["timer"] <= 0:
                self.corpses.remove(corpse)

        if self.frame % 20 != 0 or not self.corpses:
            return
        crabs = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, Crab) and self.is_alive(animal) and not animal.is_hidden
        ]
        for corpse in list(self.corpses):
            for crab in crabs:
                if math.hypot(crab.x - corpse["x"], crab.y - corpse["y"]) < 28:
                    self.corpses.remove(corpse)
                    crab._eat()
                    self.log_event("게가 사체를 청소했습니다", "info")
                    break

    def nearest_corpse(self, crab, max_dist=240):
        if not self.corpses:
            return None
        corpse = min(self.corpses, key=lambda c: math.hypot(crab.x - c["x"], crab.y - c["y"]))
        if math.hypot(crab.x - corpse["x"], crab.y - corpse["y"]) > max_dist:
            return None
        return corpse

    def update_propagules(self):
        if self.frame % 900 == 0 and random.random() < 0.55 and len(self.propagules) + len(self.saplings) < 8:
            x = random.choice((-120, 70, 250, 445, 625, 770, 900, 1040)) + random.uniform(-45, 45)
            self.propagules.append({"x": x, "y": mud_floor_level(x) - 235, "vy": 0.0, "planted": False, "growth": 0})
        for propagule in list(self.propagules):
            if not propagule["planted"]:
                propagule["vy"] += 0.25
                propagule["y"] += propagule["vy"]
                ground = mud_floor_level(propagule["x"])
                if propagule["y"] >= ground - 4:
                    propagule["y"] = ground - 4
                    propagule["planted"] = True
                    self.log_event("맹그로브 묘목이 진흙에 자리잡았습니다", "birth")
            else:
                propagule["growth"] += 1
                if propagule["growth"] >= 5400:
                    self.saplings.append({"x": propagule["x"], "growth": 0})
                    self.propagules.remove(propagule)
                    self.log_event("묘목이 어린 나무로 자랐습니다", "birth")
        for sapling in self.saplings:
            if sapling["growth"] < 7200:
                sapling["growth"] += 1

    def try_form_ant_herd(self):
        if self.frame % 300 != 0:
            return
        if any(isinstance(animal, Ant_herd) for animal in self.environment.organism_list):
            return
        ants = [
            animal for animal in self.environment.organism_list
            if isinstance(animal, Ant)
            and self.is_alive(animal)
            and not animal.is_youth
            and not getattr(animal, "is_falling", False)
        ]
        if len(ants) < 10:
            return
        center = ants[0]
        group = [a for a in ants if abs(a.x - center.x) < 90 and abs(a.y - center.y) < 45]
        if len(group) < 10:
            return
        herd = Ant_herd(x=center.x, y=center.y, v_xm=0.9, v_ym=0, power=1, name="ant_herd", ant_list=group)
        for ant in group:
            self.environment.remove_organism(ant)
        self.environment.add_organism(herd)
        self.log_event(f"개미 {len(group)}마리가 무리를 이뤘습니다!", "info")

    def herd_loses_ant(self, herd):
        herd.is_falling = False
        if herd.ant_list:
            herd.ant_list.pop()
            herd.update_herd_power()
        victim = Ant(x=herd.x, y=herd.y, v_xm=0.18, v_ym=0, name="ant", is_youth=False)
        victim.is_falling = True
        victim.fall_vy = 0.0
        victim.fall_drift = random.uniform(-0.4, 0.4)
        self.environment.add_organism(victim)
        self.log_event("물총고기가 무리에서 개미 한 마리를 떨어뜨림!", "kill")
        if len(herd.ant_list) < 6:
            self.disband_ant_herd(herd)

    def disband_ant_herd(self, herd):
        for index, ant in enumerate(herd.ant_list):
            ant.place = (herd.x + (index % 4) * 10 - 15, herd.y + (index // 4) * 6 - 6)
            if hasattr(ant, "branch_target_index"):
                del ant.branch_target_index
            self.environment.add_organism(ant)
        herd.ant_list = []
        self.environment.remove_organism(herd)
        self.log_event("개미 무리가 흩어졌습니다", "info")

    def split_ant_herd(self, herd):
        if len(herd.ant_list) < 12:
            return
        half = len(herd.ant_list) // 2
        for lst, direction in ((herd.ant_list[:half], -1), (herd.ant_list[half:], 1)):
            new_herd = Ant_herd(
                x=herd.x + direction * 20,
                y=herd.y,
                v_xm=direction * 0.9,
                v_ym=0,
                power=1,
                name="ant_herd",
                ant_list=list(lst),
            )
            new_herd.branch_target_index = getattr(herd, "branch_target_index", 0)
            new_herd.branch_direction = direction
            self.environment.add_organism(new_herd)
        herd.ant_list = []
        self.environment.remove_organism(herd)
        self.log_event("개미 무리가 두 갈래로 분열했습니다!", "info")

    def ant_herd_attack(self, herd):
        if self.frame % 45 != 0:
            return
        attack_range = 110
        candidates = []
        for a in self.environment.organism_list:
            if not self.is_alive(a) or getattr(a, "is_hidden", False):
                continue
            if isinstance(a, (Mudskipper, Crab)):
                candidates.append(a)
            elif isinstance(a, Bird) and a.is_youth:
                candidates.append(a)
        close = [
            t for t in candidates
            if math.hypot(t.x - herd.x, t.y - herd.y) < attack_range
        ]
        if not close:
            return
        target = min(close, key=lambda a: math.hypot(a.x - herd.x, a.y - herd.y))
        if herd.power <= getattr(target, "power", 2):
            return
        self.kill_animal(target)
        self.add_corpse(target)
        self.log_event(f"개미 무리가 {self.animal_label(target)}를 제압했습니다!", "kill")
        lost = max(1, len(herd.ant_list) // 6)
        for _ in range(lost):
            if herd.ant_list:
                herd.ant_list.pop()
        herd.update_herd_power()
        if len(herd.ant_list) < 4:
            self.disband_ant_herd(herd)

    def update_nests(self):
        NEST_BRANCHES = [(70, 306), (250, 286), (445, 298), (625, 288), (770, 268)]

        if self.frame % 900 == 0:
            birds = [
                a for a in self.environment.organism_list
                if isinstance(a, Bird) and self.is_alive(a) and not a.is_youth
                and getattr(a, "_nest_cd", 0) <= self.frame
            ]
            for bird in birds:
                nearest = min(NEST_BRANCHES, key=lambda p: math.hypot(p[0] - bird.x, p[1] - bird.y))
                bx, by = nearest
                if not any(n["bx"] == bx and n["by"] == by for n in self.nests):
                    if random.random() < 0.4:
                        self.nests.append({
                            "bx": bx, "by": by,
                            "egg": False, "egg_timer": 0, "age": 0,
                        })
                        bird._nest_cd = self.frame + 3600
                        self.log_event("새가 나뭇가지에 둥지를 틀었습니다", "birth")

        for nest in list(self.nests):
            nest["age"] += 1
            if not nest["egg"]:
                if nest["age"] > 600 and self.frame % 120 == 0:
                    nearby = [
                        a for a in self.environment.organism_list
                        if isinstance(a, Bird) and not a.is_youth and self.is_alive(a)
                        and math.hypot(a.x - nest["bx"], a.y - nest["by"]) < 140
                    ]
                    if nearby and random.random() < 0.3:
                        nest["egg"] = True
                        nest["egg_timer"] = random.randint(1800, 2400)
                        self.log_event("새가 둥지에 알을 낳았습니다", "birth")
            else:
                nest["egg_timer"] -= 1
                if nest["egg_timer"] <= 0:
                    nest["egg"] = False
                    bird_count = sum(isinstance(a, Bird) for a in self.environment.organism_list)
                    if bird_count < 7:
                        self.spawn_young(Bird, nest["bx"], nest["by"] - 10)
                        self.log_event("둥지에서 새끼 새가 부화했습니다!", "birth")
                    else:
                        self.log_event("둥지 알이 부화했지만 개체수 포화", "info")
            if nest["age"] > 18000 and not nest["egg"]:
                self.nests.remove(nest)

        if self.frame % 60 == 0:
            crabs = [
                a for a in self.environment.organism_list
                if isinstance(a, Crab) and self.is_alive(a) and not a.is_hidden
            ]
            for crab in crabs:
                for nest in self.nests:
                    if (
                        nest["egg"]
                        and nest["by"] > 270
                        and math.hypot(crab.x - nest["bx"], crab.y - nest["by"]) < 100
                        and random.random() < 0.015
                    ):
                        nest["egg"] = False
                        if hasattr(crab, "_eat"):
                            crab._eat()
                        self.log_event("게가 둥지의 알을 훔쳐 먹었습니다!", "kill")
                        break

    def check_bird_migration(self):
        if self.frame % 600 != 0:
            return
        birds = [
            a for a in self.environment.organism_list
            if isinstance(a, Bird) and self.is_alive(a) and not a.is_youth
        ]
        if len(birds) <= 4:
            return
        emigrant = random.choice(birds)
        self.environment.remove_organism(emigrant)
        self.log_event("새 한 마리가 다른 서식지로 이주했습니다", "info")

    def draw_nests(self, camera):
        for nest in self.nests:
            nx = nest["bx"] - camera.x
            ny = nest["by"] - camera.y
            self.canvas.create_arc(
                nx - 14, ny - 4, nx + 14, ny + 10,
                start=0, extent=-180,
                fill="#6b4c27", outline="#4a3118", width=1,
                style=tk.CHORD, tags="animals",
            )
            self.canvas.create_arc(
                nx - 14, ny - 6, nx + 14, ny + 8,
                start=0, extent=-180,
                outline="#8b6535", width=2,
                style=tk.ARC, tags="animals",
            )
            if nest["egg"]:
                self.canvas.create_oval(
                    nx - 5, ny - 9, nx + 5, ny - 2,
                    fill="#e8d5b0", outline="#c8b480", tags="animals",
                )

    def school_wander_target(self):
        if self.frame >= self._school_until:
            depth = 25 if self.weather == "storm" else 0
            self._school_target = (random.uniform(260, 1080), random.uniform(400 + depth, 505 + depth))
            self._school_until = self.frame + random.randint(240, 420)
        return self._school_target

    def update_population_history(self):
        if self.frame % 120 != 0:
            return
        orgs = self.environment.organism_list
        self.pop_history.append({
            "물": sum(isinstance(a, Fish) and a.species == Fish.PREY for a in orgs) + len(self.sea_fish),
            "포": sum(isinstance(a, Fish) and a.species == Fish.PREDATOR for a in orgs),
            "게": sum(isinstance(a, Crab) for a in orgs),
            "망": sum(isinstance(a, Mudskipper) for a in orgs),
            "새": sum(isinstance(a, Bird) for a in orgs),
            "개": self.total_ant_count(),
        })
        del self.pop_history[:-90]

    def select_at(self, world_x, world_y):
        best = None
        best_distance = 42.0
        for animal in self.environment.organism_list:
            if not self.is_alive(animal):
                continue
            distance = math.hypot(animal.x - world_x, animal.y - world_y)
            if distance < best_distance:
                best = animal
                best_distance = distance
        self.selected = best
        self.follow_selected = best is not None

    def proximity_reproduction(self):
        if self.frame % 45 != 0:
            return
        specs = (
            (Crab, 6, 36, 2000, True),
            (Mudskipper, 6, 36, 2000, True),
            (Bird, 4, 44, 2600, False),
            (WatergunFish, 4, 40, 2600, False),
            (Ant, 14, 22, 1000, False),
        )
        for cls, cap, pair_dist, cooldown, needs_low_tide in specs:
            if needs_low_tide and not self.environment.is_low_tide:
                continue
            if cls is Bird and (self.is_night() or self.weather == "storm"):
                continue
            if cls is Ant:
                total = self.total_ant_count()
            else:
                total = sum(isinstance(animal, cls) for animal in self.environment.organism_list)
            if total >= cap:
                continue
            adults = [
                animal for animal in self.environment.organism_list
                if isinstance(animal, cls)
                and self.is_alive(animal)
                and not getattr(animal, "is_youth", False)
                and not getattr(animal, "is_hidden", False)
                and not getattr(animal, "is_falling", False)
                and getattr(animal, "_repro_cd", 0) <= self.frame
            ]
            done = False
            for index, first in enumerate(adults):
                if done:
                    break
                for second in adults[index + 1:]:
                    if self.distance(first, second) > pair_dist:
                        continue
                    self.spawn_young(cls, (first.x + second.x) / 2, (first.y + second.y) / 2)
                    self.log_event(f"{self.animal_label(first)} 새끼가 태어남", "birth")
                    stamp = self.frame + cooldown
                    first._repro_cd = stamp + random.randint(0, 400)
                    second._repro_cd = stamp + random.randint(0, 400)
                    done = True
                    break

    def spawn_young(self, cls, x, y):
        if cls is Crab:
            self.counts["crab"] += 1
            animal = Crab(x=x, y=y)
            animal._max_hunger = 9000
        elif cls is Bird:
            self.counts["bird"] += 1
            animal = Bird(x=x, y=max(40, y))
            animal._max_hunger = 7200
        elif cls is WatergunFish:
            self.counts["watergun"] += 1
            animal = WatergunFish(hit_chance=0.6, x=x, y=max(392, y))
            animal._max_hunger = 5400
        elif cls is Mudskipper:
            self.counts["mudskipper"] += 1
            animal = Mudskipper(power=1.4, place=(x, y), name="mudskipper", vmax=1, age=0)
            animal._max_hunger = 130
        elif cls is Ant:
            self.counts["ant"] += 1
            animal = Ant(x=x, y=y, v_xm=0.18, v_ym=0, name="ant", is_youth=True)
        else:
            return None
        animal.age = 0
        animal.is_youth = True
        return self.environment.add_organism(animal)

    def grow_youth(self):
        thresholds = ((Bird, 900), (Crab, 900), (WatergunFish, 900), (Mudskipper, 20), (Ant, 16))
        for animal in self.environment.organism_list:
            if isinstance(animal, Ant):
                animal.age += 1
            if isinstance(animal, Fish) or not getattr(animal, "is_youth", False):
                continue
            for cls, threshold in thresholds:
                if isinstance(animal, cls) and animal.age >= threshold:
                    animal.is_youth = False
                    break

    def low_tide_predation(self):
        if not self.is_night() and self.weather != "storm":
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
            and getattr(animal, "is_youth", True)
            and self.in_zone(animal, zone)
        ]
        if not predators or not prey:
            return

        for predator in predators:
            if getattr(predator, "_eat_cd", 0) > self.frame:
                continue
            if not self.predator_can_hunt_zone(predator, zone):
                continue

            target = min(prey, key=lambda animal: self.distance(predator, animal))
            self.move_predator_toward(predator, target, zone)
            if self.distance(predator, target) <= range_px and target in prey:
                self.kill_animal(target)
                prey.remove(target)
                hungry = getattr(predator, "_hunger", 0) > getattr(predator, "_max_hunger", 1) or getattr(predator, "is_starving", False)
                predator._eat_cd = self.frame + (300 if hungry else 600)
                self.log_event(f"[{self.zone_label(zone)}] {self.animal_label(predator)}가 치어를 잡아먹음", "kill")
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
        self.canvas.delete("hud")
        self.draw_saplings(camera)
        self.draw_nests(camera)
        for animal in self.environment.organism_list:
            if not self.is_alive(animal):
                continue
            self.draw_animal(animal, camera)
        self.draw_corpses(camera)
        self.draw_eggs(camera)
        self.draw_bubbles(camera)
        self.draw_water_overlay(camera)
        self.draw_night_overlay()
        self.draw_selection(camera)
        self.draw_weather()
        self.draw_panel()
        self.draw_event_feed()
        self.draw_population_graph()

    def draw_saplings(self, camera):
        for propagule in self.propagules:
            x = propagule["x"] - camera.x
            y = propagule["y"] - camera.y
            self.canvas.create_line(x, y - 9, x, y + 9, fill="#3f6212", width=3, tags="animals")
            self.canvas.create_oval(x - 2, y - 13, x + 2, y - 8, fill="#65a30d", outline="", tags="animals")
        for sapling in self.saplings:
            x = sapling["x"] - camera.x
            ground_y = mud_floor_level(sapling["x"]) - camera.y
            size = 10 + min(1.0, sapling["growth"] / 7200) * 22
            radius = size * 0.55
            self.canvas.create_line(x, ground_y, x, ground_y - size, fill="#5b3a1e", width=2, tags="animals")
            self.canvas.create_oval(x - radius, ground_y - size - radius * 0.9, x + radius, ground_y - size + radius * 0.5, fill="#2f6b46", outline="", tags="animals")
            self.canvas.create_oval(x - radius * 0.6, ground_y - size - radius, x + radius * 0.6, ground_y - size, fill="#3d7d52", outline="", tags="animals")

    def draw_corpses(self, camera):
        for corpse in self.corpses:
            x = corpse["x"] - camera.x
            y = corpse["y"] - camera.y
            self.canvas.create_oval(x - 12, y - 5, x + 12, y + 5, fill="#9ca3af", outline="#6b7280", tags="animals")
            for ex in (-5, 3):
                self.canvas.create_line(x + ex, y - 3, x + ex + 3, y, fill="#374151", tags="animals")
                self.canvas.create_line(x + ex + 3, y - 3, x + ex, y, fill="#374151", tags="animals")

    def draw_night_overlay(self):
        level = self.darkness_level()
        if level == 0:
            return
        stipple = "gray25" if level == 1 else "gray50"
        self.canvas.create_rectangle(-2000, -2000, 3000, 2800, fill="#0b1437", stipple=stipple, outline="", tags="animals")

    def draw_weather(self):
        if self.weather == "clear":
            return
        storm = self.weather == "storm"
        drops = 70 if storm else 38
        fall = 23 if storm else 15
        slant = 7 if storm else 3
        for index in range(drops):
            seed = (index * 173) % 911
            x = (seed * 7 + index * 53 - self.frame * slant) % (VIEW_W + 60) - 30
            y = (seed * 13 + self.frame * fall + index * 37) % (VIEW_H + 20) - 20
            self.canvas.create_line(x, y, x - slant, y + 12, fill="#9fc4d8", tags="hud")

    def draw_selection(self, camera):
        selected = self.selected
        if selected is None:
            return
        if not self.is_alive(selected) or selected not in self.environment.organism_list:
            self.selected = None
            return
        x = selected.x - camera.x
        y = selected.y - camera.y
        self.canvas.create_oval(x - 26, y - 26, x + 26, y + 26, outline="#fde047", width=2, tags="animals")
        stage = "치어·새끼" if getattr(selected, "is_youth", False) else "성체"
        info = f"나이 {getattr(selected, 'age', 0)}"
        max_hunger = getattr(selected, "_max_hunger", 0)
        if max_hunger and isinstance(selected, (Bird, Crab, Mudskipper, WatergunFish)):
            ratio = min(100, int(getattr(selected, "_hunger", 0) / max_hunger * 100))
            info += f"  허기 {ratio}%"
        if isinstance(selected, Fish) and selected.species == Fish.PREY and selected.is_youth and self.environment.is_low_tide:
            names = {"pool": "작은 웅덩이", "channel": "중앙수로", "mud_water": "진흙 웅덩이"}
            info += "  피난처: " + names.get(getattr(selected, "_refuge_name", None), "-")
        if isinstance(selected, Ant_herd):
            info += f"  무리 크기 {len(selected.ant_list)}"
        self.canvas.create_rectangle(300, 8, 624, 52, fill="#0d2730", stipple="gray50", outline="#475569", tags="hud")
        self.canvas.create_text(312, 21, anchor="w", text=f"추적 중: {self.animal_label(selected)} ({stage}) — 빈 곳 클릭으로 해제", fill="#fde047", font=("맑은 고딕", 9, "bold"), tags="hud")
        self.canvas.create_text(312, 39, anchor="w", text=info, fill="white", font=("맑은 고딕", 9), tags="hud")

    def draw_population_graph(self):
        if len(self.pop_history) < 2:
            return
        x0, y0, x1, y1 = 1293, 270, 1572, 420
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="#0d2730", stipple="gray50", outline="#334155", tags="hud")
        self.canvas.create_text(x0 + 8, y0 + 11, anchor="w", text="개체수 변화", fill="#94a3b8", font=("맑은 고딕", 8, "bold"), tags="hud")
        colors = {"물": "#f5d85b", "포": "#ef4444", "게": "#fb923c", "망": "#bda37a", "새": "#e2e8f0", "개": "#94a3b8"}
        legend_x = x0 + 70
        for key, color in colors.items():
            self.canvas.create_text(legend_x, y0 + 11, anchor="w", text=key, fill=color, font=("맑은 고딕", 8), tags="hud")
            legend_x += 26
        peak = max(10, max(max(snapshot.values()) for snapshot in self.pop_history))
        span = max(1, len(self.pop_history) - 1)
        for key, color in colors.items():
            coords = []
            for index, snapshot in enumerate(self.pop_history):
                px = x0 + 8 + index * (x1 - x0 - 16) / span
                py = y1 - 8 - (snapshot[key] / peak) * (y1 - y0 - 30)
                coords.extend([px, py])
            if len(coords) >= 4:
                self.canvas.create_line(*coords, fill=color, width=1, tags="hud")

    def draw_event_feed(self):
        now = time.monotonic()
        self.event_feed = [entry for entry in self.event_feed if now - entry[0] < 12]
        if not self.event_feed:
            return
        PX = 1295
        y_start = 430
        self.canvas.create_text(PX, y_start, anchor="nw", text="생태 로그",
                                fill="#94a3b8", font=("맑은 고딕", 9, "bold"), tags="hud")
        colors = {"kill": "#fda4af", "birth": "#bbf7d0", "info": "#e2e8f0"}
        entries = self.event_feed[-15:]
        for index, (stamp, text, kind) in enumerate(entries):
            self.canvas.create_text(
                PX, y_start + 18 + index * 18,
                anchor="nw",
                text=text,
                fill=colors.get(kind, "#e2e8f0"),
                font=("맑은 고딕", 8),
                tags="hud",
            )

    def draw_eggs(self, camera):
        for egg in self.eggs:
            ex = egg["x"] - camera.x
            ey = egg["y"] - camera.y
            color = "#ffe9a8" if egg["species"] == Fish.PREY else "#ffc1ae"
            for dx, dy in ((0, 0), (5, -3), (-5, 2), (3, 4), (-4, -4)):
                self.canvas.create_oval(
                    ex + dx - 2.5, ey + dy - 2.5,
                    ex + dx + 2.5, ey + dy + 2.5,
                    fill=color, outline="#caa86a", tags="animals",
                )

    def draw_bubbles(self, camera):
        for bubble in self.bubbles:
            bx = bubble["x"] - camera.x
            by = bubble["y"] - camera.y
            r = bubble["r"]
            self.canvas.create_oval(bx - r, by - r, bx + r, by + r, outline="#cdeee8", width=1, tags="animals")

    def draw_water_overlay(self, camera):
        if self.environment.is_low_tide:
            return
        oy = -camera.y
        self.canvas.create_rectangle(
            0, oy + 380, VIEW_W, oy + 545,
            fill="#3f8f91",
            outline="",
            stipple="gray25",
            tags="animals",
        )

    def draw_animal(self, animal, camera):
        if isinstance(animal, (Fish, WatergunFish)):
            x, y = self.render_swimmer_position(animal, camera)
        else:
            x = animal.x - camera.x
            y = animal.y - camera.y

        if isinstance(animal, WatergunFish):
            self.draw_watergun_fish(x, y, animal)
        elif isinstance(animal, Fish):
            self.draw_fish(x, y, animal)
        elif isinstance(animal, Mudskipper):
            self.draw_mudskipper(x, y, animal)
        elif isinstance(animal, Bird):
            self.draw_bird(x, y, animal)
        elif isinstance(animal, Crab):
            self.draw_crab(x, y, animal)
        elif isinstance(animal, Ant_herd):
            self.draw_ant_herd(x, y, animal)
        elif isinstance(animal, Ant):
            self.draw_ant(x, y, animal)

        if isinstance(animal, (Bird, Crab, Mudskipper, WatergunFish)) and not getattr(animal, "is_hidden", False):
            max_hunger = getattr(animal, "_max_hunger", 0)
            if max_hunger:
                ratio = min(1.5, getattr(animal, "_hunger", 0) / max_hunger)
                if ratio > 0.3:
                    fullness = 1 - min(1.0, ratio / 1.5)
                    color = "#4ade80" if ratio < 0.7 else ("#facc15" if ratio < 1.0 else "#f87171")
                    self.canvas.create_rectangle(x - 11, y - 27, x + 11, y - 24, fill="#1f2937", outline="", tags="animals")
                    self.canvas.create_rectangle(x - 11, y - 27, x - 11 + 22 * fullness, y - 24, fill=color, outline="", tags="animals")

    def draw_ant_herd(self, x, y, herd):
        for index in range(min(9, max(4, len(herd.ant_list) // 2))):
            ax = x + math.sin(index * 2.1 + self.frame * 0.05) * (8 + (index % 3) * 5)
            ay = y + math.cos(index * 1.7) * 4
            self.canvas.create_oval(ax - 3, ay - 3, ax + 3, ay + 3, fill="#17110c", outline="", tags="animals")
        self.canvas.create_text(x, y - 16, text=f"개미떼 ×{len(herd.ant_list)}", fill="#fbbf24", font=("맑은 고딕", 8, "bold"), tags="animals")

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
        phase = getattr(fish, "swim_phase", 0.0)
        wag = math.sin(self.frame * 0.27 + phase) * 4
        y += math.sin(self.frame * 0.06 + phase) * 1.3
        scale = (0.72 if fish.is_youth else 1.0) * max(0.35, fade)
        body = self.fade_color("#f5d85b" if not fish.is_youth else "#ffe88a", fade)
        stripe = self.fade_color("#c58a22", fade)
        outline = self.fade_color("#7a5a16", fade)
        d = 1 if getattr(fish, "swim_vx", 0.001) >= 0 else -1
        rx = 17 * scale
        ry = 8 * scale
        self.canvas.create_polygon(
            x - d * rx * 0.8, y,
            x - d * (rx + 12 * scale), y - 7 * scale + wag * scale,
            x - d * (rx + 12 * scale), y + 7 * scale + wag * scale,
            fill=body,
            outline=outline,
            tags="animals"
        )
        self.canvas.create_oval(x - rx, y - ry, x + rx, y + ry, fill=body, outline=outline, width=1, tags="animals")
        self.canvas.create_polygon(
            x - d * 2 * scale, y - ry + 1,
            x + d * 5 * scale, y - ry - 6 * scale,
            x + d * 10 * scale, y - ry + 1,
            fill=stripe,
            outline="",
            tags="animals"
        )
        for dx in (-6, 2, 9):
            self.canvas.create_line(x + d * dx * scale, y - ry + 2, x + d * (dx - 4) * scale, y + ry - 2, fill=stripe, width=1, tags="animals")
        fin_wag = math.sin(self.frame * 0.27 + phase + 1.2) * 3 * scale
        self.canvas.create_line(x, y + 3 * scale, x - d * 7 * scale, y + 7 * scale + fin_wag, fill=stripe, width=2, tags="animals")
        if fade > 0.3:
            ex1 = x + min(d * 8, d * 12) * scale
            ex2 = x + max(d * 8, d * 12) * scale
            self.canvas.create_oval(ex1, y - 3 * scale, ex2, y + 1 * scale, fill="black", outline="", tags="animals")
        if fish.is_youth and fade > 0.45:
            glow = self.fade_color("#fff4b8", fade)
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=glow, outline="", tags="animals")

    def draw_predator_fish(self, x, y, fish):
        scale = 0.82 if fish.is_youth else 1.0
        phase = getattr(fish, "swim_phase", 0.0)
        wag = math.sin(self.frame * 0.22 + phase) * 5 * scale
        y += math.sin(self.frame * 0.05 + phase) * 1.2
        body = "#c7352f"
        dark = "#5b1416"
        d = 1 if getattr(fish, "swim_vx", -0.001) >= 0 else -1
        self.canvas.create_polygon(x - d * 25 * scale, y, x - d * 43 * scale, y - 13 * scale + wag, x - d * 43 * scale, y + 13 * scale + wag, fill=dark, outline="", tags="animals")
        self.canvas.create_oval(x - 26 * scale, y - 12 * scale, x + 26 * scale, y + 12 * scale, fill=body, outline=dark, width=2, tags="animals")
        self.canvas.create_polygon(x + d * 12 * scale, y - 10 * scale, x - d * 4 * scale, y - 24 * scale, x - d * 14 * scale, y - 9 * scale, fill=dark, outline="", tags="animals")
        self.canvas.create_polygon(x + d * 23 * scale, y - 4 * scale, x + d * 33 * scale, y, x + d * 23 * scale, y + 4 * scale, fill="#f2f2e6", outline="", tags="animals")
        ex = x + d * 14.5 * scale
        ehalf = 2.5 * scale
        self.canvas.create_oval(ex - ehalf, y - 5 * scale, ex + ehalf, y, fill="black", outline="", tags="animals")
        self.canvas.create_line(x + d * 22 * scale, y + 5 * scale, x + d * 6 * scale, y + 8 * scale, fill=dark, width=2, tags="animals")

    def draw_watergun_fish(self, x, y, watergun=None):
        age = getattr(watergun, "age", 0)
        s = 0.62 if (watergun is not None and getattr(watergun, "is_youth", False)) else 1.0
        d = 1 if math.cos(age / 75) >= 0 else -1
        home_x = getattr(watergun, "home_x", 0)
        wag = math.sin(self.frame * 0.24 + home_x * 0.1) * 3 * s
        y += math.sin(self.frame * 0.07 + home_x * 0.05) * 1.1
        body = "#ccd8d3"
        dark = "#22303a"
        self.canvas.create_polygon(
            x - d * 16 * s, y,
            x - d * 31 * s, y - 9 * s + wag,
            x - d * 31 * s, y + 9 * s + wag,
            fill="#9fb2ad", outline="", tags="animals",
        )
        self.canvas.create_oval(x - 21 * s, y - 10 * s, x + 21 * s, y + 10 * s, fill=body, outline=dark, width=1, tags="animals")
        for bar_dx in (-12, -3, 6):
            self.canvas.create_polygon(
                x + d * bar_dx * s, y - 9 * s,
                x + d * (bar_dx + 5) * s, y - 9 * s,
                x + d * (bar_dx + 2) * s, y + 3 * s,
                fill=dark, outline="", tags="animals",
            )
        self.canvas.create_oval(x + d * 11 * s, y - 5 * s, x + d * 16 * s, y, fill="black", outline="", tags="animals")
        if not self.environment.is_low_tide and (self.frame // 90) % 4 == 0:
            for step in range(5):
                jet_x = x + d * (17 + step * 7) * s
                jet_y = y - (4 + step * 9) * s
                self.canvas.create_oval(jet_x - 1.5, jet_y - 1.5, jet_x + 1.5, jet_y + 1.5, fill="#d9f7ff", outline="", tags="animals")

    def draw_mudskipper(self, x, y, mudskipper):
        if mudskipper.is_hidden:
            self.canvas.create_oval(x - 15, y - 4, x + 15, y + 7, fill="#3f2c20", outline="", tags="animals")
            self.canvas.create_oval(x - 9, y - 6, x + 9, y + 3, fill="#4a3023", outline="", tags="animals")
            self.canvas.create_oval(x - 6, y - 9, x - 1, y - 4, fill="#f6e8bd", outline="", tags="animals")
            self.canvas.create_oval(x + 1, y - 9, x + 6, y - 4, fill="#f6e8bd", outline="", tags="animals")
            self.canvas.create_oval(x - 4.5, y - 8, x - 2.5, y - 6, fill="black", outline="", tags="animals")
            self.canvas.create_oval(x + 2.5, y - 8, x + 4.5, y - 6, fill="black", outline="", tags="animals")
            return

        y -= getattr(mudskipper, "_bounce", 0.0)
        s = 0.62 if getattr(mudskipper, "is_youth", False) else 1.0
        body = "#8b6f47"
        belly = "#a98c5e"
        self.canvas.create_polygon(x + 18 * s, y - 2 * s, x + 32 * s, y - 9 * s, x + 30 * s, y + 5 * s, fill=body, outline="", tags="animals")
        self.canvas.create_oval(x - 24 * s, y - 9 * s, x + 24 * s, y + 9 * s, fill=body, outline="", tags="animals")
        self.canvas.create_oval(x - 18 * s, y - 1 * s, x + 12 * s, y + 8 * s, fill=belly, outline="", tags="animals")
        self.canvas.create_arc(x - 14 * s, y - 18 * s, x + 12 * s, y - 2 * s, start=20, extent=140, fill="#6f5635", outline="", style=tk.CHORD, tags="animals")
        self.canvas.create_line(x - 14 * s, y + 6 * s, x - 20 * s, y + 13 * s, fill="#6f5635", width=3, tags="animals")
        self.canvas.create_line(x + 6 * s, y + 6 * s, x + 12 * s, y + 13 * s, fill="#6f5635", width=3, tags="animals")
        self.canvas.create_oval(x - 12 * s, y - 18 * s, x - 2 * s, y - 8 * s, fill="#f6e8bd", outline="", tags="animals")
        self.canvas.create_oval(x + 2 * s, y - 18 * s, x + 12 * s, y - 8 * s, fill="#f6e8bd", outline="", tags="animals")
        self.canvas.create_oval(x - 9 * s, y - 15 * s, x - 6 * s, y - 12 * s, fill="black", outline="", tags="animals")
        self.canvas.create_oval(x + 6 * s, y - 15 * s, x + 9 * s, y - 12 * s, fill="black", outline="", tags="animals")

    def draw_bird(self, x, y, bird=None):
        phase = (id(bird) % 10) * 0.6 if bird is not None else 0.0
        s = 0.62 if (bird is not None and getattr(bird, "is_youth", False)) else 1.0
        flap = math.sin(self.frame * 0.24 + phase) * 10 * s
        d = 1 if (bird is None or getattr(bird, "vx", 1) >= 0) else -1
        body = "#f8fafc"
        dark = "#475569"
        self.canvas.create_polygon(x - d * 12 * s, y - 2 * s, x - d * 23 * s, y - 6 * s + flap * 0.25, x - d * 20 * s, y + 3 * s, fill=body, outline=dark, tags="animals")
        self.canvas.create_oval(x - 14 * s, y - 5 * s, x + 14 * s, y + 6 * s, fill=body, outline=dark, tags="animals")
        self.canvas.create_oval(x + d * 10 * s, y - 10 * s, x + d * 22 * s, y, fill=body, outline=dark, tags="animals")
        self.canvas.create_polygon(x + d * 21 * s, y - 6 * s, x + d * 31 * s, y - 4 * s, x + d * 21 * s, y - 2 * s, fill="#f59e0b", outline="", tags="animals")
        self.canvas.create_oval(x + d * 15 * s, y - 8 * s, x + d * 18 * s, y - 5 * s, fill="black", outline="", tags="animals")
        self.canvas.create_polygon(
            x - d * 2 * s, y - 2 * s,
            x - d * 11 * s, y - 14 * s - flap,
            x + d * 8 * s, y - 8 * s - flap * 0.6,
            fill="#e2e8f0", outline=dark, tags="animals",
        )

    def draw_crab(self, x, y, crab):
        if crab.is_hidden:
            self.canvas.create_oval(x - 16, y - 4, x + 16, y + 8, fill="#3a2a1e", outline="", tags="animals")
            self.canvas.create_oval(x - 10, y - 6, x + 10, y + 4, fill="#46321f", outline="", tags="animals")
            self.canvas.create_oval(x - 5, y - 8, x - 1, y - 4, fill="#1c1917", outline="", tags="animals")
            self.canvas.create_oval(x + 1, y - 8, x + 5, y - 4, fill="#1c1917", outline="", tags="animals")
            return

        s = 0.62 if getattr(crab, "is_youth", False) else 1.0
        color = "#c2410c"
        shade = "#9a3008"
        step = math.sin(self.frame * 0.3 + x * 0.05) * 3 * s
        for index, dx in enumerate((-12, -4, 4, 12)):
            lift = step if index % 2 == 0 else -step
            self.canvas.create_line(x + dx * s, y + 6 * s, x + (dx - 8) * s, y + 16 * s + lift * 0.4, fill=color, width=2, tags="animals")
            self.canvas.create_line(x + dx * s, y + 6 * s, x + (dx + 8) * s, y + 16 * s - lift * 0.4, fill=color, width=2, tags="animals")
        self.canvas.create_oval(x - 18 * s, y - 10 * s, x + 18 * s, y + 10 * s, fill=color, outline=shade, width=1, tags="animals")
        self.canvas.create_oval(x - 30 * s, y - 10 * s, x - 16 * s, y + 2 * s, fill=color, outline=shade, tags="animals")
        self.canvas.create_oval(x + 16 * s, y - 10 * s, x + 30 * s, y + 2 * s, fill=color, outline=shade, tags="animals")
        self.canvas.create_line(x - 28 * s, y - 8 * s, x - 24 * s, y - 13 * s, fill=shade, width=2, tags="animals")
        self.canvas.create_line(x + 28 * s, y - 8 * s, x + 24 * s, y - 13 * s, fill=shade, width=2, tags="animals")
        self.canvas.create_line(x - 6 * s, y - 9 * s, x - 8 * s, y - 16 * s, fill=shade, width=2, tags="animals")
        self.canvas.create_line(x + 6 * s, y - 9 * s, x + 8 * s, y - 16 * s, fill=shade, width=2, tags="animals")
        self.canvas.create_oval(x - 11 * s, y - 20 * s, x - 5 * s, y - 14 * s, fill="#1c1917", outline="", tags="animals")
        self.canvas.create_oval(x + 5 * s, y - 20 * s, x + 11 * s, y - 14 * s, fill="#1c1917", outline="", tags="animals")

    def draw_ant(self, x, y, ant=None):
        s = 0.7 if (ant is not None and getattr(ant, "is_youth", False)) else 1.0
        wiggle = math.sin(self.frame * 0.5 + x * 0.3)
        for dx in (-6, 0, 6):
            self.canvas.create_oval(x + (dx - 3.5) * s, y - 3.5 * s, x + (dx + 3.5) * s, y + 3.5 * s, fill="#17110c", outline="", tags="animals")
        for index, dx in enumerate((-5, 0, 5)):
            spread = 1 if index % 2 == 0 else -1
            self.canvas.create_line(x + dx * s, y, x + (dx - 4) * s, y + (6 + wiggle * spread) * s, fill="#17110c", tags="animals")
            self.canvas.create_line(x + dx * s, y, x + (dx + 4) * s, y + (6 - wiggle * spread) * s, fill="#17110c", tags="animals")
        self.canvas.create_line(x + 8 * s, y - 2 * s, x + 12 * s, y + (-6 + wiggle) * s, fill="#17110c", tags="animals")
        self.canvas.create_line(x + 8 * s, y - 2 * s, x + 11 * s, y + (-7 - wiggle) * s, fill="#17110c", tags="animals")

    def draw_panel(self):
        orgs = self.environment.organism_list
        fish_a = sum(isinstance(a, Fish) and a.species == Fish.PREY and not a.is_youth for a in orgs)
        fish_y = sum(isinstance(a, Fish) and a.species == Fish.PREY and a.is_youth for a in orgs)
        pred_a = sum(isinstance(a, Fish) and a.species == Fish.PREDATOR and not a.is_youth for a in orgs)
        pred_y = sum(isinstance(a, Fish) and a.species == Fish.PREDATOR and a.is_youth for a in orgs)
        bird_a = sum(isinstance(a, Bird) and not a.is_youth for a in orgs)
        bird_y = sum(isinstance(a, Bird) and a.is_youth for a in orgs)
        crab_a = sum(isinstance(a, Crab) and not a.is_youth for a in orgs)
        crab_y = sum(isinstance(a, Crab) and a.is_youth for a in orgs)
        mud_a = sum(isinstance(a, Mudskipper) and not a.is_youth for a in orgs)
        mud_y = sum(isinstance(a, Mudskipper) and a.is_youth for a in orgs)
        wg = sum(isinstance(a, WatergunFish) for a in orgs)
        ant = self.total_ant_count()
        tide = "간조" if self.environment.is_low_tide else "만조"
        day_n = self.frame // self.DAY_LENGTH + 1
        time_lbl = "밤" if self.is_night() else "낮"
        wx_lbl = {"clear": "맑음", "rain": "비", "storm": "폭풍"}[self.weather]

        PX = 1295
        PW = 275

        self.canvas.create_rectangle(1290, 0, VIEW_W + 300, VIEW_H, fill="#0b1e24", outline="#1e3a4a", width=1, tags="hud")
        self.canvas.create_text(PX + PW // 2, 18, text="맹그로브 생태 정보",
                                fill="#94a3b8", font=("맑은 고딕", 11, "bold"), anchor="center", tags="hud")

        self.canvas.create_rectangle(PX - 2, 30, PX + PW + 2, 50, fill="#162230", outline="", tags="hud")
        self.canvas.create_text(PX, 40, anchor="w",
                                text=f"조수: {tide}  {day_n}일차 {time_lbl}  {wx_lbl}",
                                fill="white", font=("맑은 고딕", 9, "bold"), tags="hud")

        y = 66
        for col, lbl in ((0, "생물"), (110, "성체"), (175, "새끼"), (235, "합계")):
            self.canvas.create_text(PX + col, y, anchor="w", text=lbl,
                                    fill="#64748b", font=("맑은 고딕", 9, "bold"), tags="hud")

        rows = [
            ("물고기",   fish_a,  fish_y,  "#f5d85b"),
            ("포식자",   pred_a,  pred_y,  "#ef4444"),
            ("망둥어",   mud_a,   mud_y,   "#bda37a"),
            ("새",      bird_a,  bird_y,  "#e2e8f0"),
            ("게",      crab_a,  crab_y,  "#fb923c"),
            ("물총고기", wg,      0,       "#9fb2ad"),
            ("개미",    ant,     0,       "#94a3b8"),
            ("둥지/알", len(self.nests), sum(1 for n in self.nests if n["egg"]), "#c8b480"),
        ]
        for idx, (name, adults, youth, color) in enumerate(rows):
            ry = y + 20 + idx * 22
            total = adults + youth
            self.canvas.create_text(PX,       ry, anchor="w", text=name,      fill=color,    font=("맑은 고딕", 9), tags="hud")
            self.canvas.create_text(PX + 130, ry, anchor="w", text=str(adults), fill="white", font=("맑은 고딕", 9), tags="hud")
            self.canvas.create_text(PX + 190, ry, anchor="w", text=str(youth),  fill="#86efac", font=("맑은 고딕", 9), tags="hud")
            self.canvas.create_text(PX + 250, ry, anchor="w", text=str(total),  fill="#cbd5e1", font=("맑은 고딕", 9), tags="hud")

        fy = y + 20 + len(rows) * 22
        self.canvas.create_text(PX, fy + 4, anchor="w",
                                text=f"물고기 알: {len(self.eggs)}",
                                fill="#ffe9a8", font=("맑은 고딕", 9), tags="hud")


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
        self.x = 1090
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
        self.frame.place(x=1295, y=595)
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
                takefocus=0,
            ).grid(
                row=index // 2,
                column=index % 2,
                padx=2,
                pady=2
            )


class SimControls:
    def __init__(self, root, app):
        self.app = app
        self.frame = tk.Frame(root, bg="#0d2730")
        self.frame.place(x=1295, y=555)
        font = ("맑은 고딕", 9)
        common = {"bg": "#f3f4f6", "activebackground": "#d1d5db", "font": font, "takefocus": 0}
        self.pause_button = tk.Button(self.frame, text="⏸ 정지", width=7, command=app.toggle_pause, **common)
        self.speed_button = tk.Button(self.frame, text="배속 ×1", width=7, command=app.cycle_speed, **common)
        zoom_in_button = tk.Button(self.frame, text="＋", width=2, command=app.zoom_in, **common)
        zoom_out_button = tk.Button(self.frame, text="－", width=2, command=app.zoom_out, **common)
        for column, widget in enumerate((self.pause_button, self.speed_button, zoom_in_button, zoom_out_button)):
            widget.grid(row=0, column=column, padx=2, pady=2)

    def refresh(self):
        self.pause_button.config(text="▶ 재생" if self.app.paused else "⏸ 정지")
        self.speed_button.config(text=f"배속 ×{self.app.speed}")


class MangroveSimulation:
    FRAME_DELAY_MS = 16

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("맹그로브 늪지 생태계")
        self.root.geometry(f"{VIEW_W + 300}x{VIEW_H}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=VIEW_W + 300, height=VIEW_H, highlightthickness=0)
        self.canvas.pack()

        self.keys = {"Left": False, "Right": False, "Up": False, "Down": False}
        self.paused = False
        self.speed = 1
        self.zoom = 1.0
        self.camera = Camera()
        self.background = Background(self.canvas)
        self.animal_layer = AnimalLayer(self.canvas)
        self.time_display = TimeDisplay(self.canvas)
        self.minimap = MiniMap(self.canvas, self.camera)
        self.menu_panel = MenuPanel(self.canvas)
        self.menu_button = MenuButton(self.canvas, self.menu_panel)
        self.animal_controls = AnimalControls(self.root, self.animal_layer)
        self.sim_controls = SimControls(self.root, self)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.bind_keys()
        self.game_loop()

    def on_canvas_click(self, event):
        cx, cy = VIEW_W // 2, VIEW_H // 2
        world_x = self.camera.x + cx + (event.x - cx) / self.zoom
        world_y = self.camera.y + cy + (event.y - cy) / self.zoom
        self.animal_layer.select_at(world_x, world_y)

    def toggle_pause(self, event=None):
        self.paused = not self.paused
        self.sim_controls.refresh()

    def set_speed(self, value):
        self.speed = value
        self.sim_controls.refresh()

    def cycle_speed(self):
        order = {1: 2, 2: 4, 4: 8, 8: 1}
        self.set_speed(order.get(self.speed, 1))

    def zoom_in(self, event=None):
        self.zoom = min(2.2, round(self.zoom * 1.15, 3))

    def zoom_out(self, event=None):
        self.zoom = max(0.6, round(self.zoom / 1.15, 3))

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def bind_keys(self):
        self.root.bind("<KeyPress-Left>", lambda event: self.set_key("Left", True))
        self.root.bind("<KeyPress-Right>", lambda event: self.set_key("Right", True))
        self.root.bind("<KeyPress-Up>", lambda event: self.set_key("Up", True))
        self.root.bind("<KeyPress-Down>", lambda event: self.set_key("Down", True))
        self.root.bind("<KeyRelease-Left>", lambda event: self.set_key("Left", False))
        self.root.bind("<KeyRelease-Right>", lambda event: self.set_key("Right", False))
        self.root.bind("<KeyRelease-Up>", lambda event: self.set_key("Up", False))
        self.root.bind("<KeyRelease-Down>", lambda event: self.set_key("Down", False))
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("+", self.zoom_in)
        self.root.bind("=", self.zoom_in)
        self.root.bind("-", self.zoom_out)
        self.root.bind("<MouseWheel>", self.on_mousewheel)
        for key, value in (("1", 1), ("2", 2), ("3", 4), ("4", 8)):
            self.root.bind(key, lambda event, v=value: self.set_speed(v))

    def set_key(self, key, value):
        self.keys[key] = value
        if value:
            self.animal_layer.follow_selected = False

    def game_loop(self):
        now = time.monotonic()
        dt = now - getattr(self, "_last_loop", now)
        self._last_loop = now

        self.camera.update(self.keys)

        layer = self.animal_layer
        selected = layer.selected
        if (
            selected is not None
            and layer.follow_selected
            and layer.is_alive(selected)
            and selected in layer.environment.organism_list
        ):
            follow_x = max(self.camera.min_x, min(self.camera.max_x, selected.x - VIEW_W // 2))
            follow_y = max(self.camera.min_y, min(self.camera.max_y, selected.y - VIEW_H // 2))
            self.camera.x += (follow_x - self.camera.x) * 0.08
            self.camera.y += (follow_y - self.camera.y) * 0.08

        environment = self.animal_layer.environment
        if self.paused:
            environment.last_tide_change += dt
        else:
            for _ in range(self.speed):
                self.animal_layer.update()
            if self.speed > 1:
                environment.last_tide_change -= dt * (self.speed - 1)

        self.background.draw(self.camera, self.animal_layer.tide_level)
        self.animal_layer.draw(self.camera)

        if self.zoom != 1.0:
            cx, cy = VIEW_W // 2, VIEW_H // 2
            self.canvas.scale("world", cx, cy, self.zoom, self.zoom)
            self.canvas.scale("animals", cx, cy, self.zoom, self.zoom)

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
