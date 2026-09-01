import os
import sys
import math
import random
import pygame

pygame.init()

# ============================================================
# DATA CHEF | MARESA
# PANTALLA 06 - EL CHEF PREPARA EL PANEL
# VERSION PRO V2
# ============================================================

WIDTH, HEIGHT = 1536, 864
FPS = 60

# -------------------------
# PALETA PROFESIONAL
# -------------------------
BG = (248, 245, 238)
WHITE = (255, 255, 255)
ORANGE = (247, 116, 18)
DARK_ORANGE = (210, 85, 8)
DARK = (31, 45, 55)
DARK_2 = (43, 60, 70)
MUTED = (103, 115, 123)
LIGHT_ORANGE = (255, 239, 221)
PALE_ORANGE = (255, 247, 237)
BLUE = (52, 130, 205)
LIGHT_BLUE = (233, 243, 251)
GREEN = (43, 166, 99)
LINE = (226, 218, 207)
SOFT = (242, 238, 230)
GRAY = (221, 218, 211)

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")


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
                    (max(1, int(w * scale)), max(1, int(h * scale)))
                )

        print("[DATA CHEF] OK:", name)
        return img

    except Exception as e:
        print("[DATA CHEF] Error cargando", name, ":", e)
        return None


def rr(surface, rect, color, radius=20, border=0, border_color=None):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, color, rect, border_radius=radius)

    if border:
        pygame.draw.rect(
            surface,
            border_color if border_color else color,
            rect,
            width=border,
            border_radius=radius
        )


def text(surface, value, font, color, pos, center=False):
    image = font.render(value, True, color)
    rect = image.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(image, rect)
    return rect


def line(surface, color, start, end, width=2):
    pygame.draw.line(surface, color, start, end, width)


def draw_check(surface, center, color, scale=1.0, width=3):
    """Check vectorial estable, sin depender de glifos Unicode."""
    cx, cy = center
    pts = [
        (int(cx - 7 * scale), int(cy)),
        (int(cx - 2 * scale), int(cy + 5 * scale)),
        (int(cx + 8 * scale), int(cy - 7 * scale)),
    ]
    pygame.draw.lines(
        surface,
        color,
        False,
        pts,
        max(2, int(width * scale))
    )


class SteamParticle:
    def __init__(self, x, y):
        self.reset(x, y, random.uniform(0, 1))

    def reset(self, x, y, delay=0):
        self.x = x + random.uniform(-35, 35)
        self.y = y + random.uniform(-10, 10)
        self.delay = delay
        self.age = 0
        self.life = random.uniform(1.5, 2.8)
        self.speed = random.uniform(22, 48)
        self.size = random.uniform(8, 18)
        self.wave = random.uniform(0, math.pi * 2)

    def update(self, dt, origin):
        self.age += dt

        if self.delay > 0:
            self.delay -= dt
            return

        self.y -= self.speed * dt
        self.x += math.sin(self.age * 3 + self.wave) * 18 * dt

        if self.age > self.life:
            self.reset(origin[0], origin[1])

    def draw(self, surface):
        if self.delay > 0:
            return

        alpha = int(100 * max(0, 1 - self.age / self.life))
        radius = max(2, int(self.size * (1 - self.age / self.life * 0.35)))

        layer = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)

        pygame.draw.circle(
            layer,
            (255, 255, 255, alpha),
            (radius * 2, radius * 2),
            radius
        )

        surface.blit(
            layer,
            (int(self.x - radius * 2), int(self.y - radius * 2))
        )


class FlyingIngredient:
    def __init__(self, x, y, target, icon, label, delay):
        self.start = pygame.Vector2(x, y)
        self.target = pygame.Vector2(target)
        self.icon = icon
        self.label = label
        self.delay = delay
        self.progress = 0
        self.done = False

    def update(self, dt):
        if self.done:
            return

        if self.delay > 0:
            self.delay -= dt
            return

        self.progress += dt * 0.28

        if self.progress >= 1:
            self.progress = 1
            self.done = True

    def draw(self, surface, font):
        if self.delay > 0 or self.done:
            return

        t = self.progress
        ease = 1 - (1 - t) ** 3

        p0 = self.start
        p2 = self.target

        control = pygame.Vector2(
            (p0.x + p2.x) / 2,
            min(p0.y, p2.y) - 120
        )

        pos = (
            (1 - ease) ** 2 * p0
            + 2 * (1 - ease) * ease * control
            + ease ** 2 * p2
        )

        bob = math.sin(t * math.pi * 4) * 8

        rr(
            surface,
            pygame.Rect(
                int(pos.x - 52),
                int(pos.y - 40 + bob),
                104,
                80
            ),
            WHITE,
            18,
            2,
            LIGHT_ORANGE
        )

        text(
            surface,
            self.icon,
            font,
            DARK,
            (int(pos.x), int(pos.y - 4 + bob)),
            True
        )


class DataChefScreen:
    def __init__(self):
        self.window = pygame.display.set_mode(
            (0, 0),
            pygame.RESIZABLE
        )

        pygame.display.set_caption(
            "DATA CHEF | MARESA - Preparando el Panel"
        )

        self.screen = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        self.clock = pygame.time.Clock()

        self.running = True
        self.t = 0

        self.scale = 1
        self.ox = 0
        self.oy = 0

        # -------------------------
        # ESTADOS
        # -------------------------
        self.scene = "intro"
        self.scene_time = 0
        self.panel_reveal = 0

        # -------------------------
        # IMAGENES
        # -------------------------
        self.logo = load_img("logo_maresa.png", (230, 80))
        self.chef_cooking = load_img(
            "chef_cocinando.png",
            (470, 570)
        )
        self.chef_proud = load_img(
            "chef_orgulloso.png",
            (390, 510)
        )
        self.pot = load_img(
            "olla.png",
            (330, 250)
        )
        self.panel = load_img(
            "panel_final.png",
            (760, 470)
        )

        # -------------------------
        # FUENTES
        # -------------------------
        self.fonts = {
            "micro": pygame.font.SysFont("Arial", 13),
            "tiny": pygame.font.SysFont("Arial", 16),
            "small": pygame.font.SysFont("Arial", 19),
            "body": pygame.font.SysFont("Arial", 22),
            "body_bold": pygame.font.SysFont("Arial", 22, bold=True),
            "subtitle": pygame.font.SysFont("Arial", 29, bold=True),
            "title": pygame.font.SysFont("Arial", 54, bold=True),
            "big": pygame.font.SysFont("Arial", 72, bold=True),
            "button": pygame.font.SysFont("Arial", 24, bold=True),
            "number": pygame.font.SysFont("Arial", 20, bold=True),
            "icon": pygame.font.SysFont("Segoe UI Symbol", 38),
        }

        # -------------------------
        # ANIMACION
        # -------------------------
        self.steam_origin = (1110, 535)

        self.steam = [
            SteamParticle(
                self.steam_origin[0],
                self.steam_origin[1]
            )
            for _ in range(22)
        ]

        self.ingredients = [
            FlyingIngredient(
                250, 660, (1110, 560),
                "DB", "Base de datos", 0.2
            ),
            FlyingIngredient(
                470, 710, (1110, 560),
                "✦", "Datos limpios", 0.8
            ),
            FlyingIngredient(
                720, 700, (1110, 560),
                "OK", "Datos validados", 1.4
            ),
            FlyingIngredient(
                900, 720, (1110, 560),
                "INFO", "Información", 2.0
            ),
        ]

        print("[DATA CHEF] Pantalla 06 PRO V2 iniciada.")

    # ============================================================
    # UTILIDADES
    # ============================================================

    def logical(self, pos):
        return (
            int((pos[0] - self.ox) / self.scale),
            int((pos[1] - self.oy) / self.scale)
        )

    def set_scene(self, name):
        self.scene = name
        self.scene_time = 0
        print("[DATA CHEF] ESCENA ->", name)

    def draw_shadow(self, rect, radius=24, offset=(0, 7), alpha=32):
        shadow = pygame.Surface(
            (rect.width + 30, rect.height + 30),
            pygame.SRCALPHA
        )

        rr(
            shadow,
            pygame.Rect(
                15,
                15,
                rect.width,
                rect.height
            ),
            (20, 31, 39, alpha),
            radius
        )

        self.screen.blit(
            shadow,
            (
                rect.x - 15 + offset[0],
                rect.y - 15 + offset[1]
            )
        )

    def draw_badge(self, x, y, number, label, active=False):
        color = ORANGE if active else (181, 189, 193)
        fill = LIGHT_ORANGE if active else WHITE

        rr(
            self.screen,
            pygame.Rect(x, y, 42, 42),
            fill,
            21,
            2,
            color
        )

        text(
            self.screen,
            number,
            self.fonts["number"],
            color if active else MUTED,
            (x + 21, y + 21),
            True
        )

        text(
            self.screen,
            label,
            self.fonts["tiny"],
            DARK if active else MUTED,
            (x + 54, y + 5)
        )

    # ============================================================
    # FONDO
    # ============================================================

    def draw_background(self):
        self.screen.fill(BG)

        # Manchas decorativas suaves
        pygame.draw.ellipse(
            self.screen,
            (255, 232, 207),
            (1080, -150, 620, 390)
        )

        pygame.draw.ellipse(
            self.screen,
            (255, 237, 218),
            (-190, 690, 670, 300)
        )

        # Zona de cocina
        pygame.draw.rect(
            self.screen,
            (244, 240, 232),
            (0, 145, WIDTH, 650)
        )

        # Cuadrícula muy sutil
        for x in range(0, WIDTH, 100):
            line(
                self.screen,
                (239, 235, 227),
                (x, 145),
                (x, 795),
                1
            )

        for y in range(145, 796, 90):
            line(
                self.screen,
                (239, 235, 227),
                (0, y),
                (WIDTH, y),
                1
            )

        # Partículas pequeñas
        for i in range(18):
            x = int((i * 131 + self.t * 13) % WIDTH)
            y = int(160 + (i * 71) % 610)

            pygame.draw.circle(
                self.screen,
                ORANGE,
                (x, y),
                2
            )

    # ============================================================
    # HEADER NUEVO
    # ============================================================

    def draw_header(self):
        # Línea superior
        pygame.draw.rect(
            self.screen,
            ORANGE,
            (0, 0, WIDTH, 7)
        )

        # Barra principal
        pygame.draw.rect(
            self.screen,
            WHITE,
            (0, 7, WIDTH, 126)
        )

        # Separador
        line(
            self.screen,
            LINE,
            (0, 133),
            (WIDTH, 133),
            2
        )

        # Logo
        if self.logo:
            logo_rect = self.logo.get_rect(
                midleft=(42, 69)
            )
            self.screen.blit(self.logo, logo_rect)
        else:
            text(
                self.screen,
                "maresa",
                self.fonts["subtitle"],
                ORANGE,
                (42, 52)
            )

        # Separador logo
        line(
            self.screen,
            LINE,
            (230, 35),
            (230, 102),
            2
        )

        # Marca principal
        text(
            self.screen,
            "DATA",
            self.fonts["subtitle"],
            DARK,
            (270, 42)
        )

        text(
            self.screen,
            "CHEF",
            self.fonts["subtitle"],
            ORANGE,
            (356, 42)
        )

        text(
            self.screen,
            "ESTACIÓN 04  /  COCINANDO LOS DATOS",
            self.fonts["small"],
            MUTED,
            (270, 77)
        )

        # Estado de estación
        rr(
            self.screen,
            pygame.Rect(1110, 34, 350, 65),
            DARK,
            32
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (1142, 66),
            7
        )

        text(
            self.screen,
            "PASO 04",
            self.fonts["tiny"],
            (205, 216, 221),
            (1160, 45)
        )

        text(
            self.screen,
            "PREPARANDO EL PANEL",
            self.fonts["body_bold"],
            WHITE,
            (1160, 66)
        )

    # ============================================================
    # OLLA
    # ============================================================

    def draw_pot(self, x=1110, y=585):
        if self.pot:
            rect = self.pot.get_rect(center=(x, y))
            self.screen.blit(self.pot, rect)
            return

        # Olla fallback
        pygame.draw.ellipse(
            self.screen,
            (78, 86, 95),
            (x - 140, y - 35, 280, 135)
        )

        pygame.draw.ellipse(
            self.screen,
            (44, 50, 57),
            (x - 125, y - 50, 250, 65)
        )

        pygame.draw.ellipse(
            self.screen,
            (15, 20, 24),
            (x - 105, y - 43, 210, 42)
        )

        pygame.draw.ellipse(
            self.screen,
            (130, 140, 150),
            (x - 150, y + 5, 45, 35)
        )

        pygame.draw.ellipse(
            self.screen,
            (130, 140, 150),
            (x + 105, y + 5, 45, 35)
        )

        pygame.draw.line(
            self.screen,
            (42, 47, 53),
            (x - 90, y + 85),
            (x - 65, y + 115),
            13
        )

        pygame.draw.line(
            self.screen,
            (42, 47, 53),
            (x + 90, y + 85),
            (x + 65, y + 115),
            13
        )

    # ============================================================
    # CHEF
    # ============================================================

    def draw_chef_cooking(self, box):
        """Chef contenido dentro de su tarjeta; nunca invade títulos ni otros paneles."""
        # Sombra de piso dentro del panel
        floor = pygame.Rect(box.x + 38, box.bottom - 58, 320, 24)
        pygame.draw.ellipse(self.screen, (216, 209, 199), floor)

        if self.chef_cooking:
            iw, ih = self.chef_cooking.get_size()

            # El personaje ocupa una columna propia y queda limitado al panel.
            max_w = 300
            max_h = 390
            scale = min(max_w / iw, max_h / ih)

            scaled = pygame.transform.smoothscale(
                self.chef_cooking,
                (max(1, int(iw * scale)), max(1, int(ih * scale)))
            )

            rect = scaled.get_rect(
                midbottom=(box.x + 205, box.bottom - 35)
            )

            self.screen.blit(scaled, rect)

        else:
            rr(
                self.screen,
                pygame.Rect(box.x + 70, box.y + 115, 260, 330),
                WHITE,
                28,
                2,
                ORANGE
            )
            text(
                self.screen,
                "CHEF",
                self.fonts["title"],
                ORANGE,
                (box.x + 200, box.y + 270),
                True
            )

    # ============================================================
    # INTRO PROFESIONAL
    # ============================================================

    def draw_chef_intro(self):
        """
        Chef de portada.
        Importante: queda deliberadamente por debajo del titular para
        que NUNCA se dibuje encima de las frases de introducción.
        """
        # Zona visual reservada exclusivamente al personaje.
        chef_area = pygame.Rect(90, 493, 275, 262)

        # Sombra de suelo
        pygame.draw.ellipse(
            self.screen,
            (214, 208, 198),
            (chef_area.x + 5, chef_area.bottom - 22, 255, 26)
        )

        if self.chef_cooking:
            iw, ih = self.chef_cooking.get_size()

            # Escala contenida. El límite vertical es el importante:
            # el personaje jamás puede subir hasta el titular.
            scale = min(
                275 / iw,
                262 / ih
            )

            scaled = pygame.transform.smoothscale(
                self.chef_cooking,
                (
                    max(1, int(iw * scale)),
                    max(1, int(ih * scale))
                )
            )

            # El personaje queda centrado dentro de su zona inferior.
            rect = scaled.get_rect(
                midbottom=(
                    chef_area.centerx + 5,
                    chef_area.bottom
                )
            )

            self.screen.blit(scaled, rect)

        else:
            rr(
                self.screen,
                pygame.Rect(125, 465, 220, 260),
                WHITE,
                28,
                2,
                ORANGE
            )

            text(
                self.screen,
                "CHEF",
                self.fonts["title"],
                ORANGE,
                (235, 590),
                True
            )

    def draw_intro(self):
        self.draw_background()
        self.draw_header()

        # ========================================================
        # COMPOSICIÓN PRINCIPAL
        # ========================================================
        left = pygame.Rect(55, 170, 650, 605)
        right = pygame.Rect(735, 170, 745, 605)

        # Separador limpio
        line(
            self.screen,
            (224, 217, 207),
            (720, 185),
            (720, 770),
            2
        )

        # ========================================================
        # PANEL IZQUIERDO — PRESENTACIÓN
        # ========================================================
        self.draw_shadow(left, 30, (0, 7), 18)

        rr(
            self.screen,
            left,
            (252, 248, 241),
            30,
            2,
            (235, 226, 215)
        )

        # Fondo decorativo muy sutil
        pygame.draw.circle(
            self.screen,
            (248, 235, 216),
            (205, 430),
            205
        )

        pygame.draw.circle(
            self.screen,
            (252, 242, 229),
            (205, 430),
            165
        )

        # ========================================================
        # ETIQUETA
        # ========================================================
        rr(
            self.screen,
            pygame.Rect(88, 198, 225, 34),
            LIGHT_ORANGE,
            17
        )

        text(
            self.screen,
            "04  /  ESTACIÓN DE COCINA",
            self.fonts["tiny"],
            DARK_ORANGE,
            (200, 215),
            True
        )

        # ========================================================
        # TITULAR
        # El personaje NO entra en esta zona.
        # ========================================================
        text(
            self.screen,
            "¡LA COCINA",
            self.fonts["title"],
            DARK,
            (88, 255)
        )

        text(
            self.screen,
            "ESTÁ LISTA!",
            self.fonts["title"],
            ORANGE,
            (88, 313)
        )

        # Subtítulo
        text(
            self.screen,
            "Los datos ya están preparados.",
            self.fonts["small"],
            MUTED,
            (90, 382)
        )

        text(
            self.screen,
            "Ahora los convertiremos en información",
            self.fonts["small"],
            MUTED,
            (90, 408)
        )

        text(
            self.screen,
            "útil para tomar mejores decisiones.",
            self.fonts["small"],
            MUTED,
            (90, 434)
        )

        # ========================================================
        # ETIQUETA DE RECETA
        # Se coloca en una zona propia para que NO se mezcle con
        # la última línea descriptiva ni con el chef.
        # ========================================================
        recipe_tag = pygame.Rect(90, 458, 205, 28)

        rr(
            self.screen,
            recipe_tag,
            LIGHT_ORANGE,
            14
        )

        pygame.draw.rect(
            self.screen,
            ORANGE,
            (recipe_tag.x, recipe_tag.y, 4, recipe_tag.height),
            border_radius=2
        )

        text(
            self.screen,
            "LA RECETA DE DATOS",
            self.fonts["micro"],
            DARK_ORANGE,
            recipe_tag.center,
            True
        )

        # ========================================================
        # CHEF
        # El área del personaje comienza DESPUÉS de la etiqueta.
        # Así ningún elemento puede tapar el texto.
        # ========================================================
        self.draw_chef_intro()

        # ========================================================
        # BURBUJA DEL CHEF
        # Separada del titular y del cuerpo del personaje.
        # ========================================================
        bubble = pygame.Rect(365, 535, 305, 118)

        self.draw_shadow(
            bubble,
            22,
            (0, 5),
            20
        )

        rr(
            self.screen,
            bubble,
            WHITE,
            22,
            2,
            (228, 220, 210)
        )

        # Pico apuntando al personaje
        pygame.draw.polygon(
            self.screen,
            WHITE,
            [
                (365, 580),
                (338, 597),
                (365, 610)
            ]
        )

        pygame.draw.rect(
            self.screen,
            ORANGE,
            (390, 557, 45, 5),
            border_radius=3
        )

        text(
            self.screen,
            "“Todo está preparado.”",
            self.fonts["body_bold"],
            DARK,
            (390, 575)
        )

        text(
            self.screen,
            "Ahora toca cocinar los datos.",
            self.fonts["small"],
            ORANGE,
            (390, 605)
        )

        text(
            self.screen,
            "DATA CHEF  •  RECETA FINAL",
            self.fonts["micro"],
            MUTED,
            (390, 630)
        )

        # ========================================================
        # PANEL DERECHO — RECETA
        # ========================================================
        self.draw_shadow(
            right,
            32,
            (0, 8),
            28
        )

        rr(
            self.screen,
            right,
            WHITE,
            32,
            2,
            (226, 218, 207)
        )

        header = pygame.Rect(
            right.x,
            right.y,
            right.width,
            112
        )

        rr(
            self.screen,
            header,
            DARK,
            32
        )

        pygame.draw.rect(
            self.screen,
            DARK,
            (
                header.x,
                header.bottom - 38,
                header.width,
                38
            )
        )

        text(
            self.screen,
            "RECETA FINAL",
            self.fonts["tiny"],
            (190, 202, 208),
            (770, 198)
        )

        text(
            self.screen,
            "Transformando datos en información",
            self.fonts["subtitle"],
            WHITE,
            (770, 224)
        )

        # Estado
        rr(
            self.screen,
            pygame.Rect(1288, 196, 145, 42),
            (55, 76, 87),
            21
        )

        pygame.draw.circle(
            self.screen,
            GREEN,
            (1312, 217),
            6
        )

        text(
            self.screen,
            "LISTO",
            self.fonts["tiny"],
            WHITE,
            (1327, 207)
        )

        # ========================================================
        # ETAPAS
        # ========================================================
        stages = [
            ("01", "PREPARAR", "Datos limpios", GREEN),
            ("02", "VALIDAR", "Reglas aplicadas", BLUE),
            ("03", "TRANSFORMAR", "Información útil", ORANGE),
            ("04", "COCINAR", "Panel final", DARK_ORANGE),
        ]

        # Línea de proceso detrás de las tarjetas.
        line_y = 405
        pygame.draw.line(
            self.screen,
            (222, 218, 211),
            (807, line_y),
            (1408, line_y),
            3
        )

        start_x = 770
        card_y = 340
        card_w = 157
        card_h = 156
        gap = 13

        for i, (num, title, desc, color) in enumerate(stages):
            x = start_x + i * (card_w + gap)
            card = pygame.Rect(x, card_y, card_w, card_h)

            # Última etapa destacada, las anteriores neutras.
            fill = (255, 248, 239) if i == 3 else (250, 250, 248)

            rr(
                self.screen,
                card,
                fill,
                20,
                2,
                (225, 219, 211)
            )

            # Barra lateral de estado.
            pygame.draw.rect(
                self.screen,
                color,
                (x, card_y, 6, card_h),
                border_radius=3
            )

            # Número.
            pygame.draw.circle(
                self.screen,
                color,
                (x + 35, card_y + 35),
                20
            )

            text(
                self.screen,
                num,
                self.fonts["tiny"],
                WHITE,
                (x + 35, card_y + 35),
                True
            )

            # Título.
            text(
                self.screen,
                title,
                self.fonts["tiny"],
                DARK,
                (x + 18, card_y + 70)
            )

            # Descripción.
            text(
                self.screen,
                desc,
                self.fonts["micro"],
                MUTED,
                (x + 18, card_y + 97)
            )

            # Estado inferior: primero un check vectorial,
            # después el texto. Nada de glifos que puedan romperse.
            status_y = card_y + 130

            pygame.draw.circle(
                self.screen,
                color,
                (x + 23, status_y),
                11
            )

            if i < 3:
                draw_check(
                    self.screen,
                    (x + 23, status_y),
                    WHITE,
                    0.55,
                    2
                )
                status_text = "LISTO"
            else:
                # La etapa 04 es la que se va a ejecutar.
                pygame.draw.circle(
                    self.screen,
                    WHITE,
                    (x + 23, status_y),
                    4
                )
                status_text = "SIGUIENTE"

            text(
                self.screen,
                status_text,
                self.fonts["micro"],
                color,
                (x + 41, card_y + 123)
            )

        # Separador inferior.
        line(
            self.screen,
            (224, 218, 209),
            (805, 530),
            (1407, 530),
            3
        )

        # ========================================================
        # MENSAJE
        # ========================================================
        rr(
            self.screen,
            pygame.Rect(770, 555, 675, 72),
            (247, 243, 236),
            18
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (798, 591),
            8
        )

        text(
            self.screen,
            "LA RECETA ESTÁ LISTA PARA EMPEZAR",
            self.fonts["body_bold"],
            DARK,
            (822, 570)
        )

        text(
            self.screen,
            "Presiona el botón para iniciar la preparación del panel.",
            self.fonts["small"],
            MUTED,
            (822, 600)
        )

        # ========================================================
        # CTA
        # ========================================================
        button = pygame.Rect(
            995,
            650,
            330,
            54
        )

        logical = self.logical(
            pygame.mouse.get_pos()
        )

        hover = button.collidepoint(logical)

        draw_button = button.move(
            0,
            -3 if hover else 0
        )

        rr(
            self.screen,
            draw_button.move(0, 5),
            (26, 38, 46),
            17
        )

        rr(
            self.screen,
            draw_button,
            ORANGE if hover else DARK_ORANGE,
            17
        )

        text(
            self.screen,
            "EMPEZAR A COCINAR",
            self.fonts["button"],
            WHITE,
            (draw_button.centerx - 13, draw_button.centery),
            True
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (draw_button.right - 32, draw_button.centery),
            13
        )

        pygame.draw.polygon(
            self.screen,
            ORANGE,
            [
                (draw_button.right - 28, draw_button.centery - 6),
                (draw_button.right - 28, draw_button.centery + 6),
                (draw_button.right - 21, draw_button.centery)
            ]
        )

        # ========================================================
        # FOOTER
        # ========================================================
        pygame.draw.rect(
            self.screen,
            DARK,
            (0, 800, WIDTH, 64)
        )

        text(
            self.screen,
            "DATA CHEF",
            self.fonts["small"],
            WHITE,
            (55, 822)
        )

        text(
            self.screen,
            "PREPARAR  >  LIMPIAR  >  TRANSFORMAR  >  COCINAR",
            self.fonts["tiny"],
            (185, 199, 205),
            (220, 824)
        )

        steps_x = [1080, 1160, 1240, 1320]

        for i, sx in enumerate(steps_x):
            color = ORANGE if i == 3 else (91, 106, 115)

            pygame.draw.circle(
                self.screen,
                color,
                (sx, 832),
                7
            )

            if i < 3:
                line(
                    self.screen,
                    (91, 106, 115),
                    (sx + 9, 832),
                    (sx + 71, 832),
                    2
                )

    # ============================================================
    # COCINANDO
    # ============================================================

    # ============================================================
    # PANEL SUCIO — MISMO SISTEMA VISUAL DEL DISEÑO ANTERIOR
    # ============================================================

    def draw_dirty_panel(self):
        """Pantalla de diagnóstico previa a la limpieza.
        V5: jerarquía corregida, textos separados y sin glifos rotos.
        """
        self.draw_background()
        self.draw_header()

        # ========================================================
        # HERO
        # ========================================================
        rr(
            self.screen,
            pygame.Rect(78, 158, 250, 30),
            LIGHT_ORANGE,
            15
        )

        text(
            self.screen,
            "04  /  REVISION DE DATOS",
            self.fonts["micro"],
            DARK_ORANGE,
            (203, 173),
            True
        )

        text(
            self.screen,
            "ANTES DE COCINAR",
            self.fonts["title"],
            DARK,
            (78, 195)
        )

        text(
            self.screen,
            "Detectemos los ingredientes que necesitan limpieza y validación.",
            self.fonts["body"],
            MUTED,
            (80, 252)
        )

        # Línea decorativa para cerrar el hero.
        pygame.draw.line(
            self.screen,
            ORANGE,
            (80, 282),
            (250, 282),
            3
        )

        # ========================================================
        # PANEL PRINCIPAL
        # ========================================================
        panel = pygame.Rect(78, 292, 1380, 438)

        self.draw_shadow(
            panel,
            28,
            (0, 8),
            22
        )

        rr(
            self.screen,
            panel,
            WHITE,
            28,
            2,
            (228, 220, 210)
        )

        # ========================================================
        # CABECERA
        # ========================================================
        header = pygame.Rect(
            panel.x,
            panel.y,
            panel.width,
            68
        )

        rr(
            self.screen,
            header,
            DARK,
            28
        )

        pygame.draw.rect(
            self.screen,
            DARK,
            (
                header.x,
                header.bottom - 28,
                header.width,
                28
            )
        )

        text(
            self.screen,
            "PANEL DE DATOS",
            self.fonts["small"],
            WHITE,
            (panel.x + 28, panel.y + 20)
        )

        text(
            self.screen,
            "DIAGNÓSTICO PREVIO A LA LIMPIEZA",
            self.fonts["micro"],
            (190, 205, 212),
            (panel.x + 205, panel.y + 24)
        )

        status = pygame.Rect(
            panel.right - 210,
            panel.y + 17,
            180,
            34
        )

        rr(
            self.screen,
            status,
            (67, 78, 86),
            17
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (status.x + 20, status.centery),
            5
        )

        text(
            self.screen,
            "REQUIERE LIMPIEZA",
            self.fonts["micro"],
            WHITE,
            (status.x + 34, status.y + 9)
        )

        # ========================================================
        # KPI CARDS
        # ========================================================
        cards = [
            ("REGISTROS", "18,542", BLUE, "Volumen detectado"),
            ("DUPLICADOS", "126", ORANGE, "Registros repetidos"),
            ("VALORES NULL", "84", DARK_ORANGE, "Campos incompletos"),
            ("CALIDAD", "72%", GREEN, "Antes de validar"),
        ]

        card_y = 382
        card_w = 295
        card_h = 112
        gap = 18

        for i, (label, value, color, desc) in enumerate(cards):
            x = panel.x + 28 + i * (card_w + gap)

            card = pygame.Rect(
                x,
                card_y,
                card_w,
                card_h
            )

            rr(
                self.screen,
                card,
                (249, 249, 247),
                18,
                1,
                (228, 222, 214)
            )

            # Indicador de color.
            pygame.draw.rect(
                self.screen,
                color,
                (x, card.y, 5, card.height),
                border_radius=3
            )

            text(
                self.screen,
                label,
                self.fonts["micro"],
                MUTED,
                (x + 18, card.y + 16)
            )

            text(
                self.screen,
                value,
                self.fonts["subtitle"],
                color,
                (x + 18, card.y + 40)
            )

            text(
                self.screen,
                desc,
                self.fonts["micro"],
                MUTED,
                (x + 18, card.y + 83)
            )

            # Estado visual limpio, sin caracteres Unicode.
            pygame.draw.circle(
                self.screen,
                color,
                (card.right - 25, card.y + 24),
                9
            )

            if i == 3:
                # Calidad: check.
                if "draw_check" in globals():
                    draw_check(
                        self.screen,
                        (card.right - 25, card.y + 24),
                        WHITE,
                        0.48,
                        2
                    )
                else:
                    pygame.draw.circle(
                        self.screen,
                        WHITE,
                        (card.right - 25, card.y + 24),
                        3
                    )
            else:
                pygame.draw.circle(
                    self.screen,
                    WHITE,
                    (card.right - 25, card.y + 24),
                    3
                )

        # ========================================================
        # ZONA INFERIOR: CALIDAD + ALERTAS
        # ========================================================
        diag = pygame.Rect(
            panel.x + 28,
            520,
            840,
            170
        )

        rr(
            self.screen,
            diag,
            (249, 250, 252),
            20,
            1,
            (225, 229, 233)
        )

        # --------------------------------------------------------
        # CABECERA DE LA MÉTRICA
        # Una sola línea principal para evitar amontonamiento.
        # --------------------------------------------------------
        text(
            self.screen,
            "CALIDAD DEL DATO",
            self.fonts["small"],
            DARK,
            (diag.x + 20, diag.y + 13)
        )

        text(
            self.screen,
            "DISTRIBUCIÓN DE REGISTROS",
            self.fonts["micro"],
            MUTED,
            (diag.right - 205, diag.y + 17)
        )

        # Línea sutil que separa la cabecera de las métricas.
        pygame.draw.line(
            self.screen,
            (231, 233, 235),
            (diag.x + 20, diag.y + 42),
            (diag.right - 20, diag.y + 42),
            1
        )

        # ========================================================
        # BARRAS
        # Cuatro filas uniformes, con espacio vertical suficiente.
        # ========================================================
        bars = [
            ("VÁLIDOS", 0.72, GREEN),
            ("DUPLICADOS", 0.13, ORANGE),
            ("INCOMPLETOS", 0.09, DARK_ORANGE),
            ("OTROS", 0.06, BLUE),
        ]

        label_x = diag.x + 20
        bar_x = diag.x + 220
        bar_w = 570
        bar_y = diag.y + 55
        row_h = 29
        bar_h = 14

        for i, (label, value, color) in enumerate(bars):
            y = bar_y + i * row_h

            # Etiqueta alineada al centro de cada barra.
            text(
                self.screen,
                label,
                self.fonts["micro"],
                MUTED,
                (label_x, y - 1)
            )

            # Barra base.
            rr(
                self.screen,
                pygame.Rect(
                    bar_x,
                    y,
                    bar_w,
                    bar_h
                ),
                (231, 232, 233),
                7
            )

            # Barra de valor.
            rr(
                self.screen,
                pygame.Rect(
                    bar_x,
                    y,
                    max(8, int(bar_w * value)),
                    bar_h
                ),
                color,
                7
            )

            # Porcentaje en una columna fija.
            text(
                self.screen,
                f"{int(value * 100)}%",
                self.fonts["micro"],
                DARK,
                (bar_x + bar_w + 14, y - 1)
            )
        # ========================================================
        # ALERTAS
        # ========================================================
        issues = pygame.Rect(
            940,
            520,
            490,
            170
        )

        rr(
            self.screen,
            issues,
            (255, 249, 239),
            20,
            1,
            (249, 210, 171)
        )

        text(
            self.screen,
            "ALERTAS ENCONTRADAS",
            self.fonts["small"],
            DARK,
            (issues.x + 20, issues.y + 18)
        )

        # Cada alerta tiene un indicador gráfico independiente.
        alerts = [
            ("Datos duplicados", ORANGE),
            ("Valores incompletos", DARK_ORANGE),
            ("Reglas sin validar", ORANGE),
        ]

        for i, (label, color) in enumerate(alerts):
            y = issues.y + 58 + i * 31

            pygame.draw.circle(
                self.screen,
                color,
                (issues.x + 25, y + 5),
                5
            )

            text(
                self.screen,
                label,
                self.fonts["micro"],
                DARK_ORANGE,
                (issues.x + 40, y)
            )

        # Línea inferior de estado.
        pygame.draw.line(
            self.screen,
            (239, 218, 194),
            (issues.x + 20, issues.bottom - 20),
            (issues.right - 20, issues.bottom - 20),
            1
        )

        text(
            self.screen,
            "3 puntos requieren atención",
            self.fonts["micro"],
            MUTED,
            (issues.x + 20, issues.bottom - 15)
        )

        # ========================================================
        # TEXTO GUÍA
        # ========================================================
        text(
            self.screen,
            "Los datos serán limpiados antes de entrar a la receta.",
            self.fonts["small"],
            MUTED,
            (80, 765)
        )

        # ========================================================
        # CTA
        # ========================================================
        button = pygame.Rect(
            1050,
            748,
            380,
            58
        )

        logical = self.logical(
            pygame.mouse.get_pos()
        )

        hover = button.collidepoint(logical)

        draw_button = button.move(
            0,
            -3 if hover else 0
        )

        rr(
            self.screen,
            draw_button.move(0, 5),
            (26, 38, 46),
            17
        )

        rr(
            self.screen,
            draw_button,
            ORANGE if hover else DARK_ORANGE,
            17
        )

        text(
            self.screen,
            "LIMPIAR Y COCINAR",
            self.fonts["button"],
            WHITE,
            (draw_button.centerx - 12, draw_button.centery),
            True
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (draw_button.right - 31, draw_button.centery),
            13
        )

        pygame.draw.polygon(
            self.screen,
            ORANGE,
            [
                (draw_button.right - 27, draw_button.centery - 6),
                (draw_button.right - 27, draw_button.centery + 6),
                (draw_button.right - 20, draw_button.centery),
            ]
        )


    def draw_cooking(self):
        """Escena de cocción: composición limpia, sin elementos flotantes que
        invadan la interfaz. La receta funciona como un flujo visual claro:
        FUENTE -> LIMPIEZA -> VALIDACIÓN -> INFORMACIÓN -> OLLA.
        """
        self.draw_background()
        self.draw_header()

        # ========================================================
        # HERO — TÍTULO
        # ========================================================
        rr(
            self.screen,
            pygame.Rect(78, 158, 205, 30),
            LIGHT_ORANGE,
            15
        )
        text(
            self.screen,
            "04  /  ESTACIÓN DE COCINA",
            self.fonts["micro"],
            DARK_ORANGE,
            (180, 173),
            True
        )

        title_a = "PREPARANDO"
        title_b = "TU PANEL..."
        title_font = self.fonts["title"]
        title_gap = 18
        wa = title_font.size(title_a)[0]
        wb = title_font.size(title_b)[0]
        title_x = (WIDTH - wa - title_gap - wb) // 2

        text(self.screen, title_a, title_font, DARK, (title_x, 171))
        text(
            self.screen,
            title_b,
            title_font,
            ORANGE,
            (title_x + wa + title_gap, 171)
        )

        text(
            self.screen,
            "Cada ingrediente representa datos preparados y confiables.",
            self.fonts["body"],
            MUTED,
            (WIDTH // 2, 229),
            True
        )

        pygame.draw.line(
            self.screen,
            ORANGE,
            (708, 257),
            (828, 257),
            3
        )
        pygame.draw.circle(self.screen, ORANGE, (695, 257), 4)
        pygame.draw.circle(self.screen, ORANGE, (841, 257), 4)

        # ========================================================
        # TARJETAS PRINCIPALES
        # ========================================================
        chef_box = pygame.Rect(70, 270, 600, 485)
        recipe_box = pygame.Rect(695, 270, 770, 485)

        for box in (chef_box, recipe_box):
            self.draw_shadow(box, 28, (0, 8), 24)
            rr(
                self.screen,
                box,
                WHITE,
                28,
                2,
                (226, 218, 207)
            )

        # ========================================================
        # PANEL IZQUIERDO — CHEF
        # ========================================================
        chef_header = pygame.Rect(70, 270, 600, 68)
        rr(self.screen, chef_header, DARK, 28)
        pygame.draw.rect(
            self.screen,
            DARK,
            (chef_header.x, chef_header.bottom - 28, chef_header.width, 28)
        )

        text(
            self.screen,
            "CHEF DE DATOS",
            self.fonts["small"],
            WHITE,
            (98, 291)
        )
        text(
            self.screen,
            "PREPARACIÓN EN CURSO",
            self.fonts["micro"],
            (184, 199, 205),
            (98, 315)
        )

        status = pygame.Rect(500, 287, 135, 32)
        rr(self.screen, status, (55, 76, 87), 16)
        pygame.draw.circle(self.screen, GREEN, (519, 303), 5)
        text(self.screen, "EN MARCHA", self.fonts["micro"], WHITE, (531, 294))

        # Área visual del chef, completamente separada del texto.
        pygame.draw.circle(
            self.screen,
            (255, 246, 232),
            (275, 540),
            165
        )
        pygame.draw.circle(
            self.screen,
            (252, 239, 219),
            (275, 540),
            132,
            2
        )
        pygame.draw.arc(
            self.screen,
            (246, 220, 191),
            (115, 380, 320, 320),
            math.radians(205),
            math.radians(330),
            2
        )

        self.draw_chef_cooking(pygame.Rect(95, 338, 350, 390))

        # --------------------------------------------------------
        # TIP DEL CHEF — tarjeta más compacta y con más aire
        # --------------------------------------------------------
        bubble = pygame.Rect(395, 410, 240, 148)
        self.draw_shadow(bubble, 22, (0, 5), 18)
        rr(
            self.screen,
            bubble,
            (252, 248, 241),
            22,
            2,
            (239, 215, 190)
        )

        pygame.draw.polygon(
            self.screen,
            (252, 248, 241),
            [(395, 472), (368, 487), (395, 501)]
        )

        pygame.draw.rect(
            self.screen,
            ORANGE,
            (420, 432, 42, 5),
            border_radius=3
        )
        text(self.screen, "TIP DEL CHEF", self.fonts["micro"], DARK_ORANGE, (420, 447))
        text(self.screen, "Primero mezclamos", self.fonts["body_bold"], DARK, (420, 476))
        text(self.screen, "los datos de calidad.", self.fonts["small"], ORANGE, (420, 507))
        text(self.screen, "Después los convertimos en valor.", self.fonts["micro"], MUTED, (420, 535))

        # Objetivo inferior, separado del tip.
        objective = pygame.Rect(395, 594, 240, 76)
        rr(self.screen, objective, PALE_ORANGE, 18, 1, (246, 226, 205))
        pygame.draw.circle(self.screen, ORANGE, (420, 620), 8)
        text(self.screen, "OBJETIVO", self.fonts["micro"], DARK_ORANGE, (437, 607))
        text(self.screen, "Convertir datos en valor.", self.fonts["small"], DARK, (437, 629))

        # ========================================================
        # PANEL DERECHO — RECETA
        # ========================================================
        recipe_header = pygame.Rect(695, 270, 770, 72)
        rr(self.screen, recipe_header, DARK, 28)
        pygame.draw.rect(
            self.screen,
            DARK,
            (recipe_header.x, recipe_header.bottom - 32, recipe_header.width, 32)
        )

        text(
            self.screen,
            "RECETA DE DATOS",
            self.fonts["subtitle"],
            WHITE,
            (730, 292)
        )

        status = pygame.Rect(1295, 288, 135, 34)
        rr(self.screen, status, (55, 76, 87), 17)
        pygame.draw.circle(self.screen, GREEN, (1315, 305), 5)
        text(self.screen, "LISTO", self.fonts["micro"], WHITE, (1328, 297))

        # Encabezado de la zona de ingredientes.
        text(
            self.screen,
            "FLUJO DE INFORMACIÓN",
            self.fonts["small"],
            DARK,
            (730, 365)
        )
        text(
            self.screen,
            "Cada etapa aporta una capa de calidad.",
            self.fonts["micro"],
            MUTED,
            (730, 390)
        )

        # --------------------------------------------------------
        # FLUJO DE INGREDIENTES
        # Ya no usamos tarjetas blancas ni textos sueltos como
        # "DB / OK / INFO" flotando sobre la olla.
        # --------------------------------------------------------
        ingredients = [
            ("01", "FUENTE", "Base de datos", BLUE),
            ("02", "LIMPIEZA", "Datos preparados", GREEN),
            ("03", "VALIDACIÓN", "Datos confiables", ORANGE),
            ("04", "ESTRUCTURA", "Información útil", DARK_ORANGE),
        ]

        flow_x = 730
        flow_y = 428
        flow_w = 300
        row_h = 54
        row_gap = 8

        # Línea vertical del proceso.
        line_x = flow_x + 23
        pygame.draw.line(
            self.screen,
            (222, 218, 211),
            (line_x, flow_y + 27),
            (line_x, flow_y + 3 * (row_h + row_gap) + 27),
            3
        )

        for i, (num, stage, desc, color) in enumerate(ingredients):
            y = flow_y + i * (row_h + row_gap)

            # Fondo neutro, sin tarjetas blancas superpuestas.
            rr(
                self.screen,
                pygame.Rect(flow_x, y, flow_w, row_h),
                (248, 247, 244),
                16,
                1,
                (232, 225, 216)
            )

            # Nodo numerado.
            pygame.draw.circle(self.screen, color, (flow_x + 23, y + 27), 17)
            text(self.screen, num, self.fonts["micro"], WHITE, (flow_x + 23, y + 27), True)

            # Estado principal.
            text(self.screen, stage, self.fonts["micro"], DARK, (flow_x + 52, y + 10))
            text(self.screen, desc, self.fonts["micro"], MUTED, (flow_x + 52, y + 30))

            # Check limpio a la derecha.
            pygame.draw.circle(self.screen, color, (flow_x + flow_w - 22, y + 27), 10)
            draw_check(
                self.screen,
                (flow_x + flow_w - 22, y + 27),
                WHITE,
                0.48,
                2
            )

        # --------------------------------------------------------
        # OLLA — HERO VISUAL
        # --------------------------------------------------------
        hero = pygame.Rect(1060, 385, 350, 315)
        rr(
            self.screen,
            hero,
            (253, 249, 242),
            24,
            1,
            (241, 229, 214)
        )

        text(
            self.screen,
            "COCINANDO",
            self.fonts["tiny"],
            DARK_ORANGE,
            (1235, 410),
            True
        )
        text(
            self.screen,
            "Integrando los ingredientes",
            self.fonts["micro"],
            MUTED,
            (1235, 432),
            True
        )

        pot_center = (1235, 555)

        # Conectores discretos desde cada etapa hacia el hero.
        for i in range(4):
            sy = flow_y + i * (row_h + row_gap) + row_h // 2
            start = (flow_x + flow_w + 10, sy)
            end = (1060, 510 + i * 30)

            points = []
            for k in range(16):
                u = k / 15
                px = start[0] + (end[0] - start[0]) * u
                py = start[1] + (end[1] - start[1]) * u
                py += math.sin(u * math.pi) * (5 if i % 2 == 0 else -5)
                points.append((int(px), int(py)))

            pygame.draw.lines(
                self.screen,
                (214, 211, 204),
                False,
                points,
                2
            )
            pygame.draw.circle(
                self.screen,
                ingredients[i][3],
                start,
                4
            )

        # Halo detrás de la olla.
        pygame.draw.circle(
            self.screen,
            (255, 239, 218),
            pot_center,
            118
        )
        pygame.draw.circle(
            self.screen,
            (249, 221, 188),
            pot_center,
            94,
            2
        )

        self.draw_pot(*pot_center)

        for particle in self.steam:
            particle.draw(self.screen)

        # Estado de cocción, separado de la ilustración.
        cooking_status = pygame.Rect(1085, 665, 300, 42)
        rr(
            self.screen,
            cooking_status,
            WHITE,
            21,
            1,
            (232, 222, 210)
        )
        pygame.draw.circle(self.screen, GREEN, (1110, 686), 6)
        text(
            self.screen,
            "DATOS + CALIDAD = INFORMACIÓN ÚTIL",
            self.fonts["micro"],
            DARK,
            (1125, 677)
        )

        # --------------------------------------------------------
        # ETIQUETA DE PROCESO — reemplaza los antiguos chips
        # flotantes y hace visible la animación sin ensuciar la UI.
        # --------------------------------------------------------
        process = pygame.Rect(1060, 456, 350, 40)
        rr(self.screen, process, (246, 242, 235), 20)
        text(
            self.screen,
            "PREPARAR  →  VALIDAR  →  COCINAR",
            self.fonts["micro"],
            DARK_ORANGE,
            process.center,
            True
        )

        # ========================================================
        # BARRA DE PROGRESO INFERIOR
        # ========================================================
        done = sum(1 for item in self.ingredients if item.done)
        progress = done / len(self.ingredients)

        footer = pygame.Rect(70, 775, 1395, 58)
        rr(self.screen, footer, DARK, 20)

        # Bloque izquierdo: título + porcentaje, sin superposición.
        text(
            self.screen,
            "COCINANDO INSIGHTS",
            self.fonts["small"],
            WHITE,
            (98, 791)
        )
        text(
            self.screen,
            f"{int(progress * 100)}%",
            self.fonts["body_bold"],
            ORANGE,
            (285, 787)
        )

        # Barra central.
        bar = pygame.Rect(390, 793, 620, 20)
        rr(self.screen, bar, (73, 88, 98), 10)
        if progress > 0:
            rr(
                self.screen,
                pygame.Rect(bar.x, bar.y, max(10, int(bar.width * progress)), bar.height),
                ORANGE,
                10
            )

        text(
            self.screen,
            "Los ingredientes se integran automáticamente.",
            self.fonts["micro"],
            (184, 199, 205),
            (390, 817)
        )

        # Etapas compactas a la derecha.
        steps = ["PREPARAR", "VALIDAR", "TRANSFORMAR", "COCINAR"]
        sx = 1085
        for i, label in enumerate(steps):
            x = sx + i * 92
            active = i < done
            c = ORANGE if active else (102, 115, 123)

            pygame.draw.circle(self.screen, c, (x, 800), 9)
            text(
                self.screen,
                f"0{i + 1}",
                self.fonts["micro"],
                WHITE,
                (x, 800),
                True
            )
            text(
                self.screen,
                label,
                self.fonts["micro"],
                (184, 199, 205),
                (x, 815),
                True
            )

            if i < 3:
                line(
                    self.screen,
                    (91, 106, 115),
                    (x + 12, 800),
                    (x + 80, 800),
                    2
                )

    # ============================================================
    # TRANSFORMACION
    # ============================================================

    def draw_transform(self):
        """Pantalla de transformación: jerarquía visual limpia y legible.
        El progreso nunca se dibuja encima de textos, etiquetas o estados.
        """
        self.draw_background()
        self.draw_header()

        progress = min(1.0, self.scene_time / 3.0)
        pulse = (math.sin(self.t * 4.0) + 1.0) * 0.5

        # ============================================================
        # HERO
        # ============================================================
        rr(self.screen, pygame.Rect(78, 158, 205, 30), LIGHT_ORANGE, 15)
        text(self.screen, "04  /  TRANSFORMACION", self.fonts["micro"], DARK_ORANGE,
             (180, 173), True)

        title_a = "TRANSFORMANDO"
        title_b = "DATOS..."
        f = self.fonts["title"]
        wa = f.size(title_a)[0]
        wb = f.size(title_b)[0]
        title_gap = 18
        x0 = (WIDTH - wa - title_gap - wb) // 2

        text(self.screen, title_a, f, DARK, (x0, 166))
        text(self.screen, title_b, f, ORANGE,
             (x0 + wa + title_gap, 166))

        text(
            self.screen,
            "Los ingredientes se convierten en información lista para decidir.",
            self.fonts["body"],
            MUTED,
            (WIDTH // 2, 228),
            True
        )

        pygame.draw.line(self.screen, ORANGE, (708, 258), (828, 258), 3)
        pygame.draw.circle(self.screen, ORANGE, (694, 258), 4)
        pygame.draw.circle(self.screen, ORANGE, (842, 258), 4)

        # ============================================================
        # PANEL PRINCIPAL
        # ============================================================
        panel = pygame.Rect(78, 292, 1380, 365)
        self.draw_shadow(panel, 28, (0, 8), 22)
        rr(self.screen, panel, WHITE, 28, 2, (228, 220, 210))

        # CABECERA
        header = pygame.Rect(panel.x, panel.y, panel.width, 64)
        rr(self.screen, header, DARK, 28)
        pygame.draw.rect(
            self.screen,
            DARK,
            (panel.x, panel.y + 32, panel.width, 32)
        )

        text(
            self.screen,
            "PIPELINE DE TRANSFORMACION",
            self.fonts["small"],
            WHITE,
            (panel.x + 28, panel.y + 19)
        )
        text(
            self.screen,
            "ETL  /  PROCESAMIENTO EN TIEMPO REAL",
            self.fonts["micro"],
            (190, 205, 212),
            (panel.x + 280, panel.y + 23)
        )

        status = pygame.Rect(panel.right - 176, panel.y + 16, 146, 32)
        rr(self.screen, status, (55, 76, 87), 16)
        pygame.draw.circle(self.screen, GREEN, (status.x + 21, status.centery), 5)
        text(
            self.screen,
            "EN MARCHA",
            self.fonts["micro"],
            WHITE,
            (status.x + 34, status.y + 8)
        )

        # ============================================================
        # ZONAS FIJAS
        # Importante: cada columna tiene un área propia. El indicador
        # de progreso central NO comparte espacio con textos.
        # ============================================================
        content_y = panel.y + 88

        input_box = pygame.Rect(112, content_y, 320, 224)
        output_box = pygame.Rect(1100, content_y, 320, 224)

        rr(
            self.screen,
            input_box,
            (250, 249, 246),
            22,
            1,
            (232, 225, 216)
        )
        rr(
            self.screen,
            output_box,
            (248, 250, 252),
            22,
            1,
            (220, 229, 237)
        )

        # Separadores de las tres columnas.
        line(
            self.screen,
            (235, 229, 220),
            (466, content_y + 8),
            (466, content_y + 232),
            1
        )
        line(
            self.screen,
            (235, 229, 220),
            (1070, content_y + 8),
            (1070, content_y + 232),
            1
        )

        # ============================================================
        # 01 INPUT — INGREDIENTES
        # ============================================================
        text(self.screen, "01", self.fonts["micro"], ORANGE,
             (136, content_y + 19))

        text(
            self.screen,
            "INGREDIENTES",
            self.fonts["subtitle"],
            DARK,
            (170, content_y + 14)
        )

        text(
            self.screen,
            "Fuentes preparadas",
            self.fonts["micro"],
            MUTED,
            (170, content_y + 48)
        )

        ingredients = [
            ("DB", "BASE DE DATOS", BLUE),
            ("OK", "DATOS LIMPIOS", GREEN),
            ("OK", "DATOS VALIDADOS", ORANGE)
        ]

        for i, (icon, label, color) in enumerate(ingredients):
            y = content_y + 82 + i * 42

            pygame.draw.circle(
                self.screen,
                (244, 241, 235),
                (143, y + 15),
                15
            )

            text(
                self.screen,
                icon,
                self.fonts["micro"],
                color,
                (143, y + 15),
                True
            )

            text(
                self.screen,
                label,
                self.fonts["micro"],
                DARK,
                (170, y + 7)
            )

            pygame.draw.circle(
                self.screen,
                color,
                (399, y + 15),
                5
            )

        # ============================================================
        # 02 MOTOR DE DATOS
        # ============================================================
        cx = 768

        # Título y subtítulo tienen una franja propia.
        text(
            self.screen,
            "02",
            self.fonts["micro"],
            BLUE,
            (cx - 34, content_y + 5)
        )

        text(
            self.screen,
            "MOTOR DE DATOS",
            self.fonts["small"],
            DARK,
            (cx + 2, content_y + 5),
            True
        )

        text(
            self.screen,
            "PROCESAMIENTO",
            self.fonts["micro"],
            MUTED,
            (cx, content_y + 31),
            True
        )

        # ------------------------------------------------------------
        # ANILLO DE PROGRESO
        # El anillo termina antes de la etiqueta de estado.
        # Ningún arco puede pasar por encima de texto.
        # ------------------------------------------------------------
        cy = content_y + 126
        outer_r = 82
        inner_r = 65

        pygame.draw.circle(
            self.screen,
            (247, 244, 238),
            (cx, cy),
            outer_r
        )
        pygame.draw.circle(
            self.screen,
            (232, 225, 216),
            (cx, cy),
            outer_r,
            2
        )

        # Anillo base.
        outer_arc = pygame.Rect(
            cx - outer_r,
            cy - outer_r,
            outer_r * 2,
            outer_r * 2
        )
        pygame.draw.arc(
            self.screen,
            (224, 230, 235),
            outer_arc,
            0,
            math.tau,
            7
        )

        # Progreso naranja.
        if progress > 0:
            pygame.draw.arc(
                self.screen,
                ORANGE,
                outer_arc,
                math.radians(225),
                math.radians(225) + math.tau * progress,
                8
            )

        # Anillo secundario azul.
        inner_arc = pygame.Rect(
            cx - inner_r,
            cy - inner_r,
            inner_r * 2,
            inner_r * 2
        )
        pygame.draw.arc(
            self.screen,
            (232, 237, 242),
            inner_arc,
            0,
            math.tau,
            4
        )

        if progress > 0:
            pygame.draw.arc(
                self.screen,
                BLUE,
                inner_arc,
                math.radians(35),
                math.radians(35) + math.tau * min(1, progress * 0.9),
                4
            )

        # Centro limpio: las barras NO comparten espacio con el porcentaje.
        bar_heights = (22, 34, 49, 31, 40)

        for i, h in enumerate(bar_heights):
            x = cx - 48 + i * 24
            animated = int(
                h * (0.78 + 0.22 * math.sin(self.t * 5 + i))
            )

            pygame.draw.rect(
                self.screen,
                DARK,
                (
                    x,
                    cy + 10 - animated,
                    12,
                    animated
                ),
                border_radius=4
            )

        # Porcentaje en una cápsula blanca central.
        pct_box = pygame.Rect(cx - 42, cy + 35, 84, 34)
        rr(self.screen, pct_box, WHITE, 17)

        text(
            self.screen,
            f"{int(progress * 100)}%",
            self.fonts["subtitle"],
            DARK,
            pct_box.center,
            True
        )

        # Estado separado debajo del anillo.
        status_y = content_y + 224

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (cx - 56, status_y),
            5
        )

        text(
            self.screen,
            "TRANSFORMANDO",
            self.fonts["micro"],
            ORANGE,
            (cx - 44, status_y - 7)
        )

        # Punto de actividad girando en el perímetro.
        angle = math.radians(225) + math.tau * progress + self.t * 0.35
        mx = int(cx + math.cos(angle) * outer_r)
        my = int(cy + math.sin(angle) * outer_r)

        pygame.draw.circle(self.screen, WHITE, (mx, my), 9)
        pygame.draw.circle(self.screen, ORANGE, (mx, my), 6)

        # ============================================================
        # FLUJO ANIMADO
        # Los nodos pasan por corredores laterales, nunca por textos.
        # ============================================================
        for i in range(5):
            phase = (self.t * 0.7 + i / 5.0) % 1.0

            # Entrada.
            px = 435 + phase * 260
            py = cy + math.sin(phase * math.pi) * (10 + i * 2)
            alpha = int(90 + 120 * (1 - phase))

            dot = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(
                dot,
                (*ORANGE, alpha),
                (8, 8),
                4
            )
            self.screen.blit(
                dot,
                (int(px - 8), int(py - 8))
            )

            # Salida.
            px2 = 1015 + phase * 80
            py2 = cy + math.sin(phase * math.pi) * (8 + i * 2)

            dot2 = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(
                dot2,
                (*BLUE, alpha),
                (8, 8),
                4
            )
            self.screen.blit(
                dot2,
                (int(px2 - 8), int(py2 - 8))
            )

        # ============================================================
        # 03 OUTPUT — RESULTADO
        # ============================================================
        text(
            self.screen,
            "03",
            self.fonts["micro"],
            GREEN,
            (1124, content_y + 19)
        )

        text(
            self.screen,
            "RESULTADO",
            self.fonts["subtitle"],
            DARK,
            (1158, content_y + 14)
        )

        text(
            self.screen,
            "Información útil",
            self.fonts["micro"],
            MUTED,
            (1158, content_y + 48)
        )

        kpis = [
            ("CALIDAD", "98%", GREEN),
            ("ESTRUCTURA", "OK", BLUE),
            ("INSIGHTS", "LISTOS", ORANGE)
        ]

        for i, (label, value, color) in enumerate(kpis):
            y = content_y + 84 + i * 42

            pygame.draw.circle(
                self.screen,
                color,
                (1131, y + 15),
                6
            )

            text(
                self.screen,
                label,
                self.fonts["micro"],
                MUTED,
                (1150, y + 7)
            )

            value_img = self.fonts["micro"].render(
                value,
                True,
                DARK
            )
            value_rect = value_img.get_rect(
                midright=(1392, y + 15)
            )
            self.screen.blit(value_img, value_rect)

        # Indicador final de calidad separado de la lista.
        quality_line = pygame.Rect(1124, content_y + 191, 272, 4)
        rr(self.screen, quality_line, (229, 232, 235), 2)

        quality_fill = pygame.Rect(
            quality_line.x,
            quality_line.y,
            int(quality_line.width * 0.98),
            quality_line.height
        )
        rr(self.screen, quality_fill, GREEN, 2)

        text(
            self.screen,
            "CALIDAD DE SALIDA",
            self.fonts["micro"],
            MUTED,
            (1124, content_y + 204)
        )

        text(
            self.screen,
            "98%",
            self.fonts["micro"],
            GREEN,
            (1396, content_y + 204)
        )

        # ============================================================
        # BARRA DE PROGRESO INFERIOR
        # Dos filas completamente independientes:
        #   fila 1 = progreso
        #   fila 2 = etapas
        # ============================================================
        progress_box = pygame.Rect(210, 688, 1116, 92)
        self.draw_shadow(progress_box, 22, (0, 5), 15)
        rr(self.screen, progress_box, DARK, 22)

        # Columna de texto.
        text(
            self.screen,
            "COCINANDO INSIGHTS",
            self.fonts["small"],
            WHITE,
            (242, 705)
        )

        text(
            self.screen,
            "Transformando datos en decisiones.",
            self.fonts["micro"],
            (183, 198, 205),
            (242, 737)
        )

        # Barra de progreso: únicamente ocupa la fila superior.
        bar = pygame.Rect(610, 710, 545, 15)
        rr(self.screen, bar, (73, 88, 98), 8)

        if progress > 0:
            fill_width = max(
                8,
                int(bar.width * progress)
            )
            rr(
                self.screen,
                pygame.Rect(
                    bar.x,
                    bar.y,
                    fill_width,
                    bar.height
                ),
                ORANGE,
                8
            )

        text(
            self.screen,
            f"{int(progress * 100)}%",
            self.fonts["body_bold"],
            ORANGE,
            (1190, 700)
        )

        # Etapas: se dibujan debajo de la barra, nunca sobre ella.
        steps = [
            ("01", "PREPARAR"),
            ("02", "VALIDAR"),
            ("03", "TRANSFORMAR"),
            ("04", "COCINAR")
        ]

        sx = 625
        gap = 158
        step_y = 750

        for i, (num, label) in enumerate(steps):
            x = sx + i * gap
            active = progress >= (i + 1) / 4
            c = ORANGE if active else (93, 108, 118)

            pygame.draw.circle(
                self.screen,
                c,
                (x, step_y),
                8
            )

            text(
                self.screen,
                num,
                self.fonts["micro"],
                WHITE,
                (x, step_y),
                True
            )

            text(
                self.screen,
                label,
                self.fonts["micro"],
                (183, 198, 205),
                (x, 762),
                True
            )

            if i < 3:
                line(
                    self.screen,
                    (93, 108, 118),
                    (x + 11, step_y),
                    (x + gap - 11, step_y),
                    2
                )

        # Flash final muy sutil.
        if self.scene_time > 2.3:
            flash_alpha = int(
                min(70, (self.scene_time - 2.3) * 100)
            )
            layer = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )
            layer.fill((255, 255, 255, flash_alpha))
            self.screen.blit(layer, (0, 0))

    # ============================================================
    # PANEL FINAL — RECETA TERMINADA
    # ============================================================

    def draw_chef_proud(self):
        """Chef orgulloso: columna independiente a la derecha."""
        # El chef tiene una columna propia.
        # No comparte espacio con el dashboard ni con los mensajes.
        area = pygame.Rect(1160, 335, 310, 420)

        # Halo suave
        pygame.draw.circle(
            self.screen,
            (255, 239, 218),
            (area.centerx, 520),
            145
        )
        pygame.draw.circle(
            self.screen,
            (255, 247, 237),
            (area.centerx, 520),
            118
        )

        # Sombra de piso
        pygame.draw.ellipse(
            self.screen,
            (214, 208, 198),
            (area.x + 10, area.bottom - 20, 290, 25)
        )

        if self.chef_proud:
            iw, ih = self.chef_proud.get_size()

            # Mantener el personaje dentro de su columna.
            scale = min(
                300 / iw,
                420 / ih
            )

            scaled = pygame.transform.smoothscale(
                self.chef_proud,
                (
                    max(1, int(iw * scale)),
                    max(1, int(ih * scale))
                )
            )

            rect = scaled.get_rect(
                midbottom=(area.centerx, area.bottom)
            )

            self.screen.blit(scaled, rect)

        else:
            rr(
                self.screen,
                pygame.Rect(area.x + 25, area.y + 50, 260, 300),
                WHITE,
                28,
                2,
                ORANGE
            )

            text(
                self.screen,
                "CHEF",
                self.fonts["title"],
                ORANGE,
                (area.centerx, area.y + 205),
                True
            )


    def draw_final(self):
        """Pantalla final PREMIUM: resultado terminado, jerarquía clara y cero glifos de fuente para iconos."""
        self.draw_background()
        self.draw_header()

        # ========================================================
        # HERO — RESULTADO FINAL
        # ========================================================
        rr(self.screen, pygame.Rect(70, 158, 250, 32), LIGHT_ORANGE, 16)
        text(self.screen, "04  /  RECETA TERMINADA", self.fonts["micro"],
             DARK_ORANGE, (195, 174), True)

        title_a = "¡RECETA"
        title_b = "TERMINADA!"
        title_font = self.fonts["title"]
        gap = 16
        wa = title_font.size(title_a)[0]
        wb = title_font.size(title_b)[0]
        title_x = (WIDTH - wa - wb - gap) // 2
        text(self.screen, title_a, title_font, DARK, (title_x, 157))
        text(self.screen, title_b, title_font, ORANGE,
             (title_x + wa + gap, 157))

        text(self.screen,
             "Tu información está lista para convertirse en decisiones.",
             self.fonts["body"], MUTED, (WIDTH // 2, 222), True)

        pygame.draw.line(self.screen, ORANGE, (700, 260), (836, 260), 3)
        pygame.draw.circle(self.screen, ORANGE, (686, 260), 4)
        pygame.draw.circle(self.screen, ORANGE, (850, 260), 4)

        # ========================================================
        # LAYOUT PRINCIPAL
        # ========================================================
        dashboard = pygame.Rect(58, 292, 925, 470)
        side = pygame.Rect(1010, 292, 468, 470)

        for box in (dashboard, side):
            self.draw_shadow(box, 28, (0, 8), 24)

        # ========================================================
        # DASHBOARD DE RESULTADOS
        # ========================================================
        rr(self.screen, dashboard, WHITE, 28, 2, (224, 218, 209))

        dash_header = pygame.Rect(dashboard.x, dashboard.y, dashboard.width, 72)
        rr(self.screen, dash_header, DARK, 28)
        pygame.draw.rect(self.screen, DARK,
                         (dash_header.x, dash_header.bottom - 28,
                          dash_header.width, 28))

        text(self.screen, "PANEL DE RESULTADOS", self.fonts["subtitle"], WHITE,
             (dashboard.x + 28, dashboard.y + 20))

        status = pygame.Rect(dashboard.right - 175, dashboard.y + 18, 145, 36)
        rr(self.screen, status, (55, 76, 87), 18)
        pygame.draw.circle(self.screen, GREEN, (status.x + 18, status.centery), 5)
        text(self.screen, "PANEL LISTO", self.fonts["micro"], WHITE,
             (status.x + 31, status.y + 10))

        # ========================================================
        # KPI — RESULTADOS CLAVE
        # Iconografía 100% vectorial: no usamos ✓ ni otros glifos.
        # ========================================================
        kpis = [
            ("VENTAS", "$ 2.4M", "Resultado comercial", ORANGE, "sales"),
            ("CLIENTES", "18,542", "Clientes procesados", BLUE, "clients"),
            ("CALIDAD", "98.7%", "Nivel de confiabilidad", GREEN, "quality"),
        ]

        kpi_y = dashboard.y + 94
        kpi_w = 274
        kpi_h = 108
        kpi_gap = 18

        for i, (label, value, desc, color, icon_type) in enumerate(kpis):
            x = dashboard.x + 24 + i * (kpi_w + kpi_gap)
            card = pygame.Rect(x, kpi_y, kpi_w, kpi_h)

            rr(self.screen, card, (249, 250, 251), 20, 1,
               (224, 228, 231))

            pygame.draw.rect(self.screen, color,
                             (card.x + 18, card.y + 15, 42, 5),
                             border_radius=3)

            text(self.screen, label, self.fonts["micro"], MUTED,
                 (card.x + 18, card.y + 32))
            text(self.screen, value, self.fonts["subtitle"], color,
                 (card.x + 18, card.y + 51))
            text(self.screen, desc, self.fonts["micro"], MUTED,
                 (card.x + 18, card.y + 86))

            # Icono decorativo funcional, sin caracteres Unicode.
            icon_c = (card.right - 28, card.y + 28)
            pygame.draw.circle(self.screen, color, icon_c, 11)
            pygame.draw.circle(self.screen, WHITE, icon_c, 8, 2)

            if icon_type == "sales":
                pygame.draw.line(self.screen, WHITE,
                                 (icon_c[0] - 4, icon_c[1] + 3),
                                 (icon_c[0] - 1, icon_c[1]), 2)
                pygame.draw.line(self.screen, WHITE,
                                 (icon_c[0] - 1, icon_c[1]),
                                 (icon_c[0] + 5, icon_c[1] - 5), 2)
                pygame.draw.line(self.screen, WHITE,
                                 (icon_c[0] + 2, icon_c[1] - 5),
                                 (icon_c[0] + 5, icon_c[1] - 5), 2)
                pygame.draw.line(self.screen, WHITE,
                                 (icon_c[0] + 5, icon_c[1] - 5),
                                 (icon_c[0] + 5, icon_c[1] - 2), 2)
            elif icon_type == "clients":
                pygame.draw.circle(self.screen, WHITE,
                                   (icon_c[0], icon_c[1] - 3), 2)
                pygame.draw.arc(self.screen, WHITE,
                                (icon_c[0] - 5, icon_c[1], 10, 7),
                                math.pi, math.tau, 2)
            else:
                draw_check(self.screen, icon_c, WHITE, 0.55, 2)

        # ========================================================
        # TENDENCIA
        # ========================================================
        chart = pygame.Rect(dashboard.x + 24, dashboard.y + 222, 560, 216)
        rr(self.screen, chart, (249, 250, 251), 22, 1,
           (225, 229, 233))

        text(self.screen, "TENDENCIA DEL RESULTADO", self.fonts["small"],
             DARK, (chart.x + 22, chart.y + 18))
        text(self.screen, "Evolución de los datos procesados", self.fonts["micro"],
             MUTED, (chart.x + 22, chart.y + 46))

        graph_x = chart.x + 28
        graph_y = chart.y + 78
        graph_w = 505
        graph_h = 112

        for j in range(4):
            gy = graph_y + j * 30
            pygame.draw.line(self.screen, (231, 234, 236),
                             (graph_x, gy), (graph_x + graph_w, gy), 1)

        values = [48, 72, 61, 92, 81, 116, 103]
        points = []
        for i, value in enumerate(values):
            px = graph_x + int(i * (graph_w / 6))
            py = graph_y + graph_h - value
            points.append((px, py))

        area_points = points + [
            (points[-1][0], graph_y + graph_h),
            (points[0][0], graph_y + graph_h)
        ]

        overlay = pygame.Surface((chart.width, chart.height), pygame.SRCALPHA)
        local_area = [(p[0] - chart.x, p[1] - chart.y) for p in area_points]
        pygame.draw.polygon(overlay, (247, 116, 18, 22), local_area)
        self.screen.blit(overlay, chart.topleft)

        pygame.draw.lines(self.screen, BLUE, False, points, 4)
        for i, p in enumerate(points):
            pygame.draw.circle(self.screen, WHITE, p, 7)
            pygame.draw.circle(self.screen, ORANGE, p, 5)
            text(self.screen, str(i + 1), self.fonts["micro"], MUTED,
                 (p[0], chart.bottom - 17), True)

        # ========================================================
        # CALIDAD FINAL
        # ========================================================
        quality = pygame.Rect(dashboard.x + 604, dashboard.y + 222, 297, 216)
        rr(self.screen, quality, (252, 249, 243), 22, 1,
           (239, 224, 207))

        text(self.screen, "CALIDAD DEL DATO", self.fonts["small"], DARK,
             (quality.x + 20, quality.y + 18))
        text(self.screen, "Resultado final", self.fonts["micro"], MUTED,
             (quality.x + 20, quality.y + 45))

        cx = quality.x + 82
        cy = quality.y + 127
        pygame.draw.circle(self.screen, (239, 236, 229), (cx, cy), 57)
        pygame.draw.arc(self.screen, GREEN,
                        (cx - 48, cy - 48, 96, 96),
                        math.radians(-90), math.radians(265), 12)
        pygame.draw.circle(self.screen, (252, 249, 243), (cx, cy), 32)
        text(self.screen, "98.7%", self.fonts["body_bold"], GREEN,
             (cx, cy - 3), True)
        text(self.screen, "CONFIABLE", self.fonts["micro"], MUTED,
             (cx, cy + 22), True)

        metric_x = quality.x + 150
        text(self.screen, "ESTADO", self.fonts["micro"], MUTED,
             (metric_x, quality.y + 78))
        pygame.draw.circle(self.screen, GREEN, (metric_x + 6, quality.y + 109), 4)
        text(self.screen, "VALIDADO", self.fonts["small"], GREEN,
             (metric_x + 16, quality.y + 99))

        text(self.screen, "PROCESAMIENTO", self.fonts["micro"], MUTED,
             (metric_x, quality.y + 132))
        pygame.draw.circle(self.screen, ORANGE, (metric_x + 6, quality.y + 163), 4)
        text(self.screen, "100% COMPLETO", self.fonts["small"], ORANGE,
             (metric_x + 16, quality.y + 153))

        # ========================================================
        # CINTA DE FLUJO — sin flechas Unicode
        # ========================================================
        ribbon = pygame.Rect(dashboard.x + 24, dashboard.bottom - 48,
                             dashboard.width - 48, 28)
        rr(self.screen, ribbon, LIGHT_ORANGE, 14)
        pygame.draw.circle(self.screen, ORANGE,
                           (ribbon.x + 17, ribbon.centery), 5)

        flow_labels = ["DATOS LIMPIOS", "VALIDADOS", "TRANSFORMADOS", "INFORMACIÓN ÚTIL"]
        flow_x = ribbon.x + 31
        for i, label in enumerate(flow_labels):
            text(self.screen, label, self.fonts["micro"], DARK_ORANGE,
                 (flow_x, ribbon.y + 7))
            flow_w = self.fonts["micro"].size(label)[0]
            flow_x += flow_w + 13
            if i < len(flow_labels) - 1:
                pygame.draw.line(self.screen, ORANGE,
                                 (flow_x, ribbon.centery - 4),
                                 (flow_x + 7, ribbon.centery), 2)
                pygame.draw.line(self.screen, ORANGE,
                                 (flow_x + 7, ribbon.centery),
                                 (flow_x, ribbon.centery + 4), 2)
                flow_x += 14

        # ========================================================
        # COLUMNA DEL CHEF
        # ========================================================
        rr(self.screen, side, (252, 248, 241), 28, 2,
           (235, 224, 211))

        side_header = pygame.Rect(side.x, side.y, side.width, 64)
        rr(self.screen, side_header, DARK, 28)
        pygame.draw.rect(self.screen, DARK,
                         (side_header.x, side_header.bottom - 25,
                          side_header.width, 25))

        text(self.screen, "CHEF DE DATOS", self.fonts["small"], WHITE,
             (side.x + 24, side.y + 18))

        side_status = pygame.Rect(side.right - 118, side.y + 16, 94, 32)
        rr(self.screen, side_status, (55, 76, 87), 16)
        pygame.draw.circle(self.screen, GREEN,
                           (side.right - 100, side.y + 32), 5)
        text(self.screen, "LISTO", self.fonts["micro"], WHITE,
             (side.right - 87, side.y + 24))

        # Halo y personaje dentro de una zona claramente delimitada.
        halo_center = (side.centerx, side.y + 245)
        pygame.draw.circle(self.screen, (255, 239, 218), halo_center, 155)
        pygame.draw.circle(self.screen, (255, 247, 237), halo_center, 126)

        if self.chef_proud:
            iw, ih = self.chef_proud.get_size()
            max_w, max_h = 330, 350
            scale = min(max_w / iw, max_h / ih)
            scaled = pygame.transform.smoothscale(
                self.chef_proud,
                (max(1, int(iw * scale)), max(1, int(ih * scale)))
            )
            chef_rect = scaled.get_rect(midbottom=(side.centerx, side.y + 392))
            self.screen.blit(scaled, chef_rect)
        else:
            rr(self.screen, pygame.Rect(side.x + 100, side.y + 105, 260, 300),
               WHITE, 28, 2, ORANGE)
            text(self.screen, "CHEF", self.fonts["title"], ORANGE,
                 (side.centerx, side.y + 245), True)

        pygame.draw.ellipse(self.screen, (215, 208, 198),
                            (side.x + 68, side.y + 375,
                             side.width - 136, 25))

        # Mensaje final: ahora es una tarjeta visual, no un espacio vacío.
        result_badge = pygame.Rect(side.x + 28, side.bottom - 86,
                                   side.width - 56, 54)
        rr(self.screen, result_badge, WHITE, 18, 1, (231, 221, 210))
        pygame.draw.circle(self.screen, GREEN,
                           (result_badge.x + 22, result_badge.centery), 7)
        text(self.screen, "RECETA COMPLETADA", self.fonts["small"], DARK,
             (result_badge.x + 39, result_badge.y + 8))
        text(self.screen, "Tu panel está listo para decidir.", self.fonts["micro"],
             MUTED, (result_badge.x + 39, result_badge.y + 31))

        # ========================================================
        # FOOTER — PROGRESO FINAL
        # ========================================================
        progress_box = pygame.Rect(55, 790, 1425, 57)
        self.draw_shadow(progress_box, 20, (0, 5), 18)
        rr(self.screen, progress_box, DARK, 20)

        text(self.screen, "COCINANDO INSIGHTS", self.fonts["small"], WHITE,
             (82, 802))
        text(self.screen, "100%", self.fonts["body_bold"], ORANGE,
             (252, 800))
        text(self.screen, "PROCESO COMPLETADO", self.fonts["micro"],
             (183, 198, 205), (82, 827))

        bar = pygame.Rect(395, 813, 650, 14)
        rr(self.screen, bar, (73, 88, 98), 7)
        rr(self.screen, bar, ORANGE, 7)

        steps = [
            ("01", "PREPARAR"),
            ("02", "VALIDAR"),
            ("03", "TRANSFORMAR"),
            ("04", "COCINAR")
        ]
        sx = 1110
        gap = 112
        step_y = 824

        for i, (num, label) in enumerate(steps):
            x = sx + i * gap
            if i < 3:
                line(self.screen, (91, 106, 115),
                     (x + 10, step_y), (x + gap - 10, step_y), 2)
            pygame.draw.circle(self.screen, ORANGE, (x, step_y), 9)
            text(self.screen, num, self.fonts["micro"], WHITE,
                 (x, step_y), True)
            text(self.screen, label, self.fonts["micro"],
                 (183, 198, 205), (x, 837), True)

    def draw_demo_dashboard(self, box, reveal):
        clip = pygame.Rect(
            box.x + 25,
            box.y + 25,
            int((box.width - 50) * reveal),
            box.height - 50
        )

        old_clip = self.screen.get_clip()

        self.screen.set_clip(clip)

        inner = pygame.Rect(
            box.x + 25,
            box.y + 25,
            box.width - 50,
            box.height - 50
        )

        rr(
            self.screen,
            inner,
            (248, 250, 252),
            18
        )

        text(
            self.screen,
            "PANEL DE RESULTADOS",
            self.fonts["subtitle"],
            DARK,
            (inner.x + 30, inner.y + 25)
        )

        cards = [
            ("VENTAS", "$ 2.4M", ORANGE),
            ("CLIENTES", "18,542", BLUE),
            ("CALIDAD", "98.7%", GREEN),
        ]

        x = inner.x + 30

        for title, value, color in cards:
            card = pygame.Rect(
                x,
                inner.y + 85,
                230,
                105
            )

            rr(
                self.screen,
                card,
                WHITE,
                18,
                2,
                (225, 230, 235)
            )

            text(
                self.screen,
                title,
                self.fonts["small"],
                MUTED,
                (card.x + 18, card.y + 18)
            )

            text(
                self.screen,
                value,
                self.fonts["subtitle"],
                color,
                (card.x + 18, card.y + 52)
            )

            x += 250

        graph = pygame.Rect(
            inner.x + 30,
            inner.y + 225,
            530,
            190
        )

        rr(
            self.screen,
            graph,
            WHITE,
            18,
            2,
            (225, 230, 235)
        )

        values = [
            60, 95, 80, 130,
            115, 165, 145
        ]

        px = graph.x + 35
        base_y = graph.bottom - 30
        points = []

        for i, value in enumerate(values):
            x = px + i * 70
            y = base_y - value
            points.append((x, y))

        pygame.draw.lines(
            self.screen,
            BLUE,
            False,
            points,
            4
        )

        for p in points:
            pygame.draw.circle(
                self.screen,
                ORANGE,
                p,
                6
            )

        cx, cy = (
            inner.right - 180,
            inner.y + 320
        )

        pygame.draw.circle(
            self.screen,
            LIGHT_ORANGE,
            (cx, cy),
            75
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (cx, cy),
            50,
            16
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (cx, cy),
            25
        )

        text(
            self.screen,
            "INSIGHTS",
            self.fonts["small"],
            DARK,
            (cx, cy + 95),
            True
        )

        self.screen.set_clip(old_clip)

    # ============================================================
    # EVENTOS
    # ============================================================

    def handle_events(self):
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

                elif event.key == pygame.K_SPACE:

                    if self.scene == "intro":
                        self.set_scene("dirty_panel")

                    elif self.scene == "dirty_panel":
                        self.set_scene("cooking")

                    elif self.scene == "cooking":
                        for ingredient in self.ingredients:
                            ingredient.done = True

                        self.set_scene("transform")

                    elif self.scene == "transform":
                        self.set_scene("final")

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    logical = self.logical(event.pos)

                    if self.scene == "intro":
                        button = pygame.Rect(
                            995,
                            650,
                            330,
                            54
                        )

                        if button.collidepoint(logical):
                            print(
                                "[DATA CHEF] "
                                "EMPEZAR -> PANEL SUCIO"
                            )

                            self.set_scene("dirty_panel")

                    elif self.scene == "dirty_panel":
                        button = pygame.Rect(
                            1050,
                            748,
                            380,
                            58
                        )

                        if button.collidepoint(logical):
                            print(
                                "[DATA CHEF] "
                                "DATOS SUCIOS -> COCINANDO"
                            )

                            self.set_scene("cooking")

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, dt):
        self.t += dt
        self.scene_time += dt

        if self.scene == "cooking":

            for ingredient in self.ingredients:
                ingredient.update(dt)

            done = sum(
                1
                for ingredient in self.ingredients
                if ingredient.done
            )

            for particle in self.steam:
                particle.update(
                    dt,
                    self.steam_origin
                )

            if (
                done == len(self.ingredients)
                and self.scene_time > 4
            ):
                print(
                    "[DATA CHEF] "
                    "INGREDIENTES LISTOS -> "
                    "TRANSFORMACIÓN"
                )

                self.set_scene("transform")

        elif self.scene == "transform":

            if self.scene_time >= 3.2:
                print(
                    "[DATA CHEF] "
                    "TRANSFORMACIÓN COMPLETA -> "
                    "PANEL FINAL"
                )

                self.set_scene("final")

        elif self.scene == "final":
            self.panel_reveal = 1.0

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self):
        if self.scene == "intro":
            self.draw_intro()

        elif self.scene == "dirty_panel":
            self.draw_dirty_panel()

        elif self.scene == "cooking":
            self.draw_cooking()

        elif self.scene == "transform":
            self.draw_transform()

        elif self.scene == "final":
            self.draw_final()

        # Adaptar pantalla lógica a ventana
        ww, wh = self.window.get_size()

        self.scale = min(
            ww / WIDTH,
            wh / HEIGHT
        )

        rw = max(
            1,
            int(WIDTH * self.scale)
        )

        rh = max(
            1,
            int(HEIGHT * self.scale)
        )

        self.ox = (ww - rw) // 2
        self.oy = (wh - rh) // 2

        scaled = pygame.transform.smoothscale(
            self.screen,
            (rw, rh)
        )

        self.window.fill(
            (228, 228, 228)
        )

        self.window.blit(
            scaled,
            (self.ox, self.oy)
        )

        pygame.display.flip()

    # ============================================================
    # LOOP
    # ============================================================

    def run(self):
        while self.running:

            dt = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    DataChefScreen().run()
