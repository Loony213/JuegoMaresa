import os
import sys
import math
import random
import pygame
from pygame.locals import QUIT, MOUSEMOTION, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE

# ============================================================
# DATA CHEF MARESA
# NUEVO FRONTEND - "COCINA DIGITAL"
#
# Mantiene:
#   - Pygame
#   - assets existentes
#   - selección de áreas
#   - F2 para cargar personaje
#   - ESC para salir
#   - navegación hacia pantalla_02_data_chef.py
#
# El cambio es visual/UI/UX.
# ============================================================

WIDTH, HEIGHT = 1440, 840
FPS = 60

# ------------------------------------------------------------
# PALETA
# ------------------------------------------------------------
BG = (247, 245, 241)
BG_WARM = (252, 249, 244)
WHITE = (255, 255, 255)
INK = (30, 42, 54)
INK_2 = (54, 67, 80)
MUTED = (116, 126, 137)
MUTED_2 = (158, 166, 174)
ORANGE = (245, 126, 27)
ORANGE_DARK = (218, 89, 8)
ORANGE_SOFT = (255, 238, 218)
LINE = (224, 226, 226)
LINE_2 = (235, 234, 231)
GREEN = (67, 161, 102)
BLUE = (56, 123, 216)
PURPLE = (133, 88, 180)
RED = (207, 78, 78)
CYAN = (50, 151, 171)
SHADOW = (34, 45, 57)

ASSETS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets",
)


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def asset_path(name):
    return os.path.join(ASSETS, name)


def load_image(name, max_size=None):
    path = asset_path(name)

    if not os.path.exists(path):
        print(f"[DATA CHEF] No existe: {path}")
        return None

    try:
        image = pygame.image.load(path).convert_alpha()

        if max_size:
            max_w, max_h = max_size
            w, h = image.get_size()

            if w > max_w or h > max_h:
                scale = min(max_w / w, max_h / h)
                image = pygame.transform.smoothscale(
                    image,
                    (
                        max(1, int(w * scale)),
                        max(1, int(h * scale)),
                    ),
                )

        return image

    except Exception as exc:
        print(f"[DATA CHEF] Error cargando {path}: {exc}")
        return None


def rounded_rect(
    surface,
    rect,
    color,
    radius=18,
    border=0,
    border_color=None,
):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius,
    )

    if border:
        pygame.draw.rect(
            surface,
            border_color or color,
            rect,
            width=border,
            border_radius=radius,
        )


def draw_text(
    surface,
    text,
    font,
    color,
    pos,
    center=False,
):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(rendered, rect)
    return rect


def draw_multiline(
    surface,
    lines,
    font,
    color,
    center_x,
    start_y,
    gap=2,
):
    y = start_y

    for line in lines:
        r = draw_text(
            surface,
            line,
            font,
            color,
            (center_x, y),
            center=True,
        )
        y += r.height + gap


def draw_line_arrow(
    surface,
    start,
    end,
    color,
    width=2,
):
    pygame.draw.line(
        surface,
        color,
        start,
        end,
        width,
    )

    angle = math.atan2(
        end[1] - start[1],
        end[0] - start[0],
    )

    size = 7

    p1 = (
        end[0] - math.cos(angle - 0.5) * size,
        end[1] - math.sin(angle - 0.5) * size,
    )
    p2 = (
        end[0] - math.cos(angle + 0.5) * size,
        end[1] - math.sin(angle + 0.5) * size,
    )

    pygame.draw.polygon(
        surface,
        color,
        [end, p1, p2],
    )


def draw_check(surface, center, color, radius=10):
    pygame.draw.circle(
        surface,
        color,
        center,
        radius,
    )

    x, y = center

    pygame.draw.line(
        surface,
        WHITE,
        (x - 4, y),
        (x - 1, y + 4),
        2,
    )

    pygame.draw.line(
        surface,
        WHITE,
        (x - 1, y + 4),
        (x + 5, y - 4),
        2,
    )


# ------------------------------------------------------------
# PARTÍCULAS
# ------------------------------------------------------------
class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.r = random.choice([1, 1, 2])
        self.alpha = random.randint(30, 85)
        self.speed = random.uniform(0.08, 0.3)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, t):
        self.y -= self.speed
        self.x += math.sin(
            t * 0.001 + self.phase
        ) * 0.04

        if self.y < -5:
            self.y = HEIGHT + 5
            self.x = random.uniform(0, WIDTH)

    def draw(self, surface):
        layer = pygame.Surface(
            (8, 8),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            layer,
            (*ORANGE, self.alpha),
            (4, 4),
            self.r,
        )

        surface.blit(
            layer,
            (
                int(self.x - 4),
                int(self.y - 4),
            ),
        )


# ------------------------------------------------------------
# ESTACIÓN DE COCINA
# ------------------------------------------------------------
class KitchenStation:
    def __init__(
        self,
        rect,
        role,
        description,
        color,
        image_name,
        number,
    ):
        self.base_rect = pygame.Rect(rect)
        self.rect = pygame.Rect(rect)

        self.role = role
        self.description = description
        self.color = color
        self.image_name = image_name
        self.number = number

        self.image = load_image(
            image_name,
            (105, 72),
        )

        self.hover = 0.0
        self.selected = False
        self.pulse = random.random() * math.pi * 2

    def update(self, mouse, dt):
        inside = self.base_rect.collidepoint(mouse)

        target = 1.0 if inside else 0.0

        self.hover += (
            target - self.hover
        ) * min(1.0, dt * 12)

        self.rect.x = self.base_rect.x
        self.rect.y = (
            self.base_rect.y
            - int(self.hover * 3)
        )

        self.pulse += dt * 2

        return inside

    def draw(self, surface, fonts, mouse):
        inside = self.base_rect.collidepoint(mouse)

        # Sombra
        shadow = pygame.Surface(
            (
                self.rect.w + 20,
                self.rect.h + 20,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            shadow,
            (35, 45, 55, 22 + int(self.hover * 15)),
            (
                8,
                10,
                self.rect.w,
                self.rect.h,
            ),
            border_radius=16,
        )

        surface.blit(
            shadow,
            (
                self.rect.x - 4,
                self.rect.y - 3,
            ),
        )

        # Fondo
        bg = (
            (255, 255, 255)
            if not inside
            else (255, 252, 247)
        )

        border = (
            self.color
            if inside or self.selected
            else LINE
        )

        border_width = (
            2
            if inside or self.selected
            else 1
        )

        rounded_rect(
            surface,
            self.rect,
            bg,
            radius=16,
            border=border_width,
            border_color=border,
        )

        # Banda de color
        pygame.draw.rect(
            surface,
            self.color,
            (
                self.rect.x,
                self.rect.y,
                5,
                self.rect.h,
            ),
            border_top_left_radius=16,
            border_bottom_left_radius=16,
        )

        # Número
        number_circle = (
            self.rect.x + 27,
            self.rect.y + 25,
        )

        pygame.draw.circle(
            surface,
            (
                self.color
                if inside or self.selected
                else (242, 242, 240)
            ),
            number_circle,
            14,
        )

        draw_text(
            surface,
            f"{self.number:02d}",
            fonts["micro_bold"],
            (
                WHITE
                if inside or self.selected
                else MUTED
            ),
            number_circle,
            center=True,
        )

        # Imagen
        image_box = pygame.Rect(
            self.rect.x + 52,
            self.rect.y + 10,
            106,
            self.rect.h - 20,
        )

        rounded_rect(
            surface,
            image_box,
            (
                247,
                247,
                245,
            ),
            radius=12,
        )

        # Línea decorativa
        pygame.draw.line(
            surface,
            LINE_2,
            (
                image_box.x + 8,
                image_box.bottom - 9,
            ),
            (
                image_box.right - 8,
                image_box.bottom - 9,
            ),
            1,
        )

        if self.image:
            img = self.image

            if self.hover > 0:
                factor = 1 + self.hover * 0.035

                img = pygame.transform.smoothscale(
                    img,
                    (
                        max(
                            1,
                            int(
                                img.get_width()
                                * factor
                            ),
                        ),
                        max(
                            1,
                            int(
                                img.get_height()
                                * factor
                            ),
                        ),
                    ),
                )

            ir = img.get_rect(
                center=image_box.center
            )

            surface.blit(
                img,
                ir,
            )

        # Información
        info_x = self.rect.x + 173

        title_color = (
            self.color
            if inside or self.selected
            else INK
        )

        draw_text(
            surface,
            self.role,
            fonts["station"],
            title_color,
            (info_x, self.rect.y + 18),
        )

        draw_multiline(
            surface,
            self.description,
            fonts["micro"],
            MUTED,
            info_x + 77,
            self.rect.y + 46,
            gap=1,
        )

        # CTA
        cta = pygame.Rect(
            self.rect.right - 127,
            self.rect.y + 16,
            106,
            32,
        )

        if inside or self.selected:
            cta_bg = self.color
            cta_text = WHITE
            label = "ENTRAR  →"
        else:
            cta_bg = (246, 246, 244)
            cta_text = INK_2
            label = "SELECCIONAR"

        rounded_rect(
            surface,
            cta,
            cta_bg,
            radius=10,
        )

        draw_text(
            surface,
            label,
            fonts["micro_bold"],
            cta_text,
            cta.center,
            center=True,
        )

        # Estado seleccionado
        if self.selected:
            draw_check(
                surface,
                (
                    self.rect.right - 15,
                    self.rect.top + 15,
                ),
                self.color,
                7,
            )

        return cta


# ------------------------------------------------------------
# APP
# ------------------------------------------------------------
class DataChefApp:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption(
            "DATA CHEF | MARESA"
        )

        self.window = pygame.display.set_mode(
            (0, 0),
            pygame.RESIZABLE,
        )

        self.screen = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        self.clock = pygame.time.Clock()

        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.fonts = {
            "micro": pygame.font.SysFont(
                "Segoe UI",
                11,
            ),
            "micro_bold": pygame.font.SysFont(
                "Segoe UI",
                11,
                bold=True,
            ),
            "small": pygame.font.SysFont(
                "Segoe UI",
                14,
            ),
            "body": pygame.font.SysFont(
                "Segoe UI",
                16,
            ),
            "station": pygame.font.SysFont(
                "Segoe UI",
                14,
                bold=True,
            ),
            "subtitle": pygame.font.SysFont(
                "Segoe UI",
                18,
                bold=True,
            ),
            "title": pygame.font.SysFont(
                "Segoe UI",
                47,
                bold=True,
            ),
            "hero": pygame.font.SysFont(
                "Segoe UI",
                59,
                bold=True,
            ),
            "brand": pygame.font.SysFont(
                "Segoe UI",
                22,
                bold=True,
            ),
            "section": pygame.font.SysFont(
                "Segoe UI",
                20,
                bold=True,
            ),
        }

        self.logo = load_image(
            "logo_maresa.png",
            (155, 45),
        )

        self.chef = load_image(
            "chef.png",
            (430, 590),
        )

        self.bg_image = load_image(
            "fondo.png",
            (WIDTH, HEIGHT),
        )

        # ----------------------------------------------------
        # ROLES - SE CONSERVAN
        # ----------------------------------------------------
        role_definitions = [
            (
                "TECNOLOGÍA",
                [
                    "Datos, sistemas",
                    "y calidad.",
                ],
                BLUE,
                "tecnologia.png",
            ),
            (
                "RECURSOS HUMANOS",
                [
                    "Talento, nómina",
                    "y desarrollo.",
                ],
                ORANGE,
                "rrhh.png",
            ),
            (
                "FINANZAS",
                [
                    "Presupuesto",
                    "y control contable.",
                ],
                GREEN,
                "finanzas.png",
            ),
            (
                "OPERACIONES",
                [
                    "Procesos, logística",
                    "y eficiencia.",
                ],
                PURPLE,
                "operaciones.png",
            ),
            (
                "COMERCIAL / VENTAS",
                [
                    "Clientes, mercado",
                    "y estrategia.",
                ],
                RED,
                "comercial.png",
            ),
            (
                "AUDITORÍA / RIESGO",
                [
                    "Riesgos, cumplimiento",
                    "y gobierno de datos.",
                ],
                CYAN,
                "auditoria.png",
            ),
        ]

        # ----------------------------------------------------
        # NUEVO LAYOUT:
        # izquierda = narrativa
        # centro = chef
        # derecha = estaciones horizontales
        # ----------------------------------------------------
        station_w = 490
        station_h = 89
        station_x = 875
        station_y = 167
        station_gap = 8

        self.cards = []

        for i, (
            role,
            description,
            color,
            image_name,
        ) in enumerate(role_definitions):

            y = (
                station_y
                + i
                * (station_h + station_gap)
            )

            self.cards.append(
                KitchenStation(
                    (
                        station_x,
                        y,
                        station_w,
                        station_h,
                    ),
                    role,
                    description,
                    color,
                    image_name,
                    i + 1,
                )
            )

        self.particles = [
            Particle()
            for _ in range(35)
        ]

        self.mouse = (0, 0)

        self.running = True
        self.selected_role = None

        self.message = ""
        self.message_timer = 0

        self.time = 0.0
        self.chef_bob = 0.0

    # --------------------------------------------------------
    # NAVEGACIÓN
    # --------------------------------------------------------
    def choose_role(self, role_name):
        self.selected_role = role_name

        for card in self.cards:
            card.selected = (
                card.role == role_name
            )

        self.message = (
            f"COCINA SELECCIONADA  •  {role_name}"
        )

        self.message_timer = 0.8

        pantalla_02 = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "pantalla_02_data_chef.py",
        )

        if not os.path.exists(
            pantalla_02
        ):
            self.message = (
                "Falta pantalla_02_data_chef.py"
            )
            self.message_timer = 3.0
            return

        # Mantiene el comportamiento original.
        role_arg = (
            "rrhh"
            if role_name == "RECURSOS HUMANOS"
            else "tecnologia"
        )

        try:
            import subprocess

            subprocess.Popen(
                [
                    sys.executable,
                    pantalla_02,
                    role_arg,
                ],
                cwd=os.path.dirname(
                    pantalla_02
                ),
            )

            self.running = False

        except Exception as exc:
            self.message = f"Error: {exc}"
            self.message_timer = 3.0

    # --------------------------------------------------------
    # F2
    # --------------------------------------------------------
    def open_image_picker(self):
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()

            path = filedialog.askopenfilename(
                title=(
                    "Selecciona una imagen de personaje"
                ),
                filetypes=[
                    (
                        "Imágenes",
                        "*.png *.jpg *.jpeg",
                    )
                ],
            )

            root.destroy()

            if not path:
                return

            for card in self.cards:
                if card.base_rect.collidepoint(
                    self.mouse
                ):
                    card.image = (
                        pygame.image.load(
                            path
                        ).convert_alpha()
                    )

                    w, h = (
                        card.image.get_size()
                    )

                    max_w = 106
                    max_h = 69

                    if w > max_w or h > max_h:
                        scale = min(
                            max_w / w,
                            max_h / h,
                        )

                        card.image = (
                            pygame.transform.smoothscale(
                                card.image,
                                (
                                    max(
                                        1,
                                        int(w * scale),
                                    ),
                                    max(
                                        1,
                                        int(h * scale),
                                    ),
                                ),
                            )
                        )

                    card.image_name = path

                    self.message = (
                        f"Imagen cargada para {card.role}"
                    )

                    self.message_timer = 2.5

                    break

        except Exception:
            pass

    # --------------------------------------------------------
    # FONDO
    # --------------------------------------------------------
    def draw_background(self):
        self.screen.fill(BG)

        # Base cálida
        pygame.draw.rect(
            self.screen,
            BG_WARM,
            (
                0,
                0,
                WIDTH,
                HEIGHT,
            ),
        )

        # Zona derecha ligeramente diferenciada
        pygame.draw.rect(
            self.screen,
            (250, 249, 247),
            (
                842,
                92,
                563,
                624,
            ),
        )

        # Grid fino
        for x in range(
            25,
            WIDTH,
            74,
        ):
            pygame.draw.line(
                self.screen,
                (239, 238, 235),
                (x, 92),
                (x, 715),
                1,
            )

        for y in range(
            105,
            720,
            74,
        ):
            pygame.draw.line(
                self.screen,
                (239, 238, 235),
                (0, y),
                (WIDTH, y),
                1,
            )

        # Halo naranja central
        glow = pygame.Surface(
            (620, 620),
            pygame.SRCALPHA,
        )

        for radius in range(
            260,
            20,
            -20,
        ):
            alpha = max(
                1,
                int(
                    12
                    * (
                        1
                        - radius / 280
                    )
                ),
            )

            pygame.draw.circle(
                glow,
                (
                    ORANGE[0],
                    ORANGE[1],
                    ORANGE[2],
                    alpha,
                ),
                (310, 310),
                radius,
            )

        self.screen.blit(
            glow,
            (230, 135),
        )

        # Arco decorativo
        pygame.draw.arc(
            self.screen,
            (239, 214, 191),
            (
                230,
                135,
                520,
                520,
            ),
            math.radians(205),
            math.radians(338),
            2,
        )

        # Partículas
        for particle in self.particles:
            particle.draw(self.screen)

        # Nodos
        for i in range(8):
            px = 42 + i * 180
            py = 112 + (
                math.sin(
                    self.time * 0.001
                    + i
                )
                * 7
            )

            pygame.draw.circle(
                self.screen,
                (222, 217, 209),
                (
                    int(px),
                    int(py),
                ),
                2,
            )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------
    def draw_header(self):
        # Logo
        if self.logo:
            self.screen.blit(
                self.logo,
                (45, 27),
            )
        else:
            draw_text(
                self.screen,
                "corporación maresa",
                self.fonts["brand"],
                ORANGE,
                (45, 31),
            )

        # Marca
        pygame.draw.line(
            self.screen,
            LINE,
            (210, 28),
            (210, 63),
            1,
        )

        draw_text(
            self.screen,
            "DATA",
            self.fonts["brand"],
            INK,
            (232, 29),
        )

        draw_text(
            self.screen,
            "CHEF",
            self.fonts["brand"],
            ORANGE,
            (294, 29),
        )

        # Estado
        status = pygame.Rect(
            1190,
            27,
            214,
            36,
        )

        rounded_rect(
            self.screen,
            status,
            WHITE,
            radius=18,
            border=1,
            border_color=LINE,
        )

        pygame.draw.circle(
            self.screen,
            GREEN,
            (1212, 45),
            5,
        )

        draw_text(
            self.screen,
            "EXPERIENCIA ACTIVA",
            self.fonts["micro_bold"],
            MUTED,
            (1225, 39),
        )

        # Botón cerrar
        close = pygame.Rect(
            1370,
            30,
            32,
            32,
        )

        rounded_rect(
            self.screen,
            close,
            (242, 242, 239),
            radius=10,
        )

        draw_text(
            self.screen,
            "×",
            self.fonts["subtitle"],
            MUTED,
            close.center,
            center=True,
        )

    # --------------------------------------------------------
    # HERO IZQUIERDO
    # --------------------------------------------------------
    def draw_left_content(self):
        # Etiqueta
        tag = pygame.Rect(
            46,
            104,
            204,
            30,
        )

        rounded_rect(
            self.screen,
            tag,
            ORANGE_SOFT,
            radius=15,
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (63, 119),
            4,
        )

        draw_text(
            self.screen,
            "LA COCINA DE LOS DATOS",
            self.fonts["micro_bold"],
            ORANGE_DARK,
            (75, 113),
        )

        # Título
        draw_text(
            self.screen,
            "BIENVENIDO A",
            self.fonts["subtitle"],
            INK_2,
            (46, 155),
        )

        data = draw_text(
            self.screen,
            "DATA",
            self.fonts["hero"],
            INK,
            (46, 181),
        )

        draw_text(
            self.screen,
            "CHEF",
            self.fonts["hero"],
            ORANGE,
            (
                46 + data.width + 11,
                181,
            ),
        )

        draw_text(
            self.screen,
            "TRANSFORMA DATOS EN DECISIONES.",
            self.fonts["section"],
            INK,
            (49, 256),
        )

        draw_text(
            self.screen,
            "Selecciona una cocina y comienza",
            self.fonts["body"],
            MUTED,
            (49, 293),
        )

        draw_text(
            self.screen,
            "tu receta de valor.",
            self.fonts["body"],
            MUTED,
            (49, 317),
        )

        # Misión
        mission = pygame.Rect(
            46,
            362,
            344,
            93,
        )

        rounded_rect(
            self.screen,
            mission,
            WHITE,
            radius=17,
            border=1,
            border_color=LINE,
        )

        pygame.draw.rect(
            self.screen,
            ORANGE,
            (
                mission.x,
                mission.y,
                5,
                mission.h,
            ),
            border_top_left_radius=17,
            border_bottom_left_radius=17,
        )

        draw_text(
            self.screen,
            "TU MISIÓN",
            self.fonts["micro_bold"],
            ORANGE,
            (69, 380),
        )

        draw_text(
            self.screen,
            "Prepara los datos con calidad,",
            self.fonts["small"],
            INK_2,
            (69, 404),
        )

        draw_text(
            self.screen,
            "precisión y trabajo en equipo.",
            self.fonts["small"],
            MUTED,
            (69, 425),
        )

        # Chef
        self.draw_chef()

        # Concepto
        concept = pygame.Rect(
            400,
            486,
            315,
            74,
        )

        rounded_rect(
            self.screen,
            concept,
            WHITE,
            radius=18,
            border=1,
            border_color=LINE,
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (424, 510),
            7,
        )

        draw_text(
            self.screen,
            "LOS DATOS SON",
            self.fonts["micro_bold"],
            MUTED,
            (442, 498),
        )

        draw_text(
            self.screen,
            "LOS INGREDIENTES.",
            self.fonts["subtitle"],
            INK,
            (442, 517),
        )

        draw_line_arrow(
            self.screen,
            (716, 523),
            (779, 523),
            ORANGE,
            2,
        )

        # CTA
        cta = pygame.Rect(
            46,
            595,
            344,
            48,
        )

        rounded_rect(
            self.screen,
            cta,
            ORANGE,
            radius=17,
        )

        draw_text(
            self.screen,
            "COMENZAR EXPERIENCIA",
            self.fonts["micro_bold"],
            WHITE,
            (145, 611),
        )

        draw_text(
            self.screen,
            "→",
            self.fonts["subtitle"],
            WHITE,
            (356, 605),
        )

        # Ingredientes
        draw_text(
            self.screen,
            "LOS 4 INGREDIENTES DEL CHEF",
            self.fonts["micro_bold"],
            MUTED,
            (47, 668),
        )

        ingredients = [
            ("01", "EXACTITUD", GREEN),
            ("02", "COMPLETITUD", BLUE),
            ("03", "CONSISTENCIA", ORANGE),
            ("04", "OPORTUNIDAD", PURPLE),
        ]

        x = 46

        for number, name, color in ingredients:
            pill = pygame.Rect(
                x,
                690,
                116,
                30,
            )

            rounded_rect(
                self.screen,
                pill,
                WHITE,
                radius=12,
                border=1,
                border_color=LINE,
            )

            pygame.draw.circle(
                self.screen,
                color,
                (
                    pill.x + 14,
                    pill.centery,
                ),
                4,
            )

            draw_text(
                self.screen,
                number,
                self.fonts["micro_bold"],
                MUTED_2,
                (
                    pill.x + 24,
                    pill.y + 8,
                ),
            )

            draw_text(
                self.screen,
                name,
                self.fonts["micro_bold"],
                color,
                (
                    pill.x + 43,
                    pill.y + 8,
                ),
            )

            x += 123

    # --------------------------------------------------------
    # CHEF
    # --------------------------------------------------------
    def draw_chef(self):
        if not self.chef:
            return

        bob = (
            math.sin(
                self.chef_bob
            )
            * 3
        )

        cx = 590
        cy = int(
            645 + bob
        )

        # Halo
        halo = pygame.Surface(
            (440, 540),
            pygame.SRCALPHA,
        )

        for radius in range(
            190,
            20,
            -20,
        ):
            alpha = max(
                1,
                int(
                    13
                    * (
                        1
                        - radius / 210
                    )
                ),
            )

            pygame.draw.circle(
                halo,
                (
                    ORANGE[0],
                    ORANGE[1],
                    ORANGE[2],
                    alpha,
                ),
                (220, 270),
                radius,
            )

        self.screen.blit(
            halo,
            (
                cx - 220,
                155,
            ),
        )

        # Sombra
        shadow = pygame.Surface(
            (310, 50),
            pygame.SRCALPHA,
        )

        pygame.draw.ellipse(
            shadow,
            (40, 48, 54, 40),
            (0, 8, 310, 38),
        )

        self.screen.blit(
            shadow,
            (
                cx - 155,
                651,
            ),
        )

        # Chef
        r = self.chef.get_rect()

        r.midbottom = (
            cx,
            cy,
        )

        self.screen.blit(
            self.chef,
            r,
        )

    # --------------------------------------------------------
    # HEADER ÁREAS
    # --------------------------------------------------------
    def draw_area_header(self):
        x = 875

        draw_text(
            self.screen,
            "ELIGE TU COCINA",
            self.fonts["section"],
            INK,
            (x, 104),
        )

        draw_text(
            self.screen,
            "Una estación, un reto, una receta de datos.",
            self.fonts["small"],
            MUTED,
            (x, 132),
        )

        # contador
        counter = pygame.Rect(
            1240,
            101,
            164,
            36,
        )

        rounded_rect(
            self.screen,
            counter,
            WHITE,
            radius=18,
            border=1,
            border_color=LINE,
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (1260, 119),
            4,
        )

        draw_text(
            self.screen,
            "06 ESTACIONES",
            self.fonts["micro_bold"],
            INK_2,
            (1272, 113),
        )

        # Línea guía
        pygame.draw.line(
            self.screen,
            LINE,
            (875, 151),
            (1404, 151),
            1,
        )

    # --------------------------------------------------------
    # RECETA INFERIOR
    # --------------------------------------------------------
    def draw_recipe_bar(self):
        bar = pygame.Rect(
            35,
            748,
            1370,
            60,
        )

        rounded_rect(
            self.screen,
            bar,
            WHITE,
            radius=17,
            border=1,
            border_color=LINE,
        )

        draw_text(
            self.screen,
            "TU RECETA",
            self.fonts["micro_bold"],
            ORANGE,
            (56, 758),
        )

        draw_text(
            self.screen,
            "01",
            self.fonts["micro_bold"],
            INK,
            (56, 778),
        )

        steps = [
            ("SELECCIONA", "Ingredientes"),
            ("PREPARA", "Limpia y valida"),
            ("COCINA", "Modela y organiza"),
            ("SIRVE", "Convierte en valor"),
        ]

        x_positions = [
            235,
            500,
            765,
            1030,
        ]

        for i, (
            title,
            desc,
        ) in enumerate(steps):

            x = x_positions[i]

            circle_color = (
                ORANGE
                if i == 0
                else (242, 241, 238)
            )

            pygame.draw.circle(
                self.screen,
                circle_color,
                (x, 778),
                15,
            )

            draw_text(
                self.screen,
                str(i + 1),
                self.fonts["micro_bold"],
                (
                    WHITE
                    if i == 0
                    else MUTED
                ),
                (x, 778),
                center=True,
            )

            draw_text(
                self.screen,
                title,
                self.fonts["micro_bold"],
                INK,
                (x + 25, 760),
            )

            draw_text(
                self.screen,
                desc,
                self.fonts["micro"],
                MUTED,
                (x + 25, 779),
            )

            if i < 3:
                pygame.draw.line(
                    self.screen,
                    LINE,
                    (x + 18, 778),
                    (
                        x_positions[i + 1] - 22,
                        778,
                    ),
                    1,
                )

        # Mensaje final
        final = pygame.Rect(
            1208,
            758,
            170,
            40,
        )

        rounded_rect(
            self.screen,
            final,
            ORANGE_SOFT,
            radius=12,
            border=1,
            border_color=ORANGE,
        )

        draw_text(
            self.screen,
            "DATOS → DECISIONES",
            self.fonts["micro_bold"],
            ORANGE_DARK,
            final.center,
            center=True,
        )

    # --------------------------------------------------------
    # MENSAJE
    # --------------------------------------------------------
    def draw_message(self):
        if self.message_timer <= 0:
            return

        box = pygame.Rect(
            450,
            600,
            420,
            38,
        )

        rounded_rect(
            self.screen,
            box,
            INK,
            radius=19,
        )

        draw_text(
            self.screen,
            self.message,
            self.fonts["micro_bold"],
            WHITE,
            box.center,
            center=True,
        )

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------
    def draw(self):
        self.draw_background()
        self.draw_header()
        self.draw_left_content()
        self.draw_area_header()

        for card in self.cards:
            card.draw(
                self.screen,
                self.fonts,
                self.mouse,
            )

        self.draw_recipe_bar()
        self.draw_message()

        # Atajos
        draw_text(
            self.screen,
            "F2  CARGAR PERSONAJE",
            self.fonts["micro"],
            MUTED_2,
            (36, 821),
        )

        draw_text(
            self.screen,
            "ESC  SALIR",
            self.fonts["micro"],
            MUTED_2,
            (180, 821),
        )

        # Responsive
        win_w, win_h = (
            self.window.get_size()
        )

        if (
            win_w == WIDTH
            and win_h == HEIGHT
        ):
            self.window.blit(
                self.screen,
                (0, 0),
            )

            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0

        else:
            scale = min(
                win_w / WIDTH,
                win_h / HEIGHT,
            )

            render_w = max(
                1,
                int(WIDTH * scale),
            )

            render_h = max(
                1,
                int(HEIGHT * scale),
            )

            self.scale = scale

            self.offset_x = (
                win_w - render_w
            ) // 2

            self.offset_y = (
                win_h - render_h
            ) // 2

            scaled = (
                pygame.transform.smoothscale(
                    self.screen,
                    (
                        render_w,
                        render_h,
                    ),
                )
            )

            self.window.fill(
                (232, 231, 228)
            )

            self.window.blit(
                scaled,
                (
                    self.offset_x,
                    self.offset_y,
                ),
            )

        pygame.display.flip()

    # --------------------------------------------------------
    # COORDENADAS
    # --------------------------------------------------------
    def to_logical(self, pos):
        x, y = pos

        if self.scale <= 0:
            return x, y

        return (
            int(
                (x - self.offset_x)
                / self.scale
            ),
            int(
                (y - self.offset_y)
                / self.scale
            ),
        )

    # --------------------------------------------------------
    # CLICK
    # --------------------------------------------------------
    def handle_click(self, pos):
        logical_pos = self.to_logical(pos)

        for card in self.cards:
            if card.base_rect.collidepoint(
                logical_pos
            ):
                self.choose_role(
                    card.role
                )
                return

    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------
    def run(self):
        while self.running:
            dt = (
                self.clock.tick(FPS)
                / 1000.0
            )

            self.time = (
                pygame.time.get_ticks()
            )

            self.chef_bob += dt * 2.4

            if self.message_timer > 0:
                self.message_timer -= dt

            for particle in self.particles:
                particle.update(
                    self.time
                )

            for card in self.cards:
                card.update(
                    self.mouse,
                    dt,
                )

            for event in pygame.event.get():

                if event.type == QUIT:
                    self.running = False

                elif event.type == MOUSEMOTION:
                    self.mouse = (
                        self.to_logical(
                            event.pos
                        )
                    )

                elif (
                    event.type
                    == MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.handle_click(
                        event.pos
                    )

                elif event.type == pygame.VIDEORESIZE:
                    self.window = (
                        pygame.display.set_mode(
                            event.size,
                            pygame.RESIZABLE,
                        )
                    )

                elif event.type == KEYDOWN:

                    if event.key == K_ESCAPE:
                        self.running = False

                    elif event.key == pygame.K_F2:
                        self.open_image_picker()

            self.draw()

        pygame.quit()


if __name__ == "__main__":
    DataChefApp().run()
