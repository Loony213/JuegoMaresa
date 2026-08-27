
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
    r.center = p if center else r.topleft
    if not center:
        r.topleft = p
    s.blit(a, r)
    return r

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
        self.player_y = 690.0
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
        # 4 EDIFICIOS - SUBE ESTOS 4 PNG A assets/
        # =====================================================
        self.building_files = [
            "edificio_1.png",
            "edificio_2.png",
            "edificio_3.png",
            "edificio_4.png"
        ]

        self.buildings = [
            load_img(filename, (240, 380))
            for filename in self.building_files
        ]

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
    # MINIJUEGO: los caminos aparecen SOLO al pulsar EMPEZAR
    # =====================================================

    def draw_game_paths(self):
        # Camino hacia Base de Datos
        pygame.draw.polygon(
            self.screen, (155,138,108),
            [(705,700),(775,700),(310,555),(220,555)]
        )
        pygame.draw.polygon(
            self.screen, (220,203,171),
            [(710,694),(770,694),(315,550),(225,550)]
        )

        # Camino hacia Excel
        pygame.draw.polygon(
            self.screen, (155,138,108),
            [(805,700),(875,700),(1320,555),(1280,555)]
        )
        pygame.draw.polygon(
            self.screen, (220,203,171),
            [(810,694),(870,694),(1315,550),(1285,550)]
        )

        # Camino hacia fuente externa
        pygame.draw.polygon(
            self.screen, (155,138,108),
            [(750,720),(785,720),(515,800),(475,800)]
        )
        pygame.draw.polygon(
            self.screen, (220,203,171),
            [(755,714),(780,714),(515,794),(480,794)]
        )

        # Camino hacia chat
        pygame.draw.polygon(
            self.screen, (155,138,108),
            [(815,720),(850,720),(1115,800),(1150,800)]
        )
        pygame.draw.polygon(
            self.screen, (220,203,171),
            [(820,714),(845,714),(1115,794),(1145,794)]
        )

        # Plaza central
        pygame.draw.circle(self.screen, (155,138,108), (790,700), 88)
        pygame.draw.circle(self.screen, (220,203,171), (790,700), 80)

        # Señal central para dar sensación de videojuego.
        pygame.draw.rect(
            self.screen, (105,72,42),
            (784,630,12,75),
            border_radius=5
        )
        pygame.draw.polygon(
            self.screen, (105,72,42),
            [(790,642),(850,642),(850,658),(790,658)]
        )
        pygame.draw.polygon(
            self.screen, (105,72,42),
            [(790,678),(735,678),(735,694),(790,694)]
        )

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

        self.player_x += dx * self.player_speed * dt
        self.player_y += dy * self.player_speed * dt

        self.player_x = max(45, min(WIDTH-45, self.player_x))
        self.player_y = max(270, min(HEIGHT-20, self.player_y))

        self.check_building_collision()

    def check_building_collision(self):
        for index, (bx, by) in enumerate(self.game_building_positions):
            dx = self.player_x - bx
            dy = self.player_y - by

            if math.hypot(dx, dy) < 105:
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
                            self.player_y = 690.0
                            print("[DATA CHEF] EMPEZAR -> MINIJUEGO")
                            print("[DATA CHEF] Caminos activados")

                    elif self.mode == "wrong":
                        button = pygame.Rect(625,490,285,45)

                        if button.collidepoint(pos):
                            self.mode = "game"
                            self.player_x = 790.0
                            self.player_y = 690.0
                            print("[DATA CHEF] Reintento")

                    elif self.mode == "success":
                        # Aquí luego conectamos pantalla_04.
                        pass

            if self.mode == "game":
                self.update_player(dt)

            self.draw()

        pygame.quit()

if __name__=="__main__":
    Market().run()
