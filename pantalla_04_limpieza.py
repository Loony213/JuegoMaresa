import os
import sys
import math
import subprocess
import pygame

pygame.init()

# ============================================================
# DATA CHEF — PANTALLA 04
# LA COCINA DE LOS DATOS · PASO 2: LIMPIEZA Y ORDEN
#
# REDISEÑO PREMIUM — VIDEOJUEGO CORPORATIVO / ETL
# - Layout premium tipo dashboard / videojuego corporativo
# - Sin carretera ni elementos decorativos que compitan
# - Chef integrado como personaje principal
# - Flujo visual: briefing -> datos crudos -> 4 etapas -> avance
# - Mantiene la lógica de selección, puntos y pantalla 05
# ============================================================

WIDTH, HEIGHT = 1536, 864
FPS = 60

# ============================================================
# PALETA
# ============================================================

ORANGE = (239, 102, 8)
ORANGE_DARK = (198, 75, 0)
ORANGE_SOFT = (255, 238, 224)

NAVY = (31, 45, 54)
NAVY_2 = (43, 59, 69)
NAVY_3 = (61, 77, 87)

CREAM = (247, 244, 237)
CREAM_2 = (238, 233, 224)
WHITE = (255, 255, 255)

TEXT = (39, 49, 57)
TEXT_2 = (84, 97, 105)
MUTED = (137, 148, 154)

LINE = (218, 213, 204)
LINE_DARK = (176, 187, 192)

BLUE = (67, 143, 211)
BLUE_SOFT = (230, 241, 250)

YELLOW = (225, 164, 43)
YELLOW_SOFT = (252, 243, 218)

RED = (193, 69, 51)
RED_SOFT = (250, 232, 227)

PURPLE = (126, 86, 165)
PURPLE_SOFT = (239, 232, 247)

GREEN = (48, 145, 83)
GREEN_SOFT = (226, 243, 231)

BG = (242, 239, 232)
BG_PANEL = (250, 248, 244)

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")


# ============================================================
# UTILIDADES
# ============================================================

def load_img(name, max_size=None):
    path = os.path.join(ASSETS, name)

    if not os.path.exists(path):
        print("[DATA CHEF] Falta:", path)
        return None

    try:
        img = pygame.image.load(path).convert_alpha()

        if max_size:
            mw, mh = max_size
            w, h = img.get_size()

            if w > mw or h > mh:
                scale = min(mw / w, mh / h)
                img = pygame.transform.smoothscale(
                    img,
                    (
                        max(1, int(w * scale)),
                        max(1, int(h * scale))
                    )
                )

        return img

    except Exception as exc:
        print("[DATA CHEF] Error cargando", path, exc)
        return None


def rounded(surface, rect, color, radius=16, border=0, border_color=None):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )

    if border:
        pygame.draw.rect(
            surface,
            border_color or color,
            rect,
            width=border,
            border_radius=radius
        )


def shadow(surface, rect, radius=18, offset=6, alpha=30):
    layer = pygame.Surface(
        (rect.width + 28, rect.height + 28),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        layer,
        (25, 34, 40, alpha),
        (10, 10 + offset, rect.width, rect.height),
        border_radius=radius
    )

    surface.blit(
        layer,
        (rect.x - 10, rect.y - 10)
    )


def draw_text(surface, value, font, color, pos, center=False):
    image = font.render(str(value), True, color)
    rect = image.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(image, rect)
    return rect


def draw_line_text(surface, value, font, color, x, y, max_width):
    size = font.get_height()
    name = font.get_name()
    bold = font.get_bold()

    current = font

    while size > 10:
        current = pygame.font.SysFont(
            name,
            size,
            bold=bold
        )

        if current.size(value)[0] <= max_width:
            break

        size -= 1

    draw_text(surface, value, current, color, (x, y))


def pill(surface, rect, fill, label, font, color=TEXT):
    rounded(surface, rect, fill, rect.height // 2)
    draw_text(
        surface,
        label,
        font,
        color,
        rect.center,
        center=True
    )


def circle_badge(surface, center, radius, fill, label, font):
    pygame.draw.circle(
        surface,
        fill,
        center,
        radius
    )

    draw_text(
        surface,
        label,
        font,
        WHITE,
        center,
        center=True
    )


def checkmark(surface, center, color, scale=1.0):
    x, y = center

    pygame.draw.line(
        surface,
        color,
        (x - int(8 * scale), y),
        (x - int(2 * scale), y + int(6 * scale)),
        max(2, int(3 * scale))
    )

    pygame.draw.line(
        surface,
        color,
        (x - int(2 * scale), y + int(6 * scale)),
        (x + int(10 * scale), y - int(7 * scale)),
        max(2, int(3 * scale))
    )


# ============================================================
# ICONOS
# ============================================================

def draw_task_icon(surface, kind, center, color):
    x, y = center

    if kind == "duplicates":
        r1 = pygame.Rect(x - 15, y - 11, 20, 20)
        r2 = pygame.Rect(x - 5, y - 1, 20, 20)

        pygame.draw.rect(
            surface,
            color,
            r1,
            width=3,
            border_radius=4
        )
        pygame.draw.rect(
            surface,
            color,
            r2,
            width=3,
            border_radius=4
        )

    elif kind == "nulls":
        pygame.draw.circle(
            surface,
            color,
            (x, y),
            15,
            3
        )
        pygame.draw.line(
            surface,
            color,
            (x - 8, y + 8),
            (x + 8, y - 8),
            3
        )

    elif kind == "formats":
        pygame.draw.line(
            surface,
            color,
            (x - 15, y - 7),
            (x + 15, y - 7),
            3
        )
        pygame.draw.line(
            surface,
            color,
            (x - 15, y),
            (x + 8, y),
            3
        )
        pygame.draw.line(
            surface,
            color,
            (x - 15, y + 7),
            (x + 15, y + 7),
            3
        )

    elif kind == "validation":
        pygame.draw.circle(
            surface,
            color,
            (x, y),
            15,
            3
        )
        checkmark(
            surface,
            (x, y),
            color,
            0.8
        )


def soft_panel(surface, rect, fill=WHITE, border=LINE, radius=24,
               shadow_alpha=22, shadow_offset=6):
    shadow(surface, rect, radius=radius, offset=shadow_offset,
           alpha=shadow_alpha)
    rounded(surface, rect, fill, radius, 1, border)


def draw_grid(surface, area, step=32):
    """Grid muy sutil para dar profundidad sin parecer una cuadrícula técnica."""
    x0, y0, w, h = area
    for x in range(x0, x0 + w + 1, step):
        pygame.draw.line(surface, (232, 228, 220), (x, y0), (x, y0 + h), 1)
    for y in range(y0, y0 + h + 1, step):
        pygame.draw.line(surface, (232, 228, 220), (x0, y), (x0 + w, y), 1)


def draw_ring(surface, center, radius, color, width=2, alpha=255):
    layer = pygame.Surface((radius * 2 + 12, radius * 2 + 12), pygame.SRCALPHA)
    pygame.draw.circle(
        layer, (*color, alpha), (radius + 6, radius + 6), radius, width
    )
    surface.blit(layer, (center[0] - radius - 6, center[1] - radius - 6))


def draw_metric(surface, x, y, value, label, accent):
    pygame.draw.circle(surface, accent, (x, y + 13), 5)
    draw_text(surface, str(value), pygame.font.SysFont(
        "Arial", 20, bold=True), TEXT, (x + 15, y))
    draw_text(surface, label, pygame.font.SysFont("Arial", 12),
              MUTED, (x + 15, y + 23))


def draw_step_connector(surface, x, y1, y2, active_count, index):
    color = ORANGE if index < active_count else LINE
    pygame.draw.line(surface, color, (x, y1), (x, y2), 3)


# ============================================================
# CLASE PRINCIPAL
# ============================================================

class DataKitchen:

    def __init__(self):

        self.window = pygame.display.set_mode(
            (0, 0),
            pygame.RESIZABLE
        )

        pygame.display.set_caption(
            "DATA CHEF | La Cocina de los Datos"
        )

        self.screen = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        self.clock = pygame.time.Clock()

        self.running = True
        self.t = 0.0

        self.scale = 1.0
        self.ox = 0
        self.oy = 0

        # -----------------------------
        # ESTADO
        # -----------------------------

        self.score = 1500
        self.active = None
        self.completed = set()
        self.selected = set()

        self.message = (
            "Selecciona una etapa para comenzar la limpieza."
        )

        self.message_color = ORANGE

        # -----------------------------
        # CHEF
        # -----------------------------

        self.chef = load_img(
            "chef_limpieza.png",
            (365, 455)
        )

        if self.chef is None:
            self.chef = load_img(
                "chef_jugando.png",
                (365, 455)
            )

        if self.chef is None:
            self.chef = load_img(
                "chef.png",
                (365, 455)
            )

        # -----------------------------
        # FUENTES
        # -----------------------------

        self.font = {
            "micro": pygame.font.SysFont(
                "Arial", 12
            ),
            "tiny": pygame.font.SysFont(
                "Arial", 14
            ),
            "small": pygame.font.SysFont(
                "Arial", 17
            ),
            "body": pygame.font.SysFont(
                "Arial", 20
            ),
            "body_bold": pygame.font.SysFont(
                "Arial", 20,
                bold=True
            ),
            "bold": pygame.font.SysFont(
                "Arial", 24,
                bold=True
            ),
            "card": pygame.font.SysFont(
                "Arial", 21,
                bold=True
            ),
            "title": pygame.font.SysFont(
                "Arial", 42,
                bold=True
            ),
            "hero": pygame.font.SysFont(
                "Arial", 48,
                bold=True
            ),
            "number": pygame.font.SysFont(
                "Arial", 14,
                bold=True
            ),
            "mono": pygame.font.SysFont(
                "Consolas", 15,
                bold=True
            ),
            "button": pygame.font.SysFont(
                "Arial", 18,
                bold=True
            )
        }

        # -----------------------------
        # RETOS
        # -----------------------------

        self.tasks = [
            {
                "id": "duplicates",
                "title": "Duplicados",
                "subtitle": "Registros repetidos",
                "icon": "duplicates",
                "number": "01",
                "accent": BLUE,
                "soft": BLUE_SOFT,
                "instruction": "Encuentra los registros repetidos.",
                "hint": "Selecciona las filas duplicadas.",
                "bad": {1, 3},
                "rows": [
                    ["Juan Perez", "juan@mail.com", "ACTIVO"],
                    ["Maria Lopez", "maria@mail.com", "ACTIVO"],
                    ["Carlos Ruiz", "carlos@mail.com", "ACTIVO"],
                    ["Maria Lopez", "maria@mail.com", "ACTIVO"],
                    ["Ana Torres", "ana@mail.com", "ACTIVO"],
                ],
                "fixed": "Duplicados eliminados correctamente."
            },
            {
                "id": "nulls",
                "title": "Nulos",
                "subtitle": "Datos incompletos",
                "icon": "nulls",
                "number": "02",
                "accent": YELLOW,
                "soft": YELLOW_SOFT,
                "instruction": "Encuentra los datos incompletos.",
                "hint": "Selecciona las filas con valores vacíos.",
                "bad": {1, 4},
                "rows": [
                    ["Juan Perez", "Quito", "ACTIVO"],
                    ["Maria Lopez", "NULL", "ACTIVO"],
                    ["Carlos Ruiz", "Guayaquil", "ACTIVO"],
                    ["Ana Torres", "Cuenca", "ACTIVO"],
                    ["Luis Vera", "", "ACTIVO"],
                ],
                "fixed": "Valores nulos tratados y completados."
            },
            {
                "id": "formats",
                "title": "Formatos",
                "subtitle": "Estandarización",
                "icon": "formats",
                "number": "03",
                "accent": RED,
                "soft": RED_SOFT,
                "instruction": "Detecta los formatos inconsistentes.",
                "hint": "Selecciona las filas con formato incorrecto.",
                "bad": {0, 3},
                "rows": [
                    ["Juan Perez", "15/08/26", "ACTIVO"],
                    ["Maria Lopez", "2026-08-15", "ACTIVO"],
                    ["Carlos Ruiz", "2026-08-15", "ACTIVO"],
                    ["Ana Torres", "15-08-2026", "ACTIVO"],
                    ["Luis Vera", "2026-08-15", "ACTIVO"],
                ],
                "fixed": "Formatos normalizados correctamente."
            },
            {
                "id": "validation",
                "title": "Validaciones",
                "subtitle": "Reglas de negocio",
                "icon": "validation",
                "number": "04",
                "accent": PURPLE,
                "soft": PURPLE_SOFT,
                "instruction": "Encuentra los registros que no cumplen las reglas.",
                "hint": "Selecciona los valores que parecen inválidos.",
                "bad": {2},
                "rows": [
                    ["Juan Perez", "28 años", "VÁLIDO"],
                    ["Maria Lopez", "35 años", "VÁLIDO"],
                    ["Carlos Ruiz", "245 años", "REVISAR"],
                    ["Ana Torres", "42 años", "VÁLIDO"],
                    ["Luis Vera", "31 años", "VÁLIDO"],
                ],
                "fixed": "Datos validados con las reglas del negocio."
            }
        ]

        # Tarjetas: cuadrícula 2 x 2.
        self.card_rects = [
            pygame.Rect(850, 315, 285, 150),
            pygame.Rect(1160, 315, 285, 150),
            pygame.Rect(850, 485, 285, 150),
            pygame.Rect(1160, 485, 285, 150)
        ]

        self.row_rects = []

        # Partículas mínimas
        self.particles = [
            (92, 175, 2),
            (715, 185, 2),
            (1470, 260, 2),
            (625, 305, 1),
            (1480, 590, 1),
            (760, 680, 2),
            (55, 625, 1)
        ]


    # ========================================================
    # COORDENADAS
    # ========================================================

    def logical(self, pos):
        return (
            int((pos[0] - self.ox) / self.scale),
            int((pos[1] - self.oy) / self.scale)
        )


    # ========================================================
    # FONDO
    # ========================================================

    def background(self):

        self.screen.fill(BG)

        # Área principal
        pygame.draw.rect(
            self.screen, CREAM, (0, 88, WIDTH, 702)
        )

        # Footer oscuro
        pygame.draw.rect(
            self.screen, NAVY, (0, 790, WIDTH, 74)
        )

        # Línea de marca
        pygame.draw.rect(
            self.screen, ORANGE, (0, 86, WIDTH, 3)
        )

        # Grid técnico sutil en la zona derecha
        draw_grid(self.screen, (790, 112, 690, 640), 34)

        # Glow radial detrás del chef
        halo = pygame.Surface((690, 650), pygame.SRCALPHA)
        for radius, alpha in [
            (300, 7), (255, 9), (210, 12), (165, 16)
        ]:
            pygame.draw.circle(
                halo, (239, 102, 8, alpha), (330, 315), radius
            )
        self.screen.blit(halo, (0, 125))

        # Marco visual de la zona del chef
        chef_zone = pygame.Rect(55, 112, 680, 646)
        rounded(self.screen, chef_zone, (249, 246, 239), 32, 1, (232, 226, 216))

        # Detalles de profundidad
        pygame.draw.line(
            self.screen, (230, 224, 215),
            (770, 120), (770, 755), 1
        )

        # Micro partículas
        for x, y, r in self.particles:
            pygame.draw.circle(self.screen, (218, 211, 201), (x, y), r)

        # Indicadores decorativos tipo dashboard
        pygame.draw.circle(self.screen, ORANGE, (720, 720), 3)
        pygame.draw.line(self.screen, (225, 218, 209),
                         (690, 720), (720, 720), 1)
        pygame.draw.line(self.screen, (225, 218, 209),
                         (720, 720), (748, 720), 1)


    # ========================================================
    # HEADER
    # ========================================================

    def header(self):

        pygame.draw.rect(self.screen, WHITE, (0, 0, WIDTH, 88))
        pygame.draw.rect(self.screen, ORANGE, (0, 0, WIDTH, 7))

        # Marca
        pygame.draw.circle(self.screen, ORANGE, (58, 44), 23)
        pygame.draw.arc(self.screen, WHITE, (44, 30, 28, 28), 0.25, 2.75, 4)
        pygame.draw.line(self.screen, WHITE, (53, 47), (67, 36), 3)

        draw_text(self.screen, "LA COCINA", self.font["title"],
                  TEXT, (100, 20))
        draw_text(self.screen, "DE LOS DATOS", self.font["title"],
                  ORANGE, (350, 20))

        # Separador
        pygame.draw.line(self.screen, LINE, (680, 20), (680, 68), 1)

        # Step indicator
        circle_badge(self.screen, (728, 44), 21, ORANGE, "02",
                     self.font["tiny"])
        draw_text(self.screen, "LIMPIEZA Y ORDEN",
                  self.font["body_bold"], TEXT, (760, 23))
        draw_text(self.screen, "PREPARACIÓN · ETL",
                  self.font["tiny"], MUTED, (760, 51))

        # Estado superior
        status = pygame.Rect(1080, 20, 205, 48)
        rounded(self.screen, status, (246, 242, 235), 24, 1, LINE)
        pygame.draw.circle(self.screen, GREEN, (1102, 44), 5)
        draw_text(self.screen, "ESTACIÓN ACTIVA",
                  self.font["tiny"], TEXT_2, (1115, 34))

        # Score
        score = pygame.Rect(1305, 17, 190, 54)
        rounded(self.screen, score, NAVY, 27)

        draw_text(self.screen, "PUNTOS",
                  self.font["micro"], (185, 200, 206), (1327, 25))
        draw_text(self.screen, str(self.score),
                  self.font["bold"], WHITE, (1327, 39))


    # ========================================================
    # BRIEFING / HERO
    # ========================================================

    def hero(self):

        # Cabecera de la estación
        pill(
            self.screen,
            pygame.Rect(82, 130, 188, 30),
            ORANGE_SOFT,
            "BRIEFING DEL CHEF",
            self.font["tiny"],
            ORANGE
        )

        # Título
        draw_text(
            self.screen, "PREPARA", self.font["hero"], TEXT, (82, 172)
        )
        draw_text(
            self.screen, "LOS DATOS.", self.font["hero"], ORANGE, (82, 224)
        )

        # Línea editorial
        pygame.draw.rect(self.screen, ORANGE, (84, 286, 46, 4))
        draw_text(
            self.screen,
            "Antes de cocinar, hay que limpiar.",
            self.font["body_bold"],
            TEXT,
            (143, 277)
        )

        draw_text(
            self.screen,
            "Los ingredientes llegan crudos. Tu misión es detectar",
            self.font["small"], TEXT_2, (84, 312)
        )
        draw_text(
            self.screen,
            "errores y dejarlos listos para la siguiente etapa ETL.",
            self.font["small"], MUTED, (84, 337)
        )

        # Indicadores del proceso
        metric_y = 374
        for x, value, label, accent in [
            (86, "04", "ETAPAS", ORANGE),
            (205, "125", "PTS / RETO", BLUE),
            (345, "ETL", "PROCESO", PURPLE),
        ]:
            pygame.draw.circle(self.screen, accent, (x, metric_y + 11), 4)
            draw_text(self.screen, value, self.font["body_bold"],
                      TEXT, (x + 12, metric_y))
            draw_text(self.screen, label, self.font["micro"],
                      MUTED, (x + 12, metric_y + 24))

        # Chef
        if self.chef:
            bob = int(math.sin(self.t * 2.0) * 2)
            rect = self.chef.get_rect()
            rect.midbottom = (335, 765 + bob)
            self.screen.blit(self.chef, rect)

        # Globo premium: fuera de la cara
        bubble = pygame.Rect(435, 405, 265, 132)
        shadow(self.screen, bubble, radius=24, offset=5, alpha=28)
        rounded(self.screen, bubble, WHITE, 24, 1, LINE)

        # Punta orientada hacia el chef
        pygame.draw.polygon(
            self.screen, WHITE,
            [(435, 482), (408, 500), (435, 509)]
        )

        draw_text(
            self.screen, "“Primero limpio,”",
            self.font["body_bold"], TEXT, (462, 430)
        )
        draw_text(
            self.screen, "después transformo.”",
            self.font["body_bold"], ORANGE, (462, 458)
        )

        pygame.draw.line(
            self.screen, LINE, (462, 491), (670, 491), 1
        )

        draw_text(
            self.screen, "4 etapas  ·  1 objetivo",
            self.font["tiny"], MUTED, (462, 506)
        )

        # Mini etiqueta de personaje
        chef_tag = pygame.Rect(92, 712, 178, 28)
        rounded(self.screen, chef_tag, NAVY, 14)
        pygame.draw.circle(self.screen, ORANGE, (108, 726), 4)
        draw_text(
            self.screen, "CHEF DATA · GUÍA",
            self.font["micro"], WHITE, (120, 718)
        )

        # Datos crudos
        self.raw_data_panel()


    # ========================================================
    # DATOS CRUDOS
    # ========================================================

    def raw_data_panel(self):

        panel = pygame.Rect(82, 650, 620, 105)

        shadow(self.screen, panel, radius=20, offset=5, alpha=26)
        rounded(self.screen, panel, NAVY, 20)

        # Cabecera
        draw_text(self.screen, "DATOS CRUDOS",
                  self.font["body_bold"], WHITE, (106, 666))

        pill(
            self.screen,
            pygame.Rect(588, 663, 90, 25),
            ORANGE,
            "RAW INPUT",
            self.font["micro"],
            WHITE
        )

        pygame.draw.line(
            self.screen, NAVY_3, (106, 696), (678, 696), 1
        )

        raw = [
            ("Juan Perez", "juan@mail", "DUPLICADO"),
            ("MARIA", "NULL", "INCOMPLETO"),
            ("2025/08/45", "FORMATO", "CORREGIR"),
        ]

        for i, row in enumerate(raw):
            yy = 710 + i * 13

            draw_text(self.screen, row[0], self.font["mono"],
                      (235, 240, 242), (106, yy))
            draw_text(self.screen, row[1], self.font["mono"],
                      (164, 177, 183), (300, yy))
            draw_text(
                self.screen, row[2], self.font["mono"],
                ORANGE if i != 1 else YELLOW, (510, yy)
            )


    # ========================================================
    # PANEL DE ETAPAS
    # ========================================================

    def stages(self):

        # Encabezado
        draw_text(
            self.screen, "02 / ESTACIÓN DE LIMPIEZA",
            self.font["tiny"], ORANGE, (820, 118)
        )

        draw_text(
            self.screen,
            "Elige qué ingrediente quieres limpiar",
            self.font["bold"], TEXT, (820, 141)
        )

        completed = len(self.completed)

        # Estado de progreso
        progress = pygame.Rect(820, 185, 625, 44)
        rounded(self.screen, progress, WHITE, 22, 1, LINE)

        # Mini círculos de progreso
        for i in range(4):
            cx = 845 + i * 24
            pygame.draw.circle(
                self.screen,
                GREEN if i < completed else LINE,
                (cx, 207), 5
            )

        draw_text(
            self.screen,
            f"{completed}/4",
            self.font["body_bold"], TEXT, (960, 193)
        )
        draw_text(
            self.screen,
            "ETAPAS COMPLETADAS",
            self.font["micro"], MUTED, (1005, 198)
        )

        # Barra fina
        bar = pygame.Rect(1150, 201, 270, 8)
        rounded(self.screen, bar, (232, 229, 222), 4)
        if completed:
            rounded(
                self.screen,
                pygame.Rect(
                    1150, 201,
                    int(270 * completed / 4), 8
                ),
                GREEN if completed == 4 else ORANGE,
                4
            )

        # Línea de flujo vertical entre filas
        pygame.draw.line(
            self.screen, (221, 216, 208),
            (1138, 390), (1138, 560), 2
        )

        for index, (task, rect) in enumerate(
            zip(self.tasks, self.card_rects)
        ):
            done = task["id"] in self.completed
            self.draw_stage_card(task, rect, index, done)


    def draw_stage_card(self, task, rect, index, done):

        mouse = self.logical(pygame.mouse.get_pos())
        hover = rect.collidepoint(mouse)

        accent = GREEN if done else task["accent"]

        if done:
            fill = GREEN_SOFT
            border = GREEN
        elif hover:
            fill = WHITE
            border = accent
        else:
            fill = WHITE
            border = (225, 221, 214)

        # Elevación
        shadow(
            self.screen, rect,
            radius=24,
            offset=7 if hover else 5,
            alpha=32 if hover else 20
        )

        rounded(self.screen, rect, fill, 24, 2, border)

        # Banda superior de color
        rounded(
            self.screen,
            pygame.Rect(rect.x + 18, rect.y + 15, 48, 5),
            accent, 3
        )

        # Número grande
        circle_badge(
            self.screen,
            (rect.x + 43, rect.y + 48),
            22, accent, task["number"], self.font["number"]
        )

        # Icono
        draw_task_icon(
            self.screen, task["icon"],
            (rect.x + 43, rect.y + 112), accent
        )

        # Texto
        draw_text(
            self.screen, task["title"],
            self.font["card"], TEXT,
            (rect.x + 78, rect.y + 29)
        )

        draw_text(
            self.screen, task["subtitle"],
            self.font["tiny"], MUTED,
            (rect.x + 78, rect.y + 58)
        )

        # Estado / CTA
        if done:
            pill(
                self.screen,
                pygame.Rect(rect.x + 78, rect.y + 94, 155, 27),
                GREEN,
                "✓  COMPLETADO",
                self.font["micro"], WHITE
            )
        elif hover:
            pill(
                self.screen,
                pygame.Rect(rect.x + 78, rect.y + 94, 155, 27),
                accent,
                "ABRIR ETAPA  →",
                self.font["micro"], WHITE
            )
        else:
            pill(
                self.screen,
                pygame.Rect(rect.x + 78, rect.y + 94, 155, 27),
                task["soft"],
                "ABRIR ETAPA  →",
                self.font["micro"], accent
            )

        # Punto de estado
        pygame.draw.circle(
            self.screen,
            GREEN if done else (211, 207, 199),
            (rect.right - 23, rect.y + 25), 4
        )


    # ========================================================
    # FOOTER
    # ========================================================

    def footer(self):

        completed = len(self.completed)

        # Separador superior
        pygame.draw.rect(self.screen, NAVY_2, (0, 790, WIDTH, 1))

        if completed == 4:
            title = "¡ESTACIÓN COMPLETADA!"
            subtitle = "Todos los ingredientes están limpios y listos para cocinar."
            color = GREEN
        else:
            title = "TU MISIÓN"
            subtitle = self.message
            color = ORANGE

        draw_text(
            self.screen, title,
            self.font["body_bold"], color, (82, 806)
        )

        draw_text(
            self.screen, subtitle,
            self.font["tiny"], (197, 209, 214), (82, 835)
        )

        # Estado central
        state = pygame.Rect(980, 808, 190, 34)
        rounded(self.screen, state, NAVY_2, 17)
        draw_text(
            self.screen,
            f"PROGRESO  {completed}/4",
            self.font["tiny"], WHITE,
            state.center, center=True
        )

        # CTA
        if completed == 4:
            button = pygame.Rect(1190, 802, 265, 46)
            hover = button.collidepoint(
                self.logical(pygame.mouse.get_pos())
            )

            rounded(
                self.screen, button,
                ORANGE_DARK if hover else ORANGE, 23
            )
            draw_text(
                self.screen, "SIGUIENTE ETAPA  →",
                self.font["button"], WHITE,
                button.center, center=True
            )
        else:
            status = pygame.Rect(1190, 808, 265, 34)
            rounded(self.screen, status, NAVY_2, 17)
            draw_text(
                self.screen, "SELECCIONA UNA ETAPA",
                self.font["tiny"], (192, 203, 209),
                status.center, center=True
            )


    # ========================================================
    # MODAL DEL RETO
    # ========================================================

    def challenge_panel(self):

        if self.active is None:
            return

        task = next(
            t for t in self.tasks
            if t["id"] == self.active
        )

        # Overlay
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (18, 27, 33, 180)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        # Modal
        panel = pygame.Rect(
            230,
            92,
            1075,
            700
        )

        shadow(
            self.screen,
            panel,
            radius=28,
            offset=10,
            alpha=80
        )

        rounded(
            self.screen,
            panel,
            CREAM,
            28,
            2,
            task["accent"]
        )

        # Header
        header = pygame.Rect(
            230,
            92,
            1075,
            122
        )

        rounded(
            self.screen,
            header,
            NAVY,
            28
        )

        pygame.draw.rect(
            self.screen,
            NAVY,
            (230, 160, 1075, 54)
        )

        circle_badge(
            self.screen,
            (290, 153),
            27,
            task["accent"],
            task["number"],
            self.font["small"]
        )

        draw_text(
            self.screen,
            task["title"].upper(),
            self.font["title"],
            WHITE,
            (340, 115)
        )

        draw_text(
            self.screen,
            "ESTACIÓN DE LIMPIEZA · SELECCIÓN DE DATOS",
            self.font["tiny"],
            (191, 204, 210),
            (342, 170)
        )

        pill(
            self.screen,
            pygame.Rect(
                1080,
                125,
                170,
                32
            ),
            task["soft"],
            "INGREDIENTE ACTIVO",
            self.font["micro"],
            task["accent"]
        )

        # Instrucción
        draw_text(
            self.screen,
            task["instruction"],
            self.font["bold"],
            TEXT,
            (295, 250)
        )

        draw_text(
            self.screen,
            task["hint"],
            self.font["small"],
            MUTED,
            (295, 285)
        )

        # Tabla
        table = pygame.Rect(
            295,
            330,
            945,
            320
        )

        shadow(
            self.screen,
            table,
            radius=18,
            offset=3,
            alpha=18
        )

        rounded(
            self.screen,
            table,
            WHITE,
            18,
            1,
            LINE
        )

        # Header tabla
        rounded(
            self.screen,
            pygame.Rect(
                297,
                332,
                941,
                48
            ),
            NAVY_2,
            15
        )

        headers = [
            ("SELECCIÓN", 355),
            ("NOMBRE", 505),
            ("VALOR", 800),
            ("ESTADO", 1075)
        ]

        for label, x in headers:
            draw_text(
                self.screen,
                label,
                self.font["tiny"],
                WHITE,
                (x, 356),
                center=True
            )

        # Filas
        self.row_rects = []

        y = 392

        for i, row in enumerate(task["rows"]):

            rect = pygame.Rect(
                315,
                y,
                905,
                45
            )

            self.row_rects.append(rect)

            selected = i in self.selected

            if selected:
                fill = task["soft"]
                border = task["accent"]
            else:
                fill = WHITE if i % 2 == 0 else (244, 246, 245)
                border = None

            rounded(
                self.screen,
                rect,
                fill,
                9,
                2 if selected else 0,
                border
            )

            # Selector
            cx = 355
            cy = rect.centery

            if selected:

                pygame.draw.circle(
                    self.screen,
                    task["accent"],
                    (cx, cy),
                    11
                )

                checkmark(
                    self.screen,
                    (cx, cy),
                    WHITE,
                    0.65
                )

            else:

                pygame.draw.circle(
                    self.screen,
                    (181, 192, 197),
                    (cx, cy),
                    10,
                    2
                )

            draw_text(
                self.screen,
                row[0],
                self.font["small"],
                TEXT,
                (405, cy),
                center=True
            )

            value = row[1] if row[1] else "VACÍO"

            value_color = (
                RED
                if value in ("NULL", "VACÍO")
                else TEXT
            )

            draw_text(
                self.screen,
                value,
                self.font["small"],
                value_color,
                (780, cy),
                center=True
            )

            status_color = (
                RED
                if row[2] == "REVISAR"
                else GREEN
                if row[2] == "VÁLIDO"
                else TEXT_2
            )

            draw_text(
                self.screen,
                row[2],
                self.font["small"],
                status_color,
                (1060, cy),
                center=True
            )

            y += 49

        # Footer modal
        draw_text(
            self.screen,
            f"Filas seleccionadas: {len(self.selected)}",
            self.font["small"],
            MUTED,
            (315, 686)
        )

        cancel = pygame.Rect(
            760,
            665,
            180,
            52
        )

        rounded(
            self.screen,
            cancel,
            (236, 233, 226),
            17,
            1,
            LINE
        )

        draw_text(
            self.screen,
            "CANCELAR",
            self.font["button"],
            TEXT_2,
            cancel.center,
            center=True
        )

        confirm = pygame.Rect(
            960,
            665,
            260,
            52
        )

        mouse = self.logical(
            pygame.mouse.get_pos()
        )

        hover = confirm.collidepoint(mouse)

        rounded(
            self.screen,
            confirm,
            ORANGE_DARK if hover else ORANGE,
            17
        )

        draw_text(
            self.screen,
            "COMPROBAR  ✓",
            self.font["button"],
            WHITE,
            confirm.center,
            center=True
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        self.background()
        self.header()
        self.hero()
        self.stages()
        self.footer()

        if self.active is not None:
            self.challenge_panel()

        # Escalado
        ww, wh = self.window.get_size()

        self.scale = min(
            ww / WIDTH,
            wh / HEIGHT
        )

        rw = int(WIDTH * self.scale)
        rh = int(HEIGHT * self.scale)

        self.ox = (ww - rw) // 2
        self.oy = (wh - rh) // 2

        scaled = pygame.transform.smoothscale(
            self.screen,
            (rw, rh)
        )

        self.window.fill(
            (215, 215, 215)
        )

        self.window.blit(
            scaled,
            (self.ox, self.oy)
        )

        pygame.display.flip()


    # ========================================================
    # ABRIR RETO
    # ========================================================

    def open_task(self, task):

        if task["id"] in self.completed:

            self.message = (
                f"{task['title']} ya fue completado."
            )

            self.message_color = GREEN
            return

        self.active = task["id"]
        self.selected.clear()

        self.message = task["hint"]
        self.message_color = task["accent"]

        print(
            "[DATA CHEF] MINIJUEGO:",
            task["title"]
        )


    # ========================================================
    # COMPROBAR
    # ========================================================

    def check_task(self):

        if self.active is None:
            return

        task = next(
            t for t in self.tasks
            if t["id"] == self.active
        )

        if self.selected == task["bad"]:

            self.completed.add(
                task["id"]
            )

            self.score += 125

            self.message = (
                "✓ " + task["fixed"]
            )

            self.message_color = GREEN

            print(
                "[DATA CHEF] COMPLETADO:",
                task["title"]
            )

            self.active = None
            self.selected.clear()

            if len(self.completed) == 4:

                self.message = (
                    "¡Datos limpios y listos para cocinar!"
                )

                self.message_color = GREEN

                print(
                    "[DATA CHEF] PASO 2 COMPLETADO"
                )

        else:

            self.message = (
                "Revisa otra vez: todavía hay datos "
                "que no corresponden."
            )

            self.message_color = RED

            print(
                "[DATA CHEF] RESPUESTA INCORRECTA EN:",
                task["title"]
            )


    # ========================================================
    # SIGUIENTE PANTALLA
    # ========================================================

    def open_screen_05(self):

        pantalla_05 = os.path.join(
            BASE,
            "pantalla_05_reto_chef.py"
        )

        print(
            "[DATA CHEF] CONTINUAR -> RETO DEL CHEF"
        )

        if not os.path.exists(pantalla_05):

            print(
                "[DATA CHEF] ERROR: No existe:",
                pantalla_05
            )

            self.message = (
                "ERROR: No se encontró "
                "pantalla_05_reto_chef.py"
            )

            self.message_color = RED
            return

        try:

            subprocess.Popen(
                [sys.executable, pantalla_05],
                cwd=BASE
            )

            self.running = False

        except Exception as exc:

            print(
                "[DATA CHEF] ERROR abriendo pantalla 05:",
                exc
            )

            self.message = (
                "No se pudo abrir la siguiente pantalla."
            )

            self.message_color = RED


    # ========================================================
    # CLICK
    # ========================================================

    def click(self, pos):

        # Modal
        if self.active is not None:

            for i, rect in enumerate(self.row_rects):

                if rect.collidepoint(pos):

                    if i in self.selected:
                        self.selected.remove(i)
                    else:
                        self.selected.add(i)

                    return

            cancel = pygame.Rect(
                760,
                665,
                180,
                52
            )

            if cancel.collidepoint(pos):

                self.active = None
                self.selected.clear()
                return

            confirm = pygame.Rect(
                960,
                665,
                260,
                52
            )

            if confirm.collidepoint(pos):

                self.check_task()
                return

            return

        # Siguiente
        if len(self.completed) == 4:

            button = pygame.Rect(
                1190,
                802,
                265,
                46
            )

            if button.collidepoint(pos):

                self.open_screen_05()
                return

        # Etapas
        for task, rect in zip(
            self.tasks,
            self.card_rects
        ):

            if rect.collidepoint(pos):

                self.open_task(task)
                return


    # ========================================================
    # LOOP
    # ========================================================

    def run(self):

        while self.running:

            dt = (
                self.clock.tick(FPS)
                / 1000.0
            )

            self.t += dt

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

                        if self.active is not None:

                            self.active = None
                            self.selected.clear()

                        else:

                            self.running = False

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    self.click(
                        self.logical(event.pos)
                    )

            self.draw()

        pygame.quit()


# ============================================================
# INICIO
# ============================================================

if __name__ == "__main__":
    DataKitchen().run()
