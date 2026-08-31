import os
import sys
import math
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 1536, 864
FPS = 60

ORANGE = (232, 101, 0)
ORANGE_DARK = (184, 72, 0)
CREAM = (248, 242, 226)
CREAM_2 = (238, 230, 211)
WHITE = (255, 255, 255)
DARK = (45, 55, 65)
DARK_PANEL = (44, 57, 64)
BLUE = (126, 188, 235)
GREEN = (62, 153, 88)
RED = (194, 70, 50)
YELLOW = (238, 178, 55)
GRAY = (166, 178, 184)
ROAD = (188, 181, 174)

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")


def load_img(name, max_size=None):
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path):
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

        return img
    except Exception as e:
        print("[DATA CHEF] Error cargando", path, e)
        return None


def rr(surface, rect, color, radius=18, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(
            surface,
            border_color or color,
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


class DataKitchen:
    def __init__(self):
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("DATA CHEF | La Cocina de los Datos")
        self.screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()

        self.running = True
        self.t = 0.0
        self.scale = 1.0
        self.ox = 0
        self.oy = 0

        self.score = 1500
        self.active = None
        self.completed = set()
        self.selected = set()
        self.message = "Selecciona un ingrediente para comenzar la limpieza."
        self.message_color = DARK

        self.chef = load_img("chef_limpieza.png", (340, 420))
        if self.chef is None:
            self.chef = load_img("chef_jugando.png", (340, 420))
        if self.chef is None:
            self.chef = load_img("chef.png", (340, 420))

        self.font = {
            "tiny": pygame.font.SysFont("Arial", 15),
            "small": pygame.font.SysFont("Arial", 18),
            "body": pygame.font.SysFont("Arial", 21),
            "bold": pygame.font.SysFont("Arial", 22, bold=True),
            "card": pygame.font.SysFont("Arial", 20, bold=True),
            "title": pygame.font.SysFont("Arial", 46, bold=True),
            "step": pygame.font.SysFont("Arial", 24, bold=True),
            "etl": pygame.font.SysFont("Arial", 50, bold=True),
            "mono": pygame.font.SysFont("Consolas", 17, bold=True),
            "button": pygame.font.SysFont("Arial", 24, bold=True),
        }

        # Cuatro minijuegos de limpieza.
        self.tasks = [
            {
                "id": "duplicates",
                "title": "Duplicados",
                "icon": "⧉",
                "instruction": "Encuentra los registros repetidos.",
                "hint": "Haz clic sobre las filas duplicadas.",
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
                "icon": "∅",
                "instruction": "Encuentra los datos incompletos.",
                "hint": "Selecciona las filas que contienen valores vacíos.",
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
                "icon": "⌁",
                "instruction": "Detecta los formatos inconsistentes.",
                "hint": "Selecciona las filas con formatos incorrectos.",
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
                "icon": "✓",
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
            },
        ]

        self.card_rects = [
            pygame.Rect(835, 405, 150, 165),
            pygame.Rect(1015, 405, 150, 165),
            pygame.Rect(1195, 405, 150, 165),
            pygame.Rect(1375, 405, 150, 165),
        ]

        self.row_rects = []

    def logical(self, pos):
        return (
            int((pos[0] - self.ox) / self.scale),
            int((pos[1] - self.oy) / self.scale),
        )

    def background(self):
        self.screen.fill(CREAM)

        # Suelo inferior.
        pygame.draw.rect(self.screen, ROAD, (0, 650, WIDTH, HEIGHT - 650))

        # Brillo suave de fondo.
        for radius, alpha in [(300, 18), (220, 20), (150, 25)]:
            glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 188, 88, alpha), (340, 300), radius)
            self.screen.blit(glow, (0, 0))

        # Burbujas de pensamiento.
        pygame.draw.circle(self.screen, (245, 247, 246), (520, 250), 28)
        pygame.draw.circle(self.screen, (245, 247, 246), (590, 175), 48)
        pygame.draw.circle(self.screen, (245, 247, 246), (660, 105), 70)
        pygame.draw.circle(self.screen, (179, 192, 196), (520, 250), 28, 2)
        pygame.draw.circle(self.screen, (179, 192, 196), (590, 175), 48, 2)
        pygame.draw.circle(self.screen, (179, 192, 196), (660, 105), 70, 2)

    def header(self):
        pygame.draw.rect(self.screen, ORANGE, (0, 0, WIDTH, 110))
        pygame.draw.line(self.screen, (255, 182, 106), (0, 110), (WIDTH, 110), 2)

        # Icono lupa.
        pygame.draw.circle(self.screen, WHITE, (410, 54), 20, 4)
        pygame.draw.line(self.screen, WHITE, (424, 68), (446, 90), 5)
        pygame.draw.circle(self.screen, WHITE, (410, 54), 5)

        text(
            self.screen,
            "LA COCINA DE LOS DATOS",
            self.font["title"],
            WHITE,
            (475, 35)
        )

        text(
            self.screen,
            "PASO 2 · LIMPIEZA Y ORDEN",
            self.font["step"],
            WHITE,
            (1280, 48),
            True
        )

    def chef_area(self):
        # Texto del pensamiento.
        thought = (
            "“Hmm... estos datos vienen crudos.\n"
            "Primero debo eliminar duplicados, corregir\n"
            "formatos, tratar los nulos y validar la\n"
            "información.”"
        )

        y = 130
        for line in thought.split("\n"):
            text(
                self.screen,
                line,
                self.font["bold"],
                DARK,
                (910, y),
                True
            )
            y += 26

        if self.chef:
            bob = int(math.sin(self.t * 2.4) * 5)
            rect = self.chef.get_rect()
            rect.midbottom = (430, 690 + bob)
            self.screen.blit(self.chef, rect)
        else:
            # Chef provisional si todavía no sube chef_limpieza.png.
            pygame.draw.circle(self.screen, (248, 206, 160), (430, 530), 58)
            rr(self.screen, pygame.Rect(370, 570, 120, 100), WHITE, 24)
            pygame.draw.arc(self.screen, DARK, (395, 515, 70, 40), 0.2, 2.9, 3)

        # Panel DATOS CRUDOS.
        box = pygame.Rect(95, 675, 640, 165)
        rr(self.screen, box, (250, 248, 244), 0, 3, ORANGE)

        text(self.screen, "♨  DATOS CRUDOS", self.font["step"], ORANGE, (300, 692))

        raw = [
            "Juan Perez | juan@mail",
            "DUPLICADO → ELIMINADO",
            "MARIA | NULL → COMPLETADO",
            "2025/08/45 → FORMATO CORREGIDO",
            "Quito | Quito → VALIDADO",
        ]

        colors = [
            (155, 90, 75),
            (90, 100, 85),
            (82, 116, 95),
            (124, 113, 80),
            (70, 100, 90),
        ]

        yy = 742
        for value, color in zip(raw, colors):
            text(self.screen, value, self.font["mono"], color, (135, yy))
            yy += 20

    def etl_panel(self):
        panel = pygame.Rect(790, 240, 746, 410)
        rr(self.screen, panel, (224, 227, 230), 0, 3, (137, 156, 164))

        banner = pygame.Rect(850, 285, 686, 105)
        rr(self.screen, banner, DARK_PANEL, 0)

        text(self.screen, "DATA ETL", self.font["etl"], BLUE, (1193, 312), True)
        text(
            self.screen,
            "EXTRAER → TRANSFORMAR → CARGAR",
            self.font["small"],
            WHITE,
            (1193, 365),
            True
        )

        for task, rect in zip(self.tasks, self.card_rects):
            done = task["id"] in self.completed
            active = self.active == task["id"]

            card_color = (245, 246, 245)
            border = GREEN if done else ORANGE if active else (144, 161, 170)

            rr(self.screen, rect, card_color, 0, 3 if active or done else 2, border)

            if done:
                pygame.draw.circle(self.screen, GREEN, (rect.right - 20, rect.top + 20), 13)
                text(self.screen, "✓", self.font["small"], WHITE, (rect.right - 20, rect.top + 19), True)

            text(
                self.screen,
                task["icon"],
                pygame.font.SysFont("Arial", 42, bold=True),
                ORANGE if not done else GREEN,
                (rect.centerx, rect.top + 54),
                True
            )
            text(
                self.screen,
                task["title"],
                self.font["card"],
                DARK,
                (rect.centerx, rect.top + 115),
                True
            )

            if done:
                text(
                    self.screen,
                    "LISTO",
                    self.font["tiny"],
                    GREEN,
                    (rect.centerx, rect.top + 142),
                    True
                )

    def challenge_panel(self):
        if self.active is None:
            return

        task = next(t for t in self.tasks if t["id"] == self.active)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 28, 32, 92))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(300, 165, 936, 610)
        rr(self.screen, panel, (250, 248, 242), 24, 4, ORANGE)

        text(
            self.screen,
            task["title"].upper(),
            self.font["title"],
            ORANGE,
            (768, 205),
            True
        )
        text(
            self.screen,
            task["instruction"],
            self.font["bold"],
            DARK,
            (768, 260),
            True
        )
        text(
            self.screen,
            task["hint"],
            self.font["small"],
            (94, 109, 118),
            (768, 292),
            True
        )

        # Tabla.
        table = pygame.Rect(370, 330, 796, 295)
        rr(self.screen, table, WHITE, 12, 2, (174, 188, 194))

        pygame.draw.rect(self.screen, DARK_PANEL, (372, 332, 792, 42))
        headers = ["NOMBRE", "VALOR", "ESTADO"]
        hx = [440, 720, 1010]
        for h, x in zip(headers, hx):
            text(self.screen, h, self.font["small"], WHITE, (x, 353), True)

        self.row_rects = []
        y = 385

        for i, row in enumerate(task["rows"]):
            rect = pygame.Rect(388, y, 760, 43)
            self.row_rects.append(rect)

            selected = i in self.selected
            if selected:
                color = (255, 225, 196)
                border = ORANGE
            else:
                color = (248, 248, 246) if i % 2 == 0 else (238, 242, 243)
                border = None

            rr(self.screen, rect, color, 8, 2 if selected else 0, border)

            if selected:
                pygame.draw.circle(self.screen, ORANGE, (410, rect.centery), 11)
                text(self.screen, "✓", self.font["tiny"], WHITE, (410, rect.centery), True)
            else:
                pygame.draw.circle(self.screen, (190, 199, 203), (410, rect.centery), 10, 2)

            text(self.screen, row[0], self.font["small"], DARK, (440, rect.centery), True)
            text(self.screen, row[1] if row[1] else "VACÍO", self.font["small"], DARK, (720, rect.centery), True)
            text(self.screen, row[2], self.font["small"], DARK, (1010, rect.centery), True)

            y += 47

        confirm = pygame.Rect(865, 665, 270, 58)
        rr(self.screen, confirm, ORANGE, 16)
        text(
            self.screen,
            "COMPROBAR ✓",
            self.font["button"],
            WHITE,
            confirm.center,
            True
        )

        text(
            self.screen,
            f"Seleccionados: {len(self.selected)}",
            self.font["small"],
            DARK,
            (420, 692)
        )

    def bottom(self):
        panel = pygame.Rect(650, 825, 520, 60)
        rr(self.screen, panel, (255, 249, 239), 18, 2, (230, 183, 126))

        if len(self.completed) == 4:
            label = "✓ DATOS LIMPIOS · CONTINUAR"
            color = GREEN
        else:
            label = f"PROGRESO DE LIMPIEZA: {len(self.completed)} / 4"
            color = ORANGE

        text(self.screen, label, self.font["button"], color, panel.center, True)

    def draw(self):
        self.background()
        self.header()
        self.chef_area()
        self.etl_panel()

        score_box = pygame.Rect(1265, 125, 240, 48)
        rr(self.screen, score_box, DARK_PANEL, 20)
        text(
            self.screen,
            f"⭐ {self.score}",
            self.font["bold"],
            WHITE,
            (1385, 149),
            True
        )

        # Mensaje contextual.
        text(
            self.screen,
            self.message,
            self.font["small"],
            self.message_color,
            (768, 745),
            True
        )

        self.bottom()

        if self.active is not None:
            self.challenge_panel()

        ww, wh = self.window.get_size()
        self.scale = min(ww / WIDTH, wh / HEIGHT)
        rw = int(WIDTH * self.scale)
        rh = int(HEIGHT * self.scale)
        self.ox = (ww - rw) // 2
        self.oy = (wh - rh) // 2

        scaled = pygame.transform.smoothscale(self.screen, (rw, rh))
        self.window.fill((220, 220, 220))
        self.window.blit(scaled, (self.ox, self.oy))
        pygame.display.flip()

    def open_task(self, task):
        if task["id"] in self.completed:
            self.message = f"{task['title']} ya fue completado ✓"
            self.message_color = GREEN
            return

        self.active = task["id"]
        self.selected.clear()
        self.message = task["hint"]
        self.message_color = ORANGE
        print("[DATA CHEF] MINIJUEGO:", task["title"])

    def check_task(self):
        task = next(t for t in self.tasks if t["id"] == self.active)

        if self.selected == task["bad"]:
            self.completed.add(task["id"])
            self.score += 125
            self.message = "✓ " + task["fixed"]
            self.message_color = GREEN
            print("[DATA CHEF] COMPLETADO:", task["title"])

            self.active = None
            self.selected.clear()

            if len(self.completed) == 4:
                self.message = "🎉 ¡Datos limpios y listos para cocinar!"
                self.message_color = GREEN
                print("[DATA CHEF] PASO 2 COMPLETADO")
        else:
            self.message = "Revisa otra vez: todavía hay datos que no corresponden."
            self.message_color = RED
            print("[DATA CHEF] RESPUESTA INCORRECTA EN:", task["title"])

    def click(self, pos):
        if self.active is not None:
            # Filas del minijuego.
            for i, rect in enumerate(self.row_rects):
                if rect.collidepoint(pos):
                    if i in self.selected:
                        self.selected.remove(i)
                    else:
                        self.selected.add(i)
                    return

            confirm = pygame.Rect(865, 665, 270, 58)
            if confirm.collidepoint(pos):
                self.check_task()
            return

        # Botón final.
        if len(self.completed) == 4:
            final_button = pygame.Rect(650, 825, 520, 60)
            if final_button.collidepoint(pos):
                print("[DATA CHEF] CONTINUAR -> SIGUIENTE PASO")
                # Aquí después conectaremos pantalla_05.
                self.running = False
                return

        # Tarjetas ETL.
        for task, rect in zip(self.tasks, self.card_rects):
            if rect.collidepoint(pos):
                self.open_task(task)
                return

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
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

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click(self.logical(event.pos))

            self.draw()

        pygame.quit()


if __name__ == "__main__":
    DataKitchen().run()
