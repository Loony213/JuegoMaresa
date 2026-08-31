import os
import sys
import math
import random
import pygame

pygame.init()

# ============================================================
# DATA CHEF | MARESA
# PANTALLA 06 - EL CHEF PREPARA EL PANEL
#
# Coloca estas imágenes PNG dentro de assets/
#
#   chef_cocinando.png     -> Chef cocinando
#   chef_orgulloso.png     -> Chef mostrando el resultado
#   olla.png               -> Olla (opcional, el juego dibuja una si falta)
#   panel_final.png        -> Imagen/captura del panel terminado
#   logo_maresa.png        -> Logo (opcional)
#
# Ejecutar:
#   py -3.13 pantalla_06_cocinando.py
# ============================================================

WIDTH, HEIGHT = 1536, 864
FPS = 60

BG = (250, 245, 236)
WHITE = (255, 255, 255)
ORANGE = (247, 116, 18)
DARK_ORANGE = (210, 85, 8)
BLUE = (26, 104, 210)
DARK = (39, 49, 59)
MUTED = (93, 103, 112)
GREEN = (38, 160, 92)
LIGHT_ORANGE = (255, 239, 221)
LIGHT_BLUE = (235, 244, 255)

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

        surface.blit(layer, (int(self.x - radius * 2), int(self.y - radius * 2)))


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
            pygame.Rect(int(pos.x - 52), int(pos.y - 40 + bob), 104, 80),
            WHITE,
            18,
            2,
            LIGHT_ORANGE
        )

        text(surface, self.icon, font, DARK, (int(pos.x), int(pos.y - 4 + bob)), True)


class DataChefScreen:
    def __init__(self):
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("DATA CHEF | MARESA - Preparando el Panel")

        self.screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()

        self.running = True
        self.t = 0

        self.scale = 1
        self.ox = 0
        self.oy = 0

        # -------------------------
        # ESTADOS DE LA ANIMACIÓN
        # -------------------------
        self.scene = "intro"
        self.scene_time = 0
        self.panel_reveal = 0

        # -------------------------
        # IMÁGENES
        # -------------------------
        self.logo = load_img("logo_maresa.png", (260, 90))
        self.chef_cooking = load_img("chef_cocinando.png", (500, 610))
        self.chef_proud = load_img("chef_orgulloso.png", (430, 560))
        self.pot = load_img("olla.png", (340, 260))
        self.panel = load_img("panel_final.png", (760, 470))

        # -------------------------
        # FUENTES
        # -------------------------
        self.fonts = {
            "tiny": pygame.font.SysFont("Arial", 16),
            "small": pygame.font.SysFont("Arial", 19),
            "body": pygame.font.SysFont("Arial", 23),
            "bold": pygame.font.SysFont("Arial", 23, bold=True),
            "subtitle": pygame.font.SysFont("Arial", 30, bold=True),
            "title": pygame.font.SysFont("Arial", 58, bold=True),
            "big": pygame.font.SysFont("Arial", 72, bold=True),
            "button": pygame.font.SysFont("Arial", 25, bold=True),
            "icon": pygame.font.SysFont("Segoe UI Emoji", 42),
            "emoji": pygame.font.SysFont("Segoe UI Emoji", 30),
        }

        self.steam_origin = (1060, 500)
        self.steam = [
            SteamParticle(self.steam_origin[0], self.steam_origin[1])
            for _ in range(22)
        ]

        self.ingredients = [
            FlyingIngredient(250, 660, (1060, 545), "🗄", "Base de datos", 0.2),
            FlyingIngredient(470, 710, (1060, 545), "✦", "Datos limpios", 0.8),
            FlyingIngredient(720, 700, (1060, 545), "✓", "Datos validados", 1.4),
            FlyingIngredient(900, 720, (1060, 545), "▥", "Información", 2.0),
        ]

        self.finished_ingredients = 0
        self.auto_started = False

        print("[DATA CHEF] Pantalla 06 iniciada.")

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

    # ============================================================
    # FONDO
    # ============================================================

    def draw_background(self):
        self.screen.fill(BG)

        pygame.draw.ellipse(
            self.screen,
            (255, 229, 199),
            (1080, -150, 600, 350)
        )

        pygame.draw.ellipse(
            self.screen,
            (255, 235, 215),
            (-180, 680, 650, 280)
        )

        # Azulejos decorativos
        for x in range(40, WIDTH, 120):
            for y in range(160, 500, 110):
                alpha = 22
                tile = pygame.Surface((95, 85), pygame.SRCALPHA)
                rr(tile, pygame.Rect(0, 0, 95, 85), (255, 255, 255, alpha), 15)
                self.screen.blit(tile, (x, y))

        # Partículas
        for i in range(18):
            x = int((i * 131 + self.t * 13) % WIDTH)
            y = int(130 + (i * 71) % 650)
            pygame.draw.circle(self.screen, (247, 116, 18), (x, y), 2)

    def draw_header(self):
        if self.logo:
            self.screen.blit(self.logo, (35, 25))
        else:
            text(
                self.screen,
                "maresa",
                self.fonts["title"],
                ORANGE,
                (35, 25)
            )

        text(
            self.screen,
            "DATA CHEF",
            self.fonts["subtitle"],
            DARK,
            (WIDTH // 2, 52),
            True
        )

        rr(
            self.screen,
            pygame.Rect(575, 78, 386, 40),
            LIGHT_ORANGE,
            20,
            2,
            (249, 210, 171)
        )

        text(
            self.screen,
            "Transformando datos en información",
            self.fonts["small"],
            DARK_ORANGE,
            (768, 98),
            True
        )

    # ============================================================
    # OLLA
    # ============================================================

    def draw_pot(self, x=1060, y=585):
        # Si el usuario sube olla.png
        if self.pot:
            rect = self.pot.get_rect(center=(x, y))
            self.screen.blit(self.pot, rect)
            return

        # Olla creada con pygame si no existe la imagen
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

    def draw_chef_cooking(self):
        x = 400
        y = 705 + math.sin(self.t * 2.3) * 5

        if self.chef_cooking:
            rect = self.chef_cooking.get_rect(midbottom=(x, int(y)))
            self.screen.blit(self.chef_cooking, rect)
        else:
            rr(
                self.screen,
                pygame.Rect(170, 320, 430, 380),
                WHITE,
                28,
                3,
                ORANGE
            )

            text(
                self.screen,
                "SUBE:",
                self.fonts["bold"],
                ORANGE,
                (385, 470),
                True
            )

            text(
                self.screen,
                "assets/chef_cocinando.png",
                self.fonts["small"],
                MUTED,
                (385, 510),
                True
            )

    def draw_chef_proud(self):
        x = 1250
        y = 735 + math.sin(self.t * 2) * 4

        if self.chef_proud:
            rect = self.chef_proud.get_rect(midbottom=(x, int(y)))
            self.screen.blit(self.chef_proud, rect)
        else:
            rr(
                self.screen,
                pygame.Rect(1080, 350, 360, 340),
                WHITE,
                28,
                3,
                ORANGE
            )

            text(
                self.screen,
                "SUBE:",
                self.fonts["bold"],
                ORANGE,
                (1260, 480),
                True
            )

            text(
                self.screen,
                "assets/chef_orgulloso.png",
                self.fonts["small"],
                MUTED,
                (1260, 520),
                True
            )

    # ============================================================
    # INTRO
    # ============================================================

    def draw_intro(self):
        self.draw_background()
        self.draw_header()

        pulse = 1 + math.sin(self.t * 3) * 0.03

        rr(
            self.screen,
            pygame.Rect(300, 235, 936, 390),
            WHITE,
            36,
            3,
            (249, 210, 171)
        )

        text(
            self.screen,
            "¡LA COCINA ESTÁ LISTA!",
            self.fonts["title"],
            DARK,
            (768, 330),
            True
        )

        text(
            self.screen,
            "Ahora vamos a transformar todos los datos preparados",
            self.fonts["body"],
            MUTED,
            (768, 415),
            True
        )

        text(
            self.screen,
            "en la receta final para nuestro panel.",
            self.fonts["body"],
            MUTED,
            (768, 452),
            True
        )

        size = int(105 * pulse)
        pygame.draw.circle(self.screen, LIGHT_ORANGE, (768, 535), size)
        pygame.draw.circle(self.screen, ORANGE, (768, 535), size, 5)

        text(
            self.screen,
            "👨‍🍳",
            self.fonts["big"],
            DARK,
            (768, 530),
            True
        )

        text(
            self.screen,
            "El Chef está listo para cocinar",
            self.fonts["bold"],
            ORANGE,
            (768, 680),
            True
        )

        button = pygame.Rect(600, 755, 336, 58)
        pos = self.logical(pygame.mouse.get_pos())
        hover = button.collidepoint(pos)

        draw_button = button.move(0, -3 if hover else 0)

        rr(self.screen, draw_button, ORANGE, 18)
        text(
            self.screen,
            "🔥  EMPEZAR A COCINAR",
            self.fonts["button"],
            WHITE,
            draw_button.center,
            True
        )

    # ============================================================
    # COCINANDO
    # ============================================================

    def draw_cooking(self):
        self.draw_background()
        self.draw_header()

        # Título
        text(
            self.screen,
            "PREPARANDO TU PANEL...",
            self.fonts["title"],
            DARK,
            (768, 165),
            True
        )

        subtitle = "Cada ingrediente representa datos preparados y confiables."
        text(
            self.screen,
            subtitle,
            self.fonts["body"],
            MUTED,
            (768, 215),
            True
        )

        # Zona del chef
        rr(
            self.screen,
            pygame.Rect(100, 255, 600, 480),
            WHITE,
            30,
            2,
            LIGHT_ORANGE
        )

        self.draw_chef_cooking()

        # Pensamiento
        rr(
            self.screen,
            pygame.Rect(155, 280, 390, 95),
            (255, 249, 239),
            24,
            2,
            (249, 210, 171)
        )

        text(
            self.screen,
            "“Primero mezclaremos los",
            self.fonts["small"],
            DARK,
            (350, 312),
            True
        )

        text(
            self.screen,
            "datos de calidad...”",
            self.fonts["small"],
            DARK,
            (350, 342),
            True
        )

        # Zona olla
        rr(
            self.screen,
            pygame.Rect(760, 270, 610, 465),
            (255, 252, 247),
            30,
            2,
            LIGHT_BLUE
        )

        text(
            self.screen,
            "RECETA DE DATOS",
            self.fonts["subtitle"],
            BLUE,
            (1065, 315),
            True
        )

        self.draw_pot(1060, 590)

        # Vapor
        for particle in self.steam:
            particle.draw(self.screen)

        # Ingredientes
        for ingredient in self.ingredients:
            ingredient.draw(self.screen, self.fonts["icon"])

        # Progreso
        done = sum(1 for item in self.ingredients if item.done)
        progress = done / len(self.ingredients)

        bar = pygame.Rect(400, 770, 736, 22)

        rr(self.screen, bar, (231, 231, 231), 11)

        if progress > 0:
            fill = pygame.Rect(
                bar.x,
                bar.y,
                max(8, int(bar.width * progress)),
                bar.height
            )
            rr(self.screen, fill, ORANGE, 11)

        text(
            self.screen,
            f"COCINANDO INSIGHTS... {int(progress * 100)}%",
            self.fonts["bold"],
            DARK,
            (768, 745),
            True
        )

    # ============================================================
    # TRANSFORMACIÓN
    # ============================================================

    def draw_transform(self):
        self.draw_background()
        self.draw_header()

        alpha = int(
            min(
                255,
                max(0, self.scene_time * 180)
            )
        )

        text(
            self.screen,
            "TRANSFORMANDO DATOS...",
            self.fonts["title"],
            DARK,
            (768, 285),
            True
        )

        text(
            self.screen,
            "Los ingredientes se están convirtiendo en información útil.",
            self.fonts["body"],
            MUTED,
            (768, 340),
            True
        )

        radius = int(80 + math.sin(self.t * 5) * 8)

        for i in range(4):
            r = radius + i * 28 + int(math.sin(self.t * 3 + i) * 8)
            pygame.draw.circle(
                self.screen,
                ORANGE if i % 2 == 0 else BLUE,
                (768, 505),
                r,
                4
            )

        pygame.draw.circle(self.screen, WHITE, (768, 505), 74)
        text(
            self.screen,
            "📊",
            self.fonts["big"],
            DARK,
            (768, 500),
            True
        )

        progress = min(1, self.scene_time / 3.0)

        bar = pygame.Rect(468, 690, 600, 25)
        rr(self.screen, bar, (225, 225, 225), 13)

        fill = pygame.Rect(bar.x, bar.y, int(bar.width * progress), bar.height)
        rr(self.screen, fill, GREEN, 13)

        text(
            self.screen,
            f"{int(progress * 100)}%",
            self.fonts["bold"],
            GREEN,
            (768, 650),
            True
        )

        # Destello final
        if self.scene_time > 2.3:
            flash_alpha = int(min(220, (self.scene_time - 2.3) * 300))
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
            "✨ ¡RECETA TERMINADA! ✨",
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

        # Panel
        panel_box = pygame.Rect(210, 280, 930, 490)

        rr(
            self.screen,
            panel_box,
            WHITE,
            32,
            3,
            LIGHT_BLUE
        )

        reveal = min(1, self.panel_reveal)
        visible_w = int(panel_box.width * reveal)

        if self.panel:
            panel_rect = self.panel.get_rect(
                center=(panel_box.centerx, panel_box.centery)
            )

            if panel_rect.width > panel_box.width - 40 or panel_rect.height > panel_box.height - 40:
                iw, ih = self.panel.get_size()
                scale = min(
                    (panel_box.width - 40) / iw,
                    (panel_box.height - 40) / ih
                )

                scaled = pygame.transform.smoothscale(
                    self.panel,
                    (int(iw * scale), int(ih * scale))
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
                self.screen.blit(scaled, panel_rect)
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
                self.screen.blit(self.panel, panel_rect)
                self.screen.set_clip(old_clip)

        else:
            # Panel de ejemplo si aún no sube panel_final.png
            self.draw_demo_dashboard(panel_box, reveal)

        # Chef orgulloso
        self.draw_chef_proud()

        # Mensaje final
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
            self.fonts["bold"],
            DARK_ORANGE,
            (650, 817),
            True
        )

    def draw_demo_dashboard(self, box, reveal):
        # Dashboard de muestra mientras no exista panel_final.png
        clip = pygame.Rect(
            box.x + 25,
            box.y + 25,
            int((box.width - 50) * reveal),
            box.height - 50
        )

        old_clip = self.screen.get_clip()
        self.screen.set_clip(clip)

        inner = pygame.Rect(box.x + 25, box.y + 25, box.width - 50, box.height - 50)
        rr(self.screen, inner, (248, 250, 252), 18)

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
            card = pygame.Rect(x, inner.y + 85, 230, 105)
            rr(self.screen, card, WHITE, 18, 2, (225, 230, 235))
            text(self.screen, title, self.fonts["small"], MUTED, (card.x + 18, card.y + 18))
            text(self.screen, value, self.fonts["subtitle"], color, (card.x + 18, card.y + 52))
            x += 250

        # Gráfico ficticio
        graph = pygame.Rect(inner.x + 30, inner.y + 225, 530, 190)
        rr(self.screen, graph, WHITE, 18, 2, (225, 230, 235))

        values = [60, 95, 80, 130, 115, 165, 145]
        px = graph.x + 35
        base_y = graph.bottom - 30

        points = []

        for i, value in enumerate(values):
            x = px + i * 70
            y = base_y - value
            points.append((x, y))

        pygame.draw.lines(self.screen, BLUE, False, points, 4)

        for p in points:
            pygame.draw.circle(self.screen, ORANGE, p, 6)

        # Dona simulada
        cx, cy = inner.right - 180, inner.y + 320
        pygame.draw.circle(self.screen, LIGHT_ORANGE, (cx, cy), 75)
        pygame.draw.circle(self.screen, ORANGE, (cx, cy), 50, 16)
        pygame.draw.circle(self.screen, WHITE, (cx, cy), 25)

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
                        button = pygame.Rect(600, 755, 336, 58)

                        if button.collidepoint(logical):
                            print("[DATA CHEF] EMPEZAR -> COCINANDO")
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

            done = sum(1 for ingredient in self.ingredients if ingredient.done)

            for particle in self.steam:
                particle.update(dt, self.steam_origin)

            if done == len(self.ingredients) and self.scene_time > 4:
                print("[DATA CHEF] INGREDIENTES LISTOS -> TRANSFORMACIÓN")
                self.set_scene("transform")

        elif self.scene == "transform":

            if self.scene_time >= 3.2:
                print("[DATA CHEF] TRANSFORMACIÓN COMPLETA -> PANEL FINAL")
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

        elif self.scene == "cooking":
            self.draw_cooking()

        elif self.scene == "transform":
            self.draw_transform()

        elif self.scene == "final":
            self.draw_final()

        # Adaptar pantalla lógica a ventana
        ww, wh = self.window.get_size()

        self.scale = min(ww / WIDTH, wh / HEIGHT)

        rw = max(1, int(WIDTH * self.scale))
        rh = max(1, int(HEIGHT * self.scale))

        self.ox = (ww - rw) // 2
        self.oy = (wh - rh) // 2

        scaled = pygame.transform.smoothscale(
            self.screen,
            (rw, rh)
        )

        self.window.fill((232, 232, 232))
        self.window.blit(scaled, (self.ox, self.oy))

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
