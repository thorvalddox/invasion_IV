import pygame
from random import random
from math import floor
from collections import namedtuple

class Board:
    def __init__(self,w,h):
        pygame.init()
        self.screen = pygame.display.set_mode((100*w,100*h))
        self.tiles = {}
        self.font = pygame.font.Font("RobotoMono-Regular.ttf",12)

        Tile.generate(self,w,h)
        self.selected = self.tiles[(0,0)]
    def wait(self,milliseconds):
        pygame.time.wait(milliseconds)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
    def run(self):
        self.clock = pygame.time.Clock()
        while True:
            self.clock.tick(20)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.selected,rel = self.get_tile(*event.pos)
                    rx,ry = rel
                    index = -1
                    if ry < 20:
                        index = 0
                    elif ry > 80:
                        index = 1
                    elif rx < 20:
                        index = 2
                    elif rx > 80:
                        index = 3
                    if index >= 0:
                        try:
                            amount = [0,1,0,-1][event.button]
                            self.smartmove(self.selected.border[index],amount)
                        except IndexError:
                            pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    target,_ = self.get_tile(*event.pos)
                    self.smartmove(target,100 if event.button == 3 else 1)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.handle_tiles()
                    movbuttons = (pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT)
                    if event.key in movbuttons:
                        target = self.selected.border[movbuttons.index(event.key)]
                        if target is not None:
                            if event.mod & pygame.KMOD_SHIFT:
                                self.smartmove(target,1)
                            elif event.mod & pygame.KMOD_CTRL:
                                self.smartmove(target, 100)
                            else:
                                self.selected = target
            self.redraw()

    def smartmove(self,target,amount):
        if target not in self.selected.moveto:
            return
        if self.selected.team == 0 and target.team == 0:
            if target.moveto[self.selected] > 0:
                target.move(self.selected, -amount)
            else:
                self.selected.move(target, amount)
        elif self.selected.team == 0:
            self.selected.move(target, amount)
        elif target.team == 0:
            target.move(self.selected, -amount)


    def redraw(self):
        for k,t in self.tiles.items():
            t.draw(t==self.selected)

        pygame.display.flip()

    def handle_tiles(self):
        for t in self.tiles.values():
            if t.team > 0:
                t.handle_AI_prior()
        self.redraw()
        self.wait(2000)

        allattacks = {}
        for t in self.tiles.values():
            for n in t.border:
                if n is None:
                    continue
                if t.moveto[n]:
                    allattacks[(t,n)] = (-(t.team==n.team),-(n.team==-1 or n.soldiers==0),t.moveto[n],random())
        for (t,n) in sorted(allattacks,key=allattacks.get):
            if t.attack(n):
                self.wait(500)
                self.redraw()
        self.wait(1000)
        for t in self.tiles.values():
            t.handle()
            t.team = t.occ



    def draw_text(self,text,midpos):
        x,y = midpos
        stext = self.font.render(text,True,(0,0,0))
        self.screen.blit(stext,(x-0.5*stext.get_width(),y-0.5*stext.get_height()))

    def get_tile_data(self,px,py):
        x,y = px//100,py//100
        rx,ry = px%100,py%100
        return (x,y),(rx,ry)

    def get_tile(self,px,py):
        pos,rel = self.get_tile_data(px,py)
        return self.tiles[pos],rel

    def build_village(self,team,x,y):
        tt = self.tiles[(x,y)]
        tt.occ = team
        tt.team = team
        tt.soldiers = 20
        tt.addtileprop(TileProps.village)
        tt.addtileprop(TileProps.hills)
        for i,j in ((x+1,y),(x-1,y)):
            try:
                tt = self.tiles[(i, j)]
                tt.occ = team
                tt.team = team
                tt.addtileprop(TileProps.farm)

            except KeyError:
                pass
        for i, j in ((x, y + 1), (x, y - 1)):
            try:
                tt = self.tiles[(i, j)]
                tt.occ = team
                tt.team = team
                tt.addtileprop(TileProps.forest)

            except KeyError:
                pass
        for i, j in ((x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)):
            try:
                tt = self.tiles[(i, j)]
                tt.occ = team
                tt.team = team
                tt.addtileprop(TileProps.tower)
            except KeyError:
                pass






def transform_pointlist(pointlist,move,flip,mirror=...):
    mx,my = move
    for x,y in pointlist:
        if flip:
            x,y =  y,x
        if mirror is not ...:
            mirx,miry = mirror
            x,y = 2*mirx-x,2*miry-y
        yield (x+mx,y+my)


TileProp = namedtuple("TileProp","image,regen,defence,maxmove,maxsup")
Default = TileProp("",0,0,15,20)

def load_tilepop(filename,regen,defence,maxmove,maxsup):
    return TileProp(pygame.image.load(filename),regen,defence,maxmove,maxsup)

class TileProps:
    forest = load_tilepop("forest.png",0,0,-5,-5)
    hills = load_tilepop("hills.png",0,1,-5,-5)
    mountain = load_tilepop("mountain.png",0,1,-15,-10)
    farm = load_tilepop("farm.png",1,-1,0,+5)
    village = load_tilepop("settle.png",3,2,0,+15)
    tower = load_tilepop("tower.png",0,3,-2,+10)
    castle = load_tilepop("castle.png",5,4,-5,+25)



class Tile:
    soldier_img = pygame.image.load("soldier.png")
    tank_img = pygame.image.load("tank.png")
    plane_img = pygame.image.load("plane.png")
    def __init__(self,board,pos):
        self.board = board
        self.x,self.y = pos
        self.board.tiles[pos]=self
        self.team = -1
        self.occ = self.team
        self.soldiers = 0
        self.food = 0
        self.wood = 0
        self.iron = 0
        self.gold = 0
        self.tileprops = []
        self.moveto = {}
        self.movefrom = {}
        self.border = [None,None,None,None]
    def getprop(self,name):
        ret = Default.__getattribute__(name)
        ret += sum(x.__getattribute__(name) for x in self.tileprops)
        return ret
    def addtileprop(self,tileprop):
        self.tileprops.append(tileprop)
    def connect(self):
        for i,(a,b) in enumerate(((0,-1),(0,1),(-1,0),(1,0))):#up down left right
            self.border[i] = self.board.tiles.get((self.x+a,self.y+b),None)
        self.moveto = {x:0 for x in self.border if x is not None}
    def move(self,target,amount=0):
        if not target in self.moveto.keys():
            return
        if amount>self.soldiers:
            amount = self.soldiers
        elif not amount or amount < -self.moveto[target]:
            amount = -self.moveto[target]
        if amount + self.moveto[target] > target.getprop("maxmove"):
            amount = target.getprop("maxmove") - self.moveto[target]
        self.moveto[target] += amount
        self.soldiers -= amount
    def move_dir(self,dir,amount=0):
        self.move(self.border[dir],amount)
    def draw(self,selected = False):
        color = [(127,127,127),(255,0,0),(0,63,255),(0,127,0),(255,192,0)][self.occ+1]
        relx = self.x*100
        rely = self.y*100
        pygame.draw.rect(self.board.screen, (0,0,0) if selected else (192,192,192) , (relx, rely , 100, 100), 0)
        pygame.draw.rect(self.board.screen,color,(relx+4,rely+4,92,92),0)
        if self.occ != self.team:
            color = [(127, 127, 127), (255, 0, 0), (0, 63, 255), (0, 127, 0), (255, 192, 0)][self.team + 1]
        else:
            color = 255,255,255
        for i,t in enumerate(self.tileprops):
            self.board.screen.blit(t.image,(relx+20+16*i,rely+20))
        #if self.getprop("regen"):
        #    pygame.draw.rect(self.board.screen, (0,255,255), (relx + 12, rely + 12, 76, 76), 4)
        for i,p in enumerate(((relx + 50, rely + 10),(relx + 50, rely + 90),(relx + 10, rely + 50),(relx + 90, rely + 50))):
            if self.border[i] is not None and self.moveto[self.border[i]]:
                if self.border[i].team in (self.team,-1) :
                    plist = (60,0),(40, 0), (30, 20), (70, 20)
                else:
                    plist = (50, 0), (30, 20), (70, 20)
                pygame.draw.polygon(self.board.screen, color,tuple(
                                    transform_pointlist(plist,(relx,rely),i//2,(50,50) if i%2 else ...)))
                self.board.draw_text(str(self.moveto[self.border[i]]), p)
        #for i,p in enumerate(("regen","defence","maxmove","maxsup")):
        #    self.board.draw_text(str(self.getprop(p)), (relx + 30 + 40*(i//2), rely + 60 + 20*(i%2) ))
        for i in range(self.soldiers%5):
            self.board.screen.blit(Tile.soldier_img,(relx+20+15*i,rely+40))
        for i in range((self.soldiers // 5)%5):
            self.board.screen.blit(Tile.tank_img, (relx + 20 + 15 * i, rely + 56))
        for i in range(self.soldiers // 25):
            self.board.screen.blit(Tile.plane_img, (relx + 20 + 15 * i, rely + 72))
        #self.board.draw_text(str(self.soldiers),(relx+50,rely+40))
    def handle(self):
        if self.soldiers > self.getprop("maxsup"):
            self.soldiers = self.getprop("maxsup")
        if self.getprop("regen") >= 0 and self.team >= 0:
            self.soldiers += self.getprop("regen")
    def update(self,board):
        self.movefrom = {}
        for t in board.tiles.values():
            for k,v in t.moveto.items():
                if k == self:
                    self.movefrom[t] = v
    def attack(self,other):
        if other is None:
            return False
        if self.team == other.occ:
            other.soldiers += self.moveto[other]
            self.moveto[other] = 0
            return True
        soldiers = self.moveto[other]
        counter = other.moveto[self]
        if soldiers and counter:
            soldiers,counter = do_battle(soldiers,counter)
            self.moveto[other],other.moveto[self] = soldiers,counter
        if not soldiers:
            return True
        counter = other.soldiers
        old_counter = counter
        if counter > 0:
            counter += self.getprop("defence")
        rem_sol,surv = do_battle(soldiers,counter)
        if surv > old_counter:
            surv = old_counter
        if surv:
            other.soldiers = surv
            self.moveto[other] = rem_sol
        elif rem_sol:
            other.occ = self.team
            other.soldiers = rem_sol
            self.moveto[other] = 0
        else:
            other.soldiers = 0
            self.moveto[other] = 0
        return True

    def handle_AI_spread(self):
        s = self.soldiers // (len(self.moveto) + 1)
        for k in self.moveto.keys():
            self.move(k, s)

    def handle_AI_prior(self,splitlist=(80,15,10,0)):
        slist = [int(floor(x/100*self.soldiers)) for x in splitlist]
        targetlist = sorted(self.moveto,key=self.get_priority)
        for i,t in enumerate(targetlist):
            amount = slist[i]
            self.move(t,amount)


    def get_priority(self,target):
        if self.team == target.team or target.team == -1:
            return (1,target.soldiers,-target.getprop("regen"),random())
        else:
            return (0,-target.getprop("regen"),target.soldiers,random())




    @staticmethod
    def generate(board,w,h):
        for x in range(w):
            for y in range(h):
                Tile(board,(x,y))
        for x in range(w):
            for y in range(h):
                board.tiles[(x,y)].connect()


def do_battle(att,dff):
    if att == dff:
        return 0,0
    elif att >dff:
        return att-dff**2//att,0
    else:
        return reversed(do_battle(dff,att))



if __name__=="__main__":
    b = Board(4,4)
    b.build_village(0,0,0)
    b.build_village(1,3,0)
    b.build_village(2,0,3)
    b.build_village(3,3,3)
    b.run()

