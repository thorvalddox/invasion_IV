import pygame




class Board:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800,600))
        self.tiles = {}
        self.font = pygame.font.Font("RobotoMono-Regular.ttf",12)

        Tile.generate(self,8,6)
        self.selected = self.tiles[(0,0)]
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
                    if ry < 10:
                        index = 0
                    elif ry > 90:
                        index = 1
                    elif rx < 10:
                        index = 2
                    elif rx > 90:
                        index = 3
                    if index >= 0:
                        amount = [0,1,0,-1][event.button]
                        self.selected.move_dir(index,amount)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if True or self.selected.team == 0:
                        self.target,_ = self.get_tile(*event.pos)
                        self.selected.move(self.target,100)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.handle_tiles()
            self.redraw()
    def redraw(self):
        for k,t in self.tiles.items():
            t.draw(k==self.selected)

        pygame.display.flip()

    def handle_tiles(self):
        for t in self.tiles.values():
            for n in t.border:
                if t.attack(n):
                    self.clock.tick(2)
                    self.redraw()



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




def transform_pointlist(pointlist,move,flip,mirror=...):
    mx,my = move
    for x,y in pointlist:
        if flip:
            x,y =  y,x
        if mirror is not ...:
            mirx,miry = mirror
            x,y = 2*mirx-x,2*miry-y
        yield (x+mx,y+my)


class Tile:
    def __init__(self,board,pos):
        self.board = board
        self.x,self.y = pos
        self.board.tiles[pos]=self
        self.team = -1
        self.soldiers = 0
        self.food = 0
        self.wood = 0
        self.iron = 0
        self.gold = 0
        self.moveto = {}
        self.border = [None,None,None,None]
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
        self.moveto[target] += amount
        self.soldiers -= amount
    def move_dir(self,dir,amount=0):
        self.move(self.border[dir],amount)
    def draw(self,selected = False):
        color = [(127,127,127),(255,0,0),(0,63,255),(0,127,0),(255,192,0)][self.team+1]
        relx = self.x*100
        rely = self.y*100
        pygame.draw.rect(self.board.screen, (0,0,0) if selected else (192,192,192) , (relx, rely , 100, 100), 0)
        pygame.draw.rect(self.board.screen,color,(relx+12,rely+12,76,76),0)
        for i,p in enumerate(((relx + 50, rely + 10),(relx + 50, rely + 90),(relx + 10, rely + 50),(relx + 90, rely + 50))):
            if self.border[i] is not None and self.moveto[self.border[i]]:

                pygame.draw.polygon(self.board.screen, (255, 255, 255),tuple(
                                    transform_pointlist(((50, 0), (30, 20), (70, 20)),(relx,rely),i//2,(50,50) if i%2 else ...)))
                self.board.draw_text(str(self.moveto[self.border[i]]), p)
        self.board.draw_text(str(self.soldiers),(relx+50,rely+50))

    def attack(self,other):
        if other is None:
            return False
        if self.team == other.team:
            other.soldiers += self.moveto[other]
            self.moveto[other] = 0
            return False
        soldiers = self.moveto[other]
        counter = other.moveto[self]
        if soldiers and counter:
            soldiers,counter = do_battle(soldiers,counter)
            self.moveto[other],other.moveto[self] = soldiers,counter
        if not soldiers:
            return False
        rem_sol,surv = do_battle(soldiers,other.soldiers)
        if surv:
            other.soldiers = surv
            self.moveto[other] = rem_sol
        elif rem_sol:
            other.team = self.team
            other.soldiers = rem_sol
            self.moveto[other] = 0
        else:
            other.soldiers = 0
            self.moveto[other] = 0
        return True





    @staticmethod
    def generate(board,w,h):
        for x in range(w):
            for y in range(h):
                Tile(board,(x,y))
        for x in range(w):
            for y in range(h):
                board.tiles[(x,y)].connect()


def do_battle(att,dff):
    if att > dff:
        return (att-dff**2//att,0)
    else:
        return reversed(do_battle(dff,att))

if __name__=="__main__":
    b = Board()
    tt = b.tiles[(1,1)]
    tt.team = 0
    tt.soldiers = 12
    tt = b.tiles[(4, 1)]
    tt.team = 1
    tt.soldiers = 15
    b.run()

