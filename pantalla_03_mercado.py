import os
import sys
import math
import random
import pygame

# ============================================================
# DATA CHEF
# PANTALLA 03 - EL MERCADO DE LOS INGREDIENTES
# ============================================================

pygame.init()

# Color auxiliar para textos secundarios del HUD.
MUTED = (126, 134, 142)

WIDTH, HEIGHT = 1536, 864
FPS = 60

# ============================================================
# PALETA
# ============================================================

BG = (247, 244, 238)
WHITE = (255, 255, 255)
DARK = (43, 50, 57)
DARK_2 = (71, 78, 84)

ORANGE = (239, 103, 12)
ORANGE_DARK = (211, 78, 7)
ORANGE_SOFT = (255, 243, 229)

SKY = (103, 183, 229)
ROAD = (68, 72, 72)
ROAD_DARK = (43, 47, 48)
ROAD_SHADOW = (34, 38, 39)
SIDEWALK = (220, 216, 204)
SIDEWALK_LIGHT = (242, 238, 224)
CURB = (188, 184, 174)
LANE = (245, 241, 222)
ROAD_HIGHLIGHT = (91, 95, 94)

CREAM = (255, 249, 240)
CREAM_2 = (249, 241, 229)
BORDER = (228, 218, 206)

BLUE = (42, 116, 207)
BLUE_SOFT = (232, 243, 255)

YELLOW = (226, 145, 33)
YELLOW_SOFT = (255, 244, 222)

RED = (190, 63, 48)
RED_SOFT = (255, 237, 233)

PURPLE = (123, 76, 151)
PURPLE_SOFT = (245, 236, 250)

GREEN = (52, 148, 88)
GREEN_SOFT = (231, 247, 236)

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
                    (int(w * scale), int(h * scale))
                )

        return img

    except Exception as e:
        print("[DATA CHEF] Error:", path, e)
        return None


def load_first_img(candidates, max_size=None, label="imagen"):
    for name in candidates:
        path = os.path.join(ASSETS, name)

        if os.path.exists(path):
            img = load_img(name, max_size)

            if img is not None:
                print(f"[DATA CHEF] {label}: usando {name}")
                return img, name

    print(f"[DATA CHEF] Falta {label}. Se probaron:")
    for name in candidates:
        print("   -", os.path.join(ASSETS, name))

    return None, None


def rr(surface, rect, color, radius=18, border=0, border_color=None):
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


def txt(surface, value, font, color, position, center=False):
    image = font.render(value, True, color)
    rect = image.get_rect()

    if center:
        rect.center = position
    else:
        rect.topleft = position

    surface.blit(image, rect)
    return rect


def shadow(surface, rect, radius=20, offset=5, alpha=45):
    layer = pygame.Surface(
        (rect.width + 30, rect.height + 30),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        layer,
        (25, 30, 33, alpha),
        (15 + offset, 15 + offset, rect.width, rect.height),
        border_radius=radius
    )

    surface.blit(
        layer,
        (rect.x - 15, rect.y - 15)
    )


def circle_badge(surface, center, radius, fill, label, font, text_color=WHITE):
    pygame.draw.circle(surface, fill, center, radius)
    txt(surface, label, font, text_color, center, True)


# ============================================================
# CLASE PRINCIPAL
# ============================================================

class Market:

    def __init__(self):

        self.window = pygame.display.set_mode(
            (0, 0),
            pygame.RESIZABLE
        )

        pygame.display.set_caption(
            "DATA CHEF | El Mercado de los Ingredientes"
        )

        self.screen = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        self.clock = pygame.time.Clock()
        self.running = True

        self.scale = 1.0
        self.ox = 0
        self.oy = 0
        self.t = 0.0

        # ====================================================
        # ESTADO
        # ====================================================

        self.mode = "intro"
        self.score = 1250
        self.feedback = ""

        # ====================================================
        # JUGADOR
        # ====================================================

        self.player_x = 790.0
        self.player_y = 792.0
        self.player_speed = 280.0
        self.player_moving = False

        # ====================================================
        # FUENTES / ESTACIONES
        # ====================================================

        self.building_info = [
            {
                "short": "BASE DE DATOS",
                "name": "BASE DE DATOS CORPORATIVA",
                "correct": True,
                "color": BLUE,
                "soft": BLUE_SOFT,
                "symbol": "01"
            },
            {
                "short": "ARCHIVO EXCEL",
                "name": "ARCHIVO EXCEL DEL ÁREA",
                "correct": False,
                "color": YELLOW,
                "soft": YELLOW_SOFT,
                "symbol": "02"
            },
            {
                "short": "FUENTE EXTERNA",
                "name": "FUENTES EXTERNAS NO VERIFICADAS",
                "correct": False,
                "color": RED,
                "soft": RED_SOFT,
                "symbol": "03"
            },
            {
                "short": "MENSAJE / CHAT",
                "name": "DATO COPIADO DE UN MENSAJE",
                "correct": False,
                "color": PURPLE,
                "soft": PURPLE_SOFT,
                "symbol": "04"
            }
        ]

        # ====================================================
        # IMÁGENES
        # ====================================================

        self.logo = load_img(
            "logo_maresa.png",
            (225, 65)
        )

        self.chef_img = load_img(
            "chef_pensando.png",
            (315, 450)
        )

        self.player_img = load_img(
            "chef_jugando.png",
            (105, 145)
        )

        if self.player_img is None:
            self.player_img = load_img(
                "chef.png",
                (105, 145)
            )

        self.building_files = [
            (
                "BASE DE DATOS",
                [
                    "edificio_bases_datos.png",
                    "edificio_1.png"
                ]
            ),
            (
                "ARCHIVO EXCEL",
                [
                    "edificio_archivos_excel.png",
                    "edificio_2.png"
                ]
            ),
            (
                "FUENTE EXTERNA",
                [
                    "edificio_fuentes_externas.png",
                    "edificio_fuentes_datos.png",
                    "edificio_3.png"
                ]
            ),
            (
                "MENSAJE / CHAT",
                [
                    "edificio_mensaje_chat.png",
                    "edificio_mensaje.png",
                    "edificio_chat.png",
                    "edificio_apis_sistemas.png",
                    "edificio_4.png"
                ]
            )
        ]

        self.buildings = []
        self.building_loaded_names = []

        for label, candidates in self.building_files:
            img, used_name = load_first_img(
                candidates,
                (218, 345),
                label
            )

            self.buildings.append(img)
            self.building_loaded_names.append(used_name)

        # ====================================================
        # POSICIONES DE INTRO
        # ====================================================

        self.intro_building_positions = [
            (500, 625),    # BASE DE DATOS
            (815, 625),    # ARCHIVO EXCEL
            (1130, 925),   # FUENTE EXTERNA
            (1400, 625)    # MENSAJE / CHAT
        ]

        # ====================================================
        # POSICIONES DEL MINIJUEGO
        # ====================================================

        self.game_building_positions = [
            (240, 555),
            (1310, 555),
            (500, 790),
            (1110, 790)
        ]

        # ====================================================
        # CALLES
        # ====================================================

        self.road_width = 82
        self.roundabout_radius = 92
        self.roundabout_inner = 44
        self.road_paths = self.build_road_paths()

        # ====================================================
        # FUENTES
        # ====================================================

        self.font = {
            "micro": pygame.font.SysFont("Arial", 12),
            "tiny": pygame.font.SysFont("Arial", 14),
            "small": pygame.font.SysFont("Arial", 17),
            "body": pygame.font.SysFont("Arial", 20),
            "bold": pygame.font.SysFont("Arial", 21, bold=True),
            "subtitle": pygame.font.SysFont("Arial", 26, bold=True),
            "title": pygame.font.SysFont("Arial", 42, bold=True),
            "thought": pygame.font.SysFont("Arial", 19, bold=True),
            "button": pygame.font.SysFont("Arial", 22, bold=True),
            "big": pygame.font.SysFont("Arial", 31, bold=True)
        }

        # ====================================================
        # ANIMACIONES
        # ====================================================

        self.particles = [
            [
                random.randrange(WIDTH),
                random.randrange(165, 630),
                random.uniform(0.15, 0.55)
            ]
            for _ in range(42)
        ]


    # ========================================================
    # COORDENADAS
    # ========================================================

    def logical(self, position):
        return (
            int((position[0] - self.ox) / self.scale),
            int((position[1] - self.oy) / self.scale)
        )


    # ========================================================
    # FONDO
    # ========================================================

    def background(self):

        # ----------------------------------------------------
        # CIELO
        # ----------------------------------------------------

        for y in range(143, 650):

            p = (y - 143) / 507

            color = (
                int(94 + 20 * p),
                int(178 + 10 * p),
                int(225 + 8 * p)
            )

            pygame.draw.line(
                self.screen,
                color,
                (0, y),
                (WIDTH, y)
            )

        # ----------------------------------------------------
        # SOL
        # ----------------------------------------------------

        pygame.draw.circle(
            self.screen,
            (255, 231, 193),
            (1465, 170),
            118
        )

        pygame.draw.circle(
            self.screen,
            (255, 241, 216),
            (1465, 170),
            86
        )

        # ----------------------------------------------------
        # NUBES
        # ----------------------------------------------------

        for x, y, s in [
            (45, 235, 1.0),
            (1450, 230, 0.88)
        ]:

            pygame.draw.circle(
                self.screen,
                WHITE,
                (x, y),
                int(42 * s)
            )

            pygame.draw.circle(
                self.screen,
                WHITE,
                (x + int(38 * s), y + 7),
                int(30 * s)
            )

            pygame.draw.circle(
                self.screen,
                WHITE,
                (x - int(36 * s), y + 9),
                int(29 * s)
            )

        # ----------------------------------------------------
        # EDIFICIOS DEL FONDO
        # ----------------------------------------------------

        city = [
            (0, 350, 115, 280),
            (110, 315, 105, 315),
            (215, 375, 100, 255),
            (1185, 345, 105, 285),
            (1290, 285, 105, 345),
            (1395, 360, 141, 270)
        ]

        for x, y, w, h in city:

            pygame.draw.rect(
                self.screen,
                (164, 180, 186),
                (x, y, w, h)
            )

            for wx in range(x + 14, x + w - 10, 25):

                for wy in range(y + 22, y + h - 20, 31):

                    pygame.draw.rect(
                        self.screen,
                        (208, 220, 222),
                        (wx, wy, 10, 13),
                        border_radius=2
                    )

        # ----------------------------------------------------
        # ÁRBOLES
        # ----------------------------------------------------

        for x, y in [
            (70, 560),
            (375, 565),
            (1160, 560),
            (1490, 560)
        ]:

            pygame.draw.rect(
                self.screen,
                (101, 70, 44),
                (x - 5, y, 10, 72)
            )

            pygame.draw.circle(
                self.screen,
                (52, 126, 53),
                (x, y),
                41
            )

            pygame.draw.circle(
                self.screen,
                (67, 141, 61),
                (x - 23, y + 10),
                28
            )

            pygame.draw.circle(
                self.screen,
                (48, 108, 47),
                (x + 24, y + 10),
                29
            )

        # ----------------------------------------------------
        # VEREDA
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (224, 219, 207),
            (0, 632, WIDTH, 18)
        )

        pygame.draw.line(
            self.screen,
            (190, 187, 179),
            (0, 650),
            (WIDTH, 650),
            3
        )

        # ----------------------------------------------------
        # CARRETERA / AVENIDA
        # ----------------------------------------------------

        # Franja de transición de la vereda a la avenida.
        pygame.draw.rect(
            self.screen,
            SIDEWALK,
            (0, 650, WIDTH, 9)
        )

        pygame.draw.line(
            self.screen,
            CURB,
            (0, 658),
            (WIDTH, 658),
            3
        )

        pygame.draw.rect(
            self.screen,
            ROAD_DARK,
            (0, 660, WIDTH, 204)
        )

        pygame.draw.rect(
            self.screen,
            ROAD,
            (0, 665, WIDTH, 199)
        )

        # ----------------------------------------------------
        # CARRILES
        # ----------------------------------------------------

        for x in range(-100, WIDTH + 100, 190):

            pygame.draw.polygon(
                self.screen,
                (239, 235, 217),
                [
                    (x, 800),
                    (x + 68, 800),
                    (x + 38, 818),
                    (x - 30, 818)
                ]
            )

        # ----------------------------------------------------
        # PARTÍCULAS
        # ----------------------------------------------------

        for p in self.particles:

            p[1] -= p[2]

            if p[1] < 145:
                p[1] = 630

            pygame.draw.circle(
                self.screen,
                WHITE,
                (int(p[0]), int(p[1])),
                2
            )


    # ========================================================
    # HEADER
    # ========================================================

    def header(self):

        pygame.draw.rect(
            self.screen,
            (253, 250, 245),
            (0, 0, WIDTH, 143)
        )

        pygame.draw.line(
            self.screen,
            ORANGE,
            (0, 141),
            (WIDTH, 141),
            3
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        if self.logo:
            self.screen.blit(
                self.logo,
                (38, 39)
            )

        # ----------------------------------------------------
        # SEPARADOR
        # ----------------------------------------------------

        pygame.draw.line(
            self.screen,
            (225, 218, 207),
            (230, 30),
            (230, 110),
            1
        )

        # ----------------------------------------------------
        # MARCA
        # ----------------------------------------------------

        txt(
            self.screen,
            "DATA",
            self.font["subtitle"],
            DARK,
            (270, 34)
        )

        txt(
            self.screen,
            "CHEF",
            self.font["subtitle"],
            ORANGE,
            (365, 34)
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        txt(
            self.screen,
            "EL MERCADO",
            self.font["bold"],
            DARK,
            (270, 78)
        )

        txt(
            self.screen,
            "DE LOS INGREDIENTES",
            self.font["bold"],
            ORANGE,
            (450, 78)
        )

        # ----------------------------------------------------
        # MISIÓN
        # ----------------------------------------------------

        mission = pygame.Rect(
            1080, 34, 220, 68
        )

        rr(
            self.screen,
            mission,
            WHITE,
            20,
            1,
            BORDER
        )

        circle_badge(
            self.screen,
            (1108, 68),
            19,
            ORANGE,
            "01",
            self.font["tiny"]
        )

        txt(
            self.screen,
            "PRIMER PASO",
            self.font["tiny"],
            MUTED,
            (1138, 45)
        )

        txt(
            self.screen,
            "CONSEGUIR DATOS",
            self.font["small"],
            DARK,
            (1138, 61)
        )

        txt(
            self.screen,
            "DE CALIDAD",
            self.font["small"],
            DARK,
            (1138, 78)
        )

        # ----------------------------------------------------
        # VOLVER
        # ----------------------------------------------------

        back = pygame.Rect(
            1320, 35, 190, 68
        )

        hover = back.collidepoint(
            self.logical(
                pygame.mouse.get_pos()
            )
        )

        rr(
            self.screen,
            back,
            ORANGE_SOFT if hover else WHITE,
            34,
            2,
            (247, 184, 120)
        )

        txt(
            self.screen,
            "←  VOLVER",
            self.font["bold"],
            ORANGE,
            back.center,
            True
        )


    # ========================================================
    # BRIEFING MODERNO
    # ========================================================

    def briefing(self):

        panel = pygame.Rect(
            350,
            184,
            575,
            198
        )

        shadow(
            self.screen,
            panel,
            radius=26,
            offset=4,
            alpha=50
        )

        rr(
            self.screen,
            panel,
            CREAM,
            26,
            2,
            (236, 211, 183)
        )

        # Línea naranja lateral
        pygame.draw.rect(
            self.screen,
            ORANGE,
            (350, 205, 5, 155),
            border_radius=3
        )

        # Encabezado
        pygame.draw.circle(
            self.screen,
            ORANGE,
            (382, 217),
            7
        )

        txt(
            self.screen,
            "BRIEFING DEL CHEF",
            self.font["small"],
            ORANGE,
            (399, 207)
        )

        pygame.draw.line(
            self.screen,
            BORDER,
            (380, 241),
            (895, 241),
            1
        )

        txt(
            self.screen,
            "PRIMER INGREDIENTE",
            self.font["tiny"],
            MUTED,
            (380, 257)
        )

        txt(
            self.screen,
            "DATOS DE CALIDAD",
            self.font["subtitle"],
            DARK,
            (380, 274)
        )

        txt(
            self.screen,
            "Busca la materia prima más confiable",
            self.font["body"],
            DARK,
            (380, 316)
        )

        txt(
            self.screen,
            "para preparar una receta de calidad.",
            self.font["body"],
            DARK,
            (380, 344)
        )

        # Badge de fuentes
        badge = pygame.Rect(
            775, 318, 115, 37
        )

        rr(
            self.screen,
            badge,
            ORANGE_SOFT,
            18,
            1,
            (246, 187, 127)
        )

        txt(
            self.screen,
            "4 FUENTES",
            self.font["tiny"],
            ORANGE,
            badge.center,
            True
        )


    # ========================================================
    # CHEF
    # ========================================================

    def draw_chef(self):

        if self.chef_img:

            bob = math.sin(self.t * 2.0) * 2

            r = self.chef_img.get_rect()

            r.midbottom = (
                166,
                int(863 + bob)
            )

            self.screen.blit(
                self.chef_img,
                r
            )

        # ----------------------------------------------------
        # PLACA DEL PERSONAJE
        # ----------------------------------------------------

        tag = pygame.Rect(
            44, 362, 232, 42
        )

        shadow(
            self.screen,
            tag,
            radius=21,
            offset=2,
            alpha=28
        )

        rr(
            self.screen,
            tag,
            WHITE,
            21,
            1,
            BORDER
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (67, 383),
            7
        )

        txt(
            self.screen,
            "GUÍA DEL MERCADO",
            self.font["small"],
            DARK,
            (82, 372)
        )


    # ========================================================
    # ETIQUETAS DE FUENTES
    # ========================================================

    def source_card(self, index, x, y):

        info = self.building_info[index]

        color = info["color"]

        # ----------------------------------------------------
        # Tarjeta superior
        # ----------------------------------------------------

        card = pygame.Rect(
            x - 116,
            y,
            242,
            43
        )

        shadow(
            self.screen,
            card,
            radius=21,
            offset=2,
            alpha=28
        )

        rr(
            self.screen,
            card,
            WHITE,
            21,
            2,
            color
        )

        circle_badge(
            self.screen,
            (card.x + 22, card.centery),
            15,
            color,
            info["symbol"],
            self.font["micro"]
        )

        text_center_x = int(card.x + 42 + (card.width - 52) / 2)

        txt(
            self.screen,
            info["short"],
            self.font["small"],
            color,
            (text_center_x, card.centery),
            center=True
        )



    # ========================================================
    # EDIFICIOS
    # ========================================================

    def draw_buildings(self, game=False):

        positions = (
            self.game_building_positions
            if game
            else self.intro_building_positions
        )

        for index, (img, position) in enumerate(
            zip(self.buildings, positions)
        ):

            x, y = position
            info = self.building_info[index]


            # ------------------------------------------------
            # Sombra
            # ------------------------------------------------

            shadow_surface = pygame.Surface(
                (250, 134),
                pygame.SRCALPHA
            )

            pygame.draw.ellipse(
                shadow_surface,
                (0, 0, 0, 65),
                (0, 0, 250, 34)
            )

            self.screen.blit(
                shadow_surface,
                (x - 125, y - 5)
            )

            # ------------------------------------------------
            # Edificio
            # ------------------------------------------------

            if img:

                rect = img.get_rect()

                rect.midbottom = (
                    x,
                    y
                )

                self.screen.blit(
                    img,
                    rect
                )

            else:

                rect = pygame.Rect(
                    x - 90,
                    y - 245,
                    180,
                    245
                )

                rr(
                    self.screen,
                    rect,
                    info["color"],
                    14,
                    2,
                    WHITE
                )

                txt(
                    self.screen,
                    info["short"],
                    self.font["bold"],
                    WHITE,
                    rect.center,
                    True
                )

            # ------------------------------------------------
            # Etiquetas intro
            # ------------------------------------------------

            if not game:

                label_positions = [
                    (500, 425),
                    (815, 425),
                    (1130, 425),
                    (1400, 425)
                ]

                lx, ly = label_positions[index]

                self.source_card(
                    index,
                    lx,
                    ly
                )

            # ------------------------------------------------
            # Etiquetas del minijuego
            # ------------------------------------------------

            else:

                label = pygame.Rect(
                    x - 105,
                    y - 2,
                    210,
                    34
                )

                rr(
                    self.screen,
                    label,
                    WHITE,
                    12,
                    1,
                    info["color"]
                )

                txt(
                    self.screen,
                    info["short"],
                    self.font["small"],
                    info["color"],
                    label.center,
                    True
                )


    # ========================================================
    # PANEL INFERIOR
    # ========================================================

    def bottom(self):

        box = pygame.Rect(
            330,
            790,
            1180,
            62
        )

        shadow(
            self.screen,
            box,
            radius=20,
            offset=3,
            alpha=35
        )

        rr(
            self.screen,
            box,
            WHITE,
            20,
            2,
            (235, 208, 180)
        )

        # ----------------------------------------------------
        # Paso
        # ----------------------------------------------------

        circle_badge(
            self.screen,
            (368, 821),
            19,
            ORANGE,
            "01",
            self.font["tiny"]
        )

        # ----------------------------------------------------
        # Texto
        # ----------------------------------------------------

        txt(
            self.screen,
            "ENCUENTRA LA FUENTE MÁS CONFIABLE",
            self.font["bold"],
            DARK,
            (405, 799)
        )

        txt(
            self.screen,
            "Elige la mejor materia prima para tu receta.",
            self.font["small"],
            MUTED,
            (405, 825)
        )

        # ----------------------------------------------------
        # Botón
        # ----------------------------------------------------

        button = pygame.Rect(
            1122,
            798,
            368,
            47
        )

        hover = button.collidepoint(
            self.logical(
                pygame.mouse.get_pos()
            )
        )

        if hover:
            button = button.move(0, -2)

        pygame.draw.rect(
            self.screen,
            (202, 159, 124),
            (
                button.x,
                button.y + 5,
                button.w,
                button.h
            ),
            border_radius=15
        )

        rr(
            self.screen,
            button,
            ORANGE_DARK if hover else ORANGE,
            15
        )

        txt(
            self.screen,
            "EMPEZAR A BUSCAR  →",
            self.font["button"],
            WHITE,
            button.center,
            True
        )


    # ========================================================
    # CALLES
    # ========================================================

    def build_road_paths(self):

        cx, cy = 790, 700

        return [
            [
                (cx - 88, cy),
                (650, cy),
                (650, 610),
                (430, 610),
                (430, 555),
                (240, 555)
            ],
            [
                (cx + 88, cy),
                (930, cy),
                (930, 610),
                (1160, 610),
                (1160, 555),
                (1310, 555)
            ],
            [
                (cx - 88, cy),
                (650, cy),
                (650, 775),
                (560, 775),
                (560, 790),
                (500, 790)
            ],
            [
                (cx + 88, cy),
                (930, cy),
                (930, 775),
                (1040, 775),
                (1040, 790),
                (1110, 790)
            ]
        ]


    def _polyline_round(self, color, points, width):
        """Dibuja una polilínea con uniones redondeadas."""
        if len(points) < 2:
            return

        pygame.draw.lines(
            self.screen,
            color,
            False,
            points,
            int(width)
        )

        radius = int(width / 2)
        for px, py in points:
            pygame.draw.circle(
                self.screen,
                color,
                (int(px), int(py)),
                radius
            )

    def _draw_dashes(self, points, width=4, dash_len=24, gap_len=22,
                     color=LANE, phase=0.0):
        """Línea discontinua que sigue cada tramo de una calle."""
        if len(points) < 2:
            return

        for a, b in zip(points[:-1], points[1:]):
            ax, ay = a
            bx, by = b
            dx = bx - ax
            dy = by - ay
            seg_len = math.hypot(dx, dy)

            if seg_len <= 0:
                continue

            ux = dx / seg_len
            uy = dy / seg_len
            pos = phase % (dash_len + gap_len)

            while pos < seg_len:
                dash_start = pos
                dash_end = min(pos + dash_len, seg_len)

                if dash_end > dash_start:
                    p1 = (
                        int(ax + ux * dash_start),
                        int(ay + uy * dash_start)
                    )
                    p2 = (
                        int(ax + ux * dash_end),
                        int(ay + uy * dash_end)
                    )

                    pygame.draw.line(
                        self.screen,
                        color,
                        p1,
                        p2,
                        width
                    )

                pos += dash_len + gap_len

    def _draw_crosswalk(self, center, orientation="horizontal",
                        length=58, stripe_width=7, stripe_gap=7,
                        count=6):
        """Paso peatonal limpio y discreto."""
        cx, cy = center

        if orientation == "horizontal":
            total = count * stripe_width + (count - 1) * stripe_gap
            start = cx - total / 2

            for i in range(count):
                x = int(start + i * (stripe_width + stripe_gap))
                pygame.draw.rect(
                    self.screen,
                    LANE,
                    (x, int(cy - length / 2), stripe_width, length),
                    border_radius=2
                )
        else:
            total = count * stripe_width + (count - 1) * stripe_gap
            start = cy - total / 2

            for i in range(count):
                y = int(start + i * (stripe_width + stripe_gap))
                pygame.draw.rect(
                    self.screen,
                    LANE,
                    (int(cx - length / 2), y, length, stripe_width),
                    border_radius=2
                )

    def draw_road(self, points, width=None):
        if len(points) < 2:
            return

        width = width or self.road_width

        # --------------------------------------------------------
        # 1. Sombra exterior: separa la vía del fondo.
        # --------------------------------------------------------
        self._polyline_round(
            ROAD_SHADOW,
            points,
            width + 28
        )

        # --------------------------------------------------------
        # 2. Vereda / bordillo exterior.
        # --------------------------------------------------------
        self._polyline_round(
            SIDEWALK,
            points,
            width + 20
        )

        # Franja interior de la vereda para darle profundidad.
        self._polyline_round(
            SIDEWALK_LIGHT,
            points,
            width + 12
        )

        # --------------------------------------------------------
        # 3. Bordillo oscuro y asfalto.
        # --------------------------------------------------------
        self._polyline_round(
            ROAD_DARK,
            points,
            width + 8
        )

        self._polyline_round(
            ROAD,
            points,
            width
        )

        # Brillo sutil en el borde de la calzada.
        self._polyline_round(
            ROAD_HIGHLIGHT,
            points,
            2
        )

        # --------------------------------------------------------
        # 4. Línea central discontinua.
        # --------------------------------------------------------
        self._draw_dashes(
            points,
            width=4,
            dash_len=25,
            gap_len=21,
            color=LANE
        )

    def _draw_road_details(self):
        """Detalles decorativos de la red vial para evitar un aspecto plano."""

        # Pasos peatonales donde las vías desembocan cerca de los edificios.
        self._draw_crosswalk(
            (430, 575),
            "horizontal",
            length=54,
            stripe_width=6,
            stripe_gap=7,
            count=6
        )
        self._draw_crosswalk(
            (1160, 575),
            "horizontal",
            length=54,
            stripe_width=6,
            stripe_gap=7,
            count=6
        )

        self._draw_crosswalk(
            (530, 790),
            "vertical",
            length=52,
            stripe_width=6,
            stripe_gap=7,
            count=5
        )
        self._draw_crosswalk(
            (1070, 790),
            "vertical",
            length=52,
            stripe_width=6,
            stripe_gap=7,
            count=5
        )

        # Pequeñas islas de transición en las curvas superiores.
        for x, y in [(430, 610), (1160, 610)]:
            pygame.draw.circle(
                self.screen,
                CURB,
                (x, y),
                13
            )
            pygame.draw.circle(
                self.screen,
                SIDEWALK_LIGHT,
                (x, y),
                8
            )

    def draw_game_paths(self):
        # La red vial se dibuja primero para que los edificios y el jugador
        # queden visualmente por encima.
        for path in self.road_paths:
            self.draw_road(path)

        self._draw_road_details()

        # --------------------------------------------------------
        # ROTONDA CENTRAL
        # --------------------------------------------------------
        cx, cy = 790, 700

        # Sombra.
        pygame.draw.circle(
            self.screen,
            ROAD_SHADOW,
            (cx + 4, cy + 6),
            self.roundabout_radius + 17
        )

        # Anillo de vereda.
        pygame.draw.circle(
            self.screen,
            SIDEWALK,
            (cx, cy),
            self.roundabout_radius + 14
        )

        # Bordillo.
        pygame.draw.circle(
            self.screen,
            ROAD_DARK,
            (cx, cy),
            self.roundabout_radius + 7
        )

        # Asfalto circular.
        pygame.draw.circle(
            self.screen,
            ROAD,
            (cx, cy),
            self.roundabout_radius
        )

        # Línea interior del anillo.
        pygame.draw.circle(
            self.screen,
            LANE,
            (cx, cy),
            68,
            4
        )

        # Isla central.
        pygame.draw.circle(
            self.screen,
            CURB,
            (cx, cy),
            self.roundabout_inner + 8
        )

        pygame.draw.circle(
            self.screen,
            SIDEWALK_LIGHT,
            (cx, cy),
            self.roundabout_inner + 2
        )

        pygame.draw.circle(
            self.screen,
            (86, 132, 71),
            (cx, cy),
            34
        )

        pygame.draw.circle(
            self.screen,
            (64, 106, 58),
            (cx, cy),
            24
        )

        # Arbusto central.
        for ox, oy, radius in [
            (-13, -7, 13),
            (10, -9, 12),
            (1, 10, 14),
            (17, 7, 9)
        ]:
            pygame.draw.circle(
                self.screen,
                (76, 122, 62),
                (cx + ox, cy + oy),
                radius
            )

        # Poste/bandera central.
        pygame.draw.rect(
            self.screen,
            (103, 72, 42),
            (cx - 3, cy - 72, 6, 35),
            border_radius=3
        )

        pygame.draw.polygon(
            self.screen,
            ORANGE_DARK,
            [
                (cx, cy - 76),
                (cx + 45, cy - 55),
                (cx, cy - 34)
            ]
        )

        # Cuatro pequeños cruces peatonales alrededor de la rotonda.
        self._draw_crosswalk(
            (cx - self.roundabout_radius - 10, cy),
            "vertical",
            length=38,
            stripe_width=5,
            stripe_gap=5,
            count=5
        )
        self._draw_crosswalk(
            (cx + self.roundabout_radius + 10, cy),
            "vertical",
            length=38,
            stripe_width=5,
            stripe_gap=5,
            count=5
        )
        self._draw_crosswalk(
            (cx, cy - self.roundabout_radius - 10),
            "horizontal",
            length=38,
            stripe_width=5,
            stripe_gap=5,
            count=5
        )
        self._draw_crosswalk(
            (cx, cy + self.roundabout_radius + 10),
            "horizontal",
            length=38,
            stripe_width=5,
            stripe_gap=5,
            count=5
        )


    def draw_game_paths(self):

        for path in self.road_paths:
            self.draw_road(path)

        cx, cy = 790, 700

        pygame.draw.circle(
            self.screen,
            ROAD_DARK,
            (cx, cy),
            self.roundabout_radius + 8
        )

        pygame.draw.circle(
            self.screen,
            ROAD,
            (cx, cy),
            self.roundabout_radius
        )

        pygame.draw.circle(
            self.screen,
            (236, 231, 213),
            (cx, cy),
            67,
            4
        )

        pygame.draw.circle(
            self.screen,
            (214, 201, 164),
            (cx, cy),
            self.roundabout_inner
        )

        pygame.draw.circle(
            self.screen,
            (88, 125, 66),
            (cx, cy),
            32
        )

        pygame.draw.circle(
            self.screen,
            (63, 102, 55),
            (cx, cy),
            21
        )

        pygame.draw.rect(
            self.screen,
            (105, 72, 42),
            (cx - 5, cy - 74, 10, 35),
            border_radius=4
        )

        pygame.draw.polygon(
            self.screen,
            (105, 72, 42),
            [
                (cx, cy - 80),
                (cx + 48, cy - 57),
                (cx, cy - 36)
            ]
        )


    # ========================================================
    # MOVIMIENTO DEL JUGADOR
    # ========================================================

    def nearest_point_on_segment(
        self,
        px, py,
        ax, ay,
        bx, by
    ):

        vx = bx - ax
        vy = by - ay

        length_sq = vx * vx + vy * vy

        if length_sq == 0:

            return (
                ax,
                ay,
                math.hypot(px - ax, py - ay)
            )

        t = (
            ((px - ax) * vx + (py - ay) * vy)
            / length_sq
        )

        t = max(
            0.0,
            min(1.0, t)
        )

        qx = ax + vx * t
        qy = ay + vy * t

        return (
            qx,
            qy,
            math.hypot(px - qx, py - qy)
        )


    def nearest_road_point(self, x, y):

        best_x = x
        best_y = y
        best_dist = float("inf")

        for path in self.road_paths:

            for a, b in zip(
                path[:-1],
                path[1:]
            ):

                qx, qy, dist = (
                    self.nearest_point_on_segment(
                        x, y,
                        a[0], a[1],
                        b[0], b[1]
                    )
                )

                if dist < best_dist:

                    best_x = qx
                    best_y = qy
                    best_dist = dist

        dx = x - 790
        dy = y - 700
        d = math.hypot(dx, dy)

        if (
            self.roundabout_inner
            <= d
            <= self.roundabout_radius
        ):

            return x, y, 0.0, "roundabout"

        if d < self.roundabout_inner:

            if d == 0:

                return (
                    790 + self.roundabout_inner,
                    700,
                    0.0,
                    "island"
                )

            return (
                790 + dx / d * self.roundabout_inner,
                700 + dy / d * self.roundabout_inner,
                0.0,
                "island"
            )

        if d < best_dist:

            if d == 0:

                qx = 790 + self.roundabout_radius
                qy = 700

            else:

                qx = (
                    790
                    + dx / d * self.roundabout_radius
                )

                qy = (
                    700
                    + dy / d * self.roundabout_radius
                )

            return (
                qx,
                qy,
                d - self.roundabout_radius,
                "roundabout_edge"
            )

        return (
            best_x,
            best_y,
            best_dist,
            "road"
        )


    def constrain_player_to_roads(
        self,
        old_x,
        old_y
    ):

        nx, ny, dist, zone = (
            self.nearest_road_point(
                self.player_x,
                self.player_y
            )
        )

        allowed = self.road_width * 0.42

        if zone == "roundabout":
            return

        if zone == "island":

            self.player_x = nx
            self.player_y = ny
            return

        if dist > allowed:

            dx = self.player_x - nx
            dy = self.player_y - ny

            d = math.hypot(dx, dy)

            if d > 0:

                self.player_x = (
                    nx + dx / d * allowed
                )

                self.player_y = (
                    ny + dy / d * allowed
                )

            else:

                self.player_x = nx
                self.player_y = ny

        self.player_x = max(
            45,
            min(WIDTH - 45, self.player_x)
        )

        self.player_y = max(
            270,
            min(HEIGHT - 20, self.player_y)
        )


    def update_player(self, dt):

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        self.player_moving = bool(dx or dy)

        if dx and dy:

            dx *= 0.7071
            dy *= 0.7071

        old_x = self.player_x
        old_y = self.player_y

        self.player_x += (
            dx
            * self.player_speed
            * dt
        )

        self.player_y += (
            dy
            * self.player_speed
            * dt
        )

        self.constrain_player_to_roads(
            old_x,
            old_y
        )

        self.check_building_collision()


    def draw_player(self):

        if self.player_img:

            bob = (
                math.sin(self.t * 8) * 2
                if self.player_moving
                else 0
            )

            r = self.player_img.get_rect()

            r.midbottom = (
                int(self.player_x),
                int(self.player_y + bob)
            )

            self.screen.blit(
                self.player_img,
                r
            )

        else:

            pygame.draw.circle(
                self.screen,
                (255, 190, 120),
                (
                    int(self.player_x),
                    int(self.player_y - 45)
                ),
                25
            )


    # ========================================================
    # COLISIÓN
    # ========================================================

    def check_building_collision(self):

        for index, (bx, by) in enumerate(
            self.game_building_positions
        ):

            dx = self.player_x - bx
            dy = self.player_y - by

            if math.hypot(dx, dy) < 125:

                info = self.building_info[index]

                if info["correct"]:

                    self.mode = "success"
                    self.score += 250

                    self.feedback = (
                        "¡CORRECTO! Elegiste la "
                        "Base de Datos Corporativa."
                    )

                    print(
                        "[DATA CHEF] RESPUESTA CORRECTA"
                    )

                else:

                    self.mode = "wrong"

                    self.feedback = (
                        "Esta fuente tiene riesgos "
                        "para la calidad de los datos."
                    )

                    print(
                        "[DATA CHEF] FUENTE INCORRECTA:",
                        info["short"]
                    )

                return


    # ========================================================
    # HUD DEL MINIJUEGO
    # ========================================================

    def draw_game_header(self):

        box = pygame.Rect(
            515, 178, 550, 58
        )

        shadow(
            self.screen,
            box,
            radius=18,
            offset=3,
            alpha=35
        )

        rr(
            self.screen,
            box,
            CREAM,
            18,
            2,
            (236, 177, 112)
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (545, 207),
            10
        )

        txt(
            self.screen,
            "ENCUENTRA LA FUENTE MÁS CONFIABLE",
            self.font["bold"],
            DARK,
            (565, 195)
        )

        help_box = pygame.Rect(
            590, 248, 400, 36
        )

        rr(
            self.screen,
            help_box,
            WHITE,
            16,
            1,
            BORDER
        )

        txt(
            self.screen,
            "W A S D  /  FLECHAS  PARA CAMINAR",
            self.font["small"],
            DARK,
            help_box.center,
            True
        )

        # Score
        score = pygame.Rect(
            1180, 113, 330, 44
        )

        rr(
            self.screen,
            score,
            (38, 69, 96),
            20
        )

        txt(
            self.screen,
            f"⭐ {self.score}   |   CHEF DE TECNOLOGÍA",
            self.font["small"],
            WHITE,
            score.center,
            True
        )


    # ========================================================
    # PANTALLA DE JUEGO
    # ========================================================

    def draw_game(self):

        self.background()
        self.header()
        self.draw_game_paths()
        self.draw_buildings(game=True)
        self.draw_game_header()
        self.draw_player()


    # ========================================================
    # ÉXITO
    # ========================================================

    def draw_success(self):

        self.draw_game()

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (15, 35, 25, 150)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        panel = pygame.Rect(
            440, 270, 655, 305
        )

        shadow(
            self.screen,
            panel,
            radius=28,
            offset=6,
            alpha=80
        )

        rr(
            self.screen,
            panel,
            CREAM,
            28,
            4,
            GREEN
        )

        pygame.draw.circle(
            self.screen,
            GREEN,
            (
                768,
                345
            ),
            45 + int(
                math.sin(self.t * 4) * 4
            )
        )

        txt(
            self.screen,
            "✓",
            pygame.font.SysFont(
                "Arial",
                55,
                bold=True
            ),
            WHITE,
            (768, 345),
            True
        )

        txt(
            self.screen,
            "¡INGREDIENTE CORRECTO!",
            self.font["button"],
            GREEN,
            (768, 415),
            True
        )

        txt(
            self.screen,
            "BASE DE DATOS CORPORATIVA",
            self.font["bold"],
            DARK,
            (768, 453),
            True
        )

        txt(
            self.screen,
            "La fuente más confiable para comenzar.",
            self.font["body"],
            DARK,
            (768, 487),
            True
        )

        txt(
            self.screen,
            "+250 puntos",
            self.font["bold"],
            ORANGE,
            (768, 522),
            True
        )

        button = pygame.Rect(
            625, 548, 285, 48
        )

        rr(
            self.screen,
            button,
            ORANGE,
            15
        )

        txt(
            self.screen,
            "CONTINUAR  →",
            self.font["small"],
            WHITE,
            button.center,
            True
        )


    # ========================================================
    # ERROR
    # ========================================================

    def draw_wrong(self):

        self.draw_game()

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (80, 25, 20, 125)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        panel = pygame.Rect(
            450, 300, 635, 250
        )

        shadow(
            self.screen,
            panel,
            radius=28,
            offset=6,
            alpha=70
        )

        rr(
            self.screen,
            panel,
            CREAM,
            28,
            4,
            RED
        )

        txt(
            self.screen,
            "⚠  ESA OPCIÓN NO ES LA MEJOR",
            self.font["button"],
            RED,
            (768, 365),
            True
        )

        txt(
            self.screen,
            self.feedback,
            self.font["body"],
            DARK,
            (768, 415),
            True
        )

        txt(
            self.screen,
            "Regresa al centro e inténtalo nuevamente.",
            self.font["small"],
            MUTED,
            (768, 447),
            True
        )

        button = pygame.Rect(
            625, 480, 285, 48
        )

        rr(
            self.screen,
            button,
            ORANGE,
            15
        )

        txt(
            self.screen,
            "INTENTAR DE NUEVO",
            self.font["small"],
            WHITE,
            button.center,
            True
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        self.screen.fill(BG)

        if self.mode == "intro":

            self.background()
            self.header()
            self.briefing()
            self.draw_chef()
            self.draw_buildings()
            self.bottom()

        elif self.mode == "game":

            self.draw_game()

        elif self.mode == "success":

            self.draw_success()

        elif self.mode == "wrong":

            self.draw_wrong()

        # ----------------------------------------------------
        # ESCALADO RESPONSIVO
        # ----------------------------------------------------

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
            (230, 230, 230)
        )

        self.window.blit(
            scaled,
            (self.ox, self.oy)
        )

        pygame.display.flip()


    # ========================================================
    # LOOP
    # ========================================================

    def run(self):

        while self.running:

            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt

            for e in pygame.event.get():

                # ------------------------------------------------
                # CERRAR
                # ------------------------------------------------

                if e.type == pygame.QUIT:

                    self.running = False

                # ------------------------------------------------
                # REDIMENSIONAR
                # ------------------------------------------------

                elif e.type == pygame.VIDEORESIZE:

                    self.window = pygame.display.set_mode(
                        e.size,
                        pygame.RESIZABLE
                    )

                # ------------------------------------------------
                # ESC
                # ------------------------------------------------

                elif e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_ESCAPE:

                        self.running = False

                # ------------------------------------------------
                # CLICK
                # ------------------------------------------------

                elif (
                    e.type == pygame.MOUSEBUTTONDOWN
                    and e.button == 1
                ):

                    pos = self.logical(e.pos)

                    # ============================================
                    # INTRO
                    # ============================================

                    if self.mode == "intro":

                        # Volver
                        if pygame.Rect(
                            1320,
                            35,
                            190,
                            68
                        ).collidepoint(pos):

                            print(
                                "[DATA CHEF] VOLVER"
                            )

                            self.running = False

                        # Empezar
                        elif pygame.Rect(
                            1122,
                            798,
                            368,
                            47
                        ).collidepoint(pos):

                            self.mode = "game"

                            self.player_x = 790.0
                            self.player_y = 792.0

                            print(
                                "[DATA CHEF] "
                                "EMPEZAR -> MINIJUEGO"
                            )

                            print(
                                "[DATA CHEF] "
                                "Caminos activados"
                            )

                    # ============================================
                    # WRONG
                    # ============================================

                    elif self.mode == "wrong":

                        button = pygame.Rect(
                            625,
                            480,
                            285,
                            48
                        )

                        if button.collidepoint(pos):

                            self.mode = "game"

                            self.player_x = 790.0
                            self.player_y = 792.0

                            print(
                                "[DATA CHEF] "
                                "Reintento"
                            )

                    # ============================================
                    # SUCCESS
                    # ============================================

                    elif self.mode == "success":

                        button = pygame.Rect(
                            625,
                            548,
                            285,
                            48
                        )

                        if button.collidepoint(pos):

                            pantalla_04 = os.path.join(
                                BASE,
                                "pantalla_04_limpieza.py"
                            )

                            print(
                                "[DATA CHEF] "
                                "CONTINUAR -> "
                                "PANTALLA 04 · "
                                "LIMPIEZA Y ORDEN"
                            )

                            if os.path.exists(
                                pantalla_04
                            ):

                                import subprocess

                                subprocess.Popen(
                                    [
                                        sys.executable,
                                        pantalla_04
                                    ],
                                    cwd=BASE
                                )

                                self.running = False

                            else:

                                print(
                                    "[DATA CHEF] "
                                    "ERROR: No existe:",
                                    pantalla_04
                                )

            if self.mode == "game":

                self.update_player(dt)

            self.draw()

        pygame.quit()


# ============================================================
# EJECUCIÓN

# ============================================================

if __name__ == "__main__":
    Market().run()

