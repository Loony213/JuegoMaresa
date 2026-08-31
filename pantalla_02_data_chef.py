import os
import sys
import math
import random
import pygame

pygame.init()

# ============================================================
# DATA CHEF MARESA
# PANTALLA 02 - BRIEFING DE MISIÓN
# Rediseño V3
# ============================================================

WIDTH, HEIGHT = 1536, 864
FPS = 60

# ------------------------------------------------------------
# PALETA
# ------------------------------------------------------------
BG = (249, 246, 240)
WHITE = (255, 255, 255)
CREAM = (255, 249, 239)

DARK = (37, 47, 58)
DARK_2 = (72, 82, 91)
MUTED = (126, 134, 142)
LIGHT_LINE = (229, 224, 216)

ORANGE = (247, 116, 18)
ORANGE_DARK = (218, 83, 8)
ORANGE_SOFT = (255, 234, 211)

BLUE = (39, 108, 213)
BLUE_SOFT = (234, 243, 255)

GREEN = (67, 171, 112)

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")


# ============================================================
# HELPERS
# ============================================================

def load_img(name, max_size=None):
    path = os.path.join(ASSETS, name)

    if not os.path.exists(path):
        print("[DATA CHEF] No existe:", path)
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
                        max(1, int(h * scale)),
                    ),
                )

        return img

    except Exception as exc:
        print("[DATA CHEF] Error:", exc)
        return None


def rr(surface, rect, color, radius=20, border=0, border_color=None):
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


def txt(surface, value, font, color, pos, center=False):
    rendered = font.render(value, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(rendered, rect)
    return rect


def line_text(surface, value, font, color, x, y):
    txt(surface, value, font, color, (x, y))


def wrap_text(surface, text, font, color, rect, line_gap=4):
    """Dibuja texto dentro de un rect sin salirse horizontalmente."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= rect.width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    y = rect.y
    for line in lines:
        if y + font.get_height() > rect.bottom:
            break
        txt(surface, line, font, color, (rect.x, y))
        y += font.get_height() + line_gap

    return y


# ============================================================
# PARTICULAS
# ============================================================

class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.speed = random.uniform(0.10, 0.30)
        self.r = random.choice([1, 1, 1, 2])
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, t):
        self.y -= self.speed
        self.x += math.sin(t + self.phase) * 0.025

        if self.y < -8:
            self.y = HEIGHT + 8
            self.x = random.uniform(0, WIDTH)

    def draw(self, surface):
        layer = pygame.Surface((8, 8), pygame.SRCALPHA)

        pygame.draw.circle(
            layer,
            (*ORANGE, 48),
            (4, 4),
            self.r,
        )

        surface.blit(
            layer,
            (
                int(self.x) - 4,
                int(self.y) - 4,
            ),
        )


# ============================================================
# APP
# ============================================================

class App:
    def __init__(self):
        self.window = pygame.display.set_mode(
            (0, 0),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption(
            "DATA CHEF | MARESA - Misión"
        )

        self.screen = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        self.clock = pygame.time.Clock()

        self.scale = 1.0
        self.ox = 0
        self.oy = 0

        self.running = True
        self.t = 0.0

        # ----------------------------------------------------
        # ROL
        # ----------------------------------------------------
        raw_role = (
            sys.argv[1].lower()
            if len(sys.argv) > 1
            else "tecnologia"
        )

        self.role = (
            "rrhh"
            if raw_role in (
                "rrhh",
                "recursos humanos",
                "recursos_humanos",
            )
            else "tecnologia"
        )

        if self.role == "tecnologia":
            self.role_name = "TECNOLOGÍA"
            self.role_color = BLUE
            self.role_soft = BLUE_SOFT
            self.role_img_name = "tecnologia.png"

            self.quote = (
                "Quiero crear un panel específico"
            )

            self.detail = (
                "para organizar, visualizar y convertir "
                "datos tecnológicos en información útil."
            )

        else:
            self.role_name = "RECURSOS HUMANOS"
            self.role_color = ORANGE
            self.role_soft = ORANGE_SOFT
            self.role_img_name = "rrhh.png"

            self.quote = (
                "Quiero crear un panel específico"
            )

            self.detail = (
                "para organizar, visualizar y convertir "
                "datos de talento en información útil."
            )

        # ----------------------------------------------------
        # ASSETS
        # ----------------------------------------------------
        self.logo = load_img(
            "logo_maresa.png",
            (205, 58),
        )

        self.chef = load_img(
            "chef.png",
            (430, 570),
        )

        self.person = load_img(
            self.role_img_name,
            (410, 370),
        )

        self.parts = [
            Particle()
            for _ in range(40)
        ]

        # ----------------------------------------------------
        # FONTS
        # ----------------------------------------------------
        self.fonts = {
            "xs": pygame.font.SysFont(
                "Segoe UI",
                11,
            ),
            "xs_bold": pygame.font.SysFont(
                "Segoe UI",
                11,
                bold=True,
            ),
            "small": pygame.font.SysFont(
                "Segoe UI",
                14,
            ),
            "small_bold": pygame.font.SysFont(
                "Segoe UI",
                14,
                bold=True,
            ),
            "body": pygame.font.SysFont(
                "Segoe UI",
                17,
            ),
            "body_bold": pygame.font.SysFont(
                "Segoe UI",
                17,
                bold=True,
            ),
            "title": pygame.font.SysFont(
                "Segoe UI",
                49,
                bold=True,
            ),
            "hero": pygame.font.SysFont(
                "Segoe UI",
                70,
                bold=True,
            ),
            "section": pygame.font.SysFont(
                "Segoe UI",
                21,
                bold=True,
            ),
            "button": pygame.font.SysFont(
                "Segoe UI",
                19,
                bold=True,
            ),
        }

        self.button_hover = False

        print("[DATA CHEF] Rol:", self.role_name)
        print(
            "[DATA CHEF] Chef:",
            "OK" if self.chef else "FALTA assets/chef.png",
        )
        print(
            "[DATA CHEF] Personaje:",
            "OK"
            if self.person
            else "FALTA assets/" + self.role_img_name,
        )

    # ========================================================
    # BACKGROUND
    # ========================================================

    def background(self):
        self.screen.fill(BG)

        # Formas grandes, limpias.
        pygame.draw.circle(
            self.screen,
            (255, 232, 208),
            (1460, 52),
            205,
        )

        pygame.draw.circle(
            self.screen,
            (255, 237, 220),
            (-75, 820),
            245,
        )

        # Línea horizontal decorativa.
        pygame.draw.line(
            self.screen,
            (242, 235, 225),
            (40, 142),
            (1496, 142),
            1,
        )

        # Grid muy suave.
        for x in range(75, WIDTH, 120):
            pygame.draw.line(
                self.screen,
                (245, 240, 233),
                (x, 160),
                (x, 745),
                1,
            )

        # Partículas.
        for particle in self.parts:
            particle.draw(self.screen)

        # Nodos decorativos.
        nodes = [
            (280, 177),
            (530, 225),
            (1115, 182),
            (1450, 355),
            (88, 680),
        ]

        for x, y in nodes:
            pygame.draw.circle(
                self.screen,
                (249, 211, 174),
                (x, y),
                3,
            )

    # ========================================================
    # HEADER
    # ========================================================

    def header(self):
        bar = pygame.Rect(
            36,
            25,
            WIDTH - 72,
            61,
        )

        rr(
            self.screen,
            bar,
            WHITE,
            18,
            1,
            LIGHT_LINE,
        )

        if self.logo:
            self.screen.blit(
                self.logo,
                (55, 31),
            )

        pygame.draw.line(
            self.screen,
            LIGHT_LINE,
            (235, 39),
            (235, 72),
            1,
        )

        txt(
            self.screen,
            "DATA",
            self.fonts["section"],
            DARK,
            (262, 43),
        )

        txt(
            self.screen,
            "CHEF",
            self.fonts["section"],
            ORANGE,
            (334, 43),
        )

        # Progreso
        txt(
            self.screen,
            "TU EXPERIENCIA",
            self.fonts["xs_bold"],
            MUTED,
            (1120, 42),
        )

        # 01
        pygame.draw.circle(
            self.screen,
            ORANGE,
            (1265, 55),
            14,
        )

        txt(
            self.screen,
            "01",
            self.fonts["xs_bold"],
            WHITE,
            (1265, 55),
            center=True,
        )

        pygame.draw.line(
            self.screen,
            LIGHT_LINE,
            (1281, 55),
            (1310, 55),
            2,
        )

        # 02
        pygame.draw.circle(
            self.screen,
            (238, 234, 228),
            (1327, 55),
            14,
        )

        txt(
            self.screen,
            "02",
            self.fonts["xs_bold"],
            MUTED,
            (1327, 55),
            center=True,
        )

        txt(
            self.screen,
            self.role_name,
            self.fonts["xs_bold"],
            self.role_color,
            (1352, 49),
        )

    # ========================================================
    # TITLE / HERO
    # ========================================================

    def title(self):
        # Etiqueta
        badge = pygame.Rect(
            67,
            160,
            250,
            30,
        )

        rr(
            self.screen,
            badge,
            (255, 248, 238),
            15,
            1,
            (247, 213, 178),
        )

        pygame.draw.circle(
            self.screen,
            ORANGE,
            (86, 175),
            4,
        )

        txt(
            self.screen,
            "BRIEFING DE TU RECETA",
            self.fonts["xs_bold"],
            ORANGE_DARK,
            (99, 169),
        )

        txt(
            self.screen,
            "¡BIENVENIDO!",
            self.fonts["title"],
            DARK,
            (67, 205),
        )

        data = txt(
            self.screen,
            "DATA",
            self.fonts["hero"],
            DARK,
            (65, 260),
        )

        txt(
            self.screen,
            "CHEF",
            self.fonts["hero"],
            ORANGE,
            (65 + data.width + 13, 260),
        )

        txt(
            self.screen,
            "Tu cocina, tus datos, mejores decisiones.",
            self.fonts["body_bold"],
            ORANGE_DARK,
            (70, 340),
        )

        # Subrayado visual
        pygame.draw.line(
            self.screen,
            ORANGE,
            (70, 366),
            (380, 366),
            3,
        )

    # ========================================================
    # LEFT MISSION
    # ========================================================

    def mission_panel(self):
        panel = pygame.Rect(
            67,
            405,
            410,
            292,
        )

        rr(
            self.screen,
            panel,
            WHITE,
            24,
            1,
            LIGHT_LINE,
        )

        # Barra de acento
        pygame.draw.rect(
            self.screen,
            ORANGE,
            (
                panel.x,
                panel.y,
                5,
                panel.h,
            ),
            border_radius=3,
        )

        txt(
            self.screen,
            "TU MISIÓN",
            self.fonts["section"],
            DARK,
            (93, 430),
        )

        txt(
            self.screen,
            "El objetivo de esta cocina es",
            self.fonts["small"],
            MUTED,
            (93, 466),
        )

        txt(
            self.screen,
            "convertir datos en valor.",
            self.fonts["body_bold"],
            DARK,
            (93, 489),
        )

        # Separador
        pygame.draw.line(
            self.screen,
            LIGHT_LINE,
            (93, 526),
            (450, 526),
            1,
        )

        # Tres ingredientes de la misión
        ingredients = [
            ("01", "DATOS", "Selecciona información confiable."),
            ("02", "CALIDAD", "Prepara y valida los ingredientes."),
            ("03", "VALOR", "Genera información accionable."),
        ]

        y = 548

        for number, title, description in ingredients:
            pygame.draw.circle(
                self.screen,
                ORANGE_SOFT,
                (110, y + 9),
                17,
            )

            txt(
                self.screen,
                number,
                self.fonts["xs_bold"],
                ORANGE_DARK,
                (110, y + 9),
                center=True,
            )

            txt(
                self.screen,
                title,
                self.fonts["small_bold"],
                DARK,
                (138, y),
            )

            txt(
                self.screen,
                description,
                self.fonts["xs"],
                MUTED,
                (138, y + 19),
            )

            y += 43

    # ========================================================
    # CHEF CENTRAL
    # ========================================================

    def chef_stage(self):
        # Área visual central.
        stage = pygame.Rect(
            465,
            390,
            430,
            310,
        )

        # Fondo suave
        rr(
            self.screen,
            stage,
            (255, 249, 240),
            30,
            1,
            (245, 225, 205),
        )

        # Círculo trasero
        pygame.draw.circle(
            self.screen,
            (255, 232, 207),
            (680, 520),
            145,
        )

        # Anillos
        pygame.draw.circle(
            self.screen,
            (255, 222, 187),
            (680, 520),
            125,
            2,
        )

        pygame.draw.circle(
            self.screen,
            (255, 238, 219),
            (680, 520),
            105,
            1,
        )

        # Sombra
        pygame.draw.ellipse(
            self.screen,
            (226, 219, 208),
            (545, 665, 270, 25),
        )

        if self.chef:
            bob = math.sin(
                self.t * 2.1
            ) * 3

            r = self.chef.get_rect()

            r.midbottom = (
                680,
                int(683 + bob),
            )

            self.screen.blit(
                self.chef,
                r,
            )

        # Pequeño mensaje junto al chef
        bubble = pygame.Rect(
            490,
            405,
            150,
            52,
        )

        rr(
            self.screen,
            bubble,
            WHITE,
            17,
            1,
            LIGHT_LINE,
        )

        txt(
            self.screen,
            "¡MANOS A LA OBRA!",
            self.fonts["xs_bold"],
            ORANGE_DARK,
            bubble.center,
            center=True,
        )

        # Flecha hacia personaje
        pygame.draw.line(
            self.screen,
            ORANGE,
            (640, 432),
            (615, 455),
            2,
        )

    # ========================================================
    # ROLE PANEL
    # ========================================================

    def role_panel(self):
        panel = pygame.Rect(
            910,
            160,
            555,
            537,
        )

        rr(
            self.screen,
            panel,
            WHITE,
            28,
            2,
            self.role_color,
        )

        # ----------------------------------------------------
        # CABECERA
        # ----------------------------------------------------
        header = pygame.Rect(
            912,
            162,
            551,
            102,
        )

        rr(
            self.screen,
            header,
            self.role_soft,
            26,
        )

        pill = pygame.Rect(
            938,
            185,
            82,
            32,
        )

        rr(
            self.screen,
            pill,
            WHITE,
            16,
        )

        txt(
            self.screen,
            "PASO 01",
            self.fonts["xs_bold"],
            self.role_color,
            pill.center,
            center=True,
        )

        txt(
            self.screen,
            "ESTÁS EN LA COCINA",
            self.fonts["xs_bold"],
            MUTED,
            (1040, 181),
        )

        txt(
            self.screen,
            self.role_name,
            self.fonts["section"],
            self.role_color,
            (1040, 201),
        )

        # ----------------------------------------------------
        # CONTENIDO DIVIDIDO EN DOS COLUMNAS
        # Evita que cualquier texto invada al personaje.
        # ----------------------------------------------------
        text_x = 945
        text_w = 190

        # Etiqueta
        txt(
            self.screen,
            "¿QUÉ VAMOS A COCINAR?",
            self.fonts["xs_bold"],
            MUTED,
            (text_x, 296),
        )

        # Pregunta / objetivo
        wrap_text(
            self.screen,
            self.quote,
            self.fonts["body_bold"],
            DARK,
            pygame.Rect(
                text_x,
                326,
                text_w,
                70,
            ),
            line_gap=3,
        )

        # Área seleccionada
        role_badge = pygame.Rect(
            text_x,
            395,
            190,
            34,
        )

        rr(
            self.screen,
            role_badge,
            self.role_soft,
            12,
        )

        txt(
            self.screen,
            self.role_name,
            self.fonts["small_bold"],
            self.role_color,
            role_badge.center,
            center=True,
        )

        # Reto
        txt(
            self.screen,
            "TU RETO",
            self.fonts["xs_bold"],
            MUTED,
            (text_x, 450),
        )

        wrap_text(
            self.screen,
            self.detail,
            self.fonts["small"],
            DARK_2,
            pygame.Rect(
                text_x,
                475,
                text_w,
                72,
            ),
            line_gap=4,
        )

        # ----------------------------------------------------
        # ZONA EXCLUSIVA DEL PERSONAJE
        # ----------------------------------------------------
        character_area = pygame.Rect(
            1150,
            286,
            285,
            268,
        )

        rr(
            self.screen,
            character_area,
            (250, 248, 244),
            22,
            1,
            LIGHT_LINE,
        )

        # Decoración superior
        pygame.draw.circle(
            self.screen,
            self.role_soft,
            (1181, 318),
            22,
        )

        txt(
            self.screen,
            "TU ÁREA",
            self.fonts["xs_bold"],
            self.role_color,
            (1166, 311),
        )

        # Personaje centrado en su columna.
        if self.person:
            bob = math.sin(self.t * 2.0) * 3

            r = self.person.get_rect()

            # Nunca invade la columna de texto.
            max_w = character_area.width - 20
            max_h = character_area.height - 48

            img = self.person

            if img.get_width() > max_w or img.get_height() > max_h:
                scale = min(
                    max_w / img.get_width(),
                    max_h / img.get_height(),
                )
                img = pygame.transform.smoothscale(
                    img,
                    (
                        max(1, int(img.get_width() * scale)),
                        max(1, int(img.get_height() * scale)),
                    ),
                )

            r = img.get_rect()
            r.midbottom = (
                character_area.centerx,
                int(character_area.bottom - 7 + bob),
            )

            self.screen.blit(img, r)

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------
        status = pygame.Rect(
            945,
            570,
            470,
            54,
        )

        rr(
            self.screen,
            status,
            (249, 247, 243),
            17,
            1,
            LIGHT_LINE,
        )

        pygame.draw.circle(
            self.screen,
            GREEN,
            (970, 597),
            6,
        )

        txt(
            self.screen,
            "RECETA PREPARADA",
            self.fonts["small_bold"],
            DARK,
            (989, 584),
        )

        txt(
            self.screen,
            "Datos listos para comenzar.",
            self.fonts["xs"],
            MUTED,
            (989, 603),
        )

        # ----------------------------------------------------
        # OBJETIVO
        # ----------------------------------------------------
        pygame.draw.rect(
            self.screen,
            self.role_color,
            (
                945,
                645,
                470,
                4,
            ),
            border_radius=2,
        )

        txt(
            self.screen,
            "OBJETIVO",
            self.fonts["xs_bold"],
            self.role_color,
            (945, 660),
        )

        txt(
            self.screen,
            "Construir información clara, confiable y útil.",
            self.fonts["small"],
            DARK,
            (945, 679),
        )

    # ========================================================
    # FOOTER / CTA
    # ========================================================

    def footer(self):
        # Barra de progreso
        progress = pygame.Rect(
            67,
            728,
            1398,
            62,
        )

        rr(
            self.screen,
            progress,
            WHITE,
            19,
            1,
            LIGHT_LINE,
        )

        txt(
            self.screen,
            "TU RECETA",
            self.fonts["xs_bold"],
            MUTED,
            (91, 743),
        )

        txt(
            self.screen,
            "01",
            self.fonts["section"],
            ORANGE,
            (91, 762),
        )

        steps = [
            ("SELECCIONA", 220),
            ("PREPARA", 430),
            ("COCINA", 610),
            ("SIRVE", 785),
        ]

        for i, (label, x) in enumerate(steps):
            active = i == 0

            pygame.draw.circle(
                self.screen,
                ORANGE if active else (235, 231, 225),
                (x, 759),
                13,
            )

            if active:
                txt(
                    self.screen,
                    "✓",
                    self.fonts["xs_bold"],
                    WHITE,
                    (x, 759),
                    center=True,
                )

            txt(
                self.screen,
                label,
                self.fonts["xs_bold"],
                DARK if active else MUTED,
                (x + 22, 751),
            )

            if i < 3:
                pygame.draw.line(
                    self.screen,
                    LIGHT_LINE,
                    (x + 95, 759),
                    (x + 155, 759),
                    1,
                )

        # CTA
        r = pygame.Rect(
            1128,
            738,
            305,
            42,
        )

        pos = self.logical(
            pygame.mouse.get_pos()
        )

        self.button_hover = r.collidepoint(pos)

        b = r.move(
            0,
            -2 if self.button_hover else 0,
        )

        # Sombra
        pygame.draw.rect(
            self.screen,
            (229, 211, 193),
            (
                b.x,
                b.y + 5,
                b.w,
                b.h,
            ),
            border_radius=15,
        )

        rr(
            self.screen,
            b,
            ORANGE_DARK if self.button_hover else ORANGE,
            15,
        )

        txt(
            self.screen,
            "CONTINUAR CON LA RECETA",
            self.fonts["button"],
            WHITE,
            (b.centerx - 13, b.centery),
            center=True,
        )

        pygame.draw.polygon(
            self.screen,
            WHITE,
            [
                (b.right - 34, b.centery - 7),
                (b.right - 22, b.centery),
                (b.right - 34, b.centery + 7),
            ],
        )

        # Atajo
        txt(
            self.screen,
            "ESC  SALIR",
            self.fonts["xs"],
            MUTED,
            (35, HEIGHT - 18),
        )

    # ========================================================
    # COORDINATES
    # ========================================================

    def logical(self, pos):
        if self.scale <= 0:
            return pos

        return (
            int(
                (pos[0] - self.ox)
                / self.scale
            ),
            int(
                (pos[1] - self.oy)
                / self.scale
            ),
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):
        self.background()
        self.header()
        self.title()
        self.mission_panel()
        self.chef_stage()
        self.role_panel()
        self.footer()

        ww, wh = self.window.get_size()

        self.scale = min(
            ww / WIDTH,
            wh / HEIGHT,
        )

        rw = max(
            1,
            int(WIDTH * self.scale),
        )

        rh = max(
            1,
            int(HEIGHT * self.scale),
        )

        self.ox = (ww - rw) // 2
        self.oy = (wh - rh) // 2

        scaled = pygame.transform.smoothscale(
            self.screen,
            (rw, rh),
        )

        self.window.fill(
            (232, 229, 224)
        )

        self.window.blit(
            scaled,
            (self.ox, self.oy),
        )

        pygame.display.flip()

    # ========================================================
    # RUN
    # ========================================================

    def run(self):
        while self.running:
            dt = (
                self.clock.tick(FPS)
                / 1000.0
            )

            self.t += dt

            for particle in self.parts:
                particle.update(self.t)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode(
                        event.size,
                        pygame.RESIZABLE,
                    )

                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    self.running = False

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    pos = self.logical(event.pos)

                    button = pygame.Rect(
                        1128,
                        738,
                        305,
                        42,
                    )

                    if button.collidepoint(pos):
                        pantalla_03 = os.path.join(
                            os.path.dirname(
                                os.path.abspath(__file__)
                            ),
                            "pantalla_03_mercado.py",
                        )

                        print(
                            "[DATA CHEF] CONTINUAR -> MERCADO"
                        )

                        if os.path.exists(
                            pantalla_03
                        ):
                            import subprocess

                            subprocess.Popen(
                                [
                                    sys.executable,
                                    pantalla_03,
                                ],
                                cwd=os.path.dirname(
                                    pantalla_03
                                ),
                            )

                            self.running = False

                        else:
                            print(
                                "[DATA CHEF] ERROR: No existe:",
                                pantalla_03,
                            )

            self.draw()

        pygame.quit()


if __name__ == "__main__":
    App().run()
