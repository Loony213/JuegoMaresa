
import os, sys, math, random, pygame

pygame.init()
WIDTH, HEIGHT, FPS = 1536, 864, 60

BG = (246, 242, 234)
ORANGE = (235, 103, 13)
DARK = (45, 52, 59)
WHITE = (255, 255, 255)
SKY = (104, 184, 231)
ROAD = (82, 84, 82)

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
                s = min(mw / w, mh / h)
                img = pygame.transform.smoothscale(img, (int(w*s), int(h*s)))
        return img
    except Exception as e:
        print("[DATA CHEF] Error:", path, e)
        return None

def rr(s, r, c, radius=18, border=0, bc=None):
    pygame.draw.rect(s, c, r, border_radius=radius)
    if border:
        pygame.draw.rect(s, bc or c, r, width=border, border_radius=radius)

def txt(s, v, f, c, p, center=False):
    a = f.render(v, True, c)
    r = a.get_rect()
    if center:
        r.center = p
    else:
        r.topleft = p
    s.blit(a, r)
    return r

def load_first_img(candidates, max_size=None, label="imagen"):
    """
    Carga la primera imagen que exista. Esto evita romper el juego si
    anteriormente ya tenías los edificios con sus nombres originales.
    """
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

class Market:
    def __init__(self):
        self.window = pygame.display.set_mode((0,0), pygame.RESIZABLE)
        pygame.display.set_caption("DATA CHEF | El Mercado de los Ingredientes")
        self.screen = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.running = True
        self.scale, self.ox, self.oy = 1, 0, 0
        self.t = 0
        self.mode = "intro"
        self.player_x = 790.0
        self.player_y = 792.0
        self.player_speed = 280.0
        self.player_moving = False
        self.score = 1250
        self.feedback = ""

        # Personaje del minijuego.
        self.player_img = load_img("chef_jugando.png", (105, 145))
        if self.player_img is None:
            self.player_img = load_img("chef.png", (105, 145))

        self.building_info = [
            {"short": "BASE DE DATOS", "correct": True, "color": (35,115,205)},
            {"short": "ARCHIVO EXCEL", "correct": False, "color": (230,145,35)},
            {"short": "FUENTE EXTERNA", "correct": False, "color": (190,55,38)},
            {"short": "MENSAJE / CHAT", "correct": False, "color": (118,74,145)},
        ]

        # Posiciones de los edificios cuando inicia el minijuego.
        self.game_building_positions = [
            (240, 555),
            (1310, 555),
            (500, 790),
            (1110, 790),
        ]

        # =====================================================
        # CONFIGURACIÓN DE CALLES DEL MINIJUEGO
        # =====================================================
        # Puedes ajustar estos valores si luego quieres calles
        # más anchas o una rotonda más grande.
        self.road_width = 74
        self.roundabout_radius = 92
        self.roundabout_inner = 44

        # Se generan curvas, no líneas rectas.
        self.road_paths = self.build_road_paths()

        self.font = {
            "tiny": pygame.font.SysFont("Arial", 14),
            "small": pygame.font.SysFont("Arial", 17),
            "body": pygame.font.SysFont("Arial", 20),
            "bold": pygame.font.SysFont("Arial", 21, bold=True),
            "shop": pygame.font.SysFont("Arial", 18, bold=True),
            "title": pygame.font.SysFont("Arial", 43, bold=True),
            "subtitle": pygame.font.SysFont("Arial", 25, bold=True),
            "thought": pygame.font.SysFont("Arial", 20, bold=True),
            "button": pygame.font.SysFont("Arial", 23, bold=True)
        }

        # =====================================================
        # SUBE / REEMPLAZA ESTOS PNG EN assets/
        # =====================================================
        self.chef_img = load_img("chef_pensando.png", (390, 555))

        # =====================================================
        # EDIFICIOS
        # Se restauran los nombres originales que ya venías usando.
        # Los nombres edificio_1.png ... edificio_4.png quedan solo
        # como respaldo por si alguno de tus archivos antiguos usa esos.
        # =====================================================
        self.building_files = [
            (
                "BASE DE DATOS",
                [
                    "edificio_bases_datos.png",
                    "edificio_1.png",
                ],
            ),
            (
                "ARCHIVO EXCEL",
                [
                    "edificio_archivos_excel.png",
                    "edificio_2.png",
                ],
            ),
            (
                "FUENTE EXTERNA",
                [
                    "edificio_fuentes_externas.png",
                    "edificio_fuentes_datos.png",
                    "edificio_3.png",
                ],
            ),
            (
                "MENSAJE / CHAT",
                [
                    "edificio_mensaje_chat.png",
                    "edificio_mensaje.png",
                    "edificio_chat.png",
                    "edificio_apis_sistemas.png",
                    "edificio_4.png",
                ],
            ),
        ]

        self.buildings = []
        self.building_loaded_names = []

        for label, candidates in self.building_files:
            img, used_name = load_first_img(
                candidates,
                (240, 380),
                label=label
            )
            self.buildings.append(img)
            self.building_loaded_names.append(used_name)

        self.logo = load_img("logo_maresa.png", (225,65))

        # Animación de pensamiento
        self.thought = 0.0
        self.bubbles = 0.0
        self.particles = [
            [random.randrange(WIDTH), random.randrange(125,640), random.uniform(.15,.55)]
            for _ in range(45)
        ]

    def logical(self, p):
        return (int((p[0]-self.ox)/self.scale), int((p[1]-self.oy)/self.scale))

    def background(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, SKY, (0,125,WIDTH,515))

        # edificios lejanos
        for x,y,w,h in [(0,330,105,310),(90,300,100,340),(1180,290,115,350),
                        (1290,250,95,390),(1400,315,136,325)]:
            pygame.draw.rect(self.screen,(170,180,183),(x,y,w,h))
            for wx in range(x+12,x+w-10,24):
                for wy in range(y+20,y+h-20,30):
                    pygame.draw.rect(self.screen,(210,218,218),(wx,wy,11,14))

        # nubes
        for x,y in [(45,185),(1450,175)]:
            pygame.draw.circle(self.screen,WHITE,(x,y),42)
            pygame.draw.circle(self.screen,WHITE,(x+38,y+8),31)
            pygame.draw.circle(self.screen,WHITE,(x-38,y+10),30)

        # árboles
        for x,y in [(70,545),(370,565),(1100,550),(1490,550)]:
            pygame.draw.rect(self.screen,(101,70,44),(x-6,y,12,75))
            pygame.draw.circle(self.screen,(55,126,53),(x,y),42)
            pygame.draw.circle(self.screen,(68,140,61),(x-23,y+10),28)
            pygame.draw.circle(self.screen,(52,113,46),(x+25,y+10),29)

        pygame.draw.rect(self.screen,(219,213,198),(0,625,WIDTH,17))
        pygame.draw.rect(self.screen,ROAD,(0,642,WIDTH,222))

        for x in range(-100,WIDTH+100,185):
            pygame.draw.polygon(self.screen,(235,231,213),
                [(x,750),(x+65,750),(x+35,767),(x-30,767)])

        for p in self.particles:
            p[1] -= p[2]
            if p[1] < 130: p[1] = 630
            pygame.draw.circle(self.screen,(255,255,255),(int(p[0]),int(p[1])),2)

    def header(self):
        pygame.draw.rect(self.screen,(252,249,243),(0,0,WIDTH,125))
        pygame.draw.line(self.screen,ORANGE,(0,124),(WIDTH,124),2)

        if self.logo:
            self.screen.blit(self.logo,(32,30))
        else:
            txt(self.screen,"maresa",self.font["title"],ORANGE,(35,30))

        txt(self.screen,"🛒 EL MERCADO DE LOS INGREDIENTES",
            self.font["title"],ORANGE,(345,35))
        txt(self.screen,"PRIMER PASO: CONSEGUIR DATOS DE CALIDAD",
            self.font["subtitle"],DARK,(520,94))

        back=pygame.Rect(1340,28,155,55)
        rr(self.screen,back,WHITE,28,2,(246,185,125))
        txt(self.screen,"←  VOLVER",self.font["bold"],ORANGE,back.center,True)

    def thought_cloud(self):
        # La nube aparece con escala + rebote, no de golpe.
        self.thought=min(1.0,self.thought+0.018)
        self.bubbles=min(1.0,self.bubbles+0.024)

        # Burbujas que conectan al chef con el pensamiento.
        for i,(x,y,r) in enumerate([(318,430,12),(342,393,18),(370,355,24)]):
            p=max(0,min(1,self.bubbles*1.2-i*.18))
            if p:
                rradius=int(r*(.45+.55*p))
                pygame.draw.circle(self.screen,(255,249,239),(x,y),rradius)
                pygame.draw.circle(self.screen,(224,204,183),(x,y),rradius,2)

        p=self.thought
        scale=.12 + .88*(1-(1-p)**3)
        if p > .82:
            scale += math.sin((p-.82)*24)*.025

        alpha=min(255,int(255*min(1,p*1.8)))
        w,h=int(500*scale),int(270*scale)
        layer=pygame.Surface((w+70,h+70),pygame.SRCALPHA)
        cx,cy=(w+70)//2,(h+70)//2

        cloud=[
            (-.33,0,.29),(-.20,-.18,.34),(0,-.26,.38),
            (.20,-.20,.35),(.34,0,.31),(.23,.16,.33),
            (0,.19,.35),(-.23,.14,.31)
        ]
        for dx,dy,r in cloud:
            pygame.draw.circle(layer,(222,202,181,int(alpha*.25)),
                (int(cx+dx*w+5),int(cy+dy*h+7)),int(r*h))
        for dx,dy,r in cloud:
            pygame.draw.circle(layer,(255,249,239,alpha),
                (int(cx+dx*w),int(cy+dy*h)),int(r*h))

        pygame.draw.rect(layer,(255,249,239,alpha),
            (int(w*.10),int(h*.20),int(w*.80),int(h*.48)),
            border_radius=int(h*.20))

        self.screen.blit(layer,(500-(w+70)//2,280-(h+70)//2))

        if p>.45:
            lines=[
                "“Primero iremos al mercado",
                "a buscar nuestros ingredientes.”",
                "",
                "Las bases de datos, fuentes de",
                "calidad y sistemas serán la materia",
                "prima de nuestro panel.”"
            ]
            y=187
            for line in lines:
                if line:
                    txt(self.screen,line,self.font["thought"],DARK,(500,y),True)
                    y+=27
                else:
                    y+=10

    def draw_chef(self):
        if self.chef_img:
            bob=math.sin(self.t*2.2)*3
            r=self.chef_img.get_rect()
            r.midbottom=(190,int(850+bob))
            self.screen.blit(self.chef_img,r)
        else:
            pygame.draw.circle(self.screen,(255,190,120),(180,430),70)
            txt(self.screen,"SUBE",self.font["bold"],DARK,(180,415),True)
            txt(self.screen,"chef_pensando.png",self.font["small"],DARK,(180,450),True)

        self.thought_cloud()

    def draw_buildings(self, game=False):
        if not game:
            # Escena original: SIN CAMINOS.
            positions = [
                (520, 650),
                (790, 625),
                (1060, 625),
                (1320, 650)
            ]
        else:
            # Minijuego: edificios separados para que se vean los caminos.
            positions = self.game_building_positions

        for index, (img, position) in enumerate(
            zip(self.buildings, positions)
        ):
            x, y = position

            shadow = pygame.Surface((230, 25), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0,0,0,70), (0,0,230,25))
            self.screen.blit(shadow, (x-115, y-8))

            if img:
                rect = img.get_rect()
                rect.midbottom = (x, y)
                self.screen.blit(img, rect)
            else:
                rect = pygame.Rect(x-90, y-250, 180, 250)
                rr(
                    self.screen,
                    rect,
                    self.building_info[index]["color"],
                    10,
                    2,
                    WHITE
                )
                txt(
                    self.screen,
                    f"EDIFICIO {index+1}",
                    self.font["shop"],
                    WHITE,
                    rect.center,
                    True
                )

            if game:
                label = pygame.Rect(x-105, y+5, 210, 32)
                rr(
                    self.screen,
                    label,
                    (255,249,239),
                    11,
                    2,
                    self.building_info[index]["color"]
                )
                txt(
                    self.screen,
                    self.building_info[index]["short"],
                    self.font["small"],
                    self.building_info[index]["color"],
                    label.center,
                    True
                )

    def bottom(self):
        box=pygame.Rect(430,800,930,64)
        rr(self.screen,box,(255,249,239),22,2,(236,177,112))
        pygame.draw.circle(self.screen,ORANGE,(478,832),22)
        txt(self.screen,"★",self.font["bold"],WHITE,(478,832),True)
        txt(self.screen,"Las bases de datos y fuentes confiables",
            self.font["bold"],DARK,(520,815))
        txt(self.screen,"son la clave para recetas de calidad.",
            self.font["bold"],DARK,(520,841))

        b=pygame.Rect(950,811,390,45)
        hover=b.collidepoint(self.logical(pygame.mouse.get_pos()))
        if hover: b=b.move(0,-2)
        rr(self.screen,b,ORANGE,12)
        txt(self.screen,"🛒  EMPEZAR  →",
            self.font["button"],WHITE,b.center,True)

    # =====================================================
    # MINIJUEGO: CALLES CUADRADAS TIPO MAPA URBANO
    # =====================================================

    def build_road_paths(self):
        """
        Red de calles tipo ciudad: tramos horizontales y verticales,
        con esquinas redondeadas visualmente. No usa diagonales largas.
        """
        cx, cy = 790, 700

        return [
            [
                (cx - 88, cy),
                (650, cy),
                (650, 610),
                (430, 610),
                (430, 555),
                (240, 555),
            ],
            [
                (cx + 88, cy),
                (930, cy),
                (930, 610),
                (1160, 610),
                (1160, 555),
                (1310, 555),
            ],
            [
                (cx - 88, cy),
                (650, cy),
                (650, 775),
                (560, 775),
                (560, 790),
                (500, 790),
            ],
            [
                (cx + 88, cy),
                (930, cy),
                (930, 775),
                (1040, 775),
                (1040, 790),
                (1110, 790),
            ],
        ]

    def draw_road(self, points, width=None):
        if len(points) < 2:
            return
        if width is None:
            width = self.road_width

        border_color = (43, 47, 48)
        line_color = (236, 231, 213)

        pygame.draw.lines(self.screen, border_color, False, points, width + 12)
        outer_r = (width + 12) // 2
        for x, y in points:
            pygame.draw.circle(self.screen, border_color, (int(x), int(y)), outer_r)

        pygame.draw.lines(self.screen, ROAD, False, points, width)
        inner_r = width // 2
        for x, y in points:
            pygame.draw.circle(self.screen, ROAD, (int(x), int(y)), inner_r)

        dash_len = 22.0
        gap_len = 20.0
        drawing_dash = True
        remaining = dash_len

        for a, b in zip(points[:-1], points[1:]):
            ax, ay = a
            bx, by = b
            dx = bx - ax
            dy = by - ay
            length = math.hypot(dx, dy)
            if length <= 0:
                continue

            ux = dx / length
            uy = dy / length
            pos = 0.0

            while pos < length:
                step = min(remaining, length - pos)

                if drawing_dash and step > 0:
                    p1 = (int(ax + ux * pos), int(ay + uy * pos))
                    p2 = (int(ax + ux * (pos + step)), int(ay + uy * (pos + step)))
                    pygame.draw.line(self.screen, line_color, p1, p2, 4)

                pos += step
                remaining -= step

                if remaining <= 0.001:
                    drawing_dash = not drawing_dash
                    remaining = dash_len if drawing_dash else gap_len

    def draw_game_paths(self):
        for path in self.road_paths:
            self.draw_road(path, self.road_width)

        cx, cy = 790, 700

        pygame.draw.circle(self.screen, (43, 47, 48), (cx, cy), self.roundabout_radius + 8)
        pygame.draw.circle(self.screen, ROAD, (cx, cy), self.roundabout_radius)

        pygame.draw.circle(self.screen, (236, 231, 213), (cx, cy), 67, 4)

        pygame.draw.circle(self.screen, (214, 201, 164), (cx, cy), self.roundabout_inner)
        pygame.draw.circle(self.screen, (88, 125, 66), (cx, cy), 32)
        pygame.draw.circle(self.screen, (63, 102, 55), (cx, cy), 21)

        pygame.draw.rect(
            self.screen,
            (105, 72, 42),
            (cx - 5, cy - 74, 10, 35),
            border_radius=4
        )
        pygame.draw.polygon(
            self.screen,
            (105, 72, 42),
            [(cx, cy - 80), (cx + 48, cy - 57), (cx, cy - 36)]
        )

    def nearest_point_on_segment(self, px, py, ax, ay, bx, by):
        vx = bx - ax
        vy = by - ay
        length_sq = vx*vx + vy*vy

        if length_sq == 0:
            return ax, ay, math.hypot(px-ax, py-ay)

        t = ((px-ax)*vx + (py-ay)*vy) / length_sq
        t = max(0.0, min(1.0, t))

        qx = ax + vx*t
        qy = ay + vy*t

        return qx, qy, math.hypot(px-qx, py-qy)

    def nearest_road_point(self, x, y):
        """
        Busca el punto más cercano dentro de toda la red de calles.
        Sirve para impedir que el personaje salga al césped o edificios.
        """
        best_x = x
        best_y = y
        best_dist = float("inf")

        # Calles curvas.
        for path in self.road_paths:
            for a, b in zip(path[:-1], path[1:]):
                qx, qy, dist = self.nearest_point_on_segment(
                    x, y, a[0], a[1], b[0], b[1]
                )
                if dist < best_dist:
                    best_x, best_y, best_dist = qx, qy, dist

        # Rotonda.
        dx = x - 790
        dy = y - 700
        d = math.hypot(dx, dy)

        # Dentro de la rotonda se puede caminar libremente,
        # excepto dentro de la isla central.
        if self.roundabout_inner <= d <= self.roundabout_radius:
            return x, y, 0.0, "roundabout"

        # Si intenta entrar en la isla central, lo empujamos al borde.
        if d < self.roundabout_inner:
            if d == 0:
                return 790 + self.roundabout_inner, 700, 0.0, "island"
            return (
                790 + dx/d * self.roundabout_inner,
                700 + dy/d * self.roundabout_inner,
                0.0,
                "island"
            )

        # Borde exterior de la rotonda como alternativa.
        if d < best_dist:
            if d == 0:
                qx, qy = 790 + self.roundabout_radius, 700
            else:
                qx = 790 + dx/d * self.roundabout_radius
                qy = 700 + dy/d * self.roundabout_radius
            return qx, qy, d - self.roundabout_radius, "roundabout_edge"

        return best_x, best_y, best_dist, "road"

    def constrain_player_to_roads(self, old_x, old_y):
        """
        Si el jugador intenta salir de la calle, se queda en el punto
        permitido más cercano. Así nunca puede caminar por cualquier lado.
        """
        nx, ny, dist, zone = self.nearest_road_point(
            self.player_x, self.player_y
        )

        # El personaje tiene un poco de margen dentro del asfalto.
        allowed = self.road_width * 0.42

        if zone == "roundabout":
            return

        # La isla central NO es transitable. Si entra, se proyecta
        # inmediatamente al borde interior de la rotonda.
        if zone == "island":
            self.player_x = nx
            self.player_y = ny
            return

        if dist > allowed:
            # Proyección directa al borde permitido de la calle.
            dx = self.player_x - nx
            dy = self.player_y - ny
            d = math.hypot(dx, dy)

            if d > 0:
                self.player_x = nx + dx/d * allowed
                self.player_y = ny + dy/d * allowed
            else:
                self.player_x = nx
                self.player_y = ny

        # Evita que el personaje se meta visualmente dentro del edificio.
        self.player_x = max(45, min(WIDTH-45, self.player_x))
        self.player_y = max(270, min(HEIGHT-20, self.player_y))

    def draw_player(self):
        if self.player_img:
            bob = math.sin(self.t*8)*2 if self.player_moving else 0
            r = self.player_img.get_rect()
            r.midbottom = (
                int(self.player_x),
                int(self.player_y+bob)
            )
            self.screen.blit(self.player_img, r)
        else:
            pygame.draw.circle(
                self.screen, (255,190,120),
                (int(self.player_x), int(self.player_y-45)), 25
            )
            pygame.draw.rect(
                self.screen, WHITE,
                (int(self.player_x-27), int(self.player_y-25), 54, 50),
                border_radius=12
            )

    def draw_game_header(self):
        box = pygame.Rect(510, 180, 560, 58)
        rr(
            self.screen, box, (255,249,239),
            18, 2, (236,177,112)
        )
        txt(
            self.screen,
            "🎯 ENCUENTRA LA FUENTE MÁS CONFIABLE",
            self.font["bold"],
            DARK,
            box.center,
            True
        )

        help_box = pygame.Rect(570, 245, 440, 38)
        rr(self.screen, help_box, WHITE, 16, 1, (220,215,205))
        txt(
            self.screen,
            "W A S D  /  FLECHAS  para caminar",
            self.font["small"],
            DARK,
            help_box.center,
            True
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

        self.player_x += dx * self.player_speed * dt
        self.player_y += dy * self.player_speed * dt

        # IMPORTANTE:
        # Aquí se restringe el movimiento a la red de calles.
        self.constrain_player_to_roads(old_x, old_y)

        self.check_building_collision()

    def check_building_collision(self):
        for index, (bx, by) in enumerate(self.game_building_positions):
            dx = self.player_x - bx
            dy = self.player_y - by

            if math.hypot(dx, dy) < 125:
                info = self.building_info[index]

                if info["correct"]:
                    self.mode = "success"
                    self.score += 250
                    self.feedback = "¡CORRECTO! Elegiste la Base de Datos Corporativa."
                    print("[DATA CHEF] RESPUESTA CORRECTA")
                else:
                    self.mode = "wrong"
                    self.feedback = "Esta fuente tiene riesgos para la calidad de los datos."
                    print("[DATA CHEF] FUENTE INCORRECTA:", info["short"])
                return

    def draw_game(self):
        self.background()
        self.header()
        self.draw_game_paths()
        self.draw_buildings(game=True)
        self.draw_game_header()
        self.draw_player()

        score = pygame.Rect(1180, 28, 300, 50)
        rr(self.screen, score, (38,69,96), 22)
        txt(
            self.screen,
            f"⭐ {self.score}  |  Chef de TECNOLOGÍA",
            self.font["small"],
            WHITE,
            score.center,
            True
        )

    def draw_success(self):
        self.draw_game()

        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((15,35,25,145))
        self.screen.blit(overlay, (0,0))

        panel = pygame.Rect(445, 280, 645, 285)
        rr(self.screen, panel, (255,249,239), 28, 4, (49,142,78))

        pygame.draw.circle(
            self.screen,
            (49,142,78),
            (768,350),
            45 + int(math.sin(self.t*4)*4)
        )
        txt(
            self.screen,
            "✓",
            pygame.font.SysFont("Arial",55,bold=True),
            WHITE,
            (768,350),
            True
        )
        txt(
            self.screen,
            "¡INGREDIENTE CORRECTO!",
            self.font["button"],
            (49,142,78),
            (768,420),
            True
        )
        txt(
            self.screen,
            "BASE DE DATOS CORPORATIVA",
            self.font["bold"],
            DARK,
            (768,458),
            True
        )
        txt(
            self.screen,
            "La fuente más confiable para comenzar.",
            self.font["body"],
            DARK,
            (768,492),
            True
        )
        txt(
            self.screen,
            "+250 puntos",
            self.font["bold"],
            ORANGE,
            (768,530),
            True
        )

        button = pygame.Rect(625, 575, 285, 52)
        rr(self.screen, button, ORANGE, 16)
        txt(
            self.screen,
            "CONTINUAR  →",
            self.font["small"],
            WHITE,
            button.center,
            True
        )

    def draw_wrong(self):
        self.draw_game()

        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((80,25,20,125))
        self.screen.blit(overlay, (0,0))

        panel = pygame.Rect(455, 305, 625, 235)
        rr(self.screen, panel, (255,249,239), 28, 4, (190,55,38))

        txt(
            self.screen,
            "⚠ ESA FUENTE NO ES LA MEJOR OPCIÓN",
            self.font["button"],
            (190,55,38),
            (768,370),
            True
        )
        txt(
            self.screen,
            self.feedback,
            self.font["body"],
            DARK,
            (768,420),
            True
        )
        txt(
            self.screen,
            "Haz clic para volver al centro.",
            self.font["small"],
            DARK,
            (768,458),
            True
        )

        button = pygame.Rect(625,490,285,45)
        rr(self.screen, button, ORANGE, 14)
        txt(
            self.screen,
            "INTENTAR DE NUEVO",
            self.font["small"],
            WHITE,
            button.center,
            True
        )

    def draw(self):
        self.screen.fill(BG)

        if self.mode == "intro":
            # Pantalla ORIGINAL. Aquí NO hay caminos.
            self.background()
            self.header()
            self.draw_chef()
            self.draw_buildings()
            self.bottom()

        elif self.mode == "game":
            self.draw_game()

        elif self.mode == "success":
            self.draw_success()

        elif self.mode == "wrong":
            self.draw_wrong()

        ww, wh = self.window.get_size()
        self.scale = min(ww/WIDTH, wh/HEIGHT)
        rw, rh = int(WIDTH*self.scale), int(HEIGHT*self.scale)
        self.ox = (ww-rw)//2
        self.oy = (wh-rh)//2

        scaled = pygame.transform.smoothscale(
            self.screen,
            (rw,rh)
        )

        self.window.fill((230,230,230))
        self.window.blit(scaled, (self.ox,self.oy))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

                elif e.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode(
                        e.size,
                        pygame.RESIZABLE
                    )

                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.running = False

                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    pos = self.logical(e.pos)

                    if self.mode == "intro":
                        if pygame.Rect(1340,28,155,55).collidepoint(pos):
                            self.running = False

                        # IMPORTANTE:
                        # Este es el botón que antes decía
                        # "EXPLORAR INGREDIENTES".
                        elif pygame.Rect(950,811,390,45).collidepoint(pos):
                            self.mode = "game"
                            self.player_x = 790.0
                            self.player_y = 792.0
                            print("[DATA CHEF] EMPEZAR -> MINIJUEGO")
                            print("[DATA CHEF] Caminos activados")

                    elif self.mode == "wrong":
                        button = pygame.Rect(625,490,285,45)

                        if button.collidepoint(pos):
                            self.mode = "game"
                            self.player_x = 790.0
                            self.player_y = 792.0
                            print("[DATA CHEF] Reintento")

                    elif self.mode == "success":
                        button = pygame.Rect(625, 575, 285, 52)

                        if button.collidepoint(pos):
                            pantalla_04 = os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                "pantalla_04_limpieza.py"
                            )

                            print("[DATA CHEF] CONTINUAR -> PANTALLA 04 · LIMPIEZA Y ORDEN")

                            if os.path.exists(pantalla_04):
                                import subprocess

                                subprocess.Popen(
                                    [sys.executable, pantalla_04],
                                    cwd=os.path.dirname(pantalla_04)
                                )

                                self.running = False
                            else:
                                print("[DATA CHEF] ERROR: No existe:", pantalla_04)

            if self.mode == "game":
                self.update_player(dt)

            self.draw()

        pygame.quit()

if __name__=="__main__":
    Market().run()
