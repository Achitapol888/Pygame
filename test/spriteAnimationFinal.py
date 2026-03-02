import os,sys
import pygame

#setup
WIDTH = 640
HEIGHT = 640
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Sprite Animation")
clock = pygame.time.Clock()

#game classes and objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.walkNorths = [pygame.image.load("HM_North_Stand.png").convert(),
                          pygame.image.load("HM_North_Walk_Lt.png").convert(),
                          pygame.image.load("HM_North_Walk_Rt.png").convert()]
        self.walkEasts = [pygame.image.load("HM_East_Stand.png").convert(),
                          pygame.image.load("HM_East_Walk_Lt.png").convert(),
                          pygame.image.load("HM_East_Walk_Rt.png").convert()]
        self.walkSouths = [pygame.image.load("HM_South_Stand.png").convert(),
                          pygame.image.load("HM_South_Walk_Lt.png").convert(),
                          pygame.image.load("HM_South_Walk_Rt.png").convert()]
        self.walkWests = [pygame.image.load("HM_West_Stand.png").convert(),
                          pygame.image.load("HM_West_Walk_Lt.png").convert(),
                          pygame.image.load("HM_West_Walk_Rt.png").convert()]
        self.attackNorths = [pygame.image.load("HM_North_Attack_1.png").convert(),
                             pygame.image.load("HM_North_Attack_2.png").convert(),
                             pygame.image.load("HM_North_Attack_3.png").convert(),
                             pygame.image.load("HM_North_Attack_4.png").convert(),
                             pygame.image.load("HM_North_Stand.png").convert()]
        self.attackEasts = [pygame.image.load("HM_East_Attack_1.png").convert(),
                            pygame.image.load("HM_East_Attack_2.png").convert(),
                            pygame.image.load("HM_East_Attack_3.png").convert(),
                            pygame.image.load("HM_East_Attack_4.png").convert(),
                            pygame.image.load("HM_East_Stand.png").convert()]
        self.attackSouths = [pygame.image.load("HM_South_Attack_1.png").convert(),
                             pygame.image.load("HM_South_Attack_2.png").convert(),
                             pygame.image.load("HM_South_Attack_3.png").convert(),
                             pygame.image.load("HM_South_Attack_4.png").convert(),
                             pygame.image.load("HM_South_Stand.png").convert()]
        self.attackWests = [pygame.image.load("HM_West_Attack_1.png").convert(),
                            pygame.image.load("HM_West_Attack_2.png").convert(),
                            pygame.image.load("HM_West_Attack_3.png").convert(),
                            pygame.image.load("HM_West_Attack_4.png").convert(),
                            pygame.image.load("HM_West_Stand.png").convert()]
        self.actionSits = [pygame.image.load("HM_Sit_1.png").convert(),
                           pygame.image.load("HM_Sit_2.png").convert(),
                           pygame.image.load("HM_Sit_3.png").convert(),
                           pygame.image.load("HM_Sit_4.png").convert(),
                           pygame.image.load("HM_Sit_5.png").convert()]

        self.index = 0
        self.image = self.walkSouths[self.index]
        self.rect = pygame.Rect(0,0,64,64)
        self.dir = 5
        self.lastDir = 5
        self.sit = False
        self.ani_speed = 1
        self.interFrame = 5
        self.attacking = 0
        self.playerSpeed = 4

    def update(self):
        self.ani_speed += 1
        if self.dir == 0:
            self.rect.y -= self.playerSpeed
            if self.ani_speed >= self.interFrame:
                self.ani_speed = 1
                self.index +=1
                if self.index >= len(self.walkNorths):
                    self.index =0;
                self.image = self.walkNorths[self.index]
        elif self.dir == 1:
            self.rect.x += self.playerSpeed
            if self.ani_speed >= self.interFrame:
                self.ani_speed = 1
                self.index +=1
                if self.index >= len(self.walkEasts):
                    self.index =0;
                self.image = self.walkEasts[self.index]
        elif self.dir == 2:
            self.rect.y += self.playerSpeed
            if self.ani_speed >= self.interFrame:
                self.ani_speed = 1
                self.index +=1
                if self.index >= len(self.walkSouths):
                    self.index =0;
                self.image = self.walkSouths[self.index]
        elif self.dir == 3:
            self.rect.x -= self.playerSpeed
            if self.ani_speed >= self.interFrame:
                self.ani_speed = 1
                self.index +=1
                if self.index >= len(self.walkWests):
                    self.index =0;
                self.image = self.walkWests[self.index]

        if self.attacking:
            if self.ani_speed >= 4:
                self.ani_speed = 1
                self.index +=1
            if self.index >= len(self.attackNorths):
                self.index =1
                self.attacking = 0
            elif self.lastDir == 0:
                self.image = self.attackNorths[self.index]
            elif self.lastDir == 1:
                self.image = self.attackEasts[self.index]
            elif self.lastDir == 2:
                self.image = self.attackSouths[self.index]
            elif self.lastDir == 3:
                self.image = self.attackWests[self.index]

        if self.sit:
            if self.ani_speed >= 60:
                self.ani_speed = 1
                self.index +=1
                if self.index >= len(self.actionSits):
                    self.index =0;
                    self.sit = False
                self.image = self.actionSits[self.index]
class TileMap(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.tileImages = [pygame.image.load("tile_1.png").convert(),
                           pygame.image.load("tile_2.png").convert(),
                           pygame.transform.flip(pygame.image.load("tile_2.png").convert(), 0, 1)]
        self.tileSize = self.tileImages[0].get_width()
        self.map = [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [1,1,1,1,1,1,1,1,1,1],
                    [0,0,0,0,0,0,0,0,0,0],
                    [2,2,2,2,2,2,2,2,2,2],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]]

        self.image = pygame.surface.Surface((WIDTH,HEIGHT))
        self.rect = self.image.get_rect()
        self.loadMap()
        self.px =0
        self.py =0
    def loadMap(self):
        x = 0
        y = 0
        for y in range(int(HEIGHT/self.tileSize)):
            for x in range (int(WIDTH/self.tileSize)):
                self.image.blit(self.tileImages[self.map[y][x]],(x*self.tileSize,y*self.tileSize))

    def update(self):

        for self.py in range(int(HEIGHT/self.tileSize)):
            for self.px in range (int(WIDTH/self.tileSize)):
                self.image.blit(self.tileImages[self.map[self.px][self.py]],(self.py*self.tileSize,self.px*self.tileSize))


allsprites = pygame.sprite.Group()
tileMap = TileMap()
allsprites.add(tileMap)
player = Player()
allsprites.add(player)
screen.blit(tileMap.image,(0,0))
pygame.display.flip()


#game cycle
going = 1
while going:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = 0
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_UP:
                player.dir = 0
                player.lastDir = player.dir
            if event.key == pygame.K_RIGHT:
                player.dir = 1
                player.lastDir = player.dir
            if event.key == pygame.K_DOWN:
                player.dir = 2
                player.lastDir = player.dir
            if event.key == pygame.K_LEFT:
                player.dir = 3
                player.lastDir = player.dir
            if event.key == pygame.K_SPACE:
                player.attacking = 1
                player.index = 0

        if event.type == pygame.KEYUP:
            player.dir = 5
            if event.key == pygame.K_s:
                player.sit = True

    #screen.fill((0,0,0))
    allsprites.update()

   # screen.blit(tileMap.image,player.rect.inflate((10,10)), player.rect.inflate((10,10)))
    allsprites.draw(screen)
    pygame.display.flip()

pygame.quit()
