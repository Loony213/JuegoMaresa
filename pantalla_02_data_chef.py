import os, sys, math, random
import pygame

pygame.init()

WIDTH, HEIGHT = 1536, 864
FPS = 60
BG=(250,245,236); ORANGE=(247,116,18); BLUE=(26,104,210)
DARK=(39,49,59); WHITE=(255,255,255); MUTED=(93,103,112)
LIGHT_BLUE=(235,244,255); LIGHT_ORANGE=(255,239,221)

BASE=os.path.dirname(os.path.abspath(__file__))
ASSETS=os.path.join(BASE,"assets")

def load_img(name, max_size=None):
    path=os.path.join(ASSETS,name)
    if not os.path.exists(path):
        print("[DATA CHEF] No existe:", path); return None
    try:
        img=pygame.image.load(path).convert_alpha()
        if max_size:
            mw,mh=max_size; w,h=img.get_size()
            if w>mw or h>mh:
                s=min(mw/w,mh/h)
                img=pygame.transform.smoothscale(img,(int(w*s),int(h*s)))
        return img
    except Exception as e:
        print("[DATA CHEF] Error:",e); return None

def rr(s,r,c,rad=20,border=0,bc=None):
    pygame.draw.rect(s,c,r,border_radius=rad)
    if border: pygame.draw.rect(s,bc or c,r,width=border,border_radius=rad)

def txt(s,v,f,c,p,center=False):
    a=f.render(v,True,c); r=a.get_rect()
    r.center=p if center else r.center
    if not center: r.topleft=p
    s.blit(a,r); return r

class Particle:
    def __init__(self): self.x=random.randrange(WIDTH); self.y=random.randrange(HEIGHT); self.sp=random.uniform(.2,.6)
    def update(self):
        self.y-=self.sp
        if self.y<-10: self.y=HEIGHT+10; self.x=random.randrange(WIDTH)
    def draw(self,s): pygame.draw.circle(s,(247,116,18,55),(int(self.x),int(self.y)),2)

class App:
    def __init__(self):
        self.window=pygame.display.set_mode((0,0),pygame.RESIZABLE)
        pygame.display.set_caption("DATA CHEF | MARESA - Misión")
        self.screen=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        self.clock=pygame.time.Clock(); self.scale=1; self.ox=0; self.oy=0
        self.running=True; self.t=0

        role=sys.argv[1].lower() if len(sys.argv)>1 else "tecnologia"
        self.role="rrhh" if role in ("rrhh","recursos humanos","recursos_humanos") else "tecnologia"
        if self.role=="tecnologia":
            self.role_name="TECNOLOGÍA"; self.role_color=BLUE
            self.role_img_name="tecnologia.png"
        else:
            self.role_name="RECURSOS HUMANOS"; self.role_color=ORANGE
            self.role_img_name="rrhh.png"

        self.chef=load_img("chef.png",(420,535))
        self.person=load_img(self.role_img_name,(390,390))
        self.logo=load_img("logo_maresa.png",(245,70))
        self.parts=[Particle() for _ in range(45)]
        self.fonts={
            "tiny":pygame.font.SysFont("Arial",14),
            "body":pygame.font.SysFont("Arial",20),
            "bold":pygame.font.SysFont("Arial",20,bold=True),
            "role":pygame.font.SysFont("Arial",27,bold=True),
            "title":pygame.font.SysFont("Arial",54,bold=True),
            "big":pygame.font.SysFont("Arial",68,bold=True),
            "button":pygame.font.SysFont("Arial",25,bold=True)
        }
        print("[DATA CHEF] Rol:",self.role_name)
        print("[DATA CHEF] Chef:", "OK" if self.chef else "FALTA assets/chef.png")
        print("[DATA CHEF] Personaje:", "OK" if self.person else "FALTA assets/"+self.role_img_name)

    def background(self):
        self.screen.fill(BG)
        for p in self.parts: p.draw(self.screen)
        pygame.draw.ellipse(self.screen,(255,229,199),(1170,-120,520,350))
        pygame.draw.ellipse(self.screen,(255,231,204),(-150,650,520,330))
        pygame.draw.circle(self.screen,(255,224,191),(365,82),10)
        pygame.draw.circle(self.screen,(255,224,191),(1450,465),9)

    def header(self):
        if self.logo: self.screen.blit(self.logo,(35,27))
        else: txt(self.screen,"maresa",self.fonts["title"],ORANGE,(35,25))
        txt(self.screen,"♨",self.fonts["title"],ORANGE,(580,28))
        txt(self.screen,"¡BIENVENIDO A",self.fonts["title"],DARK,(665,35))
        txt(self.screen,"DATA",self.fonts["big"],DARK,(575,96))
        txt(self.screen,"CHEF!",self.fonts["big"],ORANGE,(805,96))
        rr(self.screen,pygame.Rect(570,177,470,48),(255,247,233),24,2,(249,210,171))
        txt(self.screen,"Tu cocina, tus datos, mejores decisiones.",self.fonts["bold"],(197,92,18),(805,201),True)
        pygame.draw.circle(self.screen,ORANGE,(805,225),6+int(2*math.sin(self.t*4)))

    def chef_card(self):
        card=pygame.Rect(135,260,610,430)
        rr(self.screen,card,WHITE,28,3,ORANGE)
        rr(self.screen,pygame.Rect(137,262,606,338),(255,241,224),26)
        if self.chef:
            r=self.chef.get_rect(); r.midbottom=(340,int(605+math.sin(self.t*2.2)*4))
            self.screen.blit(self.chef,r)
        else: txt(self.screen,"SUBE assets/chef.png",self.fonts["body"],MUTED,(300,430),True)
        ix,iy=580,340
        pygame.draw.circle(self.screen,ORANGE,(ix,iy),35,4)
        txt(self.screen,"CHEF MAESTRO",self.fonts["role"],ORANGE,(ix,415),True)
        txt(self.screen,"“Claro que sí.”",self.fonts["bold"],DARK,(ix,470),True)
        rr(self.screen,pygame.Rect(137,600,606,88),ORANGE,0)
        txt(self.screen,"✦  Experto en calidad de datos",self.fonts["bold"],WHITE,(240,628))
        txt(self.screen,"Te guía con recetas y buenas prácticas.",self.fonts["body"],WHITE,(240,660))

    def role_card(self):
        card=pygame.Rect(770,260,630,430)
        rr(self.screen,card,WHITE,28,3,self.role_color)
        top=pygame.Rect(772,262,626,338)
        rr(self.screen,top,LIGHT_BLUE if self.role=="tecnologia" else LIGHT_ORANGE,26)
        ix,iy=885,348
        pygame.draw.circle(self.screen,self.role_color,(ix,iy),42,4)
        if self.person:
            r=self.person.get_rect(); r.midbottom=(1265,int(600+math.sin(self.t*2)*3))
            self.screen.blit(self.person,r)
        else: txt(self.screen,"SUBE assets/"+self.role_img_name,self.fonts["body"],MUTED,(1250,430),True)
        txt(self.screen,self.role_name,self.fonts["role"],self.role_color,(ix,420),True)
        lines=["“Quiero crear un panel","específico para",""+self.role_name+".”"]
        y=465
        for line in lines:
            txt(self.screen,line,self.fonts["bold"],DARK,(ix,y),True); y+=28
        rr(self.screen,pygame.Rect(772,600,626,88),self.role_color,0)
        txt(self.screen,"▣  Enfocado en tus necesidades",self.fonts["bold"],WHITE,(875,628))
        txt(self.screen,"Crea paneles y visores personalizados.",self.fonts["body"],WHITE,(875,660))

    def mission(self):
        box=pygame.Rect(255,720,1025,95)
        rr(self.screen,box,(255,249,239),26,2,(248,213,177))
        txt(self.screen,"◉  MISIÓN",self.fonts["role"],ORANGE,(768,752),True)
        txt(self.screen,"El objetivo es crear un panel específico para "+self.role_name+",",self.fonts["body"],DARK,(768,785),True)
        txt(self.screen,"utilizando datos de calidad para generar información confiable y accionable.",self.fonts["body"],DARK,(768,810),True)

    def button(self):
        pos=self.logical(pygame.mouse.get_pos())
        r=pygame.Rect(600,825,335,54)
        hover=r.collidepoint(pos)
        b=r.move(0,-3 if hover else 0)
        rr(self.screen,b,ORANGE,18)
        txt(self.screen,"🚀  CONTINUAR",self.fonts["button"],WHITE,(b.centerx-10,b.centery),True)
        pygame.draw.polygon(self.screen,WHITE,[(b.right-48,b.centery-9),(b.right-33,b.centery),(b.right-48,b.centery+9)])

    def logical(self,pos):
        return (int((pos[0]-self.ox)/self.scale),int((pos[1]-self.oy)/self.scale))

    def draw(self):
        self.background(); self.header(); self.chef_card(); self.role_card(); self.mission(); self.button()
        ww,wh=self.window.get_size()
        self.scale=min(ww/WIDTH,wh/HEIGHT); rw=int(WIDTH*self.scale); rh=int(HEIGHT*self.scale)
        self.ox=(ww-rw)//2; self.oy=(wh-rh)//2
        img=pygame.transform.smoothscale(self.screen,(rw,rh))
        self.window.fill((232,232,232)); self.window.blit(img,(self.ox,self.oy)); pygame.display.flip()

    def run(self):
        while self.running:
            dt=self.clock.tick(FPS)/1000; self.t+=dt
            for p in self.parts: p.update()
            for e in pygame.event.get():
                if e.type==pygame.QUIT: self.running=False
                elif e.type==pygame.VIDEORESIZE: self.window=pygame.display.set_mode(e.size,pygame.RESIZABLE)
                elif e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: self.running=False
                elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                    if pygame.Rect(600,825,335,54).collidepoint(self.logical(e.pos)):
                        print("[DATA CHEF] CONTINUAR -> conectar pantalla 03")
            self.draw()
        pygame.quit()

if __name__=="__main__": App().run()
