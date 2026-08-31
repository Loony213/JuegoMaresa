import os
import sys
import math
import random
import pygame

pygame.init()

# ============================================================
# DATA CHEF | MARESA
# PANTALLA 05 - RETO DEL CHEF
# Trivia de cultura general sobre calidad de datos
# ============================================================

WIDTH, HEIGHT = 1536, 864
FPS = 60

ORANGE = (238, 112, 0)
ORANGE_DARK = (195, 82, 0)
CREAM = (247, 242, 232)
CREAM_2 = (255, 249, 239)
DARK = (47, 58, 68)
NAVY = (36, 64, 88)
BLUE = (47, 128, 190)
GREEN = (46, 154, 89)
RED = (205, 61, 44)
GRAY = (115, 126, 137)
LIGHT_GRAY = (225, 229, 232)
WHITE = (255, 255, 255)

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")


# ------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------

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
                    (max(1, int(w * scale)), max(1, int(h * scale)))
                )

        return img

    except Exception as e:
        print("[DATA CHEF] Error cargando", name, ":", e)
        return None


def rounded_rect(surface, rect, color, radius=20, border=0, border_color=None):
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
    rendered = font.render(value, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(rendered, rect)
    return rect


def draw_centered_lines(surface, lines, font, color, center_x, start_y, gap=8):
    y = start_y

    for line in lines:
        img = font.render(line, True, color)
        rect = img.get_rect(center=(center_x, y + img.get_height() // 2))
        surface.blit(img, rect)
        y += img.get_height() + gap


# ------------------------------------------------------------
# FONDO DECORATIVO
# ------------------------------------------------------------

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
        layer = pygame.Surface((self.r * 2 + 4, self.r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            layer,
            (255, 255, 255, self.alpha),
            (self.r + 2, self.r + 2),
            self.r
        )
        surface.blit(layer, (int(self.x - self.r), int(self.y - self.r)))


# ------------------------------------------------------------
# APP
# ------------------------------------------------------------

class TriviaApp:

    def __init__(self):
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("DATA CHEF | MARESA - Reto del Chef")

        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True
        self.time = 0.0

        self.scale = 1.0
        self.ox = 0
        self.oy = 0

        # ----------------------------------------------------
        # IMÁGENES
        # ----------------------------------------------------

        self.logo = load_img("logo_maresa.png", (180, 70))

        # Se prueban varios nombres para mantener compatibilidad
        self.chef = None
        for name in [
            "chef_trivia.png",
            "chef_limpieza.png",
            "chef_jugando.png",
            "chef_pensando.png",
            "chef.png"
        ]:
            img = load_img(name, (330, 420))
            if img:
                self.chef = img
                print("[DATA CHEF] Chef trivia:", name)
                break

        # ----------------------------------------------------
        # PREGUNTAS
        # ----------------------------------------------------

        self.questions = [
            {
                "title": "PREGUNTA 1 DE 3",
                "question": "¿Qué problema ocurre cuando la misma información aparece varias veces?",
                "options": [
                    ("A", "Duplicados"),
                    ("B", "Formatos"),
                    ("C", "Visualizaciones"),
                    ("D", "Gráficos")
                ],
                "correct": 0,
                "explanation": "¡Correcto! Los datos duplicados pueden alterar los resultados de un análisis."
            },
            {
                "title": "PREGUNTA 2 DE 3",
                "question": "¿Qué es un dato nulo?",
                "options": [
                    ("A", "Información que está vacía o falta"),
                    ("B", "Información secreta"),
                    ("C", "Información duplicada"),
                    ("D", "Información incorrecta")
                ],
                "correct": 0,
                "explanation": "¡Muy bien! Un dato nulo representa información que falta o está vacía."
            },
            {
                "title": "PREGUNTA 3 DE 3",
                "question": "¿Por qué validamos los datos?",
                "options": [
                    ("A", "Para hacerlos más bonitos"),
                    ("B", "Para aumentar el tamaño del archivo"),
                    ("C", "Para comprobar que sean correctos y tengan sentido"),
                    ("D", "Para crear más gráficos")
                ],
                "correct": 2,
                "explanation": "¡Excelente! Validar ayuda a comprobar que la información sea correcta y confiable."
            }
        ]

        self.current_question = 0
        self.selected = None
        self.result = None
        self.feedback_timer = 0.0

        self.completed = False
        self.show_intro = True

        self.bubbles = [Bubble() for _ in range(42)]

        # ----------------------------------------------------
        # FUENTES
        # ----------------------------------------------------

        self.fonts = {
            "small": pygame.font.SysFont("Arial", 17),
            "medium": pygame.font.SysFont("Arial", 22),
            "medium_bold": pygame.font.SysFont("Arial", 22, bold=True),
            "large": pygame.font.SysFont("Arial", 31, bold=True),
            "title": pygame.font.SysFont("Arial", 46, bold=True),
            "big": pygame.font.SysFont("Arial", 60, bold=True),
            "question": pygame.font.SysFont("Arial", 30, bold=True),
            "option": pygame.font.SysFont("Arial", 23, bold=True),
            "feedback": pygame.font.SysFont("Arial", 25, bold=True),
        }

        self.option_rects = []

    # --------------------------------------------------------
    # ESCALA / MOUSE
    # --------------------------------------------------------

    def logical(self, pos):
        return (
            int((pos[0] - self.ox) / self.scale),
            int((pos[1] - self.oy) / self.scale)
        )

    # --------------------------------------------------------
    # FONDO
    # --------------------------------------------------------

    def draw_background(self):
        # Cielo / degradado manual
        for y in range(HEIGHT):
            t = y / HEIGHT

            if y < 150:
                c = CREAM
            else:
                tt = min(1, (y - 150) / 714)
                c = (
                    int(100 + (39 - 100) * tt),
                    int(174 + (56 - 174) * tt),
                    int(220 + (67 - 220) * tt)
                )

            pygame.draw.line(self.screen, c, (0, y), (WIDTH, y))

        # Zona inferior
        pygame.draw.rect(self.screen, (222, 216, 205), (0, 690, WIDTH, HEIGHT - 690))

        # Burbujas
        for bubble in self.bubbles:
            bubble.draw(self.screen)

        # Nubes simples
        self.draw_cloud(70, 190, 1.0)
        self.draw_cloud(1435, 210, 0.9)

    def draw_cloud(self, x, y, scale):
        col = (255, 255, 255)

        pygame.draw.circle(self.screen, col, (int(x), int(y)), int(30 * scale))
        pygame.draw.circle(self.screen, col, (int(x + 40 * scale), int(y - 15 * scale)), int(42 * scale))
        pygame.draw.circle(self.screen, col, (int(x + 85 * scale), int(y)), int(32 * scale))
        pygame.draw.rect(
            self.screen,
            col,
            pygame.Rect(
                int(x - 25 * scale),
                int(y),
                int(140 * scale),
                int(35 * scale)
            ),
            border_radius=int(15 * scale)
        )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    def draw_header(self):
        pygame.draw.rect(self.screen, ORANGE, (0, 0, WIDTH, 112))

        # Logo
        if self.logo:
            self.screen.blit(self.logo, (45, 22))
        else:
            pygame.draw.circle(self.screen, WHITE, (78, 55), 26)
            text(
                self.screen,
                "maresa",
                self.fonts["small"],
                WHITE,
                (45, 83)
            )

        # Título
        text(
            self.screen,
            "LA COCINA DE LOS DATOS",
            self.fonts["title"],
            WHITE,
            (405, 30)
        )

        text(
            self.screen,
            "PASO 3 • RETO DEL CHEF",
            self.fonts["medium_bold"],
            WHITE,
            (1280, 47)
        )

    # --------------------------------------------------------
    # CHEF / BURBUJA
    # --------------------------------------------------------

    def draw_chef_area(self):
        # Sombra
        pygame.draw.ellipse(
            self.screen,
            (177, 170, 160),
            (170, 650, 350, 38)
        )

        # Chef
        if self.chef:
            bob = math.sin(self.time * 2.0) * 7
            rect = self.chef.get_rect()
            rect.midbottom = (340, int(685 + bob))
            self.screen.blit(self.chef, rect)
        else:
            # Fallback visual si no existe una imagen
            pygame.draw.circle(self.screen, (255, 218, 177), (340, 535), 72)
            pygame.draw.circle(self.screen, WHITE, (340, 450), 58)
            pygame.draw.circle(self.screen, WHITE, (300, 470), 34)
            pygame.draw.circle(self.screen, WHITE, (380, 470), 34)
            pygame.draw.rect(self.screen, WHITE, (270, 595, 140, 90), border_radius=30)
            text(self.screen, "CHEF", self.fonts["medium_bold"], ORANGE, (340, 635), True)

        # Burbuja de diálogo
        bubble = pygame.Rect(475, 170, 500, 175)

        rounded_rect(
            self.screen,
            bubble,
            CREAM_2,
            32,
            3,
            (231, 182, 122)
        )

        # Pico de la burbuja
        pygame.draw.polygon(
            self.screen,
            CREAM_2,
            [(500, 305), (450, 350), (545, 318)]
        )

        pygame.draw.line(
            self.screen,
            (231, 182, 122),
            (500, 305),
            (450, 350),
            3
        )

        text(
            self.screen,
            "🧠",
            self.fonts["large"],
            DARK,
            (515, 192)
        )

        lines = [
            "“¡Muy bien! Ya limpiamos nuestros datos.",
            "Ahora veamos cuánto aprendiste",
            "sobre la calidad de la información.”"
        ]

        draw_centered_lines(
            self.screen,
            lines,
            self.fonts["medium_bold"],
            DARK,
            735,
            205,
            5
        )

    # --------------------------------------------------------
    # TARJETA DE INTRO
    # --------------------------------------------------------

    def draw_intro(self):
        self.draw_background()
        self.draw_header()
        self.draw_chef_area()

        card = pygame.Rect(990, 165, 460, 455)

        rounded_rect(
            self.screen,
            card,
            CREAM_2,
            30,
            3,
            ORANGE
        )

        text(
            self.screen,
            "RETO DEL CHEF",
            self.fonts["title"],
            ORANGE,
            (1220, 225),
            True
        )

        pygame.draw.circle(
            self.screen,
            (255, 237, 211),
            (1220, 330),
            62
        )

        text(
            self.screen,
            "?",
            self.fonts["big"],
            ORANGE,
            (1220, 326),
            True
        )

        intro_lines = [
            "Responde 3 preguntas rápidas",
            "sobre lo que acabas de aprender",
            "en la limpieza y validación",
            "de los datos."
        ]

        draw_centered_lines(
            self.screen,
            intro_lines,
            self.fonts["medium"],
            DARK,
            1220,
            405,
            9
        )

        btn = pygame.Rect(1095, 535, 250, 62)
        mouse = self.logical(pygame.mouse.get_pos())

        hover = btn.collidepoint(mouse)
        offset = -4 if hover else 0

        rounded_rect(
            self.screen,
            btn.move(0, offset),
            ORANGE,
            18
        )

        text(
            self.screen,
            "COMENZAR  ▶",
            self.fonts["option"],
            WHITE,
            (btn.centerx, btn.centery + offset),
            True
        )

    # --------------------------------------------------------
    # QUIZ
    # --------------------------------------------------------

    def draw_quiz(self):
        self.draw_background()
        self.draw_header()
        self.draw_chef_area()

        q = self.questions[self.current_question]

        # Contenedor principal
        panel = pygame.Rect(790, 145, 670, 570)

        rounded_rect(
            self.screen,
            panel,
            CREAM_2,
            28,
            3,
            (206, 151, 91)
        )

        # Indicador
        indicator = pygame.Rect(970, 172, 310, 42)
        rounded_rect(
            self.screen,
            indicator,
            NAVY,
            18
        )

        text(
            self.screen,
            q["title"],
            self.fonts["medium_bold"],
            WHITE,
            indicator.center,
            True
        )

        # Progreso
        for i in range(3):
            color = ORANGE if i <= self.current_question else LIGHT_GRAY
            pygame.draw.circle(
                self.screen,
                color,
                (1350 + i * 30, 193),
                7
            )

        # Pregunta
        question_box = pygame.Rect(845, 240, 560, 95)

        lines = self.wrap_text(
            q["question"],
            self.fonts["question"],
            question_box.width - 20
        )

        draw_centered_lines(
            self.screen,
            lines,
            self.fonts["question"],
            DARK,
            question_box.centerx,
            question_box.y + 8,
            5
        )

        # Opciones
        self.option_rects = []

        option_y = 365
        for i, (letter, label) in enumerate(q["options"]):
            rect = pygame.Rect(850, option_y + i * 75, 550, 58)
            self.option_rects.append(rect)

            mouse = self.logical(pygame.mouse.get_pos())
            hover = rect.collidepoint(mouse)

            fill = WHITE
            border = (190, 198, 202)

            if self.selected == i:
                if self.result is None:
                    fill = (255, 241, 218)
                    border = ORANGE

                elif i == q["correct"]:
                    fill = (220, 245, 228)
                    border = GREEN

                elif self.result is False:
                    fill = (252, 224, 220)
                    border = RED

            elif self.result is not None and i == q["correct"]:
                fill = (220, 245, 228)
                border = GREEN

            elif hover and self.result is None:
                fill = (250, 246, 239)
                border = ORANGE

            rounded_rect(
                self.screen,
                rect,
                fill,
                14,
                2,
                border
            )

            # Círculo letra
            circle_color = border
            pygame.draw.circle(
                self.screen,
                circle_color,
                (rect.x + 32, rect.centery),
                18
            )

            text(
                self.screen,
                letter,
                self.fonts["medium_bold"],
                WHITE,
                (rect.x + 32, rect.centery),
                True
            )

            text(
                self.screen,
                label,
                self.fonts["option"],
                DARK,
                (rect.x + 68, rect.centery),
                True
            )

        # Feedback
        if self.result is not None:
            feedback = pygame.Rect(835, 690, 580, 72)

            color = GREEN if self.result else RED
            fill = (224, 247, 231) if self.result else (255, 230, 225)

            rounded_rect(
                self.screen,
                feedback,
                fill,
                16,
                2,
                color
            )

            msg = q["explanation"] if self.result else "Casi... observa la respuesta correcta e inténtalo nuevamente."

            text(
                self.screen,
                "✓" if self.result else "!",
                self.fonts["feedback"],
                color,
                (feedback.x + 25, feedback.centery),
                True
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
                feedback.centerx + 15,
                feedback.y + 15,
                2
            )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    def draw_completed(self):
        self.draw_background()
        self.draw_header()

        # Tarjeta principal
        card = pygame.Rect(360, 165, 820, 510)

        rounded_rect(
            self.screen,
            card,
            CREAM_2,
            35,
            4,
            ORANGE
        )

        # Decoración
        pygame.draw.circle(self.screen, (255, 232, 196), (770, 310), 92)
        pygame.draw.circle(self.screen, ORANGE, (770, 310), 72)

        text(
            self.screen,
            "★",
            pygame.font.SysFont("Arial", 65, bold=True),
            WHITE,
            (770, 302),
            True
        )

        text(
            self.screen,
            "¡EXCELENTE TRABAJO!",
            self.fonts["big"],
            ORANGE,
            (770, 425),
            True
        )

        completed_lines = [
            "Ahora sabes que antes de analizar información",
            "debemos asegurarnos de que nuestros datos",
            "sean confiables y tengan calidad."
        ]

        draw_centered_lines(
            self.screen,
            completed_lines,
            self.fonts["medium_bold"],
            DARK,
            770,
            495,
            8
        )

        btn = pygame.Rect(600, 595, 340, 64)
        mouse = self.logical(pygame.mouse.get_pos())
        hover = btn.collidepoint(mouse)

        rounded_rect(
            self.screen,
            btn.move(0, -4 if hover else 0),
            ORANGE,
            18
        )

        text(
            self.screen,
            "CONTINUAR  ▶",
            self.fonts["option"],
            WHITE,
            (btn.centerx, btn.centery - (4 if hover else 0)),
            True
        )

    # --------------------------------------------------------
    # TEXTO CON WRAP
    # --------------------------------------------------------

    def wrap_text(self, value, font, max_width):
        words = value.split()
        lines = []
        current = ""

        for word in words:
            test = word if not current else current + " " + word

            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    # --------------------------------------------------------
    # DIBUJO PRINCIPAL
    # --------------------------------------------------------

    def draw(self):
        if self.show_intro:
            self.draw_intro()

        elif self.completed:
            self.draw_completed()

        else:
            self.draw_quiz()

        # Escalar a la ventana
        ww, wh = self.window.get_size()

        self.scale = min(ww / WIDTH, wh / HEIGHT)

        rw = max(1, int(WIDTH * self.scale))
        rh = max(1, int(HEIGHT * self.scale))

        self.ox = (ww - rw) // 2
        self.oy = (wh - rh) // 2

        scaled = pygame.transform.smoothscale(self.screen, (rw, rh))

        self.window.fill((220, 220, 220))
        self.window.blit(scaled, (self.ox, self.oy))

        pygame.display.flip()

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    def handle_click(self, pos):
        # INTRO
        if self.show_intro:
            if pygame.Rect(1095, 535, 250, 62).collidepoint(pos):
                self.show_intro = False
                print("[DATA CHEF] RETO DEL CHEF -> COMENZAR")
            return

        # FINAL
        if self.completed:
            if pygame.Rect(600, 595, 340, 64).collidepoint(pos):
                print("[DATA CHEF] RETO COMPLETADO -> SIGUIENTE PASO")

                # Aquí conectaremos la pantalla 06 cuando exista.
                # Por ahora se cierra correctamente.
                self.running = False

            return

        # QUIZ
        if self.result is not None:
            return

        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                self.selected = i

                q = self.questions[self.current_question]

                if i == q["correct"]:
                    self.result = True
                    self.feedback_timer = 1.4
                    print("[DATA CHEF] RESPUESTA CORRECTA")

                else:
                    self.result = False
                    self.feedback_timer = 1.8
                    print("[DATA CHEF] RESPUESTA INCORRECTA")

                break

    # --------------------------------------------------------
    # ACTUALIZACIÓN
    # --------------------------------------------------------

    def update(self, dt):
        self.time += dt

        for bubble in self.bubbles:
            bubble.update(dt)

        if not self.show_intro and not self.completed and self.result is not None:
            self.feedback_timer -= dt

            if self.feedback_timer <= 0:
                if self.result:
                    self.current_question += 1

                    if self.current_question >= len(self.questions):
                        self.completed = True
                        print("[DATA CHEF] TRIVIA COMPLETADA")
                    else:
                        self.selected = None
                        self.result = None

                else:
                    # Si se equivoca, puede volver a intentar la misma pregunta
                    self.selected = None
                    self.result = None

    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

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
                        self.handle_click(self.logical(event.pos))

            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    TriviaApp().run()
