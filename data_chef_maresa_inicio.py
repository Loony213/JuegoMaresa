
import os
import sys
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
    def __init__(self, rect, role, description, color, image_name):
        self.base_rect = pygame.Rect(rect)
        self.rect = pygame.Rect(rect)
        self.role = role
        self.description = description
        self.color = color
        self.image_name = image_name
        self.image = load_image(image_name, (self.rect.w - 16, 110))
        self.hover = 0.0
        self.selected = False

    def update(self, mouse, dt):
        inside = self.base_rect.collidepoint(mouse)
        target = 1.0 if inside else 0.0
        self.hover += (target - self.hover) * min(1, dt * 10)

        # Elevación suave al hacer hover (efecto de juego profesional)
        offset_y = int(self.hover * -5)
        self.rect.x = self.base_rect.x
        self.rect.y = self.base_rect.y + offset_y
        return inside

    def draw(self, surface, fonts, mouse):
        inside = self.base_rect.collidepoint(mouse)

        # Sombra dinámica en hover/seleccionado
        shadow_alpha = int(15 + self.hover * 25)
        if self.selected:
            shadow_alpha = 40

        shadow = pygame.Surface((self.rect.w + 14, self.rect.h + 14), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow,
            (20, 30, 45, shadow_alpha),
            (7, 7, self.rect.w, self.rect.h),
            border_radius=16
        )
        surface.blit(shadow, (self.rect.x - 3, self.rect.y - 3))

        # Color de borde (Acento suave del rol en normal, vívido en hover/selected)
        if self.selected:
            border_color = self.color
            border_width = 3
        elif inside:
            border_color = self.color
            border_width = 2
        else:
            border_color = tuple(min(240, c + 150) for c in BORDER)
            border_width = 1

        # Tarjeta blanca limpia corporativa
        rounded_rect(
            surface,
            self.rect,
            WHITE,
            radius=16,
            border=border_width,
            border_color=border_color
        )

        # Área reservada para la imagen del personaje (Fondo neutro/sutil acento)
        image_box = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 8,
            self.rect.w - 16,
            110
        )

        bg_tint = (246, 248, 250) if not inside else tuple(min(255, c + 215) for c in self.color)
        rounded_rect(surface, image_box, bg_tint, radius=12)

        if self.image:
            img = self.image
            ir = img.get_rect()
            ir.center = image_box.center
            surface.blit(img, ir)
        else:
            # Marco elegante reservado para el personaje (sin íconos genéricos adicionales)
            pygame.draw.rect(surface, (230, 234, 240), image_box, width=1, border_radius=12)
            draw_text(
                surface,
                "PERSONAJE",
                fonts["tiny_bold"],
                MUTED,
                image_box.center,
                center=True
            )

        # Indicador de selección si está activo
        if self.selected:
            indicator_box = pygame.Rect(self.rect.right - 26, self.rect.y + 12, 16, 16)
            pygame.draw.circle(surface, self.color, indicator_box.center, 8)
            draw_text(surface, "✓", fonts["tiny_bold"], WHITE, indicator_box.center, center=True)

        # Título del rol
        title_color = DARK if not (inside or self.selected) else self.color
        draw_text(
            surface,
            self.role,
            fonts["role"],
            title_color,
            (self.rect.centerx, self.rect.y + 132),
            center=True
        )

        # Descripción breve de 2 líneas
        draw_multiline(
            surface,
            self.description,
            fonts["tiny"],
            MUTED,
            self.rect.centerx,
            self.rect.y + 154,
            gap=2
        )

        # Botón "SELECCIONAR →"
        button = pygame.Rect(
            self.rect.x + 14,
            self.rect.bottom - 34,
            self.rect.w - 28,
            25
        )

        button_color = self.color if (inside or self.selected) else (240, 243, 246)
        text_color = WHITE if (inside or self.selected) else DARK

        rounded_rect(surface, button, button_color, radius=12)

        draw_text(
            surface,
            "SELECCIONAR →" if not self.selected else "SELECCIONADO ✓",
            fonts["button"],
            text_color,
            button.center,
            center=True
        )

        return button


class DataChefApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("DATA CHEF | MARESA")
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        self.screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Tipografías limpias y nítidas
        self.fonts = {
            "tiny": pygame.font.SysFont("Segoe UI", 12),
            "tiny_bold": pygame.font.SysFont("Segoe UI", 12, bold=True),
            "small": pygame.font.SysFont("Segoe UI", 14),
            "body": pygame.font.SysFont("Segoe UI", 15),
            "button": pygame.font.SysFont("Segoe UI", 12, bold=True),
            "role": pygame.font.SysFont("Segoe UI", 15, bold=True),
            "title": pygame.font.SysFont("Segoe UI", 40, bold=True),
            "subtitle": pygame.font.SysFont("Segoe UI", 19, bold=True),
            "brand": pygame.font.SysFont("Segoe UI", 32, bold=True),
            "footer": pygame.font.SysFont("Segoe UI", 12),
        }

        self.logo = load_image("logo_maresa.png", (220, 60))
        self.bg_image = load_image("fondo.png", (WIDTH, HEIGHT))

        chef_path = os.path.join(ASSETS, "chef.png")
        self.chef = load_image("chef.png", (380, 580))

        # 6 Roles corporativos en cuadrícula 3x2
        role_definitions = [
            (
                "TECNOLOGÍA",
                ["Gestión de datos, sistemas", "y calidad de información."],
                BLUE,
                "tecnologia.png"
            ),
            (
                "RECURSOS HUMANOS",
                ["Gestión de talento, nómina", "y desarrollo organizacional."],
                ORANGE,
                "rrhh.png"
            ),
            (
                "FINANZAS",
                ["Finanzas, presupuesto", "y control contable."],
                (35, 140, 95),
                "finanzas.png"
            ),
            (
                "OPERACIONES",
                ["Procesos, logística", "y eficiencia operativa."],
                (120, 70, 180),
                "operaciones.png"
            ),
            (
                "COMERCIAL / VENTAS",
                ["Clientes, ventas,", "mercado y estrategia."],
                (200, 60, 60),
                "comercial.png"
            ),
            (
                "AUDITORÍA / RIESGO",
                ["Riesgos, cumplimiento", "y gobierno de datos."],
                (55, 115, 165),
                "auditoria.png"
            ),
        ]

        card_w = 210
        card_h = 230
        gap_x = 16
        gap_y = 16
        start_x = 730
        start_y = 215

        self.cards = []
        for i, (role, desc, color, img_name) in enumerate(role_definitions):
            col = i % 3
            row = i // 3
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            self.cards.append(
                RoleCard((x, y, card_w, card_h), role, desc, color, img_name)
            )

        self.particles = [Particle() for _ in range(30)]
        self.mouse = (0, 0)
        self.running = True
        self.selected_role = None
        self.message = ""
        self.message_timer = 0

        self.chef_x = 570
        self.chef_bob = 0.0

    def choose_role(self, role_name):
        self.selected_role = role_name
        for card in self.cards:
            card.selected = (card.role == role_name)

        self.message = f"ROL SELECCIONADO: {role_name}"
        self.message_timer = 0.5

        pantalla_02 = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "pantalla_02_data_chef.py"
        )

        if not os.path.exists(pantalla_02):
            self.message = "Falta pantalla_02_data_chef.py"
            self.message_timer = 3.0
            return

        role_arg = "rrhh" if role_name == "RECURSOS HUMANOS" else "tecnologia"

        try:
            import subprocess
            subprocess.Popen(
                [sys.executable, pantalla_02, role_arg],
                cwd=os.path.dirname(pantalla_02)
            )
            self.running = False
        except Exception as exc:
            self.message = f"Error: {exc}"
            self.message_timer = 3.0

    def open_image_picker(self):
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(
                title="Selecciona una imagen de personaje",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
            )
            root.destroy()

            if not path:
                return

            for card in self.cards:
                if card.base_rect.collidepoint(self.mouse):
                    card.image = pygame.image.load(path).convert_alpha()
                    w, h = card.image.get_size()
                    max_w, max_h = card.rect.w - 16, 110
                    if w > max_w or h > max_h:
                        scale = min(max_w / w, max_h / h)
                        card.image = pygame.transform.smoothscale(
                            card.image,
                            (max(1, int(w * scale)), max(1, int(h * scale)))
                        )
                    card.image_name = path
                    self.message = f"Imagen cargada para {card.role}"
                    self.message_timer = 2.5
                    break
        except Exception:
            pass

    def draw_background(self):
        self.screen.fill(BG)

        for particle in self.particles:
            particle.draw(self.screen)

    def draw_brand(self):
        if self.logo:
            self.screen.blit(self.logo, (40, 20))
        else:
            draw_text(self.screen, "corporación maresa", self.fonts["brand"], ORANGE, (40, 20))

    def draw_chef(self):
        if not self.chef:
            return
        bob = math.sin(self.chef_bob) * 3.5
        r = self.chef.get_rect()
        r.midbottom = (int(self.chef_x), int(670 + bob))
        self.screen.blit(self.chef, r)

    def draw_left_panel(self):
        # 1. Encabezado principal
        draw_text(self.screen, "¡Bienvenido a", self.fonts["subtitle"], DARK, (40, 95))

        data_surf = self.fonts["title"].render("DATA ", True, DARK)
        chef_surf = self.fonts["title"].render("CHEF", True, ORANGE)
        self.screen.blit(data_surf, (40, 120))
        self.screen.blit(chef_surf, (40 + data_surf.get_width(), 120))

        # Banner "LA COCINA DE LOS DATOS"
        banner = pygame.Rect(40, 172, 230, 32)
        rounded_rect(self.screen, banner, ORANGE, radius=16)
        draw_text(self.screen, "LA COCINA DE LOS DATOS", self.fonts["tiny_bold"], WHITE, banner.center, center=True)

        # 2. Párrafo descriptivo
        draw_text(self.screen, "Transformamos datos en recetas", self.fonts["body"], DARK, (40, 218))
        draw_text(self.screen, "de valor para tomar mejores decisiones.", self.fonts["body"], DARK, (40, 240))

        # 3. Sección "Tu misión" profesional
        mission_box = pygame.Rect(40, 280, 285, 80)
        rounded_rect(self.screen, mission_box, WHITE, radius=16, border=1, border_color=BORDER)
        
        # Pequeño acento visual naranja lateral
        pygame.draw.rect(self.screen, ORANGE, (40, 280, 5, 80), border_top_left_radius=16, border_bottom_left_radius=16)

        draw_text(self.screen, "Tu misión", self.fonts["tiny_bold"], ORANGE, (58, 292))
        draw_text(self.screen, "Prepara los datos con calidad,", self.fonts["tiny"], DARK, (58, 314))
        draw_text(self.screen, "precisión y trabajo en equipo.", self.fonts["tiny"], DARK, (58, 332))

        # 4. CTA Principal "COMENZAR EXPERIENCIA →"
        btn_start = pygame.Rect(40, 375, 285, 46)
        rounded_rect(self.screen, btn_start, ORANGE, radius=18)
        draw_text(self.screen, "COMENZAR EXPERIENCIA →", self.fonts["button"], WHITE, btn_start.center, center=True)

        # 5. Sección "TUS INGREDIENTES CLAVE"
        draw_text(self.screen, "— TUS INGREDIENTES CLAVE —", self.fonts["tiny_bold"], MUTED, (40, 435))

        pillars = [
            ("EXACTITUD", ["Datos correctos", "y confiables."], GREEN),
            ("COMPLETITUD", ["Información", "completa."], BLUE),
            ("CONSISTENCIA", ["Reglas y formatos", "alineados."], ORANGE),
            ("OPORTUNIDAD", ["Datos disponibles", "a tiempo."], (140, 80, 170)),
        ]

        start_p_x = 40
        p_y = 458
        p_w, p_h = 82, 102
        gap_p = 8

        for i, (name, lines, color) in enumerate(pillars):
            px = start_p_x + i * (p_w + gap_p)
            box = pygame.Rect(px, p_y, p_w, p_h)
            rounded_rect(self.screen, box, WHITE, radius=14, border=1, border_color=BORDER)
            
            # Pequeño indicador / punto de color en lugar de ícono gigante
            pygame.draw.circle(self.screen, color, (box.centerx, box.y + 20), 5)
            draw_text(self.screen, name, self.fonts["tiny_bold"], color, (box.centerx, box.y + 36), center=True)
            draw_multiline(self.screen, lines, self.fonts["tiny"], MUTED, box.centerx, box.y + 56, gap=1)

    def draw_right_header(self):
        header_x = 1050
        header_y = 150

        draw_text(self.screen, "SELECCIONA TU ÁREA", self.fonts["subtitle"], DARK, (header_x, header_y), center=True)
        draw_text(self.screen, "→", self.fonts["subtitle"], ORANGE, (header_x - 120, header_y), center=True)
        draw_text(self.screen, "←", self.fonts["subtitle"], ORANGE, (header_x + 120, header_y), center=True)

        draw_text(
            self.screen,
            "Cada área tiene ingredientes únicos. ¡Elige el tuyo!",
            self.fonts["tiny"],
            MUTED,
            (header_x, header_y + 26),
            center=True
        )

    def draw_footer_pipeline(self):
        footer_box = pygame.Rect(35, 705, 1370, 95)
        rounded_rect(self.screen, footer_box, WHITE, radius=18, border=1, border_color=BORDER)

        draw_text(self.screen, "EN ESTA", self.fonts["tiny_bold"], ORANGE, (65, 732))
        draw_text(self.screen, "EXPERIENCIA:", self.fonts["tiny_bold"], ORANGE, (65, 750))

        steps = [
            ("1", "SELECCIONA", "Elige los datos\nadecuados."),
            ("2", "PREPARA", "Limpia, transforma\ny valida."),
            ("3", "COCINA", "Modela y organiza\nlos ingredientes."),
            ("4", "SIRVE", "Visualiza y comparte\ninformación de valor."),
        ]

        step_start_x = 210
        step_gap = 210

        for i, (num, title, desc) in enumerate(steps):
            sx = step_start_x + i * step_gap
            pygame.draw.circle(self.screen, (245, 240, 235), (sx, 752), 22)
            draw_text(self.screen, num, self.fonts["tiny_bold"], DARK, (sx, 752), center=True)

            # Subimos el título 7px (de 735 a 728) para separarlo limpiamente de la descripción
            draw_text(self.screen, title, self.fonts["tiny_bold"], DARK, (sx + 32, 728))
            draw_multiline(self.screen, desc.split("\n"), self.fonts["tiny"], MUTED, sx + 75, 750, gap=1)

            if i < len(steps) - 1:
                draw_text(self.screen, "—→", self.fonts["tiny"], ORANGE, (sx + 155, 752))

        callout = pygame.Rect(1140, 718, 245, 70)
        rounded_rect(self.screen, callout, LIGHT_ORANGE, radius=14, border=1, border_color=ORANGE)
        draw_multiline(
            self.screen,
            ["CONVIERTE DATOS", "EN DECISIONES", "INTELIGENTES"],
            self.fonts["tiny_bold"],
            ORANGE_DARK,
            callout.centerx,
            callout.y + 14,
            gap=2
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
        self.screen.fill(BG)

        self.draw_background()
        self.draw_brand()
        self.draw_left_panel()
        self.draw_right_header()

        for card in self.cards:
            card.draw(self.screen, self.fonts, self.mouse)

        self.draw_chef()
        self.draw_footer_pipeline()
        self.draw_message()

        draw_text(
            self.screen,
            "F2: Cargar personaje   •   ESC: Salir",
            self.fonts["tiny"],
            (135, 145, 155),
            (35, HEIGHT - 18)
        )

        win_w, win_h = self.window.get_size()
        if win_w == WIDTH and win_h == HEIGHT:
            self.window.blit(self.screen, (0, 0))
            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0
        else:
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
            if card.base_rect.collidepoint(logical_pos):
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
