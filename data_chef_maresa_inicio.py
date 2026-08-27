
import os
import math
import random
import pygame
from pygame.locals import QUIT, MOUSEMOTION, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE

# ============================================================
# DATA CHEF MARESA
# Pantalla inicial estilo videojuego corporativo / Genially
#
# INSTALACIÓN:
#   pip install pygame pillow
#
# IMÁGENES:
#   Coloca tus PNG/JPG dentro de:
#       assets/chef.png
#       assets/tecnologia.png
#       assets/rrhh.png
#       assets/logo_maresa.png       (opcional)
#
# Las imágenes con fondo transparente (PNG) se ven mejor.
# También puedes usar F2 para abrir un selector de imágenes
# y cargar los personajes sin tocar el código.
# ============================================================

WIDTH, HEIGHT = 1440, 840
FPS = 60

# Paleta inspirada en MARESA y en la referencia proporcionada.
BG = (248, 246, 242)
ORANGE = (245, 126, 27)
ORANGE_DARK = (217, 91, 9)
DARK = (35, 48, 61)
MUTED = (94, 105, 116)
WHITE = (255, 255, 255)
BLUE = (28, 112, 221)
BLUE_DARK = (16, 73, 151)
GREEN = (75, 151, 100)
LIGHT_BLUE = (231, 242, 255)
LIGHT_ORANGE = (255, 241, 225)
BORDER = (224, 226, 229)

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


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
            # Pygame Surface no tiene .thumbnail() como PIL.
            # Redimensionamos manteniendo la proporción.
            max_w, max_h = max_size
            w, h = image.get_size()

            if w > max_w or h > max_h:
                scale = min(max_w / w, max_h / h)
                new_size = (
                    max(1, int(w * scale)),
                    max(1, int(h * scale))
                )
                image = pygame.transform.smoothscale(image, new_size)

        return image

    except Exception as exc:
        print(f"[DATA CHEF] Error cargando {path}: {exc}")
        return None


def rounded_rect(surface, rect, color, radius=20, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(
            surface,
            border_color or color,
            rect,
            width=border,
            border_radius=radius
        )


def draw_text(surface, text, font, color, pos, center=False):
    rendered = font.render(text, True, color)
    r = rendered.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surface.blit(rendered, r)
    return r


def draw_multiline(surface, lines, font, color, center_x, start_y, gap=4):
    y = start_y
    for line in lines:
        r = draw_text(surface, line, font, color, (center_x, y), center=True)
        y += r.height + gap


def draw_icon_chart(surface, center, color):
    x, y = center
    pygame.draw.rect(surface, color, (x - 33, y - 22, 66, 48), border_radius=10)
    pygame.draw.rect(surface, WHITE, (x - 22, y - 11, 8, 25), border_radius=3)
    pygame.draw.rect(surface, WHITE, (x - 5, y - 20, 8, 34), border_radius=3)
    pygame.draw.rect(surface, WHITE, (x + 12, y - 2, 8, 16), border_radius=3)


def draw_icon_people(surface, center, color):
    x, y = center
    pygame.draw.circle(surface, color, (x, y - 17), 13)
    pygame.draw.circle(surface, color, (x - 27, y - 8), 9)
    pygame.draw.circle(surface, color, (x + 27, y - 8), 9)
    pygame.draw.ellipse(surface, color, (x - 27, y + 2, 54, 37))
    pygame.draw.ellipse(surface, color, (x - 48, y + 5, 28, 24))
    pygame.draw.ellipse(surface, color, (x + 20, y + 5, 28, 24))


def draw_star(surface, center, color, radius=16):
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = radius if i % 2 == 0 else radius * 0.42
        points.append((center[0] + math.cos(angle) * r,
                       center[1] + math.sin(angle) * r))
    pygame.draw.polygon(surface, color, points)


class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.r = random.choice([1, 1, 2, 3])
        self.speed = random.uniform(0.12, 0.45)
        self.alpha = random.randint(35, 100)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, t):
        self.y -= self.speed
        self.x += math.sin(t * 0.001 + self.phase) * 0.08
        if self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.uniform(0, WIDTH)

    def draw(self, surface):
        layer = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*ORANGE, self.alpha), (4, 4), self.r)
        surface.blit(layer, (self.x - 4, self.y - 4))


class RoleCard:
    def __init__(self, rect, role, subtitle, description, color, image_name):
        self.rect = pygame.Rect(rect)
        self.role = role
        self.subtitle = subtitle
        self.description = description
        self.color = color
        self.image_name = image_name
        self.image = load_image(image_name, (330, 270))
        self.hover = 0.0
        self.selected = False

    def update(self, mouse, dt):
        inside = self.rect.collidepoint(mouse)
        target = 1.0 if inside else 0.0
        self.hover += (target - self.hover) * min(1, dt * 8)
        return inside

    def draw(self, surface, fonts, mouse):
        inside = self.rect.collidepoint(mouse)

        # Sombra suave
        shadow = pygame.Surface((self.rect.w + 24, self.rect.h + 24), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow,
            (30, 40, 50, 22),
            (12, 12, self.rect.w, self.rect.h),
            border_radius=28
        )
        surface.blit(shadow, (self.rect.x - 6, self.rect.y - 6))

        border_color = self.color if inside or self.selected else BORDER
        border_width = 3 if inside or self.selected else 2

        rounded_rect(
            surface,
            self.rect,
            WHITE,
            radius=28,
            border=border_width,
            border_color=border_color
        )

        # Encabezado visual
        image_box = pygame.Rect(
            self.rect.x + 12,
            self.rect.y + 12,
            self.rect.w - 24,
            235
        )
        rounded_rect(
            surface,
            image_box,
            LIGHT_BLUE if self.color == BLUE else LIGHT_ORANGE,
            radius=22
        )

        if self.image:
            img = self.image
            # Centrar imagen manteniendo tamaño.
            ir = img.get_rect()
            ir.center = image_box.center
            surface.blit(img, ir)
        else:
            # Placeholder elegante hasta que el usuario suba el personaje.
            icon_center = image_box.center
            if self.color == BLUE:
                draw_icon_chart(surface, icon_center, BLUE)
            else:
                draw_icon_people(surface, icon_center, ORANGE)

            draw_text(
                surface,
                "SUBE TU PERSONAJE",
                fonts["tiny_bold"],
                MUTED,
                (image_box.centerx, image_box.bottom - 26),
                center=True
            )

        # Título
        draw_text(
            surface,
            self.role,
            fonts["role"],
            self.color,
            (self.rect.centerx, self.rect.y + 272),
            center=True
        )

        # Descripción
        draw_multiline(
            surface,
            self.description,
            fonts["body"],
            DARK,
            self.rect.centerx,
            self.rect.y + 315,
            gap=3
        )

        # Botón
        button = pygame.Rect(
            self.rect.x + 54,
            self.rect.bottom - 58,
            self.rect.w - 108,
            40
        )

        button_color = self.color
        if inside:
            button_color = tuple(min(255, c + 18) for c in self.color)

        rounded_rect(surface, button, button_color, radius=20)

        draw_text(
            surface,
            "SELECCIONAR",
            fonts["button"],
            WHITE,
            (button.centerx - 10, button.centery),
            center=True
        )

        # Flecha circular
        pygame.draw.circle(
            surface,
            tuple(max(0, c - 15) for c in button_color),
            (button.right - 24, button.centery),
            14
        )
        pygame.draw.polygon(
            surface,
            WHITE,
            [
                (button.right - 28, button.centery - 5),
                (button.right - 20, button.centery),
                (button.right - 28, button.centery + 5),
            ]
        )

        return button


class DataChefApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("DATA CHEF | MARESA")
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("DATA CHEF | MARESA")
        self.screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.fonts = {
            "tiny": pygame.font.SysFont("Arial", 11),
            "tiny_bold": pygame.font.SysFont("Arial", 11, bold=True),
            "small": pygame.font.SysFont("Arial", 14),
            "body": pygame.font.SysFont("Arial", 15),
            "button": pygame.font.SysFont("Arial", 14, bold=True),
            "role": pygame.font.SysFont("Arial", 22, bold=True),
            "title": pygame.font.SysFont("Arial", 42, bold=True),
            "subtitle": pygame.font.SysFont("Arial", 20, bold=True),
            "brand": pygame.font.SysFont("Arial", 34, bold=True),
            "footer": pygame.font.SysFont("Arial", 12),
        }

        self.logo = load_image("logo_maresa.png", (250, 70))

        # ====================================================
        # PERSONAJE PRINCIPAL
        # Busca EXPLICITAMENTE assets/chef.png
        # ====================================================
        chef_path = os.path.join(ASSETS, "chef.png")
        print(f"[DATA CHEF] Buscando chef en: {chef_path}")

        self.chef = load_image("chef.png", (340, 530))

        if self.chef is None:
            print("[DATA CHEF] ERROR: No se pudo cargar assets/chef.png")
            print("[DATA CHEF] Verifica que el archivo se llame exactamente: chef.png")
        else:
            print("[DATA CHEF] OK: chef.png cargado correctamente.")

        self.cards = [
            RoleCard(
                (735, 295, 305, 475),
                "TECNOLOGÍA",
                "Datos • Sistemas • BI",
                [
                    "Enfocado en la calidad de datos",
                    "en sistemas, bases de datos",
                    "y procesos tecnológicos."
                ],
                BLUE,
                "tecnologia.png"
            ),
            RoleCard(
                (1070, 295, 305, 475),
                "RECURSOS HUMANOS",
                "Personas • Talento • Procesos",
                [
                    "Enfocado en la calidad de datos",
                    "de colaboradores, procesos",
                    "y gestión del talento."
                ],
                ORANGE,
                "rrhh.png"
            ),
        ]

        self.particles = [Particle() for _ in range(45)]
        self.mouse = (0, 0)
        self.running = True
        self.selected_role = None
        self.message = ""
        self.message_timer = 0

        self.chef_x = 350
        self.chef_bob = 0.0

    def choose_role(self, role):
        self.selected_role = role
        self.message = f"ROL SELECCIONADO: {role}"
        self.message_timer = 2.0

    def open_image_picker(self):
        # Selector opcional para cargar personajes desde cualquier carpeta.
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(
                title="Selecciona una imagen de personaje",
                filetypes=[
                    ("Imágenes", "*.png *.jpg *.jpeg"),
                    ("PNG", "*.png"),
                    ("JPG", "*.jpg *.jpeg"),
                ]
            )
            root.destroy()

            if not path:
                return

            # Determinar qué personaje se quiere reemplazar según el mouse.
            target = None
            for card in self.cards:
                if card.rect.collidepoint(self.mouse):
                    target = card
                    break

            if target:
                target.image = pygame.image.load(path).convert_alpha()
                target.image.thumbnail((330, 270), pygame.Resampling.LANCZOS)
                target.image_name = path
                self.message = f"Imagen cargada para {target.role}"
                self.message_timer = 2.5

        except Exception as exc:
            self.message = "No se pudo abrir el selector de imágenes"
            self.message_timer = 2.5

    def draw_background(self):
        self.screen.fill(BG)

        # Degradado vertical muy suave.
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            a = int(30 * (y / HEIGHT))
            pygame.draw.line(
                overlay,
                (255, 255, 255, a),
                (0, y),
                (WIDTH, y)
            )
        self.screen.blit(overlay, (0, 0))

        # Decoración de cocina: pequeñas líneas y círculos.
        for i in range(8):
            x = 650 + i * 110
            pygame.draw.circle(
                self.screen,
                (242, 220, 198),
                (x, 112 + (i % 2) * 10),
                3
            )

        # Brillo naranja inferior izquierdo.
        glow = pygame.Surface((560, 300), pygame.SRCALPHA)
        for radius in range(280, 10, -12):
            alpha = int(1.4 * (280 - radius))
            pygame.draw.circle(
                glow,
                (*ORANGE, min(20, alpha)),
                (80, 260),
                radius
            )
        self.screen.blit(glow, (0, HEIGHT - 270))

        for particle in self.particles:
            particle.draw(self.screen)

    def draw_brand(self):
        if self.logo:
            lr = self.logo.get_rect()
            lr.topleft = (42, 25)
            self.screen.blit(self.logo, lr)
        else:
            # Logo tipográfico de respaldo.
            pygame.draw.circle(self.screen, ORANGE, (67, 57), 26)
            pygame.draw.arc(
                self.screen,
                WHITE,
                (49, 42, 36, 30),
                math.radians(205),
                math.radians(335),
                4
            )
            draw_text(
                self.screen,
                "maresa",
                self.fonts["brand"],
                ORANGE,
                (103, 35)
            )
            draw_text(
                self.screen,
                "Pasión por lo que hacemos",
                self.fonts["tiny"],
                MUTED,
                (105, 69)
            )

    def draw_chef(self):
        if not self.chef:
            # Silueta/placeholder si aún no sube el chef.
            x = int(self.chef_x)
            y = 1000
            pygame.draw.circle(self.screen, ORANGE, (x, y - 220), 58)
            pygame.draw.ellipse(self.screen, WHITE, (x - 95, y - 300, 190, 240))
            draw_text(
                self.screen,
                "SUBE chef.png",
                self.fonts["small"],
                MUTED,
                (x, y - 70),
                center=True
            )
            return

        bob = math.sin(self.chef_bob) * 3
        r = self.chef.get_rect()
        self.chef_x = 350
        self.chef_y = 560
        r.midbottom = (int(self.chef_x), int(self.chef_y + bob))
        self.screen.blit(self.chef, r)

    def draw_left_content(self):
        # Título
        draw_text(
            self.screen,
            "¡Bienvenido a",
            self.fonts["subtitle"],
            DARK,
            (430, 105),
            center=True
        )

        # DATA CHEF
        draw_text(
            self.screen,
            "DATA",
            self.fonts["title"],
            DARK,
            (430, 155),
            center=True
        )
        draw_text(
            self.screen,
            "CHEF",
            self.fonts["title"],
            ORANGE,
            (570, 155),
            center=True
        )

        # Icono de chef
        pygame.draw.circle(self.screen, ORANGE, (395, 665), 27)
        pygame.draw.arc(
            self.screen,
            WHITE,
            (333, 148, 34, 25),
            math.radians(190),
            math.radians(350),
            4
        )

        # Subtítulo
        rounded_rect(
            self.screen,
            pygame.Rect(420, 210, 390, 42),
            ORANGE,
            radius=21
        )
        draw_text(
            self.screen,
            "La cocina de la calidad de los datos",
            self.fonts["small"],
            WHITE,
            (615, 231),
            center=True
        )

        # Decoraciones
        draw_star(self.screen, (830, 105), (91, 174, 240), 9)
        draw_star(self.screen, (1380, 75), ORANGE, 10)

        # Olla DATA CHEF
        pot = pygame.Rect(110, 555, 400, 100)
        rounded_rect(self.screen, pot, ORANGE, radius=42)
        pygame.draw.rect(self.screen, ORANGE_DARK, (145, 630, 330, 25), border_radius=12)

        draw_text(
            self.screen,
            "DATA CHEF",
            self.fonts["subtitle"],
            WHITE,
            pot.center,
            center=True
        )

        # Ingredientes de calidad
        jars = [
            ("EXACTITUD", GREEN),
            ("COMPLETITUD", BLUE),
            ("CONSISTENCIA", ORANGE),
            ("OPORTUNIDAD", (150, 108, 175)),
        ]

        for i, (name, color) in enumerate(jars):
            x = 55 + i * 125
            y = 660
            jar = pygame.Rect(x, y, 105, 110)
            rounded_rect(self.screen, jar, WHITE, radius=14, border=2, border_color=BORDER)
            pygame.draw.circle(self.screen, color, (x + 52, y + 35), 17)
            draw_text(
                self.screen,
                name,
                self.fonts["tiny_bold"],
                color,
                (x + 52, y + 82),
                center=True
            )

        # Burbuja
        bubble = pygame.Rect(60, 210, 245, 125)
        rounded_rect(self.screen, bubble, WHITE, radius=22, border=1, border_color=BORDER)
        draw_multiline(
            self.screen,
            ["Datos", "limpios, decisiones", "inteligentes."],
            self.fonts["body"],
            DARK,
            bubble.centerx,
            bubble.y + 22,
            gap=2
        )
        pygame.draw.polygon(
            self.screen,
            WHITE,
            [
                (bubble.right - 55, bubble.bottom - 2),
                (bubble.right - 28, bubble.bottom + 22),
                (bubble.right - 70, bubble.bottom + 7),
            ]
        )
        draw_text(
            self.screen,
            "♥",
            self.fonts["subtitle"],
            ORANGE,
            (bubble.centerx, bubble.bottom - 25),
            center=True
        )

    def draw_right_header(self):
        draw_text(
            self.screen,
            "ESCOGE TU ROL",
            self.fonts["subtitle"],
            DARK,
            (1065, 225),
            center=True
        )

        # Flechas decorativas
        draw_text(
            self.screen,
            "→",
            self.fonts["subtitle"],
            ORANGE,
            (955, 225),
            center=True
        )
        draw_text(
            self.screen,
            "←",
            self.fonts["subtitle"],
            ORANGE,
            (1175, 225),
            center=True
        )

    def draw_footer(self):
        footer = pygame.Rect(170, 790, 700, 40)
        rounded_rect(self.screen, footer, WHITE, radius=22, border=1, border_color=BORDER)

        items = [
            ("✓", "Calidad\nen cada dato"),
            ("★", "Decisiones\ncon confianza"),
            ("◎", "Procesos\neficientes"),
            ("♟", "Trabajamos\njuntos"),
        ]

        x = footer.x + 70
        for icon, text in items:
            draw_text(
                self.screen,
                icon,
                self.fonts["subtitle"],
                ORANGE,
                (x, footer.centery - 5),
                center=True
            )
            draw_multiline(
                self.screen,
                text.split("\n"),
                self.fonts["tiny"],
                DARK,
                x + 52,
                footer.y + 8,
                gap=0
            )
            x += 165

        draw_text(
            self.screen,
            "MARESA • DATA CHEF",
            self.fonts["footer"],
            MUTED,
            (1180, 810),
            center=True
        )

    def draw_message(self):
        if self.message_timer <= 0:
            return

        box = pygame.Rect(470, 735, 500, 44)
        rounded_rect(self.screen, box, DARK, radius=22)
        draw_text(
            self.screen,
            self.message,
            self.fonts["small"],
            WHITE,
            box.center,
            center=True
        )

    def draw(self):
        # Todo se dibuja en una resolución lógica fija y luego
        # se ajusta proporcionalmente a cualquier monitor.
        self.screen.fill(BG)

        self.draw_background()
        self.draw_brand()
        self.draw_left_content()
        self.draw_right_header()

        for card in self.cards:
            card.draw(self.screen, self.fonts, self.mouse)

        self.draw_chef()
        self.draw_footer()
        self.draw_message()

        draw_text(
            self.screen,
            "F2: cargar personaje • ESC: salir",
            self.fonts["tiny"],
            (135, 145, 155),
            (20, HEIGHT - 22)
        )

        win_w, win_h = self.window.get_size()
        scale = min(win_w / WIDTH, win_h / HEIGHT)
        render_w = max(1, int(WIDTH * scale))
        render_h = max(1, int(HEIGHT * scale))
        self.scale = scale
        self.offset_x = (win_w - render_w) // 2
        self.offset_y = (win_h - render_h) // 2

        scaled = pygame.transform.smoothscale(
            self.screen,
            (render_w, render_h)
        )

        self.window.fill((235, 235, 235))
        self.window.blit(scaled, (self.offset_x, self.offset_y))
        pygame.display.flip()

    def to_logical(self, pos):
        x, y = pos
        if self.scale <= 0:
            return (x, y)
        return (
            int((x - self.offset_x) / self.scale),
            int((y - self.offset_y) / self.scale)
        )

    def handle_click(self, pos):
        logical_pos = self.to_logical(pos)
        for card in self.cards:
            button = pygame.Rect(
                card.rect.x + 54,
                card.rect.bottom - 58,
                card.rect.w - 108,
                40
            )
            if button.collidepoint(logical_pos):
                self.choose_role(card.role)
                return

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.chef_bob += dt * 2.4

            if self.message_timer > 0:
                self.message_timer -= dt

            for particle in self.particles:
                particle.update(pygame.time.get_ticks())

            for card in self.cards:
                card.update(self.mouse, dt)

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                elif event.type == MOUSEMOTION:
                    self.mouse = self.to_logical(event.pos)

                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

                elif event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode(
                        event.size,
                        pygame.RESIZABLE
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
