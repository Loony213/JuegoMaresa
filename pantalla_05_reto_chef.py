import os
import sys
import math
import random
import subprocess
import pygame

pygame.init()

# ============================================================
# DATA CHEF | MARESA
# PANTALLA 05 - RETO DEL CHEF
# Trivia de cultura general sobre calidad de datos
# ============================================================

WIDTH, HEIGHT = 1536, 864
FPS = 60

ORANGE = (239, 102, 8)
ORANGE_DARK = (196, 72, 0)
CREAM = (247, 244, 237)
CREAM_2 = (255, 251, 245)
DARK = (35, 48, 57)
NAVY = (27, 43, 53)
NAVY_2 = (39, 59, 70)
BLUE = (59, 143, 211)
GREEN = (46, 154, 89)
RED = (203, 67, 51)
PURPLE = (124, 88, 171)
GRAY = (115, 126, 137)
LIGHT_GRAY = (224, 227, 225)
LINE = (220, 216, 208)
WHITE = (255, 255, 255)

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")


# ============================================================
# UTILIDADES
# ============================================================

def load_img(name, max_size=None):
    path = os.path.join(ASSETS, name)

    if not os.path.exists(path):
        return None

    try:
        img = pygame.image.load(path).convert_alpha()

        if max_size:
            max_w, max_h = max_size
            w, h = img.get_size()

            if w > max_w or h > max_h:
                scale = min(max_w / w, max_h / h)

                img = pygame.transform.smoothscale(
                    img,
                    (
                        max(1, int(w * scale)),
                        max(1, int(h * scale))
                    )
                )

        return img

    except Exception as e:
        print("[DATA CHEF] Error cargando", name, ":", e)
        return None


def rounded_rect(surface, rect, color, radius=20, border=0, border_color=None):
    rect = pygame.Rect(rect)

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )

    if border:
        pygame.draw.rect(
            surface,
            border_color if border_color else color,
            rect,
            width=border,
            border_radius=radius
        )


def text(surface, value, font, color, pos, center=False):
    rendered = font.render(value, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(rendered, rect)

    return rect


def draw_centered_lines(
    surface,
    lines,
    font,
    color,
    center_x,
    start_y,
    gap=8
):
    y = start_y

    for line in lines:

        img = font.render(line, True, color)

        rect = img.get_rect(
            center=(
                center_x,
                y + img.get_height() // 2
            )
        )

        surface.blit(img, rect)

        y += img.get_height() + gap


def shadow(surface, rect, radius=20, offset=7, alpha=28):
    layer = pygame.Surface(
        (rect.width + 30, rect.height + 30), pygame.SRCALPHA
    )
    pygame.draw.rect(
        layer,
        (15, 25, 31, alpha),
        (10, 10 + offset, rect.width, rect.height),
        border_radius=radius
    )
    surface.blit(layer, (rect.x - 10, rect.y - 10))


def premium_panel(surface, rect, fill=WHITE, border=LINE,
                  radius=24, width=1):
    shadow(surface, rect, radius=radius, offset=6, alpha=25)
    rounded_rect(surface, rect, fill, radius, width, border)


def draw_chip(surface, rect, label, fill, color=WHITE):
    rounded_rect(surface, rect, fill, rect.height // 2)
    text(surface, label, pygame.font.SysFont("Arial", 13, bold=True),
         color, rect.center, True)


def draw_progress_dots(surface, x, y, current, total):
    for i in range(total):
        if i < current:
            color = ORANGE
            radius = 7
        elif i == current:
            color = ORANGE
            radius = 9
        else:
            color = (207, 211, 210)
            radius = 6
        pygame.draw.circle(surface, color, (x + i * 28, y), radius)


def draw_glow(surface, center, radius, color, alpha=20):
    layer = pygame.Surface((radius * 2 + 40, radius * 2 + 40), pygame.SRCALPHA)
    for r in range(radius, 20, -12):
        a = max(1, int(alpha * (radius - r + 12) / radius))
        pygame.draw.circle(layer, (*color, a),
                           (radius + 20, radius + 20), r)
    surface.blit(layer, (center[0] - radius - 20, center[1] - radius - 20))


def draw_starburst(surface, center, radius, color):
    x, y = center
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = int(x + math.cos(rad) * (radius - 7))
        y1 = int(y + math.sin(rad) * (radius - 7))
        x2 = int(x + math.cos(rad) * radius)
        y2 = int(y + math.sin(rad) * radius)
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)


# ============================================================
# UI PREMIUM — DATA CHEF
# ============================================================

def panel_shadow(surface, rect, radius=26, offset=10, alpha=55):
    """Sombra suave multicapa para dar profundidad."""
    for i in range(4, 0, -1):
        a = max(4, alpha // (i + 1))
        rr = pygame.Rect(
            rect.x - i * 2,
            rect.y + offset - i,
            rect.width + i * 4,
            rect.height + i * 4
        )
        layer = pygame.Surface(
            (rr.width + 20, rr.height + 20),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            layer,
            (10, 22, 29, a),
            (10, 10, rr.width, rr.height),
            border_radius=radius + i * 2
        )
        surface.blit(layer, (rr.x - 10, rr.y - 10))


def draw_panel(surface, rect, fill, border=None, radius=24, width=1,
               shadow_on=True):
    if shadow_on:
        panel_shadow(surface, rect, radius, 8, 42)
    rounded_rect(
        surface,
        rect,
        fill,
        radius,
        width,
        border if border else fill
    )


def draw_grid(surface, rect, spacing=34, color=(255,255,255), alpha=10):
    layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for x in range(0, rect.width + 1, spacing):
        pygame.draw.line(layer, (*color, alpha), (x, 0), (x, rect.height), 1)
    for y in range(0, rect.height + 1, spacing):
        pygame.draw.line(layer, (*color, alpha), (0, y), (rect.width, y), 1)
    surface.blit(layer, rect.topleft)


def draw_data_nodes(surface, center, scale=1.0, t=0.0):
    """Mini visual de datos: nodos + conexiones."""
    cx, cy = center
    pts = [
        (cx - 82*scale, cy - 12*scale),
        (cx - 25*scale, cy - 55*scale),
        (cx + 44*scale, cy - 30*scale),
        (cx + 76*scale, cy + 30*scale),
        (cx + 8*scale, cy + 62*scale),
        (cx - 55*scale, cy + 40*scale),
    ]
    for i in range(len(pts)):
        pygame.draw.line(
            surface,
            (194, 214, 221),
            pts[i],
            pts[(i + 1) % len(pts)],
            max(1, int(2 * scale))
        )
    pulse = 1 + math.sin(t * 3.0) * 0.12
    for i, (x, y) in enumerate(pts):
        r = int((7 if i % 2 == 0 else 5) * scale * pulse)
        pygame.draw.circle(surface, ORANGE if i in (1,4) else WHITE,
                           (int(x), int(y)), r)
        pygame.draw.circle(surface, (255,255,255),
                           (int(x), int(y)), r + 5, 1)


def draw_ring(surface, center, radius, color, width=2, alpha=80):
    layer = pygame.Surface((radius*2+30, radius*2+30), pygame.SRCALPHA)
    pygame.draw.circle(
        layer, (*color, alpha),
        (radius+15, radius+15), radius, width
    )
    surface.blit(
        layer,
        (center[0]-radius-15, center[1]-radius-15)
    )


def draw_badge(surface, center, number, label):
    cx, cy = center
    pygame.draw.circle(surface, ORANGE, (cx, cy), 31)
    pygame.draw.circle(surface, WHITE, (cx, cy), 31, 2)
    text(surface, number, pygame.font.SysFont("Arial", 15, bold=True),
         WHITE, (cx, cy-1), True)
    text(surface, label, pygame.font.SysFont("Arial", 11, bold=True),
         (188, 198, 202), (cx, cy+47), True)


def draw_check_icon(surface, center, radius=16, fill=GREEN):
    pygame.draw.circle(surface, fill, center, radius)
    pygame.draw.line(
        surface, WHITE,
        (center[0]-6, center[1]),
        (center[0]-1, center[1]+5),
        3
    )
    pygame.draw.line(
        surface, WHITE,
        (center[0]-1, center[1]+5),
        (center[0]+7, center[1]-6),
        3
    )


def draw_arrow_button(surface, rect, label, hover=False):
    draw = rect.move(0, -3 if hover else 0)
    if hover:
        panel_shadow(surface, draw, 20, 7, 55)
    rounded_rect(
        surface,
        draw,
        ORANGE_DARK if hover else ORANGE,
        20
    )
    # pequeño chevron
    pygame.draw.circle(surface, (255, 255, 255), (draw.right-31, draw.centery), 12)
    pygame.draw.polygon(
        surface, ORANGE,
        [
            (draw.right-35, draw.centery-5),
            (draw.right-27, draw.centery),
            (draw.right-35, draw.centery+5)
        ]
    )
    text(
        surface, label,
        pygame.font.SysFont("Arial", 21, bold=True),
        WHITE,
        (draw.centerx-10, draw.centery),
        True
    )


# ============================================================
# FONDO DECORATIVO
# ============================================================

class Bubble:

    def __init__(self):

        self.x = random.randint(0, WIDTH)
        self.y = random.randint(130, HEIGHT)

        self.r = random.randint(2, 5)

        self.speed = random.uniform(6, 18)

        self.alpha = random.randint(35, 100)

    def update(self, dt):

        self.y -= self.speed * dt

        if self.y < 130:

            self.y = HEIGHT + random.randint(10, 100)

            self.x = random.randint(0, WIDTH)

    def draw(self, surface):

        layer = pygame.Surface(
            (
                self.r * 2 + 4,
                self.r * 2 + 4
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            layer,
            (255, 255, 255, self.alpha),
            (
                self.r + 2,
                self.r + 2
            ),
            self.r
        )

        surface.blit(
            layer,
            (
                int(self.x - self.r),
                int(self.y - self.r)
            )
        )


# ============================================================
# APP
# ============================================================

class TriviaApp:

    def __init__(self):

        self.window = pygame.display.set_mode(
            (0, 0),
            pygame.RESIZABLE
        )

        pygame.display.set_caption(
            "DATA CHEF | MARESA - Reto del Chef"
        )

        self.screen = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        self.clock = pygame.time.Clock()

        self.running = True

        self.time = 0.0

        self.scale = 1.0
        self.ox = 0
        self.oy = 0

        # ----------------------------------------------------
        # IMÁGENES
        # ----------------------------------------------------

        self.logo = load_img(
            "logo_maresa.png",
            (180, 70)
        )

        # Compatibilidad con los chefs usados
        # en las pantallas anteriores
        self.chef = None

        for name in [
            "chef_trivia.png",
            "chef_limpieza.png",
            "chef_jugando.png",
            "chef_pensando.png",
            "chef.png"
        ]:

            img = load_img(
                name,
                (330, 420)
            )

            if img:

                self.chef = img

                print(
                    "[DATA CHEF] Chef trivia:",
                    name
                )

                break

        # ----------------------------------------------------
        # PREGUNTAS
        # ----------------------------------------------------

        self.questions = [

            {
                "title": "PREGUNTA 1 DE 3",

                "question":
                    "¿Qué problema ocurre cuando la misma información aparece varias veces?",

                "options": [

                    ("A", "Duplicados"),

                    ("B", "Formatos"),

                    ("C", "Visualizaciones"),

                    ("D", "Gráficos")

                ],

                "correct": 0,

                "explanation":
                    "¡Correcto! Los datos duplicados pueden alterar los resultados de un análisis."
            },


            {
                "title": "PREGUNTA 2 DE 3",

                "question":
                    "¿Qué es un dato nulo?",

                "options": [

                    (
                        "A",
                        "Información que está vacía o falta"
                    ),

                    (
                        "B",
                        "Información secreta"
                    ),

                    (
                        "C",
                        "Información duplicada"
                    ),

                    (
                        "D",
                        "Información incorrecta"
                    )

                ],

                "correct": 0,

                "explanation":
                    "¡Muy bien! Un dato nulo representa información que falta o está vacía."
            },


            {
                "title": "PREGUNTA 3 DE 3",

                "question":
                    "¿Por qué validamos los datos?",

                "options": [

                    (
                        "A",
                        "Para hacerlos más bonitos"
                    ),

                    (
                        "B",
                        "Para aumentar el tamaño del archivo"
                    ),

                    (
                        "C",
                        "Para comprobar que sean correctos y tengan sentido"
                    ),

                    (
                        "D",
                        "Para crear más gráficos"
                    )

                ],

                "correct": 2,

                "explanation":
                    "¡Excelente! Validar ayuda a comprobar que la información sea correcta y confiable."
            }

        ]

        self.current_question = 0

        self.selected = None
        self.result = None

        self.feedback_timer = 0.0

        self.completed = False

        self.show_intro = True

        self.bubbles = [

            Bubble()

            for _ in range(42)

        ]

        # ----------------------------------------------------
        # FUENTES
        # ----------------------------------------------------

        self.fonts = {

            "small":
                pygame.font.SysFont(
                    "Arial",
                    17
                ),

            "medium":
                pygame.font.SysFont(
                    "Arial",
                    22
                ),

            "medium_bold":
                pygame.font.SysFont(
                    "Arial",
                    22,
                    bold=True
                ),

            "large":
                pygame.font.SysFont(
                    "Arial",
                    31,
                    bold=True
                ),

            "title":
                pygame.font.SysFont(
                    "Arial",
                    46,
                    bold=True
                ),

            "big":
                pygame.font.SysFont(
                    "Arial",
                    60,
                    bold=True
                ),

            "question":
                pygame.font.SysFont(
                    "Arial",
                    30,
                    bold=True
                ),

            "option":
                pygame.font.SysFont(
                    "Arial",
                    23,
                    bold=True
                ),

            "feedback":
                pygame.font.SysFont(
                    "Arial",
                    25,
                    bold=True
                )

        }

        self.option_rects = []


    # ========================================================
    # ESCALA / MOUSE
    # ========================================================

    def logical(self, pos):

        return (

            int(
                (pos[0] - self.ox)
                / self.scale
            ),

            int(
                (pos[1] - self.oy)
                / self.scale
            )

        )


    # ========================================================
    # FONDO
    # ========================================================

    def draw_background(self):

        # ====================================================
        # COMPOSICIÓN: "LABORATORIO DE DATOS"
        # ====================================================

        # Fondo principal
        self.screen.fill(NAVY)

        # Panel izquierdo azul profundo
        left = pygame.Rect(0, 112, 710, 648)
        for y in range(left.height):
            t = y / max(1, left.height)
            col = (
                int(42 - 12*t),
                int(105 - 28*t),
                int(139 - 25*t)
            )
            pygame.draw.line(
                self.screen, col,
                (left.x, left.y+y),
                (left.right, left.y+y)
            )

        # Panel derecho marfil
        right = pygame.Rect(710, 112, 826, 648)
        pygame.draw.rect(self.screen, CREAM_2, right)

        # Unión visual
        pygame.draw.rect(
            self.screen, ORANGE,
            (700, 112, 10, 648)
        )

        # Grid técnico en el lado izquierdo
        draw_grid(
            self.screen,
            pygame.Rect(0, 112, 710, 648),
            42,
            WHITE,
            8
        )

        # Círculos de profundidad detrás del chef
        draw_ring(self.screen, (310, 470), 245, WHITE, 2, 24)
        draw_ring(self.screen, (310, 470), 195, ORANGE, 2, 90)
        draw_ring(self.screen, (310, 470), 145, WHITE, 1, 30)

        # Halo
        draw_glow(
            self.screen, (310, 450),
            220, (255, 152, 53), 18
        )

        # Elementos flotantes
        for bubble in self.bubbles:
            bubble.draw(self.screen)

        # Sol gráfico en esquina derecha
        draw_glow(
            self.screen, (1430, 175),
            100, (255, 166, 60), 10
        )
        pygame.draw.circle(
            self.screen, (255, 239, 212),
            (1430, 175), 66
        )
        pygame.draw.circle(
            self.screen, CREAM_2,
            (1430, 175), 48
        )

        # Microdecoraciones
        for x, y, r in [
            (64, 175, 3), (650, 190, 4), (675, 690, 3),
            (744, 151, 3), (1480, 710, 3), (1320, 710, 2)
        ]:
            pygame.draw.circle(self.screen, (178, 202, 211), (x, y), r)

        # Footer
        pygame.draw.rect(
            self.screen, (232, 228, 219),
            (0, 760, WIDTH, 104)
        )
        pygame.draw.line(
            self.screen, (211, 205, 195),
            (70, 760), (1466, 760), 1
        )

        text(
            self.screen,
            "DATA CHEF",
            pygame.font.SysFont("Arial", 12, bold=True),
            DARK, (70, 802)
        )
        text(
            self.screen,
            "ACADEMIA DE CALIDAD DE DATOS",
            pygame.font.SysFont("Arial", 12),
            GRAY, (180, 802)
        )

        # Progreso general
        steps = [
            ("01", "PREPARAR"),
            ("02", "LIMPIAR"),
            ("03", "RETAR"),
            ("04", "COCINAR"),
        ]
        start_x = 930
        for i, (num, label) in enumerate(steps):
            x = start_x + i * 125
            active = i == 2
            pygame.draw.circle(
                self.screen,
                ORANGE if active else (190, 193, 191),
                (x, 807),
                14
            )
            text(
                self.screen, num,
                pygame.font.SysFont("Arial", 10, bold=True),
                WHITE if active else CREAM_2,
                (x, 807), True
            )
            text(
                self.screen, label,
                pygame.font.SysFont("Arial", 10, bold=True),
                DARK if active else GRAY,
                (x + 25, 801)
            )
            if i < len(steps)-1:
                pygame.draw.line(
                    self.screen,
                    (190, 193, 191),
                    (x+16, 807),
                    (x+105, 807),
                    2
                )

    # ========================================================
    # HEADER
    # ========================================================

    def draw_header(self):

        pygame.draw.rect(self.screen, WHITE, (0, 0, WIDTH, 112))
        pygame.draw.rect(self.screen, ORANGE, (0, 0, WIDTH, 6))
        pygame.draw.line(
            self.screen, (228, 225, 219),
            (0, 111), (WIDTH, 111), 1
        )

        # Logo
        if self.logo:
            logo = self.logo
            if logo.get_width() > 150:
                ratio = 150 / logo.get_width()
                logo = pygame.transform.smoothscale(
                    logo,
                    (150, max(1, int(logo.get_height() * ratio)))
                )
            self.screen.blit(logo, (46, 20))

        # Marca del producto
        pygame.draw.line(
            self.screen, LINE,
            (220, 25), (220, 86), 1
        )

        text(
            self.screen, "LA COCINA",
            self.fonts["title"], DARK, (255, 22)
        )
        text(
            self.screen, "DE LOS DATOS",
            self.fonts["title"], ORANGE, (485, 22)
        )

        # Módulo de etapa
        stage = pygame.Rect(845, 22, 325, 68)
        rounded_rect(self.screen, stage, (246, 244, 240), 18, 1, LINE)

        pygame.draw.circle(
            self.screen, ORANGE, (875, 56), 21
        )
        text(
            self.screen, "03",
            pygame.font.SysFont("Arial", 13, bold=True),
            WHITE, (875, 56), True
        )

        text(
            self.screen, "RETO DEL CHEF",
            self.fonts["medium_bold"],
            DARK, (908, 31)
        )
        text(
            self.screen, "COMPROBACIÓN DE APRENDIZAJE",
            pygame.font.SysFont("Arial", 13),
            GRAY, (908, 60)
        )

        # Estado
        status = pygame.Rect(1250, 21, 235, 70)
        rounded_rect(self.screen, status, NAVY, 20)

        pygame.draw.circle(
            self.screen, ORANGE, (1277, 45), 5
        )
        text(
            self.screen, "MISIÓN ACTIVA",
            pygame.font.SysFont("Arial", 13, bold=True),
            WHITE, (1292, 31)
        )
        text(
            self.screen, "3 PREGUNTAS",
            pygame.font.SysFont("Arial", 13),
            (190, 204, 210), (1292, 57)
        )

    # ========================================================
    # CHEF
    # ========================================================

    def draw_chef_area(self):

        # Etiqueta
        chip = pygame.Rect(55, 138, 205, 34)
        rounded_rect(
            self.screen, chip,
            (20, 65, 82), 17, 1, (103, 155, 176)
        )
        pygame.draw.circle(
            self.screen, GREEN, (76, 155), 5
        )
        text(
            self.screen,
            "CHEF · GUÍA DE LA MISIÓN",
            pygame.font.SysFont("Arial", 12, bold=True),
            WHITE, (90, 147)
        )

        # Visual de datos
        draw_data_nodes(
            self.screen, (120, 600),
            0.85, self.time
        )

        # Plataforma del chef
        pygame.draw.ellipse(
            self.screen,
            (19, 55, 70),
            (112, 676, 395, 40)
        )
        pygame.draw.ellipse(
            self.screen,
            (232, 226, 215),
            (135, 667, 345, 28)
        )

        # Chef
        if self.chef:
            bob = math.sin(self.time * 2.0) * 4
            rect = self.chef.get_rect()
            rect.midbottom = (315, int(680 + bob))
            self.screen.blit(self.chef, rect)
        else:
            pygame.draw.circle(
                self.screen, (255, 218, 177),
                (315, 450), 70
            )

        # Speech bubble con cola integrada
        bubble = pygame.Rect(370, 190, 285, 190)
        panel_shadow(self.screen, bubble, 25, 7, 45)
        rounded_rect(
            self.screen, bubble,
            WHITE, 25, 2, (238, 173, 92)
        )

        pygame.draw.polygon(
            self.screen, WHITE,
            [
                (400, 340),
                (342, 390),
                (414, 366)
            ]
        )
        pygame.draw.line(
            self.screen, (238, 173, 92),
            (399, 340), (342, 390), 2
        )

        # Acento
        pygame.draw.rect(
            self.screen, ORANGE,
            (398, 215, 45, 5),
            border_radius=2
        )

        text(
            self.screen,
            "¡MUY BIEN!",
            pygame.font.SysFont("Arial", 14, bold=True),
            ORANGE, (398, 232)
        )

        draw_centered_lines(
            self.screen,
            [
                "Ya limpiamos",
                "nuestros datos."
            ],
            self.fonts["medium_bold"],
            DARK, 512, 258, 5
        )

        text(
            self.screen,
            "Ahora comprobemos cuánto aprendiste.",
            pygame.font.SysFont("Arial", 13),
            GRAY, (512, 323), True
        )

        pygame.draw.line(
            self.screen, LINE,
            (405, 348), (620, 348), 1
        )
        text(
            self.screen,
            "CALIDAD  →  CONFIABILIDAD",
            pygame.font.SysFont("Arial", 11, bold=True),
            ORANGE, (512, 359), True
        )

        # Mini tarjeta de misión en el lado izquierdo
        mini = pygame.Rect(52, 570, 165, 70)
        rounded_rect(
            self.screen, mini, (21, 67, 85), 16
        )
        text(
            self.screen, "MISIÓN 03",
            pygame.font.SysFont("Arial", 11, bold=True),
            ORANGE, (68, 586)
        )
        text(
            self.screen, "CALIDAD DE DATOS",
            pygame.font.SysFont("Arial", 12, bold=True),
            WHITE, (68, 607)
        )
        text(
            self.screen, "Reto desbloqueado",
            pygame.font.SysFont("Arial", 10),
            (180, 198, 202), (68, 625)
        )

    # ========================================================
    # INTRO
    # ========================================================

    def draw_intro(self):

        self.draw_background()
        self.draw_header()
        self.draw_chef_area()

        # ====================================================
        # CONSOLA DEL RETO — LADO DERECHO
        # ====================================================

        console = pygame.Rect(735, 138, 735, 590)
        draw_panel(
            self.screen, console,
            (247, 244, 237),
            (224, 171, 92),
            30, 2
        )

        # Header de consola
        console_head = pygame.Rect(737, 140, 731, 112)
        rounded_rect(
            self.screen, console_head,
            NAVY, 28
        )
        pygame.draw.rect(
            self.screen, NAVY,
            (737, 205, 731, 47)
        )

        # Número
        pygame.draw.circle(
            self.screen, ORANGE,
            (780, 194), 29
        )
        pygame.draw.circle(
            self.screen, WHITE,
            (780, 194), 29, 2
        )
        text(
            self.screen, "03",
            pygame.font.SysFont("Arial", 15, bold=True),
            WHITE, (780, 194), True
        )

        text(
            self.screen,
            "RETO DEL CHEF",
            pygame.font.SysFont("Arial", 34, bold=True),
            WHITE, (823, 166)
        )
        text(
            self.screen,
            "PON A PRUEBA TU CRITERIO",
            pygame.font.SysFont("Arial", 13, bold=True),
            (187, 204, 211), (824, 211)
        )

        # Estado de misión en el header
        text(
            self.screen,
            "NIVEL 03",
            pygame.font.SysFont("Arial", 11, bold=True),
            ORANGE, (1378, 168), True
        )
        draw_progress_dots(
            self.screen, 1350, 207, 0, 3
        )

        # ====================================================
        # BLOQUE VISUAL CENTRAL
        # ====================================================

        # Círculo principal
        center = (1105, 350)

        # Anillos
        draw_ring(
            self.screen, center, 103,
            (238, 169, 91), 2, 75
        )
        draw_ring(
            self.screen, center, 84,
            (255, 199, 126), 2, 90
        )
        draw_glow(
            self.screen, center, 92,
            (255, 164, 57), 14
        )

        pygame.draw.circle(
            self.screen,
            (255, 239, 214),
            center, 68
        )
        pygame.draw.circle(
            self.screen,
            WHITE,
            center, 55, 2
        )

        # Signo de pregunta
        text(
            self.screen,
            "?",
            pygame.font.SysFont("Arial", 65, bold=True),
            ORANGE,
            (center[0], center[1]-4),
            True
        )

        # Estrellitas
        for dx, dy in [(-105,-70), (104,-48), (96,76), (-93,72)]:
            pygame.draw.line(
                self.screen, (239, 169, 91),
                (center[0]+dx-5, center[1]+dy),
                (center[0]+dx+5, center[1]+dy), 2
            )
            pygame.draw.line(
                self.screen, (239, 169, 91),
                (center[0]+dx, center[1]+dy-5),
                (center[0]+dx, center[1]+dy+5), 2
            )

        # ====================================================
        # TITULAR + DESCRIPCIÓN
        # ====================================================

        # ====================================================
        # TITULAR — bloque compacto
        # ====================================================

        text(
            self.screen,
            "¿ESTÁS LISTO?",
            pygame.font.SysFont("Arial", 34, bold=True),
            DARK,
            (1105, 448),
            True
        )

        text(
            self.screen,
            "PARA EL RETO DEL CHEF",
            pygame.font.SysFont("Arial", 21, bold=True),
            ORANGE,
            (1105, 480),
            True
        )

        # La descripción queda en una zona propia para que
        # nunca sea invadida por las tarjetas inferiores.
        draw_centered_lines(
            self.screen,
            [
                "Responde 3 preguntas rápidas sobre",
                "limpieza, validación y calidad de datos."
            ],
            pygame.font.SysFont("Arial", 16),
            GRAY,
            1105, 507, 3
        )

        # Separador visual
        pygame.draw.line(
            self.screen,
            (224, 218, 207),
            (810, 552),
            (1400, 552),
            1
        )

        # ====================================================
        # 3 MICRO-TARJETAS — ZONA INFERIOR
        # ====================================================

        cards = [
            ("01", "LIMPIEZA", "Detecta"),
            ("02", "VALIDACIÓN", "Comprueba"),
            ("03", "CALIDAD", "Decide"),
        ]

        for i, (num, title, sub) in enumerate(cards):
            x = 790 + i * 215
            r = pygame.Rect(x, 565, 195, 58)

            rounded_rect(
                self.screen, r,
                WHITE, 14, 1, LINE
            )

            # Indicador lateral de etapa
            pygame.draw.rect(
                self.screen,
                ORANGE if i == 2 else (207, 211, 209),
                (r.x, r.y, 5, r.height),
                border_radius=3
            )

            pygame.draw.circle(
                self.screen,
                ORANGE if i == 2 else (207, 211, 209),
                (r.x + 30, r.centery),
                13
            )

            text(
                self.screen, num,
                pygame.font.SysFont("Arial", 9, bold=True),
                WHITE if i == 2 else CREAM_2,
                (r.x + 30, r.centery), True
            )

            text(
                self.screen, title,
                pygame.font.SysFont("Arial", 11, bold=True),
                DARK, (r.x + 52, r.y + 13)
            )

            text(
                self.screen, sub,
                pygame.font.SysFont("Arial", 10),
                GRAY, (r.x + 52, r.y + 35)
            )

        # ====================================================
        # CTA — separado de las tarjetas
        # ====================================================

        btn = pygame.Rect(970, 638, 275, 53)
        mouse = self.logical(pygame.mouse.get_pos())
        hover = btn.collidepoint(mouse)

        draw_arrow_button(
            self.screen,
            btn,
            "COMENZAR RETO",
            hover
        )

        text(
            self.screen,
            "Pulsa para iniciar la primera pregunta",
            pygame.font.SysFont("Arial", 10),
            GRAY,
            (1108, 706),
            True
        )

    # ========================================================
    # QUIZ
    # ========================================================

    def draw_quiz(self):

        self.draw_background()
        self.draw_header()
        self.draw_chef_area()

        q = self.questions[self.current_question]

        # Panel de preguntas
        panel = pygame.Rect(760, 135, 705, 575)
        premium_panel(
            self.screen, panel,
            CREAM_2, (224, 173, 103), 30, 2
        )

        # Encabezado interno
        top = pygame.Rect(762, 137, 701, 105)
        rounded_rect(
            self.screen, top,
            NAVY, 28
        )
        pygame.draw.rect(
            self.screen, NAVY,
            (762, 190, 701, 52)
        )

        # Pregunta / progreso
        text(
            self.screen,
            "RETO DEL CHEF",
            self.fonts["small"],
            (186, 204, 211),
            (800, 159)
        )

        text(
            self.screen,
            q["title"],
            self.fonts["medium_bold"],
            WHITE,
            (800, 185)
        )

        draw_progress_dots(
            self.screen,
            1265, 170,
            self.current_question + 1,
            3
        )

        text(
            self.screen,
            f"{self.current_question + 1}/3",
            pygame.font.SysFont("Arial", 12, bold=True),
            (194, 207, 213),
            (1370, 185)
        )

        # Pregunta
        question_box = pygame.Rect(815, 265, 595, 90)
        pygame.draw.rect(
            self.screen,
            (250, 247, 241),
            question_box,
            border_radius=18
        )

        pygame.draw.rect(
            self.screen,
            ORANGE,
            (815, 265, 6, 90),
            border_radius=3
        )

        lines = self.wrap_text(
            q["question"],
            self.fonts["question"],
            question_box.width - 55
        )

        draw_centered_lines(
            self.screen,
            lines,
            self.fonts["question"],
            DARK,
            question_box.centerx + 8,
            question_box.y + 14,
            5
        )

        # Instrucción
        text(
            self.screen,
            "ELIGE LA RESPUESTA CORRECTA",
            pygame.font.SysFont("Arial", 12, bold=True),
            ORANGE,
            (820, 375)
        )

        # ====================================================
        # OPCIONES — CONTENIDAS DENTRO DEL PANEL
        # ====================================================

        self.option_rects = []

        # Área útil interna del panel.
        # Se deja margen suficiente para que ningún texto pueda
        # invadir el borde izquierdo/derecho.
        option_x = 800
        option_w = 625
        option_y = 405
        option_h = 50
        option_gap = 12

        option_font = pygame.font.SysFont("Arial", 21, bold=True)

        for i, (letter, label) in enumerate(q["options"]):

            rect = pygame.Rect(
                option_x,
                option_y + i * (option_h + option_gap),
                option_w,
                option_h
            )

            self.option_rects.append(rect)

            mouse = self.logical(pygame.mouse.get_pos())
            hover = rect.collidepoint(mouse)

            fill = WHITE
            border = (209, 211, 208)

            if self.selected == i:
                if self.result is None:
                    fill = (255, 240, 220)
                    border = ORANGE
                elif i == q["correct"]:
                    fill = (224, 246, 231)
                    border = GREEN
                elif self.result is False:
                    fill = (252, 226, 222)
                    border = RED

            elif self.result is not None and i == q["correct"]:
                fill = (224, 246, 231)
                border = GREEN

            elif hover and self.result is None:
                fill = (252, 248, 241)
                border = ORANGE

            rounded_rect(
                self.screen,
                rect,
                fill,
                15,
                2,
                border
            )

            # ------------------------------------------------
            # Indicador A / B / C / D
            # ------------------------------------------------

            pygame.draw.circle(
                self.screen,
                border,
                (rect.x + 31, rect.centery),
                16
            )

            text(
                self.screen,
                letter,
                pygame.font.SysFont("Arial", 13, bold=True),
                WHITE,
                (rect.x + 31, rect.centery),
                True
            )

            # ------------------------------------------------
            # Texto de la respuesta
            # ------------------------------------------------
            # IMPORTANTE:
            # antes se centraba el texto con un punto fijo.
            # Ahora queda anclado desde la izquierda, dentro
            # del rectángulo, evitando que respuestas largas
            # se salgan visualmente del panel.
            label_x = rect.x + 62
            label_right = rect.right - 55
            available_width = label_right - label_x

            label_lines = self.wrap_text(
                label,
                option_font,
                available_width
            )

            if len(label_lines) == 1:
                text(
                    self.screen,
                    label_lines[0],
                    option_font,
                    DARK,
                    (label_x, rect.centery),
                    False
                )
            else:
                # Protección adicional para respuestas largas.
                total_h = len(label_lines) * option_font.get_height()
                start_y = rect.centery - total_h // 2

                for line in label_lines:
                    text(
                        self.screen,
                        line,
                        option_font,
                        DARK,
                        (label_x, start_y)
                    )
                    start_y += option_font.get_height()

            # ------------------------------------------------
            # Estado de respuesta
            # ------------------------------------------------

            if self.result is not None:

                if i == q["correct"]:
                    text(
                        self.screen,
                        "✓",
                        self.fonts["medium_bold"],
                        GREEN,
                        (rect.right - 27, rect.centery),
                        True
                    )

                elif self.selected == i and self.result is False:
                    text(
                        self.screen,
                        "×",
                        self.fonts["medium_bold"],
                        RED,
                        (rect.right - 27, rect.centery),
                        True
                    )

        # Feedback
        if self.result is not None:

            feedback = pygame.Rect(
                805, 670, 615, 82
            )

            color = GREEN if self.result else RED
            fill = (226, 247, 232) if self.result else (253, 231, 227)

            rounded_rect(
                self.screen,
                feedback,
                fill,
                18,
                2,
                color
            )

            icon = "✓" if self.result else "!"
            text(
                self.screen,
                icon,
                self.fonts["feedback"],
                color,
                (835, feedback.centery),
                True
            )

            msg = (
                q["explanation"]
                if self.result
                else "Casi... revisa el concepto y vuelve a intentarlo."
            )

            feedback_lines = self.wrap_text(
                msg,
                self.fonts["small"],
                feedback.width - 75
            )

            draw_centered_lines(
                self.screen,
                feedback_lines,
                self.fonts["small"],
                DARK,
                feedback.centerx + 10,
                feedback.y + 17,
                2
            )


    # ========================================================
    # FINAL
    # ========================================================

    def draw_completed(self):

        self.draw_background()
        self.draw_header()

        # ====================================================
        # PANTALLA DE ÉXITO — COMPOSICIÓN FINAL
        # ====================================================
        # Todo el contenido queda dentro de una única tarjeta
        # con márgenes internos consistentes.

        card = pygame.Rect(300, 145, 935, 570)

        premium_panel(
            self.screen,
            card,
            CREAM_2,
            ORANGE,
            34,
            3
        )

        # ----------------------------------------------------
        # Cabecera de la tarjeta
        # ----------------------------------------------------

        header = pygame.Rect(
            card.x + 2,
            card.y + 2,
            card.width - 4,
            82
        )

        rounded_rect(
            self.screen,
            header,
            NAVY,
            30
        )

        pygame.draw.rect(
            self.screen,
            NAVY,
            (
                header.x,
                header.bottom - 30,
                header.width,
                30
            )
        )

        # Pequeño indicador de estado
        pygame.draw.circle(
            self.screen,
            ORANGE,
            (card.x + 43, card.y + 41),
            6
        )

        text(
            self.screen,
            "MISIÓN COMPLETADA",
            pygame.font.SysFont("Arial", 13, bold=True),
            (190, 204, 210),
            (card.x + 60, card.y + 25)
        )

        text(
            self.screen,
            "RETO DEL CHEF",
            pygame.font.SysFont("Arial", 11),
            (145, 164, 173),
            (card.x + 60, card.y + 48)
        )

        # Progreso de las 3 preguntas
        progress_x = card.right - 112

        for i in range(3):
            px = progress_x + i * 28

            pygame.draw.circle(
                self.screen,
                GREEN,
                (px, card.y + 32),
                7
            )

            pygame.draw.circle(
                self.screen,
                WHITE,
                (px, card.y + 32),
                7,
                1
            )

            text(
                self.screen,
                "✓",
                pygame.font.SysFont("Arial", 9, bold=True),
                WHITE,
                (px, card.y + 32),
                True
            )

        text(
            self.screen,
            "3 / 3",
            pygame.font.SysFont("Arial", 11, bold=True),
            (190, 204, 210),
            (card.right - 55, card.y + 55),
            True
        )

        # ----------------------------------------------------
        # EMBLEMA DE LOGRO — SELLO DE CALIDAD
        # ----------------------------------------------------
        # Sustituye el círculo naranja vacío por un emblema con
        # identidad visual: sello, escudo y check de calidad.

        center = (card.centerx, 335)

        draw_glow(
            self.screen,
            center,
            112,
            (255, 170, 65),
            20
        )

        # Aura exterior
        pygame.draw.circle(
            self.screen,
            (255, 239, 215),
            center,
            98
        )

        # Anillo técnico discontinuo
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = int(center[0] + math.cos(rad) * 91)
            y1 = int(center[1] + math.sin(rad) * 91)
            x2 = int(center[0] + math.cos(rad) * 99)
            y2 = int(center[1] + math.sin(rad) * 99)
            pygame.draw.line(
                self.screen,
                (238, 169, 91),
                (x1, y1),
                (x2, y2),
                3
            )

        # Medalla exterior
        pygame.draw.circle(
            self.screen,
            ORANGE,
            center,
            76
        )

        pygame.draw.circle(
            self.screen,
            (255, 191, 115),
            center,
            76,
            3
        )

        # Centro oscuro: da contraste y evita la sensación de vacío.
        pygame.draw.circle(
            self.screen,
            NAVY,
            center,
            57
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            center,
            48,
            2
        )

        # Escudo de certificación
        shield = [
            (center[0], center[1] - 34),
            (center[0] + 27, center[1] - 22),
            (center[0] + 22, center[1] + 17),
            (center[0], center[1] + 38),
            (center[0] - 22, center[1] + 17),
            (center[0] - 27, center[1] - 22),
        ]

        pygame.draw.polygon(
            self.screen,
            ORANGE,
            shield
        )

        pygame.draw.lines(
            self.screen,
            WHITE,
            True,
            shield,
            2
        )

        # Check grande de calidad
        pygame.draw.line(
            self.screen,
            WHITE,
            (center[0] - 15, center[1] + 1),
            (center[0] - 4, center[1] + 12),
            6
        )

        pygame.draw.line(
            self.screen,
            WHITE,
            (center[0] - 4, center[1] + 12),
            (center[0] + 18, center[1] - 13),
            6
        )

        # Etiqueta inferior eliminada para mantener el emblema limpio
        # y evitar que aparezca texto detrás de “¡RETO SUPERADO!”.

        # Destellos laterales
        draw_starburst(
            self.screen,
            (center[0] - 115, center[1] - 46),
            9,
            ORANGE
        )

        draw_starburst(
            self.screen,
            (center[0] + 115, center[1] + 38),
            8,
            (238, 169, 91)
        )

        # Tres pequeños nodos: representan las 3 preguntas superadas.
        for i, dx in enumerate((-31, 0, 31)):
            pygame.draw.circle(
                self.screen,
                GREEN,
                (center[0] + dx, center[1] - 105),
                5
            )

        # ----------------------------------------------------
        # MENSAJE PRINCIPAL
        # ----------------------------------------------------

        title_font = pygame.font.SysFont(
            "Arial",
            46,
            bold=True
        )

        text(
            self.screen,
            "¡RETO SUPERADO!",
            title_font,
            ORANGE,
            (card.centerx, 450),
            True
        )

        # Línea de acento debajo del título
        pygame.draw.rect(
            self.screen,
            ORANGE,
            (
                card.centerx - 35,
                478,
                70,
                4
            ),
            border_radius=2
        )

        completed_lines = [
            "Has demostrado que puedes identificar problemas",
            "de calidad y tomar mejores decisiones con los datos."
        ]

        draw_centered_lines(
            self.screen,
            completed_lines,
            self.fonts["medium_bold"],
            DARK,
            card.centerx,
            500,
            6
        )

        # ----------------------------------------------------
        # RESULTADO + CTA
        # ----------------------------------------------------
        # Ambos elementos forman una única fila y están
        # calculados desde los límites de la tarjeta.

        bottom_y = 585

        result_box = pygame.Rect(
            card.x + 95,
            bottom_y,
            410,
            50
        )

        rounded_rect(
            self.screen,
            result_box,
            NAVY,
            25
        )

        # Check visual
        pygame.draw.circle(
            self.screen,
            GREEN,
            (result_box.x + 28, result_box.centery),
            13
        )

        pygame.draw.line(
            self.screen,
            WHITE,
            (result_box.x + 22, result_box.centery),
            (result_box.x + 27, result_box.centery + 5),
            2
        )

        pygame.draw.line(
            self.screen,
            WHITE,
            (result_box.x + 27, result_box.centery + 5),
            (result_box.x + 35, result_box.centery - 6),
            2
        )

        text(
            self.screen,
            "3 / 3  RESPUESTAS CORRECTAS",
            pygame.font.SysFont("Arial", 15, bold=True),
            WHITE,
            (result_box.x + 57, result_box.centery),
            False
        )

        # Botón perfectamente contenido dentro del panel
        btn = pygame.Rect(
            result_box.right + 18,
            bottom_y,
            250,
            50
        )

        mouse = self.logical(pygame.mouse.get_pos())
        hover = btn.collidepoint(mouse)

        draw_arrow_button(
            self.screen,
            btn,
            "CONTINUAR",
            hover
        )

        # ----------------------------------------------------
        # Siguiente estación
        # ----------------------------------------------------

        text(
            self.screen,
            "SIGUIENTE ESTACIÓN",
            pygame.font.SysFont("Arial", 10, bold=True),
            ORANGE,
            (card.centerx - 112, 663)
        )

        text(
            self.screen,
            "COCINANDO LOS DATOS",
            pygame.font.SysFont("Arial", 13, bold=True),
            DARK,
            (card.centerx + 8, 660)
        )


    # ========================================================
    # TEXTO WRAP
    # ========================================================

    def wrap_text(
        self,
        value,
        font,
        max_width
    ):

        words = value.split()

        lines = []

        current = ""

        for word in words:

            test = (
                word
                if not current
                else current + " " + word
            )

            if font.size(
                test
            )[0] <= max_width:

                current = test

            else:

                if current:

                    lines.append(
                        current
                    )

                current = word

        if current:

            lines.append(
                current
            )

        return lines


    # ========================================================
    # DIBUJO PRINCIPAL
    # ========================================================

    def draw(self):

        if self.show_intro:

            self.draw_intro()

        elif self.completed:

            self.draw_completed()

        else:

            self.draw_quiz()

        # Escalado
        ww, wh = self.window.get_size()

        self.scale = min(
            ww / WIDTH,
            wh / HEIGHT
        )

        rw = max(
            1,
            int(
                WIDTH *
                self.scale
            )
        )

        rh = max(
            1,
            int(
                HEIGHT *
                self.scale
            )
        )

        self.ox = (
            ww - rw
        ) // 2

        self.oy = (
            wh - rh
        ) // 2

        scaled = pygame.transform.smoothscale(

            self.screen,

            (
                rw,
                rh
            )

        )

        self.window.fill(
            (
                220,
                220,
                220
            )
        )

        self.window.blit(

            scaled,

            (
                self.ox,
                self.oy
            )

        )

        pygame.display.flip()


    # ========================================================
    # EVENTOS
    # ========================================================

    def handle_click(
        self,
        pos
    ):

        # ----------------------------------------------------
        # INTRO
        # ----------------------------------------------------

        if self.show_intro:

            if pygame.Rect(
                970,
                638,
                275,
                53
            ).collidepoint(pos):

                self.show_intro = False

                print(
                    "[DATA CHEF] RETO DEL CHEF -> COMENZAR"
                )

            return


        # ----------------------------------------------------
        # FINAL -> PANTALLA 06
        # ----------------------------------------------------

        if self.completed:

            # Debe coincidir con el botón dibujado en draw_completed().
            # La posición se mantiene dentro de la tarjeta central.
            if pygame.Rect(
                1013,
                585,
                250,
                50
            ).collidepoint(
                pos
            ):

                print(
                    "[DATA CHEF] RETO COMPLETADO -> PANTALLA 06 COCINANDO"
                )

                pantalla_06 = os.path.join(

                    BASE,

                    "pantalla_06_cocinando.py"

                )

                if os.path.exists(
                    pantalla_06
                ):

                    try:

                        subprocess.Popen(

                            [

                                sys.executable,

                                pantalla_06

                            ],

                            cwd=BASE

                        )

                        # Cerramos la pantalla 05
                        self.running = False

                    except Exception as e:

                        print(
                            "[DATA CHEF] ERROR abriendo Pantalla 06:",
                            e
                        )

                else:

                    print(
                        "[DATA CHEF] ERROR: No existe:"
                    )

                    print(
                        pantalla_06
                    )

            return


        # ----------------------------------------------------
        # QUIZ
        # ----------------------------------------------------

        if self.result is not None:

            return

        for i, rect in enumerate(
            self.option_rects
        ):

            if rect.collidepoint(
                pos
            ):

                self.selected = i

                q = self.questions[
                    self.current_question
                ]

                if i == q["correct"]:

                    self.result = True

                    self.feedback_timer = 1.4

                    print(
                        "[DATA CHEF] RESPUESTA CORRECTA"
                    )

                else:

                    self.result = False

                    self.feedback_timer = 1.8

                    print(
                        "[DATA CHEF] RESPUESTA INCORRECTA"
                    )

                break


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        self.time += dt

        for bubble in self.bubbles:

            bubble.update(
                dt
            )

        if (

            not self.show_intro

            and

            not self.completed

            and

            self.result is not None

        ):

            self.feedback_timer -= dt

            if self.feedback_timer <= 0:

                if self.result:

                    self.current_question += 1

                    if (

                        self.current_question
                        >=
                        len(
                            self.questions
                        )

                    ):

                        self.completed = True

                        print(
                            "[DATA CHEF] TRIVIA COMPLETADA"
                        )

                    else:

                        self.selected = None

                        self.result = None

                else:

                    # Puede volver a intentar
                    self.selected = None

                    self.result = None


    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    def run(self):

        while self.running:

            dt = (
                self.clock.tick(
                    FPS
                )
                / 1000.0
            )

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False


                elif event.type == pygame.VIDEORESIZE:

                    self.window = pygame.display.set_mode(

                        event.size,

                        pygame.RESIZABLE

                    )


                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.running = False


                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        self.handle_click(

                            self.logical(
                                event.pos
                            )

                        )

            self.update(
                dt
            )

            self.draw()

        pygame.quit()


# ============================================================
# INICIO
# ============================================================

if __name__ == "__main__":

    TriviaApp().run()