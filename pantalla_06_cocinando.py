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
        self.dirty_reveal = 0
        self.transform_progress = 0

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
                "✓", "Datos validados", 1.4
            ),
            FlyingIngredient(
                900, 720, (1110, 560),
                "▥", "Información", 2.0
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

        start_x = 770
        card_y = 320
        card_w = 157
        gap = 13

        for i, (num, title, desc, color) in enumerate(stages):
            x = start_x + i * (card_w + gap)

            card = pygame.Rect(
                x,
                card_y,
                card_w,
                155
            )

            rr(
                self.screen,
                card,
                PALE_ORANGE if i == 3 else (249, 249, 247),
                20,
                2,
                (225, 219, 211)
            )

            pygame.draw.rect(
                self.screen,
                color,
                (x, card_y, 6, 155),
                border_radius=3
            )

            pygame.draw.circle(
                self.screen,
                color,
                (x + 35, card_y + 35),
                19
            )

            text(
                self.screen,
                num,
                self.fonts["tiny"],
                WHITE,
                (x + 35, card_y + 35),
                True
            )

            text(
                self.screen,
                title,
                self.fonts["tiny"],
                DARK,
                (x + 18, card_y + 72)
            )

            text(
                self.screen,
                desc,
                self.fonts["micro"],
                MUTED,
                (x + 18, card_y + 100)
            )

            pygame.draw.circle(
                self.screen,
                color,
                (x + card_w - 27, card_y + 126),
                10
            )

            text(
                self.screen,
                "✓",
                self.fonts["micro"],
                WHITE,
                (x + card_w - 27, card_y + 126),
                True
            )

        line(
            self.screen,
            (224, 218, 209),
            (805, 530),
            (1407, 530),
            4
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
            "PREPARAR  →  LIMPIAR  →  RETAR  →  COCINAR",
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
    # PANEL SUCIO - ASÍ QUEDARÍA SIN LIMPIEZA
    # ============================================================

    def draw_dirty_panel(self):
        self.draw_background()
        self.draw_header()
        text(self.screen, "ANTES DE COCINAR...", self.fonts["title"], DARK, (768, 145), True)
        text(self.screen, "Así se vería el panel usando datos sucios, duplicados y sin validar.", self.fonts["body"], MUTED, (768, 205), True)

        box = pygame.Rect(150, 245, 1236, 485)
        rr(self.screen, box, WHITE, 30, 3, (240, 190, 190))
        inner = pygame.Rect(box.x+22, box.y+22, box.width-44, box.height-44)
        rr(self.screen, inner, (249,250,252), 20)
        text(self.screen, "PANEL DE RESULTADOS", self.fonts["subtitle"], DARK, (inner.x+25, inner.y+20))
        rr(self.screen, pygame.Rect(inner.right-300, inner.y+15, 270, 38), (255,232,232), 12, 2, (235,120,120))
        text(self.screen, "⚠ DATOS SIN VALIDAR", self.fonts["small"], (190,70,70), (inner.right-165, inner.y+34), True)

        cards=[("VENTAS", "$ 2.4M", ORANGE),("CLIENTES", "NULL", (210,70,70)),("VENTAS", "$ 2.4M", ORANGE),("CALIDAD", "145%", (210,70,70))]
        for i,(title,value,color) in enumerate(cards):
            card=pygame.Rect(inner.x+28+i*285, inner.y+82+(i%2)*8, 255, 100)
            rr(self.screen, card, WHITE, 16, 2, (225,225,225))
            text(self.screen,title,self.fonts["small"],MUTED,(card.x+16,card.y+14))
            text(self.screen,value,self.fonts["subtitle"],color,(card.x+16,card.y+48))

        graph=pygame.Rect(inner.x+28, inner.y+210, 705, 220)
        rr(self.screen, graph, WHITE, 16, 2, (225,225,225))
        text(self.screen,"VENTAS POR PERIODO (DATOS INCONSISTENTES)",self.fonts["small"],DARK,(graph.x+18,graph.y+15))
        for gy in range(graph.y+55,graph.bottom-15,35):
            pygame.draw.line(self.screen,(230,230,230),(graph.x+18,gy),(graph.right-18,gy),1)
        vals=[35,145,55,175,70,155,40,190]
        pts=[]
        for i,v in enumerate(vals): pts.append((graph.x+35+i*82, graph.bottom-20-int(v*.85)))
        pygame.draw.lines(self.screen,(210,70,70),False,pts,4)
        for pt in pts: pygame.draw.circle(self.screen,(210,70,70),pt,6)

        table=pygame.Rect(inner.x+765,inner.y+210,inner.width-793,220)
        rr(self.screen,table,WHITE,16,2,(225,225,225))
        rows=[("CLIENTE","VALOR"),("JUAN","$500"),("juan ","$500"),("JUAN","NULL"),("Maria","$-250"),("PEDRO","$1,000"),("Pedro ","$1,000")]
        for i,(a,b) in enumerate(rows):
            y=table.y+15+i*28
            if i==0: rr(self.screen,pygame.Rect(table.x+8,y-5,table.width-16,25),(240,240,240),7)
            col=DARK if i==0 else ((190,70,70) if ("NULL" in b or "-" in b or i in (2,3,6)) else MUTED)
            text(self.screen,a,self.fonts["tiny"],col,(table.x+16,y))
            text(self.screen,b,self.fonts["tiny"],col,(table.x+table.width-105,y))

        problems=["✕ Datos duplicados","✕ Valores NULL","✕ Datos inconsistentes","✕ Métricas incorrectas"]
        for i,label in enumerate(problems):
            x=180+i*300
            rr(self.screen,pygame.Rect(x,748,270,38),(255,238,238),15,2,(240,170,170))
            text(self.screen,label,self.fonts["small"],(190,70,70),(x+135,767),True)

        button=pygame.Rect(585,800,366,52)
        hover=button.collidepoint(self.logical(pygame.mouse.get_pos()))
        draw_button=button.move(0,-3 if hover else 0)
        rr(self.screen,draw_button,ORANGE,18)
        text(self.screen,"👨‍🍳  LIMPIAR Y COCINAR",self.fonts["button"],WHITE,draw_button.center,True)

    # ============================================================
    # COCINANDO
    # ============================================================

    def draw_cooking(self):
        self.draw_background()
        self.draw_header()

        # ========================================================
        # TÍTULO — ZONA EXCLUSIVA, SIN PERSONAJES ENCIMA
        # ========================================================
        title_y = 171

        # Etiqueta de estación
        rr(
            self.screen,
            pygame.Rect(78, 158, 190, 30),
            LIGHT_ORANGE,
            15
        )
        text(
            self.screen,
            "04  /  ESTACIÓN DE COCINA",
            self.fonts["micro"],
            DARK_ORANGE,
            (173, 173),
            True
        )

        # --------------------------------------------------------
        # TÍTULO CORREGIDO
        # Se calcula el ancho REAL de ambas palabras para que
        # "PREPARANDO TU PANEL..." quede como un solo titular,
        # perfectamente centrado y sin superposición.
        # --------------------------------------------------------
        title_a = "PREPARANDO"
        title_b = "TU PANEL..."
        title_font = self.fonts["title"]
        title_gap = 18

        width_a = title_font.size(title_a)[0]
        width_b = title_font.size(title_b)[0]
        total_width = width_a + title_gap + width_b

        title_x = (WIDTH - total_width) // 2

        text(
            self.screen,
            title_a,
            title_font,
            DARK,
            (title_x, title_y)
        )

        text(
            self.screen,
            title_b,
            title_font,
            ORANGE,
            (title_x + width_a + title_gap, title_y)
        )

        text(
            self.screen,
            "Cada ingrediente representa datos preparados y confiables.",
            self.fonts["body"],
            MUTED,
            (768, 226),
            True
        )

        # Pequeño detalle decorativo de cocina
        pygame.draw.line(
            self.screen, ORANGE, (708, 253), (828, 253), 3
        )
        pygame.draw.circle(self.screen, ORANGE, (695, 253), 4)
        pygame.draw.circle(self.screen, ORANGE, (841, 253), 4)

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
        # TARJETA DEL CHEF
        # ========================================================
        rr(
            self.screen,
            pygame.Rect(70, 270, 600, 68),
            DARK,
            28
        )
        pygame.draw.rect(
            self.screen,
            DARK,
            (70, 310, 600, 28)
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

        # Indicador activo
        rr(
            self.screen,
            pygame.Rect(500, 287, 135, 32),
            (55, 76, 87),
            16
        )
        pygame.draw.circle(
            self.screen, GREEN, (519, 303), 5
        )
        text(
            self.screen,
            "EN MARCHA",
            self.fonts["micro"],
            WHITE,
            (531, 294)
        )

        # Fondo visual del chef: halo, pero sin invadir texto.
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

        # Líneas decorativas tipo radar
        pygame.draw.arc(
            self.screen,
            (246, 220, 191),
            (115, 380, 320, 320),
            math.radians(205),
            math.radians(330),
            2
        )

        # Chef estrictamente contenido en su zona
        self.draw_chef_cooking(
            pygame.Rect(95, 338, 350, 390)
        )

        # ========================================================
        # BURBUJA / TIP DEL CHEF — COLUMNA DERECHA
        # ========================================================
        bubble = pygame.Rect(390, 405, 245, 160)

        self.draw_shadow(
            bubble,
            22,
            (0, 5),
            18
        )

        rr(
            self.screen,
            bubble,
            (252, 248, 241),
            22,
            2,
            (239, 215, 190)
        )

        # Pico hacia el chef
        pygame.draw.polygon(
            self.screen,
            (252, 248, 241),
            [
                (390, 470),
                (362, 486),
                (390, 501)
            ]
        )

        pygame.draw.rect(
            self.screen,
            ORANGE,
            (415, 429, 42, 5),
            border_radius=3
        )

        text(
            self.screen,
            "TIP DEL CHEF",
            self.fonts["micro"],
            DARK_ORANGE,
            (415, 444)
        )

        text(
            self.screen,
            "“Primero mezclaremos",
            self.fonts["body_bold"],
            DARK,
            (415, 472)
        )
        text(
            self.screen,
            "los datos de calidad...”",
            self.fonts["small"],
            ORANGE,
            (415, 503)
        )

        # Mini insight inferior
        rr(
            self.screen,
            pygame.Rect(390, 594, 245, 76),
            PALE_ORANGE,
            18
        )
        pygame.draw.circle(
            self.screen, ORANGE, (415, 620), 8
        )
        text(
            self.screen,
            "OBJETIVO",
            self.fonts["micro"],
            DARK_ORANGE,
            (432, 607)
        )
        text(
            self.screen,
            "Convertir datos en valor.",
            self.fonts["small"],
            DARK,
            (432, 629)
        )

        # ========================================================
        # RECETA DE DATOS
        # ========================================================
        # Cabecera azul para diferenciarla visualmente del chef.
        rr(
            self.screen,
            pygame.Rect(695, 270, 770, 72),
            DARK,
            28
        )
        pygame.draw.rect(
            self.screen,
            DARK,
            (695, 310, 770, 32)
        )

        text(
            self.screen,
            "RECETA DE DATOS",
            self.fonts["subtitle"],
            WHITE,
            (730, 292)
        )

        rr(
            self.screen,
            pygame.Rect(1295, 288, 135, 34),
            (55, 76, 87),
            17
        )
        pygame.draw.circle(
            self.screen, GREEN, (1315, 305), 5
        )
        text(
            self.screen,
            "LISTO",
            self.fonts["micro"],
            WHITE,
            (1328, 297)
        )

        # Subtítulo de receta
        text(
            self.screen,
            "INGREDIENTES DE LA INFORMACIÓN",
            self.fonts["tiny"],
            MUTED,
            (730, 365)
        )

        # ========================================================
        # INGREDIENTES — COLUMNA IZQUIERDA
        # ========================================================
        ingredient_cards = [
            ("DB", "BASE DE DATOS", "Origen", BLUE),
            ("✦", "DATOS LIMPIOS", "Preparados", GREEN),
            ("✓", "DATOS VALIDADOS", "Confiables", ORANGE),
            ("▥", "INFORMACIÓN", "Estructurada", DARK_ORANGE),
        ]

        card_x = 730
        card_y = 397
        card_w = 280
        card_h = 64
        card_gap = 10

        for i, (icon, name, desc, color) in enumerate(ingredient_cards):
            y = card_y + i * (card_h + card_gap)

            rr(
                self.screen,
                pygame.Rect(card_x, y, card_w, card_h),
                (250, 249, 246),
                18,
                1,
                (231, 224, 215)
            )

            pygame.draw.circle(
                self.screen,
                (242, 238, 230),
                (card_x + 34, y + 32),
                23
            )

            text(
                self.screen,
                icon,
                self.fonts["tiny"],
                color,
                (card_x + 34, y + 32),
                True
            )

            text(
                self.screen,
                name,
                self.fonts["micro"],
                DARK,
                (card_x + 70, y + 17)
            )
            text(
                self.screen,
                desc,
                self.fonts["micro"],
                MUTED,
                (card_x + 70, y + 37)
            )

            pygame.draw.circle(
                self.screen,
                color,
                (card_x + card_w - 22, y + 32),
                9
            )
            text(
                self.screen,
                "✓",
                self.fonts["micro"],
                WHITE,
                (card_x + card_w - 22, y + 32),
                True
            )

        # ========================================================
        # CONEXIONES HACIA LA OLLA
        # ========================================================
        pot_center = (1260, 548)

        for i in range(4):
            sy = card_y + i * (card_h + card_gap) + card_h // 2
            start_pt = (card_x + card_w + 10, sy)

            # Curva simulada con segmentos suaves
            points = []
            for k in range(13):
                u = k / 12
                px = start_pt[0] + (pot_center[0] - start_pt[0]) * u
                py = sy + (pot_center[1] - sy) * u
                py += math.sin(u * math.pi) * (8 + i * 2)
                points.append((int(px), int(py)))

            pygame.draw.lines(
                self.screen,
                (222, 216, 207),
                False,
                points,
                2
            )

            pygame.draw.circle(
                self.screen,
                ORANGE if i == 2 else (198, 205, 208),
                start_pt,
                4
            )

        # ========================================================
        # OLLA — ELEMENTO HERO
        # ========================================================
        rr(
            self.screen,
            pygame.Rect(1035, 390, 380, 300),
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
            (1225, 414),
            True
        )

        # Anillo detrás de la olla
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

        # Olla principal
        self.draw_pot(*pot_center)

        # Vapor animado
        for particle in self.steam:
            particle.draw(self.screen)

        # Etiqueta inferior del hero
        rr(
            self.screen,
            pygame.Rect(1090, 657, 340, 42),
            WHITE,
            21,
            1,
            (232, 222, 210)
        )
        pygame.draw.circle(
            self.screen,
            GREEN,
            (1115, 678),
            6
        )
        text(
            self.screen,
            "DATOS + CALIDAD = INFORMACIÓN ÚTIL",
            self.fonts["micro"],
            DARK,
            (1130, 669)
        )

        # ========================================================
        # ANIMACIONES DE INGREDIENTES
        # ========================================================
        for ingredient in self.ingredients:
            ingredient.draw(
                self.screen,
                self.fonts["icon"]
            )

        # ========================================================
        # BARRA DE PROGRESO INFERIOR
        # ========================================================
        done = sum(
            1 for item in self.ingredients
            if item.done
        )
        progress = done / len(self.ingredients)

        # Banda de estado
        rr(
            self.screen,
            pygame.Rect(70, 775, 1395, 58),
            DARK,
            20
        )

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
            (260, 788)
        )

        bar = pygame.Rect(330, 792, 780, 22)
        rr(
            self.screen,
            bar,
            (73, 88, 98),
            11
        )

        if progress > 0:
            fill = pygame.Rect(
                bar.x,
                bar.y,
                max(10, int(bar.width * progress)),
                bar.height
            )
            rr(
                self.screen,
                fill,
                ORANGE,
                11
            )

        # Marcadores de etapas
        steps = [
            ("01", "PREPARAR"),
            ("02", "VALIDAR"),
            ("03", "TRANSFORMAR"),
            ("04", "COCINAR"),
        ]

        sx = 1170
        for i, (num, label) in enumerate(steps):
            active = i <= done
            c = ORANGE if active else (102, 115, 123)

            pygame.draw.circle(
                self.screen,
                c,
                (sx + i * 68, 804),
                9
            )

            text(
                self.screen,
                num,
                self.fonts["micro"],
                WHITE,
                (sx + i * 68, 804),
                True
            )

        text(
            self.screen,
            "Los ingredientes se integran automáticamente.",
            self.fonts["micro"],
            (184, 199, 205),
            (330, 818)
        )

    # ============================================================
    # TRANSFORMACION
    # ============================================================

    def draw_transform(self):
        """Pantalla de transformación: pipeline visual tipo dashboard enterprise."""
        self.draw_background()
        self.draw_header()

        progress = min(1.0, self.scene_time / 3.0)
        pulse = (math.sin(self.t * 4.0) + 1.0) * 0.5

<<<<<<< HEAD
        text(
            self.screen,
            "LA RECETA ESTÁ FUNCIONANDO...",
            self.fonts["title"],
            DARK,
            (768, 285),
            True
        )

        text(
            self.screen,
            "Los datos sucios se están limpiando, organizando y convirtiendo en información confiable.",
            self.fonts["body"],
            MUTED,
            (768, 340),
            True
        )
=======
        # ============================================================
        # HERO / TITULO
        # ============================================================
        rr(self.screen, pygame.Rect(78, 158, 205, 30), LIGHT_ORANGE, 15)
        text(self.screen, "04  /  TRANSFORMACION", self.fonts["micro"], DARK_ORANGE,
             (180, 173), True)

        title_a = "TRANSFORMANDO"
        title_b = "DATOS..."
        f = self.fonts["title"]
        wa = f.size(title_a)[0]
        wb = f.size(title_b)[0]
        x0 = (WIDTH - wa - wb - 18) // 2
        text(self.screen, title_a, f, DARK, (x0, 166))
        text(self.screen, title_b, f, ORANGE, (x0 + wa + 18, 166))
>>>>>>> 5eb0eb3 (Actualizacion del juego)

        text(self.screen,
             "Los ingredientes se convierten en información lista para decidir.",
             self.fonts["body"], MUTED, (WIDTH // 2, 228), True)

        pygame.draw.line(self.screen, ORANGE, (708, 258), (828, 258), 3)
        pygame.draw.circle(self.screen, ORANGE, (694, 258), 4)
        pygame.draw.circle(self.screen, ORANGE, (842, 258), 4)

        # ============================================================
        # PANEL PRINCIPAL
        # ============================================================
        panel = pygame.Rect(78, 292, 1380, 365)
        self.draw_shadow(panel, 28, (0, 8), 22)
        rr(self.screen, panel, WHITE, 28, 2, (228, 220, 210))

        # Cabecera compacta
        rr(self.screen, pygame.Rect(panel.x, panel.y, panel.width, 64), DARK, 28)
        pygame.draw.rect(self.screen, DARK,
                         (panel.x, panel.y + 32, panel.width, 32))
        text(self.screen, "PIPELINE DE TRANSFORMACION", self.fonts["small"], WHITE,
             (panel.x + 28, panel.y + 19))
        text(self.screen, "ETL  /  PROCESAMIENTO EN TIEMPO REAL", self.fonts["micro"],
             (190, 205, 212), (panel.x + 280, panel.y + 23))

        status = pygame.Rect(panel.right - 176, panel.y + 16, 146, 32)
        rr(self.screen, status, (55, 76, 87), 16)
        pygame.draw.circle(self.screen, GREEN, (status.x + 21, status.centery), 5)
        text(self.screen, "EN MARCHA", self.fonts["micro"], WHITE,
             (status.x + 34, status.y + 8))

        # ============================================================
        # COLUMNAS: INPUT -> TRANSFORMACION -> OUTPUT
        # ============================================================
        content_y = panel.y + 92

        # ----- INPUT -----
        input_box = pygame.Rect(112, content_y, 320, 220)
        rr(self.screen, input_box, (250, 249, 246), 22, 1, (232, 225, 216))
        text(self.screen, "01", self.fonts["micro"], ORANGE, (136, content_y + 20))
        text(self.screen, "INGREDIENTES", self.fonts["subtitle"], DARK,
             (170, content_y + 14))
        text(self.screen, "Fuentes preparadas", self.fonts["micro"], MUTED,
             (170, content_y + 48))

        ingredients = [
            ("DB", "BASE DE DATOS", BLUE),
            ("✓", "DATOS LIMPIOS", GREEN),
            ("▦", "DATOS VALIDADOS", ORANGE),
        ]
        for i, (icon, label, color) in enumerate(ingredients):
            y = content_y + 82 + i * 42
            pygame.draw.circle(self.screen, (244, 241, 235), (143, y + 15), 15)
            text(self.screen, icon, self.fonts["micro"], color, (143, y + 15), True)
            text(self.screen, label, self.fonts["micro"], DARK, (170, y + 7))
            pygame.draw.circle(self.screen, color, (399, y + 15), 5)

        # ----- CENTRO: MOTOR -----
        cx, cy = 768, content_y + 111

        # Separadores de columna
        line(self.screen, (235, 229, 220), (466, content_y + 12), (466, content_y + 230), 1)
        line(self.screen, (235, 229, 220), (1070, content_y + 12), (1070, content_y + 230), 1)

        text(self.screen, "02", self.fonts["micro"], BLUE, (cx - 28, content_y + 8))
        text(self.screen, "MOTOR DE DATOS", self.fonts["small"], DARK,
             (cx + 2, content_y + 5), True)

        # Anillo base y halo
        pygame.draw.circle(self.screen, (247, 244, 238), (cx, cy), 93)
        pygame.draw.circle(self.screen, (232, 225, 216), (cx, cy), 93, 2)
        pygame.draw.circle(self.screen, (250, 248, 244), (cx, cy), 74)

        # Arcos de actividad
        arc = pygame.Rect(cx - 82, cy - 82, 164, 164)
        pygame.draw.arc(self.screen, (226, 232, 238), arc, 0, math.tau, 7)
        if progress > 0:
            pygame.draw.arc(self.screen, ORANGE, arc, math.radians(225),
                            math.radians(225) + math.tau * progress, 8)
            arc2 = pygame.Rect(cx - 67, cy - 67, 134, 134)
            pygame.draw.arc(self.screen, BLUE, arc2, math.radians(35),
                            math.radians(35) + math.tau * min(1, progress * 0.9), 4)

        # Nodo central con barras de datos animadas
        bar_heights = (22, 34, 49, 31, 40)
        for i, h in enumerate(bar_heights):
            x = cx - 48 + i * 24
            animated = int(h * (0.78 + 0.22 * math.sin(self.t * 5 + i)))
            pygame.draw.rect(self.screen, DARK, (x, cy + 12 - animated, 12, animated), border_radius=4)

        text(self.screen, f"{int(progress * 100)}%", self.fonts["subtitle"], DARK,
             (cx, cy + 47), True)
        text(self.screen, "TRANSFORMANDO", self.fonts["micro"], ORANGE,
             (cx, cy + 76), True)

        # Punto de actividad girando
        angle = math.radians(225) + math.tau * progress + self.t * 0.35
        mx = int(cx + math.cos(angle) * 93)
        my = int(cy + math.sin(angle) * 93)
        pygame.draw.circle(self.screen, WHITE, (mx, my), 9)
        pygame.draw.circle(self.screen, ORANGE, (mx, my), 6)

        # Flujo visual izquierda -> centro -> derecha
        for i in range(5):
            phase = (self.t * 0.7 + i / 5.0) % 1.0
            px = 435 + phase * 260
            py = cy + math.sin(phase * math.pi) * (12 + i * 2)
            alpha = int(90 + 120 * (1 - phase))
            dot = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*ORANGE, alpha), (8, 8), 4)
            self.screen.blit(dot, (int(px - 8), int(py - 8)))

            px2 = 1015 + phase * 80
            py2 = cy + math.sin(phase * math.pi) * (10 + i * 2)
            dot2 = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(dot2, (*BLUE, alpha), (8, 8), 4)
            self.screen.blit(dot2, (int(px2 - 8), int(py2 - 8)))

        # ----- OUTPUT -----
        output_box = pygame.Rect(1100, content_y, 320, 220)
        rr(self.screen, output_box, (248, 250, 252), 22, 1, (220, 229, 237))
        text(self.screen, "03", self.fonts["micro"], GREEN, (1124, content_y + 20))
        text(self.screen, "RESULTADO", self.fonts["subtitle"], DARK,
             (1158, content_y + 14))
        text(self.screen, "Información útil", self.fonts["micro"], MUTED,
             (1158, content_y + 48))

        kpis = [("CALIDAD", "98%", GREEN), ("ESTRUCTURA", "OK", BLUE), ("INSIGHTS", "LISTOS", ORANGE)]
        for i, (label, value, color) in enumerate(kpis):
            y = content_y + 84 + i * 42
            pygame.draw.circle(self.screen, color, (1131, y + 15), 6)
            text(self.screen, label, self.fonts["micro"], MUTED, (1150, y + 7))
            text(self.screen, value, self.fonts["micro"], DARK, (1370, y + 7))

        # ============================================================
        # BARRA DE ESTADO INFERIOR
        # ============================================================
        progress_box = pygame.Rect(210, 688, 1116, 92)
        self.draw_shadow(progress_box, 22, (0, 5), 15)
        rr(self.screen, progress_box, DARK, 22)

        text(self.screen, "COCINANDO INSIGHTS", self.fonts["small"], WHITE,
             (242, 705))
        text(self.screen, "Transformando datos en decisiones.", self.fonts["micro"],
             (183, 198, 205), (242, 737))

        bar = pygame.Rect(610, 710, 545, 15)
        rr(self.screen, bar, (73, 88, 98), 8)
        if progress > 0:
            rr(self.screen, pygame.Rect(bar.x, bar.y, max(8, int(bar.width * progress)), bar.height),
               ORANGE, 8)

        text(self.screen, f"{int(progress * 100)}%", self.fonts["body_bold"], ORANGE,
             (1190, 700))

        steps = [("01", "PREPARAR"), ("02", "VALIDAR"), ("03", "TRANSFORMAR"), ("04", "COCINAR")]
        sx = 625
        gap = 158
        for i, (num, label) in enumerate(steps):
            x = sx + i * gap
            active = progress >= (i + 1) / 4
            c = ORANGE if active else (93, 108, 118)
            pygame.draw.circle(self.screen, c, (x, 755), 8)
            text(self.screen, num, self.fonts["micro"], WHITE, (x, 755), True)
            text(self.screen, label, self.fonts["micro"], (183, 198, 205), (x, 766), True)
            if i < 3:
                line(self.screen, (93, 108, 118), (x + 11, 755), (x + gap - 11, 755), 2)

        # Flash final muy sutil
        if self.scene_time > 2.3:
            flash_alpha = int(min(70, (self.scene_time - 2.3) * 100))
            layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            layer.fill((255, 255, 255, flash_alpha))
            self.screen.blit(layer, (0, 0))

    # ============================================================
    # PANEL FINAL
    # ============================================================

    def draw_final(self):
        self.draw_background()
        self.draw_header()

        text(
            self.screen,
            "¡RECETA TERMINADA!",
            self.fonts["title"],
            ORANGE,
            (768, 165),
            True
        )

        text(
            self.screen,
            "TU PANEL ESTÁ LISTO",
            self.fonts["subtitle"],
            DARK,
            (768, 225),
            True
        )

        panel_box = pygame.Rect(
            210,
            280,
            930,
            490
        )

        self.draw_shadow(
            panel_box,
            32,
            (0, 8),
            25
        )

        rr(
            self.screen,
            panel_box,
            WHITE,
            32,
            3,
            LIGHT_BLUE
        )

        reveal = min(
            1,
            self.panel_reveal
        )

        if self.panel:
            panel_rect = self.panel.get_rect(
                center=panel_box.center
            )

            if (
                panel_rect.width > panel_box.width - 40
                or
                panel_rect.height > panel_box.height - 40
            ):
                iw, ih = self.panel.get_size()

                scale = min(
                    (panel_box.width - 40) / iw,
                    (panel_box.height - 40) / ih
                )

                scaled = pygame.transform.smoothscale(
                    self.panel,
                    (
                        int(iw * scale),
                        int(ih * scale)
                    )
                )

                panel_rect = scaled.get_rect(
                    center=panel_box.center
                )

                clip = pygame.Rect(
                    panel_rect.x,
                    panel_rect.y,
                    int(panel_rect.width * reveal),
                    panel_rect.height
                )

                old_clip = self.screen.get_clip()

                self.screen.set_clip(clip)
                self.screen.blit(
                    scaled,
                    panel_rect
                )
                self.screen.set_clip(old_clip)

            else:
                clip = pygame.Rect(
                    panel_rect.x,
                    panel_rect.y,
                    int(panel_rect.width * reveal),
                    panel_rect.height
                )

                old_clip = self.screen.get_clip()

                self.screen.set_clip(clip)
                self.screen.blit(
                    self.panel,
                    panel_rect
                )
                self.screen.set_clip(old_clip)

        else:
            self.draw_demo_dashboard(
                panel_box,
                reveal
            )

        self.draw_chef_proud()

        rr(
            self.screen,
            pygame.Rect(250, 790, 800, 55),
            LIGHT_ORANGE,
            20,
            2,
            (249, 210, 171)
        )

        text(
            self.screen,
            "“Datos de calidad → Información confiable → Mejores decisiones.”",
            self.fonts["body_bold"],
            DARK_ORANGE,
            (650, 817),
            True
        )

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
                            1015,
                            650,
                            300,
                            52
                        )

                        if button.collidepoint(logical):
<<<<<<< HEAD
                            print("[DATA CHEF] EMPEZAR -> PANEL SUCIO")
                            self.set_scene("dirty_panel")

                    elif self.scene == "dirty_panel":
                        button = pygame.Rect(585, 800, 366, 52)
                        if button.collidepoint(logical):
                            print("[DATA CHEF] DATOS SUCIOS -> COCINANDO")
=======
                            print(
                                "[DATA CHEF] "
                                "EMPEZAR -> COCINANDO"
                            )

>>>>>>> 5eb0eb3 (Actualizacion del juego)
                            self.set_scene("cooking")

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, dt):
        self.t += dt
        self.scene_time += dt

        if self.scene == "dirty_panel":
            self.dirty_reveal = min(1, self.dirty_reveal + dt * 1.5)

        elif self.scene == "cooking":

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

            self.panel_reveal = min(
                1,
                self.panel_reveal + dt * 0.75
            )

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

        # Adaptar pantalla lógica a ventana.
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
